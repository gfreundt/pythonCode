import os, json
from tqdm import tqdm
import sqlite3


def dt(text):
    return f"{text[6:]}-{text[3:5]}-{text[:2]}"


def main():
    DB = os.path.join(os.curdir, "test2.db")
    JSONDB = os.path.join(os.curdir, "data", "complete_data.json")

    conn = sqlite3.connect(DB)

    cursor = conn.cursor()

    with open("sqlite_cmd.txt", "r") as sql:
        cmd = sql.read()

    cursor.executescript(cmd)

    with open(JSONDB, mode="r") as file:
        data_raw = json.load(file)

    for r, record in enumerate(data_raw):

        # usuarios
        cmd = f"""INSERT OR IGNORE INTO usuarios (
            Nombre, DocTipo, DocNum, Telefono, Correo )
            VALUES (?,?,?,?,?)"""

        values = (
            record["nombre"],
            record["documento"]["tipo"],
            record["documento"]["numero"],
            record["telefono"],
            record.get("correo", ""),
        )
        cursor.execute(cmd, values)

        select = "SELECT IdUsuario FROM usuarios WHERE DocNum = ?"
        cursor.execute(select, (record["documento"]["numero"],))
        IdUsuario = cursor.fetchone()[0]

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
    conn.close()

    return


'''

        # placas
        cmd = f"""INSERT OR IGNORE INTO placas (
            Clase, Numero, Tipo, FechaExp, Restricciones, FechaHasta, Centro, Actualizado)
            VALUES (?,?,?,?,?,?,?,?)"""

        # cmd = f"""INSERT OR IGNORE INTO satimpsDetalle (
        #     Codigo, Ano, Periodo, Documento, TotalAPagar)
        #     VALUES (?,?,?,?,?)"""

        # _rec = record["documento"]["deuda_tributaria_sat"]
        # if _rec:
        #     for deuda in _rec:
        #         _de = deuda["deudas"]
        #         if _de:
        #             for d in _de:
        #                 values = (
        #                     deuda["codigo"],
        #                     d["ano"],
        #                     d["periodo"],
        #                     d["documento"],
        #                     d["total_a_pagar"],
        #                 )
        #                 cursor.execute(cmd, values)
        #         else:
        #             values = (deuda["codigo"], "", "", "", "")
        #             cursor.execute(cmd, values)

        # cmd = f"""INSERT OR IGNORE INTO satimps (
        #     Codigo, Actualizado)
        #     VALUES (?,?)"""

        # _rec = record["documento"]["deuda_tributaria_sat"]
        # if _rec:
        #     for deuda in _rec:
        #         values = (
        #             f'{deuda["codigo"]:0>7}',
        #             record["documento"]["deuda_tributaria_sat_actualizado"],
        #         )
        #         cursor.execute(cmd, values)

    conn.commit()
    conn.close()
'''
main()
