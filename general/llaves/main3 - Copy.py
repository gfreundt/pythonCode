from random import randrange, shuffle
from copy import deepcopy as copy
from tkinter import Tk, Label, Text, END, font
from pprint import pprint
from datetime import datetime as dt
import json
import uuid


def pregunta_arbol():
    arbol = []

    gmk = int(input("Numero de GMKs: "))

    for mk in range(gmk):
        arbol.append([])
        _key = int(input(f"    Numero de MK para GMK-{mk+1:02d}: "))

        for k in range(_key):
            _key = int(
                input(f"            Numero de K para SMK-{mk+1:02d}-{k+1:02d}: ")
            )

            arbol[mk].append(_key)

    return arbol


def muestra_arbol(ggmk, todas_las_llaves, todas_maestras, resumen=False):

    totalx = 0
    total = 1

    print(f"GGMK | Codigo:{ggmk['codigo']}")
    for p, gmk in enumerate(ggmk["subkeys"], start=1):
        total += 1
        print("|")
        print(f"|{'-'*9}GMK-{p:02d} <> Codigo:{gmk['codigo']}")

        for q, mk in enumerate(gmk["subkeys"], start=1):
            total += 1
            print(f"{' ' if p==len(ggmk['subkeys']) else '|'}{' '*9}|")
            print(
                f"{' ' if p==len(ggmk['subkeys']) else '|'}{' '*9}{' ' if q==len(gmk['subkeys'])+1 else '|'}{'-'*9} MK-{p:02d}-{q:02d} <> Codigo:{mk['codigo']}"
            )
            print(
                f"{' ' if p==len(ggmk['subkeys']) else '|'}{' '*9}{' ' if q==len(gmk['subkeys']) else '|'}{' '*10}|"
            )
            if resumen:
                print(
                    f"{' ' if p==len(ggmk['subkeys']) else '|'}{' '*9}{' ' if q==len(gmk['subkeys']) else '|'}{' '*10}Unicas: {len(mk['subkeys'])}"
                )
                totalx += len(mk["subkeys"])
            else:
                for r, key in enumerate(mk["subkeys"], start=1):
                    totalx += 1
                    print(
                        f"{' ' if p==len(ggmk['subkeys']) else '|'}{' '*9}{' ' if q==len(gmk['subkeys']) else '|'}{' '*10}{' ' if r==len(mk['subkeys'])+1 else '|'}{'-'*9}{key['secuencia']} <> Codigo:{key['codigo']} - Cilindro:{key['cilindro']:<30} ({cantidad_master_pines(key['cilindro'])} MP) | Validaciones: GGMK:{llave_abre_cilindro(ggmk['codigo'], key['cilindro'])} GMK:{llave_abre_cilindro(gmk['codigo'], key['cilindro'])} MK:{llave_abre_cilindro(mk['codigo'], key['cilindro'])} UNICA:{llave_es_unica(mk['codigo'],todas_las_llaves)} CRUZADA: {llave_no_cruzada(key['cilindro'], todas_maestras, [ggmk['codigo'],gmk['codigo'],mk['codigo']])}"
                    )
    print(f"\nTotal Llaves: {total+totalx:,}")
    print(f"Total Puertas: {totalx:,}")


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


def llave_es_unica(llave, todas_las_llaves):
    if todas_las_llaves.count(llave) == 1:
        return 1
    return 0


def llave_no_cruzada(cilindro, todas_maestras, mis_maestras):
    for maestra in todas_maestras:
        if maestra in mis_maestras:
            continue
        if llave_abre_cilindro(maestra, cilindro):
            return 0

    return 1


def cantidad_master_pines(cilindro):
    return cilindro.count(":")


def asigna_master_pin_pos(rama, mp_pos):
    while True:
        new_mp_pos = randrange(1, 6)
        if not any([i == new_mp_pos for i in mp_pos.values()]):
            mp_pos[rama] = new_mp_pos
            return mp_pos


