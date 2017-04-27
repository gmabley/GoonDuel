from flask import Flask, redirect, render_template, request, url_for
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.sql.expression import func
import string, random, datetime

app = Flask(__name__)
app.config["DEBUG"] = False

SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
    username="sleppy",
    password="notarealpass",
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
    vibes = db.Column(db.Float)

class Code(db.Model):
    __tablename__ = "codes"

    code = db.Column(db.String(5), primary_key=True)
    time = db.Column(db.DateTime)

@app.route("/", methods=["GET"])
def userlist():
    return render_template("userlist.html", goons1=Goon.query.order_by(Goon.rank.desc()).all(), goons2=Goon.query.order_by(Goon.vibes.desc()).all())

@app.route("/duel", methods=["GET", "POST"])
def duel():
    if request.method == "GET":
        timenow = datetime.datetime.utcnow()
        key = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5))
        key = Code(code=key, time=timenow)
        db.session.add(key)
        db.session.commit()
        return render_template("duel.html", goons=Goon.query.order_by(func.rand()).limit(2).all(), key=key)

    timenow = datetime.datetime.utcnow()
    thresh = timenow - datetime.timedelta(minutes=3)
    old = db.session.query(Code).filter(Code.time < thresh).all()
    for i in old:
        db.session.delete(i)
        db.session.commit()
    key = request.form["code"]
    secret = Code.query.filter_by(code=key).first()
    if (secret is None):
        return "Invalid key.  You are either a dirty cheater, or you waited too long to vote."
    if "skip" in request.form:
        db.session.delete(secret)
        db.session.commit()
        return redirect(url_for("duel"))
    elif "one" in request.form:
        name1 = request.form["one"].split(" is better than ")[0]
        name2 = request.form["one"].split(" is better than ")[1]
        goon1=Goon.query.filter_by(name=name1).first()
        goon2=Goon.query.filter_by(name=name2).first()
        rank1 = goon1.rank
        rank2 = goon2.rank
        goon1.rank = elo(rank1, rank2, 0)
        goon2.rank = elo(rank1, rank2, 1)
        db.session.delete(secret)
        db.session.commit()
        return redirect(url_for("duel"))
    elif "two" in request.form:
        name1 = request.form["two"].split(" is better than ")[0]
        name2 = request.form["two"].split(" is better than ")[1]
        goon1=Goon.query.filter_by(name=name1).first()
        goon2=Goon.query.filter_by(name=name2).first()
        rank1 = goon1.rank
        rank2 = goon2.rank
        goon1.rank = elo(rank1, rank2, 0)
        goon2.rank = elo(rank1, rank2, 1)
        db.session.delete(secret)
        db.session.commit()
        return redirect(url_for("duel"))

@app.route("/vibes", methods=["GET", "POST"])
def vibes():
    goons=Goon.query.order_by(func.rand()).limit(2).all()
    if request.method == "GET":
        timenow = datetime.datetime.utcnow()
        key = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5))
        key = Code(code=key, time=timenow)
        db.session.add(key)
        db.session.commit()
        return render_template("vibes.html", goons=goons, key=key)

    timenow = datetime.datetime.utcnow()
    thresh = timenow - datetime.timedelta(minutes=2)
    old = db.session.query(Code).filter(Code.time < thresh).all()
    for i in old:
        db.session.delete(i)
        db.session.commit()
    key = request.form["code"]
    secret = Code.query.filter_by(code=key).first()
    if (secret is None):
        return "fuck you, stop trying to cheat!"
    if "skip" in request.form:
        db.session.delete(secret)
        db.session.commit()
        return redirect(url_for("vibes"))
    elif "one" in request.form:
        name1 = request.form["one"].split(" has better vibes than ")[0]
        name2 = request.form["one"].split(" has better vibes than ")[1]
        goon1=Goon.query.filter_by(name=name1).first()
        goon2=Goon.query.filter_by(name=name2).first()
        vibes1 = goon1.vibes
        vibes2 = goon2.vibes
        goon1.vibes = elo(vibes1, vibes2, 0)
        goon2.vibes = elo(vibes1, vibes2, 1)
        db.session.delete(secret)
        db.session.commit()
        return redirect(url_for("vibes"))
    elif "two" in request.form:
        name1 = request.form["two"].split(" has better vibes than ")[0]
        name2 = request.form["two"].split(" has better vibes than ")[1]
        goon1=Goon.query.filter_by(name=name1).first()
        goon2=Goon.query.filter_by(name=name2).first()
        vibes1 = goon1.vibes
        vibes2 = goon2.vibes
        goon1.vibes = elo(vibes1, vibes2, 0)
        goon2.vibes = elo(vibes1, vibes2, 1)
        db.session.delete(secret)
        db.session.commit()
        return redirect(url_for("vibes"))

@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "GET":
        return render_template("add.html")

    goon = Goon(name=request.form["name"], rank=1000, vibes=1000)
    db.session.add(goon)
    db.session.commit()
    return redirect(url_for("add"))

def elo(win, loss, result):
    adjustWin = pow(10, (win / 400))
    adjustLoss = pow(10, (loss / 400))
    expectedWin = adjustWin / (adjustWin + adjustLoss)
    expectedLoss = adjustLoss / (adjustWin + adjustLoss)
    newWin = win + 32 * (1 - expectedWin)
    newLoss = loss + 32 * (0 - expectedLoss)
    if (result == 0):
        return newWin
    else:
        return newLoss

