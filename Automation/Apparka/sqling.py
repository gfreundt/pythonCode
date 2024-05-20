import os, json, csv
import sqlite3
from tqdm import tqdm
import time


def dt(text):
    return f"{text[6:]}-{text[3:5]}-{text[:2]}"


def json_to_sql():
    JSONDB = os.path.join(os.curdir, "data", "complete_data.json")

    with open("sqlite_cmd.txt", "r") as sql:
        cmd = sql.read()

    cursor.executescript(cmd)

    with open(JSONDB, mode="r") as file:
        data_raw = json.load(file)

    for record in data_raw:

        # if IdUsuario has no unique ID from PNET do not include
        if record["idUsuario"] == 0:
            continue

        # usuarios
        cmd = f"""INSERT OR IGNORE INTO usuarios (
            IdUsuario, Nombre, DocTipo, DocNum, Telefono, Correo)
            VALUES (?,?,?,?,?,?)
            """

        values = (
            record["idUsuario"],
            record["nombre"],
            record["documento"]["tipo"],
            record["documento"]["numero"],
            record["telefono"],
            record.get("correo", ""),
        )
        cursor.execute(cmd, values)

        select = "SELECT IdUsuario FROM usuarios WHERE DocNum = ?"
        cursor.execute(select, (record["documento"]["numero"],))
        IdUsuario = cursor.fetchone()
        if not IdUsuario:
            continue
        else:
            IdUsuario = IdUsuario[0]

        # brevetes
        cmd = f"""INSERT OR IGNORE INTO brevetes (
            IdUsuario_FK, Clase, Numero, Tipo, FechaExp, Restricciones, FechaHasta, Centro, Actualizado)
            VALUES (?,?,?,?,?,?,?,?,?)"""

        _rec = record["documento"]["brevete"]
        if _rec:
            values = (
                IdUsuario,
                _rec["clase"],
                _rec["numero"],
                _rec["tipo"],
                dt(_rec["fecha_expedicion"]),
                _rec["restricciones"],
                dt(_rec["fecha_hasta"]),
                _rec["centro"],
                dt(record["documento"]["brevete_actualizado"]),
            )
            cursor.execute(cmd, values)

        # satimps
        cmd = f"""INSERT OR IGNORE INTO satimps (
            IdUsuario_FK, Codigo, Actualizado)
            VALUES (?,?,?)"""

        cmd2 = f"""INSERT OR IGNORE INTO satimpDeudas (
                    IdSatimp_FK, Ano, Periodo, Documento, TotalAPagar)
                    VALUES (?,?,?,?,?)"""

        _rec = record["documento"]["deuda_tributaria_sat"]
        if _rec:
            for deuda in _rec:
                cdg = f'{deuda["codigo"]:0>7}'
                values = (
                    IdUsuario,
                    cdg,
                    dt(record["documento"]["deuda_tributaria_sat_actualizado"]),
                )
                cursor.execute(cmd, values)

                select = "SELECT IdSatimp FROM satimps WHERE Codigo = ?"
                cursor.execute(select, (cdg,))
                IdSatimp = cursor.fetchone()[0]

                # satimps detalle
                for d in deuda["deudas"]:
                    values = (
                        IdSatimp,
                        d["ano"],
                        d["periodo"],
                        d["documento"],
                        d["total_a_pagar"],
                    )
                    cursor.execute(cmd2, values)

        # placas
        cmd = """INSERT OR IGNORE INTO placas (
            IdUsuario_FK, Placa)
            VALUES (?,?)"""

        cmd2 = """INSERT OR IGNORE INTO revtecs (
                    IdPlaca_FK,
                    Certificadora,
                    Placa,
                    Certificado,
                    FechaDesde,
                    FechaHasta,
                    Resultado,
                    Vigencia,
                    Actualizado)
                    VALUES (?,?,?,?,?,?,?,?,?)"""

        cmd3 = """INSERT OR IGNORE INTO sutrans (
                    IdPlaca_FK,
                    Documento,
                    Tipo,
                    FechaDoc,
                    CodigoInfrac,
                    Clasificacion,
                    Actualizado)
                    VALUES (?,?,?,?,?,?,?)"""

        _rec = record["vehiculos"]
        if _rec:
            for vehiculo in _rec:
                values = (IdUsuario, vehiculo["placa"])
                cursor.execute(cmd, values)

                select = "SELECT IdPlaca FROM placas WHERE Placa = ?"
                cursor.execute(select, (vehiculo["placa"],))
                IdPlaca = cursor.fetchone()[0]

                # revtecs
                _rtec = vehiculo["rtecs"]
                if _rtec:
                    _rtec = _rtec[0]
                    values = (
                        IdPlaca,
                        _rtec["certificadora"],
                        _rtec["placa"],
                        _rtec["certificado"],
                        dt(_rtec["fecha_desde"]),
                        dt(_rtec["fecha_hasta"]),
                        _rtec["resultado"],
                        _rtec["vigencia"],
                        dt(vehiculo["rtecs_actualizado"]),
                    )
                    cursor.execute(cmd2, values)

                # sutrans
                _sut = vehiculo["multas"]["sutran"]
                if _sut:
                    values = (
                        IdPlaca,
                        _sut["documento"],
                        _sut["tipo"],
                        dt(_sut["fecha_documento"]),
                        _sut["codigo_infraccion"],
                        _sut["clasificacion"],
                        dt(vehiculo["multas"]["sutran_actualizado"]),
                    )
                    cursor.execute(cmd3, values)

    conn.commit()


