from flask import Flask, render_template, request, redirect, flash, session, jsonify
from flask_wtf import FlaskForm
from random import randrange
from string import ascii_uppercase
from pprint import pprint
import sqlite3
from datetime import datetime as dt
from datetime import timedelta as td

from validation import Actions
import data_extraction
import forms


class Database:

    def __init__(self):
        self.conn = sqlite3.connect("test.db", check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.reload_db()

    def reload_db(self):
        # load members and create lists for validation
        self.cursor.execute("SELECT * FROM members")
        self.users = self.cursor.fetchall()


# initialize Flask app
app = Flask(__name__)
app.config["SECRET_KEY"] = "sdlkfjsdlojf3r49tgf8"
app.config["TEMPLATES_AUTO_RELOAD"] = True


# root endpoint
@app.route("/")
def root():
    return redirect("log")


# login endpoint
@app.route("/log", methods=["GET", "POST"])
def log():
    # if user already logged in, go directly to main page
    if "user" in session:
        return redirect("reportes")

    # if user not logged in, display log-in page
    form = forms.LoginForm()
    if form.validate_on_submit():
        # flash("Login ok", "success")
        result = ACTIONS.login(request.form, db=db)
        session["user"] = result["data"]
        return redirect("reportes")

    return render_template("log.html", form=form)


# registration endpoints
@app.route("/reg", methods=["GET", "POST"])
def reg():
    form = forms.RegisterFormPage1()

    if form.validate_on_submit():
        session["generated_validation_code"] = "".join(
            [ascii_uppercase[randrange(0, len(ascii_uppercase))] for _ in range(4)]
        )
        print("@@@@@", session["generated_validation_code"])
        session["reg_data"] = list(request.form.values())
        return redirect("reg-2")

    return render_template("reg.html", form=form)


@app.route("/reg-2", methods=["GET", "POST"])
def reg2():
    if "reg_data" not in session:
        return redirect("reg")

    form = forms.RegisterFormPage2()
    if form.validate_on_submit():
        if request.form["codigo"].upper() != session["generated_validation_code"]:
            return render_template("error.html", msg="Codigo Equivocado")
        else:
            cod = "TST-005"
            nom = session["reg_data"][1]
            dni = session["reg_data"][2]
            cor = session["reg_data"][3]
            cel = session["reg_data"][4]
            pwd = request.form["password"]

            db.cursor.execute(f"SELECT IdMember FROM members ORDER BY IdMember DESC")
            rec = int(db.cursor.fetchone()[0]) + 1
            dat = dt.now().strftime("%Y-%m-%d %H:%M:%S")

            db.cursor.execute(
                f"INSERT INTO members VALUES ({rec},'{cod}','{nom}','DNI','{dni}','{cel}','{cor}',0,0,'{dat}',0,'{pwd}')"
            )

            db.conn.commit()
            session.clear()
            db.reload_db()
            return render_template("reg-3.html")

    return render_template("reg-2.html", form=form)


# password recovery endpoints
@app.route("/rec", methods=["GET", "POST"])
def rec():

    form = forms.RecoverFormPage1()
    if form.validate_on_submit():
        session["generated_validation_code"] = "".join(
            [ascii_uppercase[randrange(0, len(ascii_uppercase))] for _ in range(4)]
        )
        print("@@@@@", session["generated_validation_code"])
        session["correo"] = request.form["correo"]
        return redirect("rec-2")

    return render_template("rec.html", form=form)


@app.route("/rec-2", methods=["GET", "POST"])
def rec2():

    form = forms.RecoverFormPage2()
    if form.validate_on_submit():
        if request.form["codigo"].upper() != session["generated_validation_code"]:
            return render_template("error.html", msg="Codigo Equivocado")
        else:
            session["generated_validation_code"] = None
            ACTIONS.update_password(
                correo=session["correo"], password=request.form["password"], db=db
            )
            session.clear()
            return render_template("rec-3.html")

    return render_template("rec-2.html", form=form)


# dashboard endpoints
@app.route("/reportes", methods=["GET", "POST"])
def reportes():

    # user not logged in, go to login page
    if not session["user"]:
        return render_template("log.html")

    if request.method == "POST":
        session["selection"] = request.form["selection"]

    else:
        session["data"] = data_extraction.get_user_data(
            cursor=db.cursor, user=session["user"]
        )
        session["selection"] = ""

    data = session["data"]
    return render_template(
        "reportes.html",
        user=data["user"],
        brevete=data["brevete"],
        satimps=data["satimps"],
        record=data["record"],
        placas=data["placas"],
        sutrans=data["sutrans"],
        satmuls=data["satmuls"],
        papeletas=data["papeletas"],
        soats=data["soats"],
        revtecs=data["revtecs"],
        sunarps=data["sunarps"],
        selection=session["selection"],
    )


# my account endpoint (NAVBAR)
@app.route("/mic", methods=["GET", "POST"])
def mic():
    # user not logged in, got to login page
    if "user" not in session:
        return redirect("log")

    # opening form, retrieve data and show in form
    form = forms.MiCuenta()
    if not form.validate_on_submit():
        db.cursor.execute(
            f"SELECT * FROM placas WHERE IdMember_FK = {session['user'][0]}"
        )
        placas = [i[2] for i in db.cursor.fetchall()]
        db.cursor.execute(
            f"SELECT Fecha FROM mensajes WHERE IdMember_FK = {session['user'][0]} ORDER BY Fecha DESC"
        )
        _fecha = db.cursor.fetchone()
        siguiente_mensaje = (
            (
                max(
                    dt.strptime(_fecha[0], "%Y-%m-%d %H:%M:%S") + td(days=30),
                    dt.now() + td(days=1),
                ).strftime("%Y-%m-%d")
            )
            if _fecha
            else (dt.now() + td(days=1)).strftime("%Y-%m-%d %H:%M:%S")
        )
        comm = {
            "siguiente_mensaje": siguiente_mensaje,
            "opt_in_mensajes": True,
            "Soat": True,
            "Brevete": True,
            "RevTec": False,
            "Dni": False,
            "opt_in_alertas1": True,
            "Sutran": False,
            "Sat": True,
            "Mtc": False,
            "opt_in_alertas2": False,
        }
        return render_template("mi_cuenta.html", form=form, placas=placas, comm=comm)

    # returning from completed form, update database
    incoming = request.form

    # process updated placas
    db.cursor.execute(f"DELETE FROM placas WHERE IdMember_FK = {session['user'][0]}")
    db.cursor.execute(f"SELECT IdPlaca FROM placas ORDER BY IdPlaca DESC")
    rec = int(db.cursor.fetchone()[0]) + 1
    for placa in (incoming["placa1"], incoming["placa2"], incoming["placa3"]):
        db.cursor.execute(
            f"INSERT INTO placas VALUES ({rec}, {session['user'][0]}, '{placa}')"
        )
        rec += 1

    # TODO: process updated communication options

    db.conn.commit()

    return render_template("mic-2.html")


# home endpoint (NAVBAR)
@app.route("/home")
def home():
    return redirect("log")


# logout endpoint (NAVBAR)
@app.route("/logout")
def logout():
    session.clear()
    return redirect("log")


if __name__ == "__main__":
    db = Database()
    ACTIONS = Actions()
    app.run(debug=True)
