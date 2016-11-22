from flask import render_template

from . import app
from .database import session, Entry

from flask import flash
from flask import request, redirect, url_for
from flask.ext.login import login_user, login_required, logout_user
from werkzeug.security import check_password_hash
from .database import User

PAGINATE_BY = 10

@app.route("/")
@app.route("/page/<int:page>/?limit=20")

def entries(page=1):
    # Zero-indexed page
    page_index = page - 1

    count = session.query(Entry).count()
    
    PAGINATE_BY = int(request.args.get('limit', 10))
    
    start = page_index * PAGINATE_BY
    end = start + PAGINATE_BY

    total_pages = (count - 1) // PAGINATE_BY + 1
    has_next = page_index < total_pages - 1
    has_prev = page_index > 0

    entries = session.query(Entry)
    entries = entries.order_by(Entry.datetime.desc())
    entries = entries[start:end]

    return render_template("entries.html",
        entries=entries,
        has_next=has_next,
        has_prev=has_prev,
        page=page,
        total_pages=total_pages
    )
    
@app.route("/")
@app.route("/entry/add", methods=["GET"])
@login_required
def add_entry_get():
    return render_template("add_entry.html")    

from flask.ext.login import current_user

@app.route("/entry/add", methods=["POST"])
@login_required
def add_entry_post():
    entry = Entry(
        title=request.form["title"],
        content=request.form["content"],
        author=current_user
    )
    session.add(entry)
    session.commit()
    return redirect(url_for("entries"))
   
@app.route("/entry/<int:id>")
#return 1 of id
def single_entry(id):
    #query for all entries
    entries = session.query(Entry)
    #match entries with id
    entries = entries.filter(Entry.id == id).all()
    return render_template("entries.html", entries=entries)
    
# GET to return existing entry
@app.route("/entry/<int:id>/edit", methods=["GET"])
@login_required
def edit_entry(id):
    entry = session.query(Entry)
    entry = entry.filter(Entry.id == id).first()
    return render_template("edit_entry.html", entry_title=entry.title, entry_content=entry.content)

# POST edited entry
@app.route("/entry/<int:id>/edit", methods=["POST"])
@login_required
def edit_entry_post(id):
    entry = session.query(Entry)
    entry = entry.filter(Entry.id == id).first()
    entry.title=request.form["title"]
    entry.content=request.form["content"]
    session.commit()
    return redirect(url_for("entries"))
    
@app.route("/entry/<int:id>/delete", methods=["GET"])
@login_required
def delete_entry(id):
    entry = session.query(Entry)
    entry = entry.filter(Entry.id == id).first()
    return render_template("delete_entry.html", entry_title=entry.title)

@app.route("/entry/<int:id>/delete", methods=["POST"])
@login_required
def delete_entry_post(id):
    entry = session.query(Entry)
    entry = entry.filter(Entry.id == id).first()
    session.delete(entry)
    session.commit()
    return redirect(url_for("entries"))
    
@app.route("/login", methods=["GET"])
def login_get():
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def login_post():
    email = request.form["email"]
    password = request.form["password"]
    user = session.query(User).filter_by(email=email).first()
    if not user or not check_password_hash(user.password, password):
        flash("Incorrect username or password", "danger")
        return redirect(url_for("login_get"))

    login_user(user)
    return redirect(request.args.get('next') or url_for("entries"))
    
@app.route("/logout", methods=["GET"])
def logout_get():
    logout_user()
    return redirect(url_for ("login_get"))