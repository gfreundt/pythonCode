import itertools as it
import random


def generador(ggmk, formato):

    def combinaciones(codigo, matriz, ggmk):

        # todas las combinaciones validas cambiando los pines que correspondan
        m = list(codigo)
        for p in matriz:
            m[p] = PAR if int(ggmk[p]) % 2 == 0 else IMPAR

        return [i for i in it.product(*m) if (i != codigo and valida_codigo(i))]

    def con_smk(level1, matriz, ggmk):

        # cuatro niveles: GMK, MK, SMK, K
        todas_maestras = {ggmk}
        llaves = []
        for n1, l1 in enumerate(level1):
            level2 = combinaciones(l1, matriz[1], ggmk)
            for n2, l2 in enumerate(level2):
                level3 = combinaciones(l2, matriz[2], ggmk)
                for n3, l3 in enumerate(level3):
                    level4 = combinaciones(l3, matriz[3], ggmk)
                    for n4, l4 in enumerate(level4):
                        llaves.append(
                            (
                                a_codigo(ggmk),
                                a_codigo(l1),
                                a_codigo(l2),
                                a_codigo(l3),
                                a_codigo(l4),
                                f"K-{n1+1:02d}-{n2+1:02d}-{n3+1:02d}-{n4+1:02d}",
                                calcula_cilindro(llave=l4, ggmk=ggmk),
                                calcula_cilindro(llave=l4, ggmk=ggmk).count(":"),
                            )
                        )
                        # actualizar lista de maestras
                        todas_maestras.update({a_codigo(l1)})
                        todas_maestras.update({a_codigo(l2)})

        return llaves, todas_maestras

    def sin_smk(level1, matriz, ggmk):

        # tres niveles: GMK, MK, K
        todas_maestras = {ggmk}
        llaves = []
        for n1, l1 in enumerate(level1):
            level2 = combinaciones(l1, matriz[1], ggmk)
            for n2, l2 in enumerate(level2):
                level4 = combinaciones(l2, matriz[3], ggmk)
                for n4, l4 in enumerate(level4):
                    llaves.append(
                        (
                            a_codigo(ggmk),
                            a_codigo(l1),
                            a_codigo(l2),
                            0,
                            a_codigo(l4),
                            f"K-{n1+1:02d}-{n2+1:03d}-{n4+1:03d}",
                            calcula_cilindro(llave=l4, ggmk=ggmk),
                            calcula_cilindro(llave=l4, ggmk=ggmk).count(":"),
                        )
                    )
                    # actualizar lista de maestras
                    todas_maestras.update({a_codigo(l1)})
                    todas_maestras.update({a_codigo(l2)})

        return llaves, todas_maestras

    PAR = tuple(str(i) for i in range(0, 10, 2))
    IMPAR = tuple(str(i) for i in range(1, 10, 2))

    a_codigo = lambda i: "".join(i)

    matriz = genera_matriz_aleatoria(formato)

    ggmk = tuple(i for i in ggmk)
    level1 = combinaciones(ggmk, matriz[0], ggmk)

    # elige entre arbol con SMK o sin SMK
    if len([i for i in matriz if len(i) > 0]) == 4:
        llaves, todas_maestras = con_smk(level1, matriz, ggmk)
    else:
        llaves, todas_maestras = sin_smk(level1, matriz, ggmk)

    # eliminar llaves con maestras cruzadas
    llaves2 = [
        i
        for i in llaves
        if valida_llave_no_cruzada(i[6], (i[0], i[1], i[2]), todas_maestras)
    ]

    # TODO: crear secuencia de llave
    if len(llaves) > len(llaves2):
        pass
        # print(len(llaves), len(llaves2))

    return llaves2, genera_nombre_tabla(a_codigo(ggmk), matriz)


def genera_todas_maestras(llaves):
    maestras = {llaves[0][0]}
    for llave in llaves:
        maestras.update(llave[1])
        maestras.update(llave[2])

    return list(maestras)


def genera_matriz_aleatoria(formato):

    # lista desordenada aleatoria del 0-5
    _pines = list(range(0, 6))
    random.shuffle(_pines)

    # crear matriz en blanco en orden: GMK, MK, SMK, K
    matriz = [[] for _ in range(4)]

    # asigna item de lista desordenada segun pines por nivel de llave
    for s, m in enumerate(formato.split("-")[1:]):
        for _ in range(int(m)):
            matriz[s].append(_pines.pop())

    # cambia a ineditable
    return tuple(tuple(i) for i in matriz)


def calcula_cilindro(llave, ggmk):

    ggmk = (int(i) for i in ggmk)

    cilindro = []
    for g, k in zip(ggmk, llave):
        if g == k:
            cilindro.append(f"[{g}]")
        else:
            cilindro.append(f"[{min(int(g),int(k))}:{abs(int(g)-int(k))}]")

    return "".join(cilindro)


def valida_codigo(codigo):

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


def genera_nombre_tabla(ggmk, matriz):

    nombre = "("
    for i in matriz:
        for j in i:
            nombre += f"{j}"
        nombre += ")("

    return f"L-{ggmk}-{nombre[:-1]}"


def valida_llave_no_cruzada(cilindro, mis_maestras, todas_maestras):

    # revisa cilindro contra todas las llaves maestras que no le corresponden para asegurar que no lo abran
    for maestra in todas_maestras:
        if maestra in mis_maestras:
            continue
        if valida_llave_abre_cilindro([maestra], cilindro):
            return False
    return True


def valida_llave_abre_cilindro(llaves, cilindro):

    # crea lista de todas las llaves que pueden abrir ese cilindro
    opciones = [
        f"{pos[1]}{int(pos[1]) + int(pos[3])}" if ":" in pos else pos[1]
        for pos in cilindro.split("]")[:-1]
    ]
    g = [i.replace("[", "").replace(":", "") for i in opciones]
    cilindros = ["".join(i) for i in it.product(*g)]

    # revisa llaves de lista y ver si abren cilindro
    for llave in llaves:
        if llave not in cilindros:
            return False
    return True
