from random import randrange
from string import ascii_uppercase
import sqlite3
from pprint import pprint


class Actions:

    def __init__(self):
        return
        self.conn = sqlite3.connect("test.db", check_same_thread=False)
        self.cursor = self.conn.cursor()

        # load members
        cmd = f"SELECT * FROM members"
        self.cursor.execute(cmd)
        self.user_db = self.cursor.fetchall()
        self.dni_list = [i[4] for i in self.user_db]
        self.celular_list = [i[5] for i in self.user_db]
        self.correo_list = [i[6] for i in self.user_db]

    def registration(self, form_data):
        return

        self.registration_attempt = {i: form_data[i] for i in form_data}

        # perform validations
        if any(not form_data[i] for i in self.registration_attempt):
            return {"code": 0, "msg": "All Fields Must be Filled, Try Again"}
        if self.registration_attempt["dni"] in self.dni_list:
            return {"code": 0, "msg": "DNI already in used. Select New One."}
        if self.registration_attempt["correo"] in self.correo_list:
            return {"code": 0, "msg": "Correo already exists. Select New One."}
        if self.registration_attempt["celular"] in self.celular_list:
            return {"code": 0, "msg": "Celular already exists. Select New One."}

        data = self.registration_attempt.update(
            {"code": self.generated_validation_code}
        )

        return {"code": 1, "msg": None, "data": data}

    def registration2(self, form_data):
        return

        # validation code matches
        if form_data["validation_code"].upper() != self.generated_validation_code:
            return {"code": 0, "msg": f"Error in Validation Code"}

        # TODO:update SQL
        return {"code": 1, "msg": "User Registered"}

    def recover(self, form_data):
        return

        if not form_data["correo"]:
            return {"code": 0, "msg": f"Must Enter Correo"}

        # generate random validation code
        self.generated_validation_code = "".join(
            [ascii_uppercase[randrange(0, len(ascii_uppercase))] for _ in range(4)]
        )
        print(self.generated_validation_code)

        return {"code": 1, "msg": None}

    def login(self, form_data, db):

        for user in db.users:
            if user[6] == form_data["correo"]:
                if user[11] == form_data["password"]:
                    # TODO: add placas
                    print("@@@@@@@@@@", user)
                    return {"code": 1, "msg": "Login Succesful", "data": user}
                else:
                    db.cursor.execute(
                        f"UPDATE members SET CountFailedLogins = {int(user[8])+1} WHERE IdMember = '{user[0]}'"
                    )
                    db.conn.commit()
                    return {"code": 0, "msg": "Wrong Password"}
        return {"code": 0, "msg": "Wrong correo"}

    def password_comply(self, password):
        return

        # between 6 and 10 characters
        if len(password) < 6 or len(password) > 10:
            return False
        # must include one number
        if len([i for i in password if i in "0123456789"]) == 0:
            return False
        # must include one uppercase letter
        if len([i for i in password if i in ascii_uppercase]) == 0:
            return False

        return True

    def update_password(self, correo, password, db):
        cmd = f"UPDATE members SET Password = '{password}' WHERE Correo = '{correo}'"
        db.cursor.execute(cmd)
        db.conn.commit()
