from flask import Flask, render_template, request, redirect, flash, session
from flask_wtf import FlaskForm
from random import randrange
from string import ascii_uppercase
from pprint import pprint
import sqlite3
from datetime import datetime as dt

from validation import Actions
import data_extraction
import forms


class Database:

    def __init__(self):
        self.conn = sqlite3.connect("test.db", check_same_thread=False)
        self.cursor = self.conn.cursor()
        # load members and create lists for validation
        self.cursor.execute("SELECT * FROM members")
        self.users = self.cursor.fetchall()


# initialize Flask app
app = Flask(__name__)
app.config["SECRET_KEY"] = "sdlkfjsdlojf3r49tgf8"


# root endpoint
@app.route("/")
def root():
    return redirect("log")


# login endpoint
@app.route("/log", methods=["GET", "POST"])
def log():
    # if user already logged in, go directly to main page
    if "user_data" in session:
        return redirect("main")

    # if user not logged in, display log-in page
    form = forms.LoginForm()

    if form.validate_on_submit():
        # flash("Login ok", "success")
        result = ACTIONS.login(request.form, db=db)
        if result["code"] == 0:
            return render_template("error.html", msg=result["msg"])
        else:
            session["user_data"] = result["data"]
            return redirect("main")

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
@app.route("/main", methods=["GET"])
def main():
    if session["user_data"]:
        data = data_extraction.get_user_data(
            cursor=db.cursor, user=session["user_data"]
        )
        return render_template(
            "main.html",
            user=data["user"],
            brevete=data["brevete"],
            record=data["record"],
        )
    else:
        return render_template("log.html")


# my account endpoint (NAVBAR)
@app.route("/micuenta")
def mi_cuenta():
    if "user_data" not in session:
        return redirect("log")

    form = forms.MiCuenta()

    db.cursor.execute(f"SELECT * FROM placas WHERE IdMember_FK = 23")
    placas = [i[2] for i in db.cursor.fetchall()]
    print(placas)
    return render_template("mi_cuenta.html", form=form, placas=placas)


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
