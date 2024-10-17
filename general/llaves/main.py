from random import randrange, shuffle
from copy import deepcopy as copy
from pprint import pprint


def define_arbol():
    total = 0

    arbol = []

    gmk = int(input("Numero de Grand Master Keys: "))

    for mk in range(gmk):
        arbol.append([])
        _key = int(input(f"    Numero de MK para GMK-{mk+1:02d}: "))

        for smk in range(_key):
            arbol[mk].append([])
            _key = int(input(f"        Numero de SMK para MK-{mk+1:02d}-{smk+1:02d}: "))

            for k in range(_key):
                _key = int(
                    input(
                        f"            Numero de K para SMK-{mk+1:02d}-{smk+1:02d}-{k+1:02d}: "
                    )
                )

                arbol[mk][smk].append(_key)
                total += _key

    return arbol, total


def cuenta_cilindros(arbol):
    total = 0
    for gmk in arbol:
        for mk in gmk:
            for smk in mk:
                total += smk
    return total


def muestra_arbol2(arbol):
    print("GGMK")
    for p, gmk in enumerate(arbol, start=1):
        print(f"|{'-'*9}GMK-{p:02d}")
        for q, mk in enumerate(gmk, start=1):
            print(
                f"{' ' if p==len(arbol) else '|'}{' '*9}{' ' if q==len(gmk) else '|'}{'-'*9} MK-{p:02d}-{q:02d}"
            )
            for r, smk in enumerate(mk, start=1):
                print(
                    f"{' ' if p==len(arbol) else '|'}{' '*9}{' ' if q==len(gmk) else '|'}{' '*10}{' ' if r==len(mk) else '|'}{'-'*9}SMK-{p:02d}-{q:02d}-{r:02d}"
                )
                for k in range(smk):
                    print(
                        f"{' ' if p==len(arbol) else '|'}{' '*9}{' ' if q==len(gmk) else '|'}{' '*10}{' ' if r==len(mk) else '|'}{' '*9}|{'-'*9}K-{p:02d}-{q:02d}-{r:02d}-{k:03d}"
                    )
                print(
                    f"{' ' if p==len(arbol) else '|'}{' '*9}{' ' if q==len(gmk) else '|'}{' '*10}{' ' if r==len(mk) else '|'}"
                )
            print(
                f"{' ' if p==len(arbol) else '|'}{' '*9}{' ' if q==len(gmk) else '|'}"
            )
        print(f"{' ' if p==len(arbol) else '|'}")


def muestra_arbol(arbol):
    print(f"GGMK | Codigo:{arbol['codigo']}")
    for p, gmk in enumerate(arbol["subkeys"], start=1):
        print(f"{' ' if p==len(arbol['subkeys']) else '|'}")
        print(f"|{'-'*9}GMK-{p:02d} | Codigo:{gmk['codigo']}")

        for q, mk in enumerate(gmk["subkeys"], start=1):
            print(
                f"{' ' if p==len(arbol['subkeys']) else '|'}{' '*9}{' ' if q==len(gmk['subkeys']) else '|'}"
            )
            print(
                f"{' ' if p==len(arbol['subkeys']) else '|'}{' '*9}{' ' if q==len(gmk['subkeys']) else '|'}{'-'*9} MK-{p:02d}-{q:02d} | Codigo:{mk['codigo']}"
            )
            for r, smk in enumerate(mk["subkeys"], start=1):
                print(
                    f"{' ' if p==len(arbol['subkeys']) else '|'}{' '*9}{' ' if q==len(gmk['subkeys']) else '|'}{' '*10}{' ' if r==len(mk['subkeys']) else '|'}"
                )
                print(
                    f"{' ' if p==len(arbol['subkeys']) else '|'}{' '*9}{' ' if q==len(gmk['subkeys']) else '|'}{' '*10}{' ' if r==len(mk) else '|'}{'-'*9}SMK-{p:02d}-{q:02d}-{r:02d} | Codigo:{smk['codigo']}"
                )
                for s, key in enumerate(smk["subkeys"]):

                    print(
                        f"{' ' if p==len(arbol['subkeys']) else '|'}{' '*9}{' ' if q==len(gmk['subkeys']) else '|'}{' '*10}{' ' if r==len(mk['subkeys']) else '|'}{' '*9}|{'-'*9}{key['secuencia']} Codigo:{key['codigo']} | Cilindro:{key['cilindro']:<30} | Validaciones> GGMK:{llave_abre_cilindro(arbol['codigo'], key['cilindro'])} GMK:{llave_abre_cilindro(gmk['codigo'], key['cilindro'])} MK:{llave_abre_cilindro(mk['codigo'], key['cilindro'])} SMK:{llave_abre_cilindro(smk['codigo'], key['cilindro'])}"
                    )


