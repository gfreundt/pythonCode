from random import randrange
from string import ascii_uppercase
import re


class FormValidate:

    def __init__(self, db):

        self.conn = db.conn
        self.cursor = db.cursor

        # load members
        cmd = f"SELECT * FROM members"
        self.cursor.execute(cmd)
        self.user_db = self.cursor.fetchall()
        self.dnis = [i[4] for i in self.user_db]
        self.celulares = [str(i[5]) for i in self.user_db]
        self.correos = [i[6] for i in self.user_db]

    def log(self, form_data, db):

        # TODO: replace with SQL request

        for user in db.users:
            if user[6] == form_data["correo"]:
                if user[11] == form_data["password"]:
                    return False
                else:
                    return {"password": ["Contraseña equivocada"]}

        return {"correo": ["Correo no registrado"]}

    def reg(self, reg, page, codigo=None):

        # realizar todas las validaciones
        errors = {
            "nombre": [],
            "dni": [],
            "correo": [],
            "celular": [],
            "codigo": [],
            "password1": [],
            "password2": [],
        }

        if page == 1:

            # nombre
            if len(reg["nombre"]) < 6:
                errors["nombre"].append("Nombre debe tener minimo 5 digitos")

            # dni
            if not re.match(r"^[0-9]{8}$", reg["dni"]):
                errors["dni"].append("DNI solamente debe tener 8 digitos")
            if reg["dni"] in self.dnis:
                errors["dni"].append("DNI ya esta registado")

            # correo
            if not re.match(
                r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", reg["correo"]
            ):
                errors["correo"].append("Ingrese un correo valido")
            if reg["correo"] in self.correos:
                errors["correo"].append("Correo ya esta registrado")

            # celular
            if not re.match(r"^[0-9]{9}$", reg["celular"]):
                errors["celular"].append("Ingrese un celular valido")
            if reg["celular"] in self.celulares:
                errors["celular"].append("Celular ya esta registrado")

        elif page == 2:

            # codigo
            if not re.match(r"^[A-Za-z]{4}$", reg["codigo"]):
                errors["codigo"].append("Codigo de validacion son 4 letras")
            if reg["codigo"] != codigo:
                errors["codigo"].append("Codigo de validacion incorrecto")

            # constraseña
            if not re.match(r"^(?=.*[A-Z])(?=.*\d).{6,20}$", reg["password1"]):
                errors["password1"].append(
                    "Al menos 6 caracteres e incluir una mayuscula y un numero"
                )

            # validacion de constraseña
            if reg["password1"] != reg["password2"]:
                errors["password2"].append("Contraseñas no coinciden")

        return errors

    def rec(self, rec, page, codigo=None):

        # realizar todas las validaciones
        errors = {
            "correo": [],
            "codigo": [],
            "password1": [],
            "password2": [],
        }

        if page == 1:

            # correo
            if not re.match(
                r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", rec["correo"]
            ):
                errors["correo"].append("Ingrese un correo valido")
            elif rec["correo"] not in self.correos:
                errors["correo"].append("Correo no esta registrado")

        elif page == 2:

            # codigo
            if not re.match(r"^[A-Za-z]{4}$", rec["codigo"]):
                errors["codigo"].append("Codigo de validacion son 4 letras")
            if rec["codigo"] != codigo:
                errors["codigo"].append("Codigo de validacion incorrecto")

            # contraseña
            if not re.match(r"^(?=.*[A-Z])(?=.*\d).{6,20}$", rec["password1"]):
                errors["password1"].append(
                    "Al menos 6 caracteres e incluir una mayuscula y un numero"
                )

            # validacion de constraseña
            if rec["password1"] != rec["password2"]:
                errors["password2"].append("Contraseñas no coinciden")

        return errors

    def mic(self, mic):

        # TODO: complete validations

        # realizar todas las validaciones
        errors = {
            "placa1": [],
            "placa2": [],
            "placa3": [],
            "correo": [],
            "password1": [],
            "password2": [],
        }

        # placa
        return errors

        # contraseña
        # if not re.match(r"^(?=.*[A-Z])(?=.*\d).{6,20}$", rec["password1"]):
        #     errors["password1"].append(
        #         "Al menos 6 caracteres e incluir una mayuscula y un numero"
        #     )

        # # validacion de constraseña
        # if rec["password1"] != rec["password2"]:
        #     errors["password2"].append("Contraseñas no coinciden")

        return errors

    def update_password(self, correo, password, db):
        cmd = f"UPDATE members SET Password = '{password}' WHERE Correo = '{correo}'"
        db.cursor.execute(cmd)
        db.conn.commit()