def csv_to_sql():

    # create table usuarios and placasnew
    cmd = """
            DROP TABLE IF EXISTS usuarios;

            CREATE TABLE
                usuarios (
                IdUsuario INTEGER PRIMARY KEY,
                Nombre TEXT (40),
                DocTipo TEXT (12),
                DocNum TEXT (12) UNIQUE,
                Telefono TEXT (9),
                Correo TEXT (30)
                );

            DROP TABLE IF EXISTS placasNew;

            CREATE TABLE
                placasNew (
                IdPlacas INTEGER,
                IdUsuario_FK INTEGER,
                Placa TEXT (6)
                );
         """

    cursor.executescript(cmd)

    # read csv file (raw) imported from FTP (PNET data)
    csv_path = os.path.join(os.curdir, "data", "raw", "USUARIOS APPARKA MAY 2024.csv")
    with open(csv_path, mode="r", encoding="utf-8") as csv_file:
        csv_data = [
            [i.strip().upper() for i in j] for j in csv.reader(csv_file, delimiter=",")
        ][2:]

    # populate data into tables
    for line in csv_data:
        if line[1] and line[1][0].isalpha():
            # populate usuarios table
            cmd = """INSERT OR IGNORE INTO usuarios (
                     IdUsuario, Nombre, DocTipo, DocNum, Correo, Telefono)
                     VALUES (?,?,?,?,?,?)            
                  """
            conn.execute(cmd, line[:6])

            if len(line[6]) == 6:
                # populate placasNew table
                cmd = """INSERT OR IGNORE INTO placasNew (
                        IdPlacas, IdUsuario_FK, Placa)
                        VALUES (NULL, ?,?)            
                    """
                conn.execute(cmd, (line[0], line[6]))

    conn.commit()


def merge_placas():

    cursor.executescript(
        """ CREATE TABLE temp AS
            SELECT placas.IdPlaca, placasNew.IdUsuario_FK, placas.Placa
            FROM placas
            LEFT JOIN placasNew
            ON placas.Placa = placasNew.Placa;
            
            DROP TABLE placas;

            CREATE TABLE placas AS
            SELECT DISTINCT *
            FROM temp;

            DROP TABLE temp;

            DROP TABLE placasNew
            """
    )

    conn.commit()


start = time.time()

DB = os.path.join(os.curdir, "test3.db")
conn = sqlite3.connect(DB)
cursor = conn.cursor()


json_to_sql()  # only while scraping is done on json file -- stop when scraping directly into SQL
csv_to_sql()  # reset usuarios with outside data
merge_placas()  # incorporate new placas to old placas, keep old placas key

end = time.time()

print(f"Total time: {end-start:.2f}")
