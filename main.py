from flask import Flask, render_template, request, redirect, url_for, session
import json
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"

DATA_FILE = "helpers.json"
USER_FILE = "users.json"

def load_helpers():
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE,"r",encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def save_helpers(helpers):
    with open(DATA_FILE,"w",encoding="utf-8") as f:
        json.dump(helpers,f,indent=2,ensure_ascii=False)

def load_users():
    if not os.path.exists(USER_FILE):
        return []
    try:
        with open(USER_FILE,"r",encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def save_users(users):
    with open(USER_FILE,"w",encoding="utf-8") as f:
        json.dump(users,f,indent=2,ensure_ascii=False)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/helpers")
def helpers():
    helpers=load_helpers()
    return render_template("helpers.html",helpers=helpers)

@app.route("/search")
def search():
    query=request.args.get("q","").lower().strip()
    helpers=load_helpers()
    if query=="":
        return render_template("helpers.html",helpers=helpers)
    results=[h for h in helpers if any(query in h[k].lower() for k in ["name","skill","location","phone","email"] if k in h)]
    return render_template("helpers.html",helpers=results)

@app.route("/register",methods=["GET","POST"])
def register():
    if request.method=="POST":
        name=request.form["name"]
        email=request.form["email"]
        password=request.form["password"]
        users=load_users()
        if any(u["email"]==email for u in users):
            return render_template("register.html",error="Email already registered")
        users.append({"name":name,"email":email,"password":password})
        save_users(users)
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/login",methods=["GET","POST"])
def login():
    if request.method=="POST":
        email=request.form["email"]
        password=request.form["password"]
        users=load_users()
        for u in users:
            if u["email"]==email and u["password"]==password:
                session["logged_in"]=True
                session["user_email"]=email
                session["user_name"]=u["name"]
                return redirect(url_for("home"))
        return render_template("login.html",error="Invalid login credentials")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

@app.route("/add_helper",methods=["GET","POST"])
def add_helper():
    if "logged_in" not in session:
        return redirect(url_for("login"))
    if request.method=="POST":
        skill=request.form["skill"]
        location=request.form["location"]
        phone=request.form["phone"]
        helpers=load_helpers()
        helpers.append({
            "name":session["user_name"],
            "skill":skill,
            "location":location,
            "phone":phone,
            "email":session["user_email"]
        })
        save_helpers(helpers)
        return redirect(url_for("helpers"))
    return render_template("add_helper.html")

@app.route("/api/suggestions")
def get_suggestions():
    helpers=load_helpers()
    s=set()
    for h in helpers:
        for k in ["name","skill","location"]:
            s.add(h.get(k,""))
    return list(s)

if __name__=="__main__":
    app.run(host="0.0.0.0",port=5000)