def valida_codigo(codigo):

    # string to tuple
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

    # ??

    return True


def llave_abre_cilindro(llave, cilindro):

    opciones = []
    for pos in cilindro.split("]")[:-1]:
        if ":" in pos:
            opciones.append((pos[1], int(pos[1]) + int(pos[3])))
        else:
            opciones.append((pos[1],))

    cilindros = []
    for a in opciones[0]:
        for b in opciones[1]:
            for c in opciones[2]:
                for d in opciones[3]:
                    for e in opciones[4]:
                        for f in opciones[5]:
                            cilindros.append(f"{a}{b}{c}{d}{e}{f}")

    if llave in cilindros:
        return 1

    return 0


def asigna_master_pin_pos(rama, mp_pos):
    while True:
        new_mp_pos = randrange(1, 6)
        if not any([i == new_mp_pos for i in mp_pos.values()]):
            mp_pos[rama] = new_mp_pos
            return mp_pos


def asigna_codigo(arbol):

    mp_pos = {"gmk": 0, "mk": 0, "smk": 0}

    # valores iniciales arbitrarios
    ggmk = gmk = mk = smk = key = (1, 2, 3, 4, 5, 6)

    # crear GGMK al azar
    while not (valida_codigo(ggmk)):
        ggmk = tuple(randrange(0, 10) for _ in range(6))
    cilindro = list(ggmk)

    mp_pos = asigna_master_pin_pos(rama="gmk", mp_pos=mp_pos)
    mp_pos = asigna_master_pin_pos(rama="mk", mp_pos=mp_pos)
    mp_pos = asigna_master_pin_pos(rama="smk", mp_pos=mp_pos)

    print(mp_pos)

    return

    for gmk in arbol:
        gmk_available_pos = [0]
        gmk_mp_pos = 0
        while gmk_mp_pos in gmk_available_pos:
            gmk_mp_pos = randrange(1, 6)
        gmk_available_pos.append(gmk_mp_pos)

        print(gmk_available_pos)
        return

        for mk in gmk:
            for smk in mk:

                print(smk)

    return
    # crear GMKs de la GGMK

    # crear cilindro de 3 master pins
    cilindro = list(ggmk)
    for _ in range(3):
        cilindro = nuevo_master_pin(cilindro)

    return ggmk, cilindro


def nuevo_master_pin(cilindro):

    while True:
        pos_modificar = randrange(1, 6)  # no se modifica primer pin
        if type(cilindro[pos_modificar]) is list:
            print("Pin ya es maestro")
            continue

        master_pin = randrange(2, 9)  # master pin debe ser entre 2 y 8
        if master_pin + cilindro[pos_modificar] > 9:
            print("Pin + master pin > 9")
            continue

        cilindro[pos_modificar] = [cilindro[pos_modificar], master_pin]

        return cilindro


def crea_arbol(estructura):
    _gmks = []
    for p, gmk in enumerate(estructura, start=1):
        _mks = []
        for q, mk in enumerate(gmk, start=1):
            _smks = []
            for r, smk in enumerate(mk, start=1):
                _keys = []
                for k in range(smk):
                    _keys.append(
                        {
                            "secuencia": f"K-{p:02d}-{q:02d}-{r:02d}-{k+1:03d}",
                            "tipo": "key",
                            "cilindro": "999999",
                            "codigo": "000000",
                        }
                    )
                _smks.append(
                    {
                        "secuencia": f"SMK-{p:02d}-{q:02d}-{r:02d}",
                        "tipo": "smk",
                        "subkeys": _keys,
                        "codigo": "000000",
                    }
                )
            _mks.append(
                {
                    "secuencia": f"MK-{p:02d}-{q:02d}",
                    "tipo": "mk",
                    "subkeys": _smks,
                    "codigo": "000000",
                }
            )
        _gmks.append(
            {
                "secuencia": f"GMK-{p:02d}",
                "tipo": "gmk",
                "subkeys": _mks,
                "codigo": "000000",
            }
        )
    ggmk = {"secuencia": f"GGMK", "tipo": "ggmk", "subkeys": _gmks, "codigo": "000000"}

    return ggmk


