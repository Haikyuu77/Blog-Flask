
from flask import Flask, redirect, url_for, render_template, request, session, flash
from datetime import timedelta
from flask.sessions import NullSession
from flask.templating import render_template_string
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import backref

app = Flask(__name__)
app.secret_key = "konichiwa"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.permanent_session_lifetime = timedelta(minutes=30)

db = SQLAlchemy(app)
# Tip:use sessions to login and logout
# Database


class Psy(db.Model):
    ind = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    pwd = db.Column("Password", db.String(100))
    msg = db.relationship('Notes', backref='user')

    def __init__(self, name, email, pwd):
        self.name = name
        self.email = email
        self.pwd = pwd


class Notes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    blog = db.Column(db.String(500))
    blog_name = db.Column(db.String(100))
    user_id = db.Column(db.Integer, db.ForeignKey('psy.ind'))

    def __init__(self, blog, blog_name, user_id):
        self.blog = blog
        self.blog_name = blog_name
        self.user_id = user_id


# Login in page
@app.route("/", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        testmail = request.form["email"]
        testpwd = request.form["password"]
        found_user = Psy.query.filter_by(email=testmail, pwd=testpwd).first()
        if found_user:
            session["email"] = testmail
            session["password"] = testpwd
            session["user"] = found_user.name
            return redirect(url_for("blog"))
        else:
            flash("user does not exist", "error")
            return redirect(url_for("login"))
    else:
        return render_template("index.html")


# Sign in page
@app.route("/signup", methods=["POST", "GET"])
def signup():
    # post used for the case when we are passing data to the signup page
    if request.method == "POST":
        mail = request.form["email"]
        name = request.form["nm"]
        password = request.form["password"]
        if not mail or not name or not password:
            flash("Fill info", "info")
            return redirect(url_for("signup"))
        # database variable
        found_user = Psy.query.filter_by(email=mail).first()
        if found_user:
            flash("Gmail used !!", "error")
            return redirect(url_for("signup"))
        else:
            # database entry
            entry = Psy(name, mail, password)
            db.session.add(entry)
            db.session.commit()
        return redirect(url_for("login"))
    else:
        return render_template("signup.html")


# Blog page
@app.route("/blog")
def blog():
    return render_template("home.html")


# Creation page
@app.route("/write", methods=["POST", "GET"])
def write():
    if request.method == "POST":
        name = request.form["name"]
        blog = request.form["blog"]
        _user = Psy.query.filter_by(email=session["email"]).first()
        entry = Notes(blog, name, _user.ind)
        db.session.add(entry)
        db.session.commit()
        return redirect(url_for("blog"))
    else:
        if "flag" in session:
            session.pop("flag")
            return render_template("write.html", name=session["bname"], text=session["blog"])

        return render_template("write.html", name="", text="")


# Delete Blog
@app.route("/delete", methods=["POST", "GET"])
def delete():
    if request.method == "POST":
        name = request.form["blogname"]
        user_ = Notes.query.filter_by(blog_name=name).delete()
        if user_:
            db.session.commit()
            return redirect(url_for("blog"))
        else:
            return render_template("delete.html", content="Element not found!")
    else:
        return render_template("delete.html")


# Edit blog
@app.route("/update", methods=["POST", "GET"])
def update():
    if request.method == "POST":
        name = request.form["update"]
        user_ = Notes.query.filter_by(blog_name=name).first()
        if user_:
            blog = user_.blog
            bname = user_.blog_name
            session["blog"] = blog
            session["bname"] = bname
            session["flag"] = 1
            user_ = Notes.query.filter_by(blog_name=name).delete()
            db.session.commit()
            return redirect(url_for("write"))
        else:
            return render_template("update.html", content="Such a blog doesnt exist")
    else:
        return render_template("update.html")


# Logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# Database viewer
@ app.route("/view")
def view():
    return render_template("database.html", data=Psy.query.all())


# Trial function
@ app.route("/out")
def out():
    mail = session["email"]
    user_ = Psy.query.filter_by(email=mail).first()
    id = user_.ind
    return render_template("test.html", data=Notes.query.filter_by(user_id=id).all())


# Clear database
@ app.route("/clear")
def clear():
    db.session.query(Psy).delete()
    db.session.commit()
    db.session.query(Notes).delete()
    db.session.commit()
    return render_template("test.html", content="database cleared")


# Executing statement
if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)
