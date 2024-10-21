from random import randrange, shuffle
from copy import deepcopy as copy
from tkinter import Tk, Label, Text, END, font
from pprint import pprint


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


def muestra_arbol(ggmk):

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
            for r, key in enumerate(mk["subkeys"], start=1):
                totalx += 1
                print(
                    f"{' ' if p==len(ggmk['subkeys']) else '|'}{' '*9}{' ' if q==len(gmk['subkeys']) else '|'}{' '*10}{' ' if r==len(mk['subkeys'])+1 else '|'}{'-'*9}{key['secuencia']} <> Codigo:{key['codigo']} - Cilindro:{key['cilindro']:<30} | Validaciones: GGMK:{llave_abre_cilindro(ggmk['codigo'], key['cilindro'])} GMK:{llave_abre_cilindro(gmk['codigo'], key['cilindro'])} MK:{llave_abre_cilindro(mk['codigo'], key['cilindro'])}"
                )
    print(f"\nTotal Llaves: {total+totalx}")
    print(f"Total Puertas: {totalx}")


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
            codigo_base=ggmk["codigo"],
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
                codigo_base=gmk["codigo"],
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
                    codigo_base=mk["codigo"],
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


def crea_libro(ggmk):

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


def main(arbol=None):

    if not arbol:
        arbol = pregunta_arbol()
    ggmk = crea_matriz(arbol)

    while True:
        try:
            ggmk = crea_codigos(ggmk)
            break
        except KeyboardInterrupt:
            quit()
        except BufferError:
            pass

    muestra_arbol(ggmk)


arbol = ([13, 201, 110], [201, 10, 160, 7], [256, 1, 3, 6], [8])
arbol = ([3, 2, 1], [2, 1, 3, 7], [2, 1, 3, 6], [2, 3])


arbol = (
    [300, 300, 300, 300],
    [300, 300, 300, 300],
    [300, 300, 300, 300],
    [300, 300, 300, 300],
)
main(arbol)

quit()

# a = crea_libro("236582")
# a = crea_libro("855327")

# imprime_libro(a)