def crea_codigos(arbol):

    mp_pos = genera_mp_pos()

    codigo_ggmk = "123456"

    # crear GGMK al azar
    while not (valida_codigo(codigo_ggmk)):
        codigo_ggmk = "".join(str(randrange(0, 10)) for _ in range(6))

    arbol["codigo"] = copy(codigo_ggmk)

    usados = []
    for a, gmk in enumerate(arbol["subkeys"]):
        x = siguiente_codigo(
            tipo="gmk",
            codigo_base=arbol["codigo"],
            mp_pos=mp_pos,
            usados=usados,
        )

        if x == -1:
            break
        gmk["codigo"] = copy(x)
        usados.append(copy(x))

        for b, mk in enumerate(gmk["subkeys"]):

            x = siguiente_codigo(
                tipo="mk",
                codigo_base=gmk["codigo"],
                mp_pos=mp_pos,
                usados=usados,
            )

            if x == -1:
                break

            mk["codigo"] = copy(x)
            usados.append(copy(x))

            for c, smk in enumerate(mk["subkeys"]):
                x = siguiente_codigo(
                    tipo="smk",
                    codigo_base=mk["codigo"],
                    mp_pos=mp_pos,
                    usados=usados,
                )

                if x == -1:
                    break

                smk["codigo"] = copy(x)
                usados.append(copy(x))

                for d, k in enumerate(smk["subkeys"]):
                    x = siguiente_codigo(
                        tipo="k",
                        codigo_base=smk["codigo"],
                        mp_pos=mp_pos,
                        usados=usados,
                    )

                    if x == -1:
                        break

                    k["cilindro"] = crea_cilindro(
                        ggmk=codigo_ggmk,
                        key=copy(x),
                    )
                    k["codigo"] = copy(x)
                    usados.append(copy(x))

                    # pprin@", a, b, c, d)

    return arbol


def siguiente_codigo(tipo, codigo_base, mp_pos, usados):

    counter = 0

    while True:
        # crear nueva cifra para posicion de master pin con multiplo de 2 de diferencia
        nueva_cifra = (int(codigo_base[mp_pos[tipo]]) + randrange(1, 10) * 2) % 10

        # cambiar cifra de master pin con nueva cifra
        codigo_nuevo = [i for i in codigo_base]
        codigo_nuevo[mp_pos[tipo]] = str(nueva_cifra)
        codigo_nuevo = "".join(codigo_nuevo)

        # comprobar que el codigo no ha sido usado previamente
        if codigo_nuevo not in usados and valida_codigo(codigo_nuevo):
            # print("******", codigo_nuevo, sorted(usados))
            return codigo_nuevo

        counter += 1
        if counter > 500:
            return -1
            raise BufferError


def genera_mp_pos():
    pines = list(range(0, 6))
    shuffle(pines)
    mp_pos = {"gmk": pines[0]}
    mp_pos.update({"mk": pines[1]})
    mp_pos.update({"smk": pines[2]})
    mp_pos.update({"k": pines[3]})

    return mp_pos


def crea_cilindro(ggmk, key):

    ggmk = (int(i) for i in ggmk)
    key = (int(i) for i in key)

    cilindro = []
    for g, k in zip(ggmk, key):
        if g == k:
            cilindro.append(f"[{g}]")
        else:
            cilindro.append(f"[{min(g,k)}:{abs(g-k)}]")

    return "".join(cilindro)


def all_combos():
    all = []
    x = range(1, 10, 2)
    for a in [8]:
        for b in x:
            for c in x:
                for d in x:
                    for e in x:
                        for f in x:
                            codigo = f"{a}{b}{c}{d}{e}{f}"
                            if valida_codigo(codigo):
                                all.append(codigo)
                                print(codigo)

    print(len(all))


# c = [
#     [
#         [19, 22],
#         [87, 12, 33, 1],
#         [99, 74],
#         [77, 1, 56],
#     ],
#     [[87, 22, 12, 7], [77, 45]],
#     [
#         [19, 33, 33, 145, 11],
#         [
#             2,
#             5,
#             5,
#             44,
#         ],
#         [1, 5, 4, 9, 6],
#     ],
# ]


d = (
    [[3, 2, 4, 3], [4, 4, 2, 1], [3, 2], [1, 1, 1]],
    [
        [2, 1, 2, 1],
        [2, 2],
    ],
    [
        [2, 1, 3, 4],
        [2, 4, 4, 4],
        [1, 3, 3, 2],
    ],
    [[8, 7, 7, 7], [7, 7, 7, 7], [7, 7, 7, 7], [7, 7, 7, 7]],
)

arbol = crea_arbol(d)
# pprint(arbol)
# muestra_arbol(arbol)
# quit()
tries = 0
while True:
    try:
        arbol = crea_codigos(arbol)
        break
    except KeyboardInterrupt:
        quit()
    except BufferError:
        pass


muestra_arbol(arbol)
# pprint(arbol)
quit()


#     print(a["codigo"])

#     for b in a["subkeys"]:

#         print("    ", b["codigo"])

#         for c in b["subkeys"]:

#             print("         ", c["codigo"])

# quit()

# print(c)

# print(cuenta_cilindros(c))

# muestra_arbol(c)


llave = "154761"
cilindro = "[1][2:3][4][4:3][6][1:5]"
print(llave_abre_cilindro(llave=llave, cilindro=cilindro))

asigna_codigo(c)

# print(f"ggmk: {a}")
# print(f"Cilindro: {b}")
