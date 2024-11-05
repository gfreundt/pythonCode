import itertools


def gui(*args):
    pass


def valida_libro_completo(cursor, nombre_tabla):

    # extraer toda las filas de la tabla
    cursor.execute(f"SELECT * FROM '{nombre_tabla}'")
    table_data = cursor.fetchall()

    # extrae todos los codigos de las master keys en la tabla
    cursor.execute(
        f"SELECT * FROM (SELECT GGMK FROM '{nombre_tabla}' UNION SELECT GMK FROM '{nombre_tabla}' UNION SELECT MK FROM '{nombre_tabla}' UNION SELECT SMK FROM '{nombre_tabla}' WHERE GGMK IS NOT 0)"
    )
    todas_maestras = [i[0] for i in cursor.fetchall()]

    # extraer todos los codigos de las llaves de la tabla
    cursor.execute(f"SELECT K FROM '{nombre_tabla}'")
    llaves_usadas = [i[0] for i in cursor.fetchall()]

    for row in table_data:
        if not all(
            [
                valida_llave_es_unica(llave=row[4], llaves_usadas=llaves_usadas),
                valida_llave_abre_cilindro(
                    llaves=[row[0], row[1], row[2]], cilindro=row[6]
                ),
                valida_llave_no_cruzada(
                    cilindro=row[6],
                    mis_maestras=[i for i in row[:5] if i != 0],
                    todas_maestras=todas_maestras,
                ),
            ]
        ):
            return False

    return True


def valida_llave_abre_cilindro(llaves, cilindro):

    # crea lista de todas las llaves que pueden abrir ese cilindro
    opciones = [
        f"{pos[1]}{int(pos[1]) + int(pos[3])}" if ":" in pos else pos[1]
        for pos in cilindro.split("]")[:-1]
    ]
    g = [i.replace("[", "").replace(":", "") for i in opciones]
    cilindros = ["".join(i) for i in itertools.product(*g)]

    # revisa llaves de lista y ver si abren cilindro
    for llave in llaves:
        if llave not in cilindros:
            return False
    return True


def valida_llave_es_unica(llave, llaves_usadas):

    # revisa que solo haya una vez este codigo de llave en todo el libro
    if llaves_usadas.count(llave) == 1:
        return True
    return False


def valida_llave_no_cruzada(cilindro, mis_maestras, todas_maestras):

    # revisa cilindro contra todas las llaves maestras que no le corresponden para asegurar que no lo abran
    for maestra in todas_maestras:
        if maestra in mis_maestras:
            continue
        if valida_llave_abre_cilindro([maestra], cilindro):
            return False
    return True


def valida_codigo(codigo):

    # no puede tener mas o menos de 6 digitos
    if len(codigo) != 6:
        return False

    codigo = tuple(int(i) for i in codigo)

    # no puede haber 8 o 9 de diferencia entre pines
    for position in range(len(codigo) - 1):
        c = codigo[position]
        n = codigo[position + 1]
        if abs(n - c) >= 8:
            return False

    # no puede haber una secuencia [par-impar-par-impar-par-impar] o [impar-par-impar-par-impar-par]
    test = [int(i) % 2 for i in codigo]
    if test == [0, 1, 0, 1, 0, 1] or test == [1, 0, 1, 0, 1, 0]:
        return False

    # no pueden haber tres pines seguidos iguales
    for pos in range(4):
        if codigo[pos : pos + 3].count(codigo[pos]) == 3:
            return False

    return True
