
# A very simple Flask Hello World app for you to get started with...

from flask import Flask, redirect, render_template, request, url_for
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.sql.expression import func

app = Flask(__name__)
app.config["DEBUG"] = True

SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
    username="sleppy",
    password="george22",
    hostname="sleppy.mysql.pythonanywhere-services.com",
    databasename="sleppy$goons",
)
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
db = SQLAlchemy(app)

class Goon(db.Model):
    __tablename__ = "goons"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    rank = db.Column(db.Float)

@app.route("/", methods=["GET", "POST"])
def userlist():
    if request.method == "GET":
        return render_template("userlist.html", goons=Goon.query.all())

    goon = Goon(name=request.form["name"], rank=0)
    db.session.add(goon)
    db.session.commit()
    return redirect(url_for("userlist"))

@app.route("/duel", methods=["GET", "POST"])
def duel():
    if request.method == "GET":
        return render_template("duel.html", goons=Goon.query.order_by(func.rand()).limit(2).all())

    return redirect(url_for("duel"))


