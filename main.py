from flask import Flask, render_template, request, redirect
from operator import itemgetter
import datetime
import json
import uuid

app = Flask(__name__)

db_file = 'db.json'
try:
    with open(db_file) as f:
        posts = json.load(f)
except FileNotFoundError:
    posts = []

@app.route("/")
def index():
    return redirect("/feed")


@app.route("/feed", methods=["GET", "POST"])
def feed():
    if request.method == "POST":
        title = request.form["title"]
        description = request.form["description"]
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        post_id = str(uuid.uuid4())
        post = {"id": post_id, "title": title, "description": description, "timestamp": timestamp}
        posts.insert(0, post)
        with open(db_file, 'w') as f:
            json.dump(posts, f, indent=4)
        return redirect("/feed", code=303)
    posts_sorted = sorted(posts, key=itemgetter("timestamp"), reverse=True)
    return render_template("base.html", posts=posts_sorted)


@app.route("/feed/share/<id>")
def share(id):
    post = next((p for p in posts if p["id"] == id), None)
    if not post:
        return "Post not found"
    return render_template("shared.html", post=post)

@app.route("/signup")
def signup():
    return render_template("signup.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.errorhandler(404)
def not_found(e):
    return render_template("404.html")


if __name__ == '__main__':
    app.run(debug=True)
