import os, json, uuid
import sqlite3


def load_members():
    DATABASE = os.path.join(os.getcwd(), "data", "members.json")
    with open(DATABASE, mode="r", encoding="utf-8") as file:
        return json.load(file)


def connect_and_reset():
    SQLDATABASE = os.path.join(os.getcwd(), "data", "members.sqlite")
    conn = sqlite3.connect(SQLDATABASE)
    cursor = conn.cursor()

    SQLSCRIPT1 = os.path.join(os.getcwd(), "sql_script1.sql")
    with open(SQLSCRIPT1, mode="r", encoding="utf-8") as file:
        cmd = file.read()
    cursor.executescript(cmd)

    return conn, cursor


def sql(table, fields):
    qmarks = ",".join(["?" for i in range(len(fields))])
    return f"INSERT INTO {table} ({','.join(fields)}) VALUES ({qmarks})"


def main():
    db = load_members()
    conn, cursor = connect_and_reset()

    for member in db:

        res = member["Resultados"]

        # members table
        cmd = sql(
            "members",
            ["NombreCompleto", "DocTipo", "DocNum", "Celular", "Correo", "CodMember"],
        )
        values = list(member["Datos"].values())[:5] + [
            "SAP-" + str(uuid.uuid4())[-6:].upper()
        ]
        cursor.execute(cmd, values)

        cmd = f"SELECT * FROM members WHERE DocNum = '{values[2]}'"
        cursor.execute(cmd)
        idmember = cursor.fetchone()[0]

        # satimp tables
        for satimp in res.get("Satimp", []):
            cmd = sql("satimpCodigos", ["IdMember_FK", "Codigo"])
            values = (idmember, satimp["codigo"])
            cursor.execute(cmd, values)

            cmd = f"SELECT * FROM satimpCodigos WHERE IdMember_FK = {values[0]}"
            cursor.execute(cmd)
            idcodigo = cursor.fetchone()[0]

            for deuda in satimp["deudas"]:
                cmd = sql(
                    "satimpDeudas",
                    [
                        "IdCodigo_FK",
                        "Ano",
                        "Periodo",
                        "DocNum",
                        "TotalAPagar",
                        "LastUpdate",
                    ],
                )
                values = [idcodigo] + list(deuda.values()) + [res["Satimp_Actualizado"]]
                cursor.execute(cmd, values)

        # brevetes table
        cmd = sql(
            "brevetes",
            [
                "IdMember_FK",
                "Clase",
                "Numero",
                "Tipo",
                "FechaExp",
                "Restricciones",
                "FechaHasta",
                "Centro",
                "LastUpdate",
            ],
        )
        values = (
            [idmember] + list(res["Brevete"].values()) + [res["Brevete_Actualizado"]]
        )
        cursor.execute(cmd, values)

        # placas table
        for pla, placa in enumerate(member["Datos"]["Placas"]):
            cmd = sql("placas", ["IdMember_FK", "Placa"])
            values = [idmember] + [placa]
            cursor.execute(cmd, values)

            cmd = f"SELECT * FROM placas WHERE Placa = '{placa}'"
            cursor.execute(cmd)
            idplaca = cursor.fetchone()[0]

            # revtecs table
            if res["Revtec"] and res["Revtec"][pla]:
                cmd = sql(
                    "revtecs",
                    [
                        "Placa_FK",
                        "Certificadora",
                        "PlacaValidate",
                        "Certificado",
                        "FechaDesde",
                        "FechaHasta",
                        "Resultado",
                        "Vigencia",
                        "LastUpdate",
                    ],
                )
                values = (
                    [placa]
                    + list(res["Revtec"][pla][0].values())
                    + [res["Revtec_Actualizado"]]
                )
                cursor.execute(cmd, values)

            # soats tables
            if res["Soat"] and res["Soat"][pla]:
                cmd = sql(
                    "soats",
                    [
                        "IdPlaca_FK",
                        "Aseguradora",
                        "FechaInicio",
                        "FechaFin",
                        "PlacaValidate",
                        "Certificado",
                        "Uso",
                        "Clase",
                        "Vigencia",
                        "Tipo",
                        "FechaVenta",
                        "LastUpdate",
                        "ImgFilename",
                        "ImgUpdate",
                    ],
                )
                values = (
                    [idplaca]
                    + list(res["Soat"][pla].values())
                    + [res["Revtec_Actualizado"]]
                    + [res["SoatImage"][str(pla)]["Soat_Imagen"]]
                    + [res["Revtec_Actualizado"]]
                )
                cursor.execute(cmd, values)

            # sunarps table
            if res.get("Sunarp", False):
                cmd = sql(
                    "sunarps",
                    [
                        "IdPlaca_FK",
                        "PlacaValidate",
                        "Serie",
                        "VIN",
                        "Motor",
                        "Color",
                        "Marca",
                        "Modelo",
                        "PlacaVigente",
                        "PlacaAnterior",
                        "Estado",
                        "Anotaciones",
                        "Sede",
                        "Propietarios",
                        "Ano",
                        "LastUpdate",
                        "ImgFilename",
                        "ImgUpdate",
                    ],
                )
                values = (
                    [idplaca]
                    + [None] * 13
                    + [res["Sunarp_Actualizado"]]
                    + [res["Sunarp"][pla]["archivo"]]
                    + [res["Sunarp_Actualizado"]]
                )
                cursor.execute(cmd, values)

            # sutran table
            if res["Sutran"] and res["Sutran"][pla]:
                cmd = sql(
                    "sutrans",
                    [
                        "IdPlaca_FK",
                        "Documento",
                        "Tipo",
                        "FechaDoc",
                        "CodigoInfrac",
                        "Clasificacion",
                        "LastUpdate",
                    ],
                )
                values = (
                    [idplaca]
                    + list(res["Sutran"][pla].values())
                    + [res["Revtec_Actualizado"]]
                )
                cursor.execute(cmd, values)

        # mensajes
        envios = member["Envios"]
        if envios["Bienvenida"]:
            cmd = sql(
                "mensajes",
                [
                    "IdMember_FK",
                    "Fecha",
                    "Hash",
                ],
            )
            values = (
                [idmember]
                + [envios["Bienvenida"]["fecha"]]
                + [envios["Bienvenida"]["hash"]]
            )
            x = envios["Bienvenida"]["hash"]
            cursor.execute(cmd, values)
            cursor.execute(f'SELECT * FROM mensajes WHERE Hash = "{x}"')
            idmsg = cursor.fetchone()[0]
            cmd = "INSERT INTO mensajeContenidos (IdMensaje_FK, IdTipoMensaje_FK) VALUES (?,?)"
            values = (idmsg, 12)
            cursor.execute(cmd, values)

    conn.commit()
    conn.close()


main()
