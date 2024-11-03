import itertools as it
import random

from herramientas import validaciones


def con_smk(level1, matriz, codigo_ggmk):

    # cuatro niveles: GMK, MK, SMK, K
    todas_maestras = {codigo_ggmk}
    llaves = []
    for n1, l1 in enumerate(level1):
        level2 = combinaciones(l1, matriz[1], codigo_ggmk)
        for n2, l2 in enumerate(level2):
            level3 = combinaciones(l2, matriz[2], codigo_ggmk)
            for n3, l3 in enumerate(level3):
                level4 = combinaciones(l3, matriz[3], codigo_ggmk)
                for n4, l4 in enumerate(level4):
                    llaves.append(
                        (
                            "".join(codigo_ggmk),
                            "".join(l1),
                            "".join(l2),
                            "".join(l3),
                            "".join(l4),
                            f"K-{n1+1:02d}-{n2+1:02d}-{n3+1:02d}-{n4+1:02d}",
                            calcula_cilindro(llave=l4, codigo_ggmk=codigo_ggmk),
                            calcula_cilindro(llave=l4, codigo_ggmk=codigo_ggmk).count(
                                ":"
                            ),
                        )
                    )
                    # actualizar lista de maestras
                    todas_maestras.update({"".join(l1)})
                    todas_maestras.update({"".join(l2)})

    return llaves, todas_maestras


def sin_smk(level1, matriz, codigo_ggmk):

    # tres niveles: GMK, MK, K
    todas_maestras = {codigo_ggmk}
    llaves = []
    for n1, l1 in enumerate(level1):
        level2 = combinaciones(l1, matriz[1], codigo_ggmk)
        for n2, l2 in enumerate(level2):
            level4 = combinaciones(l2, matriz[3], codigo_ggmk)
            for n4, l4 in enumerate(level4):
                llaves.append(
                    (
                        "".join(codigo_ggmk),
                        "".join(l1),
                        "".join(l2),
                        0,
                        "".join(l4),
                        f"K-{n1+1:02d}-{n2+1:03d}-{n4+1:03d}",
                        calcula_cilindro(llave=l4, codigo_ggmk=codigo_ggmk),
                        calcula_cilindro(llave=l4, codigo_ggmk=codigo_ggmk).count(":"),
                    )
                )
                # actualizar lista de maestras
                todas_maestras.update({"".join(l1)})
                todas_maestras.update({"".join(l2)})

    return llaves, todas_maestras


def combinaciones(codigo_origen, matriz, codigo_ggmk):

    # crea series de 5 numeros pares o 5 impares
    PAR = tuple(str(i) for i in range(0, 10, 2))
    IMPAR = tuple(str(i) for i in range(1, 10, 2))

    # todas las combinaciones validas cambiando los pines que correspondan
    m = list(codigo_origen)
    for p in matriz:
        m[p] = PAR if int(codigo_ggmk[p]) % 2 == 0 else IMPAR

    return [
        i
        for i in it.product(*m)
        if (i != codigo_origen and validaciones.valida_codigo(i))
    ]


def genera_todas_maestras(llaves):

    # crea una lista de todas las llaves maestras GGMK - SMK (para validaciones)
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


def calcula_cilindro(llave, codigo_ggmk):

    # computa nomenclatura de cilindro (master pin + pin para que llave y maestras abran)
    codigo_ggmk = (int(i) for i in codigo_ggmk)

    cilindro = []
    for g, k in zip(codigo_ggmk, llave):
        if int(g) == int(k) or int(g) == 0 or int(k) == 0:
            cilindro.append(f"[{g}]")
        else:
            cilindro.append(f"[{min(int(g),int(k))}:{abs(int(g)-int(k))}]")

    return "".join(cilindro)


def genera_nombre_tabla(codigo_ggmk, matriz):

    # crea nombre con formato L- (codigo_ggmk) (pines usados para cada nivel de matriz)
    nombre = "("
    for i in matriz:
        for j in i:
            nombre += f"{j}"
        nombre += ")("

    return f"L-{codigo_ggmk}-{nombre[:-1]}"


def main(codigo_ggmk, formato):

    # crea una matriz aleatoria de cuales pines cambiaran para generar combinaciones
    matriz = genera_matriz_aleatoria(formato)

    # crea el primer nivel de combinaciones originadas en la GGMK
    codigo_ggmk = tuple(i for i in codigo_ggmk)
    level1 = combinaciones(codigo_ggmk, matriz[0], codigo_ggmk)

    # elige entre generador de arbol con/sin SMK
    if len([i for i in matriz if len(i) > 0]) == 4:
        llaves, todas_maestras = con_smk(level1, matriz, codigo_ggmk)
    else:
        llaves, todas_maestras = sin_smk(level1, matriz, codigo_ggmk)

    # elimina llaves con maestras cruzadas (mas de una posicion de la matriz > 1 pin)
    llaves2 = [
        i
        for i in llaves
        if validaciones.valida_llave_no_cruzada(
            i[6], (i[0], i[1], i[2]), todas_maestras
        )
    ]

    # TODO: reestablece la secuencia de las llaves en caso se hayan eliminado llaves por cruzadas
    if len(llaves) > len(llaves2):
        pass
        # print(len(llaves), len(llaves2))

    return llaves2, genera_nombre_tabla("".join(codigo_ggmk), matriz)