def crea_matriz(arbol):
    _gmks = []
    for p, gmk in enumerate(arbol, start=1):
        _mks = []
        for q, mk in enumerate(gmk, start=1):
            _keys = []
            for k in range(mk):
                _keys.append(
                    {
                        "secuencia": f"K-{p:02d}-{q:02d}-{k+1:03d}",
                        "tipo": "key",
                        "cilindro": "999999",
                        "codigo": "000000",
                    }
                )
            _mks.append(
                {
                    "secuencia": f"MK-{p:02d}-{q:02d}",
                    "tipo": "mk",
                    "subkeys": _keys,
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


def crea_codigos(ggmk):

    mp_pos = genera_mp_pos()

    codigo_ggmk = "123456"
    # crear GGMK al azar
    while not (valida_codigo(codigo_ggmk)):
        codigo_ggmk = "".join(str(randrange(0, 10)) for _ in range(6))

    ggmk["codigo"] = copy(codigo_ggmk)

    usados = [copy(codigo_ggmk)]
    for gmk in ggmk["subkeys"]:

        x = siguiente_codigo(
            tipo="gmk",
            codigo_base=(
                ggmk["codigo"] if not ggmk["subkeys"] else ggmk["subkeys"][-1]["codigo"]
            ),
            mp_pos=mp_pos,
            usados=usados,
        )
        if x == -1:
            break
        gmk["codigo"] = copy(x)
        usados.append(copy(x))

        for mk in gmk["subkeys"]:

            x = siguiente_codigo(
                tipo="mk",
                codigo_base=(
                    gmk["codigo"]
                    if not gmk["subkeys"]
                    else gmk["subkeys"][-1]["codigo"]
                ),
                mp_pos=mp_pos,
                usados=usados,
            )
            if x == -1:
                break
            mk["codigo"] = copy(x)
            usados.append(copy(x))

            for k in mk["subkeys"]:
                x = siguiente_codigo(
                    tipo="k",
                    codigo_base=(
                        mk["codigo"]
                        if not mk["subkeys"]
                        else mk["subkeys"][-1]["codigo"]
                    ),
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

    return ggmk


def siguiente_codigo(tipo, codigo_base, mp_pos, usados):

    k = 0

    while True:

        codigo_nuevo = [i for i in codigo_base]
        pos = mp_pos[tipo]

        if len(pos) == 1:

            codigo_nuevo[pos[0]] = str((int(codigo_nuevo[pos[0]]) + 2) % 10)
            codigo_nuevo = "".join(codigo_nuevo)

            if codigo_nuevo in usados:
                return -1

            if valida_codigo(codigo_nuevo):
                return codigo_nuevo

            return -1

        else:

            for a in range(0, 9, 2):
                codigo_nuevo[pos[3]] = str((int(codigo_nuevo[pos[3]]) + a) % 10)
                for b in range(0, 9, 2):
                    codigo_nuevo[pos[2]] = str((int(codigo_nuevo[pos[2]]) + b) % 10)
                    for c in range(0, 9, 2):
                        codigo_nuevo[pos[1]] = str((int(codigo_nuevo[pos[1]]) + c) % 10)
                        for d in range(0, 9, 2):
                            codigo_nuevo[pos[0]] = str(
                                (int(codigo_nuevo[pos[0]]) + d) % 10
                            )
                            cn = "".join(codigo_nuevo)
                            if cn not in usados and valida_codigo(cn):
                                return cn
            return -1


def siguiente_codigo2(tipo, codigo_base, mp_pos, usados):

    counter = 0

    while True:
        codigo_nuevo = [i for i in codigo_base]
        mp = mp_pos[tipo]
        shuffle(mp)
        for pos in mp:
            # crear nueva cifra para posicion de master pin con multiplo de 2 de diferencia
            nueva_cifra = (int(codigo_base[pos]) + randrange(1, 10) * 2) % 10

            # cambiar cifra de master pin con nueva cifra
            codigo_nuevo[pos] = str(nueva_cifra)

        # comprobar que el codigo no ha sido usado previamente
        codigo_nuevo = "".join(codigo_nuevo)
        if codigo_nuevo not in usados and valida_codigo(codigo_nuevo):
            return codigo_nuevo

        counter += 1
        if counter > 2000:
            return -1
            raise BufferError


def genera_mp_pos():
    pines = list(range(0, 6))
    shuffle(pines)
    mp_pos = {"gmk": pines[0:1]}
    mp_pos.update({"mk": pines[1:2]})
    mp_pos.update({"k": pines[2:]})

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


def crea_libro2(ggmk):

    suma = 0

    mp_pos = genera_mp_pos()
    print(mp_pos)
    moviles = mp_pos["k"]
    x = [int(i) % 2 for i in ggmk]

    output = []
    for one in range(0, 10, 2):
        new_code = [i for i in ggmk]
        new_code[mp_pos["gmk"][0]] = str(one + x[mp_pos["gmk"][0]])

        n = []
        for two in range(0, 10, 2):
            new_code[mp_pos["mk"][0]] = str(two + x[mp_pos["mk"][0]])

            o = []
            for a in range(0, 10, 2):
                new_code[moviles[0]] = str(a + x[moviles[0]])

                p = []
                for b in range(0, 10, 2):
                    new_code[moviles[1]] = str(b + x[moviles[1]])

                    q = []
                    for c in range(0, 10, 2):
                        new_code[moviles[2]] = str(c + x[moviles[2]])

                        r = []
                        for d in range(0, 10, 2):
                            new_code[moviles[3]] = str(d + x[moviles[3]])
                            nc = "".join(new_code)
                            if nc != ggmk and valida_codigo(nc):
                                r.append("".join(agrega_formato(ggmk, new_code)))
                                suma += 1

                            else:
                                r.append("                ")

                        q.append(r)

                    p.append(q)

                o.append(p)

        n.append(o)

    return n


def crea_libro(codigo_ggmk="123456"):

    todas_maestras = []
    mp_pos = genera_mp_pos()

    # crear GGMK al azar si codigo ingresado no es valido o no se pasa
    while not (valida_codigo(codigo_ggmk)):
        print("GGMK al azar")
        codigo_ggmk = "".join(str(randrange(0, 10)) for _ in range(6))

    ggmk = {
        "codigo": copy(codigo_ggmk),
        "nombre": "GGMK",
        "proyecto": "",
        "notas": "",
        "fecha": "",
        "subkeys": [],
    }

    usados = [copy(codigo_ggmk)]
    todas_maestras.append(copy(codigo_ggmk))

    c1 = 0
    while True:
        x1 = siguiente_codigo(
            tipo="gmk",
            codigo_base=(
                ggmk["codigo"] if not ggmk["subkeys"] else ggmk["subkeys"][-1]["codigo"]
            ),
            mp_pos=mp_pos,
            usados=usados,
        )
        if x1 == -1:
            break
        ggmk["subkeys"].append(
            {
                "codigo": copy(x1),
                "subkeys": [],
                "secuencia": f"GMK-{c1+1:02d}",
            }
        )
        usados.append(copy(x1))
        todas_maestras.append(copy(x1))

        c2 = 0
        while True:
            x2 = siguiente_codigo(
                tipo="mk",
                codigo_base=(
                    x1
                    if not ggmk["subkeys"][c1]["subkeys"]
                    else ggmk["subkeys"][c1]["subkeys"][-1]["codigo"]
                ),
                mp_pos=mp_pos,
                usados=usados,
            )
            if x2 == -1:
                break
            ggmk["subkeys"][c1]["subkeys"].append(
                {
                    "codigo": copy(x2),
                    "subkeys": [],
                    "secuencia": f"MK-{c1+1:02d}-{c2+1:02d}",
                }
            )
            usados.append(copy(x2))
            todas_maestras.append(copy(x2))

            c3 = 0
            while True:
                x3 = siguiente_codigo(
                    tipo="k",
                    codigo_base=(
                        x2
                        if not ggmk["subkeys"][c1]["subkeys"][c2]["subkeys"]
                        else ggmk["subkeys"][c1]["subkeys"][c2]["subkeys"][-1]["codigo"]
                    ),
                    mp_pos=mp_pos,
                    usados=usados,
                )
                if x3 == -1:
                    break
                ggmk["subkeys"][c1]["subkeys"][c2]["subkeys"].append(
                    {
                        "codigo": copy(x3),
                        "cilindro": crea_cilindro(ggmk=codigo_ggmk, key=copy(x3)),
                        "secuencia": f"K-{c1+1:02d}-{c2+1:02d}-{c3+1:03d}",
                    }
                )
                usados.append(copy(x3))
                c3 += 1
            c2 += 1
        c1 += 1
    return ggmk, usados, todas_maestras


def agrega_formato(ggmk, new_code):

    text = ""
    for g, n in zip(ggmk, new_code):
        if g == n:
            text += f"#{n}"
        else:
            text += f"%{n}"

    return text


def imprime_libro(libro):

    print((libro[0][0][0][0]))

    windows = [Tk(), Tk(), Tk(), Tk(), Tk()]

    for up, upx in enumerate(libro):

        for pg, page in enumerate(upx):

            windows[pg].title(f"MK = {x}")

            for i in range(1, 26, 5):
                h = Text(
                    windows[pg],
                    height=1,
                    width=30,
                    bg="white",
                    font=font.Font(family="Arial Bold", size=10),
                )
                h.grid(
                    column=i,
                    row=0,
                    columnspan=5,
                    padx=0,
                    pady=0,
                    ipadx=12,
                    ipady=0,
                )
                h.insert(END, "123456")

            for j in range(1, 26, 5):
                h = Text(windows[pg], height=5, width=5, bg="white")
                h.grid(
                    column=0,
                    row=j,
                    rowspan=5,
                    padx=0,
                    pady=0,
                    ipadx=0,
                    ipady=8,
                )

            for blk, block in enumerate(page):
                for i, a in enumerate(block):
                    for j, b in enumerate(a):
                        bg = f'{"lightgray" if (blk+pg)%2==0 else "white"}'

                        T = Text(
                            windows[pg],
                            height=1,
                            width=6,
                            bg=bg,
                            font=font.Font(family="Arial", size=10),
                        )
                        T.grid(
                            column=(i + blk * 5) + 1, row=(j + pg * 5) + 1, sticky=""
                        )

                        word = [
                            i
                            for k, i in enumerate(libro[up][pg][blk][i][j])
                            if k % 2 == 1
                        ]
                        fmt = [
                            i
                            for k, i in enumerate(libro[up][pg][blk][i][j])
                            if k % 2 == 0
                        ]
                        T.insert(END, "".join(word))

                        for k, f in enumerate(fmt):
                            T.tag_add(f"text{k}", f"1.{k}", f"1.{k+1}")
                            T.tag_configure(
                                f"text{k}",
                                font=font.Font(
                                    family="Arial", size=10, underline=(f == "%")
                                ),
                            )

    windows[0].mainloop()


def graba_arbol(ggmk, nombre, notas, fecha):
    ggmk["proyecto"] = nombre
    ggmk["notas"] = notas
    ggmk["fecha"] = fecha

    with open("proyectos.json", "w") as outfile:
        json_object = json.dumps(ggmk, indent=4)
        outfile.write(json_object)


def main():

    x = input("Codigo: ")
    y = input("Nombre: ")
    z = input("Notas: ")
    f = dt.strftime(dt.now(), "%Y-%m-%d")

    # crea arbol de libro completo
    ggmk, todas_las_llaves, todas_maestras = crea_libro(x)

    # muestra arbol de libro completo
    muestra_arbol(ggmk, todas_las_llaves, todas_maestras, resumen=True)

    # graba arbol
    graba_arbol(ggmk, nombre=y, notas=z, fecha=f)


if __name__ == "__main__":

    main()


"""     
        output = f"GGMK | Codigo:{self.ggmk['codigo']}\n"
        for p, gmk in enumerate(self.ggmk["subkeys"], start=1):
            total += 1
            output += "|\n"
            output += f"|{'-'*9}GMK-{p:02d} <> Codigo:{gmk['codigo']}\n"

            for q, mk in enumerate(gmk["subkeys"], start=1):
                total += 1
                output += f"{' ' if p==len(self.ggmk['subkeys']) else '|'}{' '*9}|\n"
                output += f"{' ' if p==len(self.ggmk['subkeys']) else '|'}{' '*9}{' ' if q==len(gmk['subkeys'])+1 else '|'}{'-'*9} MK-{p:02d}-{q:02d} <> Codigo:{mk['codigo']}\n"
                output += f"{' ' if p==len(self.ggmk['subkeys']) else '|'}{' '*9}{' ' if q==len(gmk['subkeys']) else '|'}{' '*10}|\n"

                if not detalle:
                    output += f"{' ' if p==len(self.ggmk['subkeys']) else '|'}{' '*9}{' ' if q==len(gmk['subkeys']) else '|'}{' '*10}Unicas: {len(mk['subkeys'])}\n"
                    totalx += len(mk["subkeys"])
                else:
                    for r, key in enumerate(mk["subkeys"], start=1):
                        totalx += 1
                        output += f"{' ' if p==len(self.ggmk['subkeys']) else '|'}{' '*9}{' ' if q==len(gmk['subkeys']) else '|'}{' '*10}{' ' if r==len(mk['subkeys'])+1 else '|'}{'-'*9}{key['secuencia']} <> Codigo:{key['codigo']} - Cilindro:{key['cilindro']:<30} ({cantidad_master_pines(key['cilindro'])} MP) | Validaciones: self.ggmk:{valida_llave_abre_cilindro(self.ggmk['codigo'], key['cilindro'])} GMK:{valida_llave_abre_cilindro(gmk['codigo'], key['cilindro'])} MK:{valida_llave_abre_cilindro(mk['codigo'], key['cilindro'])} UNICA:{self.valida_llave_es_unica(mk['codigo'])} CRUZADA:{self.valida_llave_no_cruzada(key['cilindro'],[self.ggmk['codigo'],gmk['codigo'],mk['codigo']])}\n"

        output += f"\nTotal Llaves: {total+totalx:,}\n"
        output += f"Total Puertas: {totalx:,}\n"
"""
