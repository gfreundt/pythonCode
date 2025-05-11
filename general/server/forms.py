from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField
from wtforms.validators import (
    DataRequired,
    Email,
    Length,
    EqualTo,
    Regexp,
    ValidationError,
    Optional,
)
import sqlite3


class Test:
    pass


# custom error validations
def dni_no_en_db(form, field):
    if field.data in todos_dni:
        raise ValidationError("DNI ya registrado.")


def correo_no_en_db(form, field):
    if field.data in todos_correo:
        raise ValidationError("Correo ya registrado.")


def correo_si_en_db(form, field):
    test.user = field.data
    if field.data not in todos_correo:
        raise ValidationError("Correo no existe.")


def celular_no_en_db(form, field):
    if field.data in todos_celular:
        raise ValidationError("Celular ya registrado.")


def password_correcto(form, field):
    if usuario_pwd[test.user] != field.data:
        raise ValidationError("Contraseña equivocada.")


# def codigo_validacion(form, field):
#     if field.data != todos_celular:
#         raise ValidationError("Celular ya existe en base de datos.")


def load_db():
    conn = sqlite3.connect("test.db", check_same_thread=False)
    cursor = conn.cursor()
    # load members and create lists for validation
    cmd = f"SELECT * FROM members"
    cursor.execute(cmd)
    db = cursor.fetchall()
    return (
        [i[4] for i in db],
        [i[5] for i in db],
        [i[6] for i in db],
        {i[6]: i[11] for i in db},
    )


class LoginForm(FlaskForm):

    correo = StringField(
        "Correo Electrónico",
        [
            DataRequired(message="El correo es requerido"),
            Email(message="Ingrese un correo electrónico válido"),
            correo_si_en_db,
        ],
    )
    password = PasswordField(
        "Contraseña",
        [
            DataRequired(message="La contraseña es requerida"),
            password_correcto,
        ],
    )
    submit = SubmitField("Empezar")


class RegisterFormPage1(FlaskForm):

    nombre = StringField(
        "Nombre",
        [
            DataRequired(message="El nombre es requerido"),
            Length(
                min=3, max=50, message="El nombre debe tener entre 3 y 50 caracteres"
            ),
        ],
    )
    dni = StringField(
        "DNI",
        [
            DataRequired(message="El DNI es requerido"),
            Regexp(r"^\d{8}$", message="El DNI debe tener 8 dígitos"),
            dni_no_en_db,
        ],
    )
    correo = StringField(
        "Correo Electrónico",
        [
            DataRequired(message="El correo es requerido"),
            Email(message="Ingrese un correo electrónico válido"),
            correo_no_en_db,
        ],
    )
    celular = StringField(
        "Celular",
        [
            DataRequired(message="El celular es requerido"),
            Regexp(r"^\d{9}$", message="El celular debe tener 9 dígitos"),
            celular_no_en_db,
        ],
    )


class RegisterFormPage2(FlaskForm):

    codigo = StringField(
        "Codigo de Validacion",
        [
            DataRequired(message="Codigo requerido"),
            Regexp(
                r"^[A-Z]{4}$",
                message="Codigo debe tener 4 letras",
            ),
        ],
    )

    password = PasswordField(
        "Contraseña",
        [
            DataRequired(message="La contraseña es requerida"),
            Length(min=6, message="La contraseña debe tener al menos 6 caracteres"),
            Regexp(
                r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{6,}$",
                message="Contraseña minimo 6 digitos y tener mayúsculas y minúsculas",
            ),
        ],
    )

    confirmar_password = PasswordField(
        "Confirmar Contraseña",
        [
            DataRequired(message="Por favor confirme su contraseña"),
            EqualTo("password", message="Las contraseñas no coinciden"),
        ],
    )
    submit = SubmitField("Registrarse")


class RecoverFormPage1(FlaskForm):

    correo = StringField(
        "Correo Electrónico",
        [
            DataRequired(message="El correo es requerido"),
            Email(message="Ingrese un correo electrónico válido"),
            correo_si_en_db,
        ],
    )


class RecoverFormPage2(FlaskForm):

    codigo = StringField(
        "Codigo de Validacion",
        [
            DataRequired(message="Codigo requerido"),
            Regexp(
                r"^[A-Z]{4}$",
                message="Codigo debe tener 4 letras",
            ),
        ],
    )

    password = PasswordField(
        "Contraseña",
        [
            DataRequired(message="La contraseña es requerida"),
            Length(min=6, message="La contraseña debe tener al menos 6 caracteres"),
            Regexp(
                r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{6,}$",
                message="Contraseña minimo 6 digitos y tener mayúsculas y minúsculas",
            ),
        ],
    )

    confirmar_password = PasswordField(
        "Confirmar Contraseña",
        [
            DataRequired(message="Por favor confirme su contraseña"),
            EqualTo("password", message="Las contraseñas no coinciden"),
        ],
    )


class MiCuenta(FlaskForm):

    placa1 = StringField(
        "Placa 1",
        validators=[
            Optional(),  # Explicitly allows empty
            Regexp(
                r"^[A-Z0-9]{6,7}$",
                message="La placa debe tener 6 o 7 caracteres alfanuméricos",
            ),
        ],
    )
    placa2 = StringField(
        "Placa 2",
        validators=[
            Optional(),  # Explicitly allows empty
            Regexp(
                r"^[A-Z0-9]{6,7}$",
                message="La placa debe tener 6 o 7 caracteres alfanuméricos",
            ),
        ],
    )
    placa3 = StringField(
        "Placa 3",
        validators=[
            Optional(),  # Explicitly allows empty
            Regexp(
                r"^[A-Z0-9]{6,7}$",
                message="La placa debe tener 6 o 7 caracteres alfanuméricos",
            ),
        ],
    )
    submit = SubmitField("Actualizar")


todos_dni, todos_celular, todos_correo, usuario_pwd = load_db()
test = Test()
