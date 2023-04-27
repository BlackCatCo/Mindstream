from flask import Flask, render_template, request, redirect, make_response
from operator import itemgetter

try:
    from myapp.scripts.database.handler import Handler
except ImportError:
    from scripts.database.handler import Handler



app = Flask(__name__)

# db_file = 'db.json'
# try:
#     with open(db_file) as f:
#         posts = json.load(f)
# except FileNotFoundError:
#     posts = []

handler = Handler()
posts = handler.posts.get_all()




@app.route("/")
def index():
    return redirect("/feed")


@app.route("/feed", methods=["GET", "POST"])
def feed():
    if request.method == "POST":
        title = request.form["title"]
        description = request.form["description"]

        key = request.cookies.get('key')
        username = 'Anonymous'
        if key != None:
            user = handler.user.get(key)
            username = user['name']

        handler.posts.add(title, description, username)

        return redirect("/feed", code=303)
    
    posts_sorted = sorted(posts, key=itemgetter("timestamp"), reverse=True)
    return render_template("base.html", posts=posts_sorted)


@app.route("/feed/share/<id>")
def share(id):
    post = next((p for p in posts if p["id"] == id), None)
    if not post:
        return "Post not found"
    return render_template("shared.html", post=post)

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        error = handler.user._check_proper_login(username, password)

        key = None
        if error == None:
            auth = handler.user.add(username, password)
            if auth:
                key = handler.user.get_name(username)['key']
            else:
                error = 'That username is already in use!'
        
        res = make_response(render_template("signup.html", error=error))
        if key != None:
            res = make_response(redirect('/feed'))
            res.set_cookie('key', key, max_age=63072000) # Sets a cookie with the key for 2 years

        return res
    else:
        return render_template("signup.html", error=None)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        error = handler.user._check_proper_login(username, password)

        key = None
        if error == None:
            auth = handler.user.check_login(username, password)
            if auth:
                key = handler.user.get_name(username)['key']
                key = handler.user.refresh_key(key)
            else:
                error = 'Authentication failed! Wrong username or password.'
        
        res = make_response(render_template("login.html", error=error))
        if key != None:
            res = make_response(redirect('/feed'))
            res.set_cookie('key', key, max_age=63072000) # Sets a cookie with the key for 2 years

        return res
    else:
        return render_template("login.html", error=None)

@app.errorhandler(404)
def not_found(e):
    return render_template("404.html")


if __name__ == '__main__':
    app.run(debug=True)
