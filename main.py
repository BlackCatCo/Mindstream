from flask import Flask, render_template, request, redirect, make_response
from operator import itemgetter

# Maybe add global paw = True or False depending on this expression. (paw = pythonanywhere)
try:
    from myapp.scripts.database.handler import Handler
    from myapp.scripts.admin import Admin
except ImportError:
    from scripts.database.handler import Handler
    from scripts.admin import Admin



app = Flask(__name__)


handler = Handler()
posts = handler.posts.get_all()


admin = Admin(app, handler)
admin.run()


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
    for p in posts_sorted:
        p['comment-count'] = len(p['comments'])
    return render_template("feed.html", posts=posts_sorted, user=handler.user.get( request.cookies.get('key') ))


@app.route("/feed/share/<id>", methods=['GET', 'POST'])
def share(id):
    post = next((p for p in posts if p["id"] == id), None)
    if not post:
        return "Post not found"
    
    if request.method == "POST":
        comment_text = request.form.get('comment')
        if comment_text != '':
            user = handler.user.get( request.cookies.get('key') )
            if user != None:
                handler.posts.add_comment(id, comment_text, user['name'])
                return redirect(f"/feed/share/{id}", code=303)
                
            else:
                return redirect("/signup")

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
        
        res = make_response(render_template("user/signup.html", error=error))
        if key != None:
            res = make_response(redirect('/feed'))
            res.set_cookie('key', key, max_age=63072000) # Sets a cookie with the key for 2 years

        return res
    else:
        return render_template("user/signup.html", error=None)

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
        
        res = make_response(render_template("user/login.html", error=error))
        if key != None:
            res = make_response(redirect('/feed'))
            res.set_cookie('key', key, max_age=63072000) # Sets a cookie with the key for 2 years

        return res
    else:
        return render_template("user/login.html", error=None)

@app.route("/logout")
def logout():
    res = make_response(redirect('/feed'))
    res.set_cookie('key', '', max_age=0)
    return res


@app.route("/profile")
def profile():
    user = handler.user.get(request.cookies.get('key'))
    if user == None:
        return redirect('/signup')
    else:
        return redirect(f'/profile/{user["name"]}')

@app.route("/profile/<username>")
def profile_u(username):
    user = handler.user.get(request.cookies.get('key'))

    puser = handler.user.get_name(username)
    
    if puser == None:
        return render_template("404.html")
    else:
        info = handler.user.get_profile(puser['key'])
        return render_template('user/profile.html', user=user, info=info)



@app.errorhandler(404)
def not_found(e):
    return render_template("404.html")


if __name__ == '__main__':
    app.run(debug=True)
