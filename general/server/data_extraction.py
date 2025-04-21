import os


def get_user_data(cursor, user):

    _info = {"user": user}

    member = user[0]

    # add brevete information
    cursor.execute(
        f"SELECT * FROM brevetes WHERE IdMember_FK = {member} ORDER BY LastUpdate DESC"
    )
    _m = cursor.fetchone()
    if _m:
        _info.update(
            {
                "brevete": {
                    "numero": _m[2],
                    "clase": _m[1],
                    "formato": _m[3],
                    "fecha_desde": _m[4],
                    "fecha_hasta": _m[6],
                    "restricciones": _m[5],
                    "local": _m[7],
                    "puntos": _m[8],
                    "record": _m[9],
                }
            }
        )
    else:
        _info.update({"brevete": {}})

    # add RECORD DE CONDUCTOR image
    cursor.execute(
        f"SELECT * FROM recordConductores WHERE IdMember_FK = {member} ORDER BY LastUpdate DESC"
    )
    for _m in cursor.fetchall():
        # add image to attachment list
        _img_path = os.path.join(os.curdir, "data", "images", _m[1])
        if True:  # os.path.isfile(_img_path):
            _info.update({"record": str(_m[1])})

    return _info
