import math
import random
import tkinter as tk
import tkinter.font as tkfont

FONDO = "#10131f"
FONDO_ARRIBA = "#090c17"
FONDO_ABAJO = "#181c36"
PANEL = "#1a1e30"
COL_CASILLA = "#20253a"
COL_CASILLA_HOVER = "#2a3050"
BORDE = "#2c3350"
TEXTO = "#eceef7"
APAGADO = "#7c84a3"
COLOR_X = "#ff6b57"
COLOR_O = "#35e0c4"
DORADO = "#ffcf5c"


def mezclar(c1, c2, t):
    a = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(c2[i:i + 2], 16) for i in (1, 3, 5)]
    return "#%02x%02x%02x" % tuple(int(x + (y - x) * t) for x, y in zip(a, b))


def rect_redondeado(c, x1, y1, x2, y2, r, **kw):
    p = [x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r,
         x2, y2 - r, x2, y2, x2 - r, y2, x1 + r, y2,
         x1, y2, x1, y2 - r, x1, y1 + r, x1, y1]
    return c.create_polygon(p, smooth=True, **kw)


LINEAS = [(0, 1, 2), (3, 4, 5), (6, 7, 8),
          (0, 3, 6), (1, 4, 7), (2, 5, 8),
          (0, 4, 8), (2, 4, 6)]


def ganador(tablero):
    for a, b, c in LINEAS:
        if tablero[a] and tablero[a] == tablero[b] == tablero[c]:
            return tablero[a], (a, b, c)
    return None, None


def libres(tablero):
    return [i for i, v in enumerate(tablero) if not v]


def jugada_que_cierra(tablero, ficha):
    for i in libres(tablero):
        tablero[i] = ficha
        g, _ = ganador(tablero)
        tablero[i] = ""
        if g == ficha:
            return i
    return None


def minimax(tablero, turno, yo, prof):
    g, _ = ganador(tablero)
    if g == yo:
        return 10 - prof
    if g:
        return prof - 10
    if not libres(tablero):
        return 0
    otro = "O" if turno == "X" else "X"
    puntajes = []
    for i in libres(tablero):
        tablero[i] = turno
        puntajes.append(minimax(tablero, otro, yo, prof + 1))
        tablero[i] = ""
    return max(puntajes) if turno == yo else min(puntajes)


def mejor_jugada(tablero, yo):
    otro = "X" if yo == "O" else "O"
    mejor, candidatas = -99, []
    for i in libres(tablero):
        tablero[i] = yo
        p = minimax(tablero, otro, yo, 1)
        tablero[i] = ""
        if p > mejor:
            mejor, candidatas = p, [i]
        elif p == mejor:
            candidatas.append(i)
    return random.choice(candidatas)


def jugada_maquina(tablero, nivel, yo="O"):
    otro = "X" if yo == "O" else "O"
    disponibles = libres(tablero)

    if nivel == "facil":
        if random.random() < 0.2:
            j = jugada_que_cierra(tablero, yo)
            if j is not None:
                return j
        return random.choice(disponibles)

    if nivel == "medio":
        if random.random() < 0.25:
            return random.choice(disponibles)
        for ficha in (yo, otro):
            j = jugada_que_cierra(tablero, ficha)
            if j is not None:
                return j
        if 4 in disponibles:
            return 4
        esquinas = [i for i in (0, 2, 6, 8) if i in disponibles]
        return random.choice(esquinas or disponibles)

    if len(disponibles) == 9:
        return random.choice([0, 2, 4, 6, 8])
    return mejor_jugada(tablero, yo)


class Triki:
    ANCHO, ALTO = 520, 760
    TAM, SEP = 130, 10
    BX, BY = 55, 290
    CAPAS = ((18, 0.08), (10, 0.18), (0, 1.0))
    NOMBRE_NIVEL = {"facil": "FÁCIL", "medio": "MEDIA", "dificil": "DIFÍCIL"}

    def __init__(self, root):
        self.root = root
        root.title("Triki")
        root.configure(bg=FONDO)
        root.resizable(False, False)

        self.c = tk.Canvas(root, width=self.ANCHO, height=self.ALTO,
                           bg=FONDO, highlightthickness=0)
        self.c.pack()

        disponibles = set(tkfont.families())
        preferidas = ("Segoe UI", "Poppins", "Montserrat", "Ubuntu",
                      "Helvetica Neue", "Cantarell", "DejaVu Sans")
        self.familia = next((f for f in preferidas if f in disponibles), "Helvetica")

        self.trabajos = []
        self.bucle = None
        self.flotantes = []
        self.piezas = []
        self.botones = []
        self.boton_activo = None
        self.cursor_actual = ""
        self.pantalla = "menu"
        self.modo = "cpu"
        self.nivel = "medio"
        self.hover = None

        self.c.bind("<Button-1>", self.al_hacer_clic)
        self.c.bind("<Motion>", self.al_mover)
        root.bind("<Escape>", lambda e: self.menu() if self.pantalla == "juego" else None)
        self.menu()

    def fuente(self, tam, negrita=False):
        return (self.familia, tam, "bold" if negrita else "normal")

    def despues(self, ms, fn):
        self.trabajos.append(self.root.after(ms, fn))

    def cancelar_trabajos(self):
        for t in self.trabajos:
            self.root.after_cancel(t)
        self.trabajos = []

    def limpiar(self):
        self.cancelar_trabajos()
        if self.bucle is not None:
            self.root.after_cancel(self.bucle)
            self.bucle = None
        self.flotantes = []
        self.botones = []
        self.boton_activo = None
        self.c.delete("all")
        self.cursor_actual = ""
        self.c.config(cursor="")

    def fondo(self):
        paso = 8
        for y in range(0, self.ALTO, paso):
            self.c.create_rectangle(0, y, self.ANCHO, y + paso,
                                    fill=mezclar(FONDO_ARRIBA, FONDO_ABAJO, y / self.ALTO),
                                    outline="", tags="fondo")

    def ambiente(self):
        for k in range(10):
            ficha = "X" if k % 2 == 0 else "O"
            base = COLOR_X if ficha == "X" else COLOR_O
            color = mezclar(FONDO_ABAJO, base, random.uniform(0.10, 0.22))
            r = random.uniform(14, 30)
            f = {"ficha": ficha, "x": random.uniform(20, 500), "y": random.uniform(0, self.ALTO),
                 "vx": random.uniform(-0.2, 0.2), "vy": random.uniform(0.25, 0.7),
                 "r": r, "ang": random.uniform(0, 6.28), "va": random.uniform(-0.012, 0.012)}
            if ficha == "X":
                f["ids"] = [self.c.create_line(0, 0, 0, 0, width=r / 3, fill=color,
                                               capstyle="round", tags="ambiente") for _ in range(2)]
            else:
                f["ids"] = [self.c.create_oval(0, 0, 0, 0, width=r / 3, outline=color, tags="ambiente")]
            self.situar_flotante(f)
            self.flotantes.append(f)
        self.bucle = self.root.after(40, self.mover_ambiente)

    def situar_flotante(self, f):
        x, y, r = f["x"], f["y"], f["r"]
        if f["ficha"] == "X":
            for k, i in enumerate(f["ids"]):
                a = f["ang"] + k * math.pi / 2 + math.pi / 4
                dx, dy = r * math.cos(a), r * math.sin(a)
                self.c.coords(i, x - dx, y - dy, x + dx, y + dy)
        else:
            self.c.coords(f["ids"][0], x - r, y - r, x + r, y + r)

    def mover_ambiente(self):
        for f in self.flotantes:
            f["y"] -= f["vy"]
            f["x"] += f["vx"]
            f["ang"] += f["va"]
            if f["y"] < -50:
                f["y"] = self.ALTO + 50
                f["x"] = random.uniform(20, 500)
            self.situar_flotante(f)
        self.bucle = self.root.after(40, self.mover_ambiente)

    def linea_brillo(self, x1, y1, x2, y2, grosor, color, base, tags):
        return [self.c.create_line(x1, y1, x2, y2, width=grosor + extra,
                                   fill=mezclar(base, color, alfa), capstyle="round", tags=tags)
                for extra, alfa in self.CAPAS]

    def situar_linea(self, ids, x1, y1, x2, y2):
        for i in ids:
            self.c.coords(i, x1, y1, x2, y2)

    def circulo_brillo(self, cx, cy, r, grosor, color, base, tags):
        for extra, alfa in self.CAPAS:
            self.c.create_oval(cx - r, cy - r, cx + r, cy + r, width=grosor + extra,
                               outline=mezclar(base, color, alfa), tags=tags)

    def x_capas(self, cx, cy, r, grosor, color, base, tags):
        l1, l2 = [], []
        for extra, alfa in self.CAPAS:
            for lista, (ax, ay) in ((l1, (cx - r, cy - r)), (l2, (cx + r, cy - r))):
                lista.append(self.c.create_line(ax, ay, ax, ay, width=grosor + extra,
                                                fill=mezclar(base, color, alfa),
                                                capstyle="round", tags=tags))
        return l1, l2

    def x_brillo(self, cx, cy, r, grosor, color, base, tags):
        l1, l2 = self.x_capas(cx, cy, r, grosor, color, base, tags)
        self.situar_linea(l1, cx - r, cy - r, cx + r, cy + r)
        self.situar_linea(l2, cx + r, cy - r, cx - r, cy + r)

    def casilla(self, x1, y1, tam, radio):
        rect_redondeado(self.c, x1, y1 + 5, x1 + tam, y1 + tam + 5, radio,
                        fill=mezclar(FONDO, "#000000", 0.55), outline="")
        return rect_redondeado(self.c, x1, y1, x1 + tam, y1 + tam, radio,
                               fill=COL_CASILLA, outline=BORDE, width=1)

    def pastilla(self, x, y, texto, color, tam, tags, pad_x=18, pad_y=9, alfa=0.12):
        t = self.c.create_text(x, y, text=texto, font=self.fuente(tam, True), fill=color, tags=tags)
        x1, y1, x2, y2 = self.c.bbox(t)
        p = rect_redondeado(self.c, x1 - pad_x, y1 - pad_y, x2 + pad_x, y2 + pad_y,
                            (y2 - y1 + 2 * pad_y) / 2,
                            fill=mezclar(PANEL, color, alfa),
                            outline=mezclar(BORDE, color, 0.45), tags=tags)
        self.c.tag_lower(p, t)

    def boton(self, cx, cy, w, h, texto, comando, color=COLOR_X,
              sub=None, estilo="solido", tam=16, nivel=None):
        x1, y1, x2, y2 = cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2

        if estilo == "solido":
            base, hover = color, mezclar(color, "#ffffff", 0.16)
            tcol, borde, scol = FONDO, "", mezclar(color, FONDO, 0.7)
            sombra = mezclar(color, "#000000", 0.55)
        else:
            base, hover = PANEL, COL_CASILLA_HOVER
            tcol, borde, scol = TEXTO, BORDE, APAGADO
            sombra = mezclar(FONDO, "#000000", 0.5)

        rect_redondeado(self.c, x1, y1 + 5, x2, y2 + 5, 16, fill=sombra, outline="")
        rect = rect_redondeado(self.c, x1, y1, x2, y2, 16, fill=base, outline=borde, width=2)
        if sub:
            self.c.create_text(cx, cy - 11, text=texto, font=self.fuente(tam, True), fill=tcol)
            self.c.create_text(cx, cy + 14, text=sub, font=self.fuente(10), fill=scol)
        else:
            self.c.create_text(cx, cy, text=texto, font=self.fuente(tam, True), fill=tcol)
        if nivel:
            for i in range(3):
                bx = x2 - 64 + i * 14
                alto = 10 + i * 7
                self.c.create_rectangle(bx, cy + 14 - alto, bx + 9, cy + 14,
                                        fill=FONDO if i < nivel else mezclar(base, FONDO, 0.3),
                                        outline="")

        self.botones.append({"area": (x1, y1, x2, y2), "rect": rect, "base": base,
                             "hover": hover, "comando": comando})

    def boton_en(self, x, y):
        for b in reversed(self.botones):
            x1, y1, x2, y2 = b["area"]
            if x1 <= x <= x2 and y1 <= y <= y2:
                return b
        return None

    def poner_cursor(self, nombre):
        if nombre != self.cursor_actual:
            self.cursor_actual = nombre
            self.c.config(cursor=nombre)

    def menu(self):
        self.limpiar()
        self.pantalla = "menu"
        self.fondo()
        self.ambiente()

        self.c.create_text(264, 104, text="T R I K I", font=self.fuente(52, True),
                           fill=mezclar(FONDO_ARRIBA, COLOR_X, 0.55))
        self.c.create_text(260, 100, text="T R I K I", font=self.fuente(52, True), fill=TEXTO)
        self.c.create_text(260, 152, text="T R E S   E N   L Í N E A",
                           font=self.fuente(10, True), fill=APAGADO)
        self.c.create_rectangle(216, 174, 258, 177, fill=COLOR_X, outline="")
        self.c.create_rectangle(262, 174, 304, 177, fill=COLOR_O, outline="")

        t, s = 64, 8
        x0, y0 = 260 - (3 * t + 2 * s) / 2, 215
        disposicion = ["X", "O", "", "O", "X", "", "", "", "X"]
        centros = []
        for i in range(9):
            f, col = divmod(i, 3)
            x1, y1 = x0 + col * (t + s), y0 + f * (t + s)
            self.casilla(x1, y1, t, 14)
            centros.append((x1 + t / 2, y1 + t / 2))
        (ax, ay), (bx, by) = centros[0], centros[8]
        self.linea_brillo(ax - 24, ay - 24, bx + 24, by + 24, 5, DORADO, COL_CASILLA, "logo")
        for i, ficha in enumerate(disposicion):
            cx, cy = centros[i]
            if ficha == "X":
                self.x_brillo(cx, cy, 15, 7, COLOR_X, COL_CASILLA, "logo")
            elif ficha == "O":
                self.circulo_brillo(cx, cy, 15, 7, COLOR_O, COL_CASILLA, "logo")

        self.boton(260, 480, 340, 72, "Contra la máquina", self.pantalla_dificultad,
                   COLOR_X, sub="Un jugador · tres dificultades")
        self.boton(260, 565, 340, 72, "Dos jugadores", lambda: self.empezar("dos"),
                   COLOR_O, sub="Los dos en el mismo equipo")
        self.boton(260, 645, 340, 50, "Salir", self.root.destroy, estilo="fantasma", tam=13)

        self.c.create_text(260, 724, text="Hecho en Python con tkinter",
                           font=self.fuente(9), fill=APAGADO)

    def pantalla_dificultad(self):
        self.limpiar()
        self.pantalla = "dificultad"
        self.fondo()
        self.ambiente()

        self.c.create_text(260, 125, text="¿Qué tan en serio?", font=self.fuente(30, True), fill=TEXTO)
        self.c.create_text(260, 172, text="Tú juegas con X", font=self.fuente(12), fill=APAGADO)
        self.c.create_rectangle(216, 198, 258, 201, fill=COLOR_X, outline="")
        self.c.create_rectangle(262, 198, 304, 201, fill=COLOR_O, outline="")

        self.boton(260, 290, 340, 76, "Fácil", lambda: self.empezar("cpu", "facil"),
                   COLOR_O, sub="Se distrae casi siempre", nivel=1)
        self.boton(260, 380, 340, 76, "Media", lambda: self.empezar("cpu", "medio"),
                   DORADO, sub="Bloquea, pero a veces se le va", nivel=2)
        self.boton(260, 470, 340, 76, "Difícil", lambda: self.empezar("cpu", "dificil"),
                   COLOR_X, sub="No se le puede ganar", nivel=3)
        self.boton(260, 575, 340, 50, "← Volver", self.menu, estilo="fantasma", tam=13)

    def empezar(self, modo, nivel=None):
        self.modo = modo
        self.nivel = nivel
        self.puntos = {"X": 0, "O": 0, "=": 0}
        self.numero_ronda = 0
        self.pantalla_juego()

    def pantalla_juego(self):
        self.limpiar()
        self.pantalla = "juego"
        self.fondo()

        self.boton(80, 48, 110, 40, "← Menú", self.menu, estilo="fantasma", tam=11)
        self.boton(440, 48, 140, 40, "Nueva ronda", self.nueva_ronda, estilo="fantasma", tam=11)

        if self.modo == "cpu":
            etiqueta = f"VS MÁQUINA · {self.NOMBRE_NIVEL[self.nivel]}"
        else:
            etiqueta = "DOS JUGADORES"
        self.pastilla(260, 48, etiqueta, APAGADO, 9, "chip", pad_x=16, pad_y=8)

        self.rects = []
        for i in range(9):
            f, col = divmod(i, 3)
            x1 = self.BX + col * (self.TAM + self.SEP)
            y1 = self.BY + f * (self.TAM + self.SEP)
            self.rects.append(self.casilla(x1, y1, self.TAM, 20))

        self.c.create_text(260, 736, text="Esc para volver al menú", font=self.fuente(9), fill=APAGADO)
        self.nueva_ronda()

    def centro(self, i):
        f, col = divmod(i, 3)
        return (self.BX + col * (self.TAM + self.SEP) + self.TAM / 2,
                self.BY + f * (self.TAM + self.SEP) + self.TAM / 2)

    def casilla_en(self, x, y):
        for i in range(9):
            f, col = divmod(i, 3)
            x1 = self.BX + col * (self.TAM + self.SEP)
            y1 = self.BY + f * (self.TAM + self.SEP)
            if x1 <= x <= x1 + self.TAM and y1 <= y <= y1 + self.TAM:
                return i
        return None

    def reiniciar_casillas(self):
        for r in self.rects:
            self.c.itemconfig(r, fill=COL_CASILLA, outline=BORDE)

    def nueva_ronda(self):
        self.cancelar_trabajos()
        self.c.delete("marca", "fantasma", "linea", "confeti")
        self.tablero = [""] * 9
        self.turno = "X" if self.numero_ronda % 2 == 0 else "O"
        self.numero_ronda += 1
        self.terminada = False
        self.resultado = None
        self.celebrar = False
        self.bloqueado = False
        self.hover = None
        self.reiniciar_casillas()
        self.actualizar_panel()
        self.turno_maquina()

    def turno_maquina(self):
        if self.modo == "cpu" and self.turno == "O" and not self.terminada:
            self.bloqueado = True
            self.despues(650, self.juega_maquina)

    def juega_maquina(self):
        self.colocar(jugada_maquina(self.tablero, self.nivel, "O"))

    def colocar(self, i):
        self.bloqueado = True
        self.hover = None
        self.c.delete("fantasma")
        self.reiniciar_casillas()
        self.tablero[i] = self.turno
        self.animar_marca(i, self.turno, self.despues_de_jugar)

    def despues_de_jugar(self):
        g, linea = ganador(self.tablero)
        if g:
            self.puntos[g] += 1
            self.terminada = True
            self.resultado = g
            self.celebrar = self.modo == "dos" or g == "X"
            self.actualizar_panel()
            self.animar_linea(linea)
        elif all(self.tablero):
            self.puntos["="] += 1
            self.terminada = True
            self.resultado = "="
            self.actualizar_panel()
            self.bloqueado = False
        else:
            self.turno = "O" if self.turno == "X" else "X"
            self.actualizar_panel()
            if self.modo == "cpu" and self.turno == "O":
                self.turno_maquina()
            else:
                self.bloqueado = False

    def animar_marca(self, i, ficha, listo):
        cx, cy = self.centro(i)
        r, g, pasos = 32, 12, 14

        if ficha == "X":
            l1, l2 = self.x_capas(cx, cy, r, g, COLOR_X, COL_CASILLA, "marca")

            def paso(k):
                t = 1 - (1 - k / pasos) ** 2
                p1, p2 = min(1, t * 2), max(0, t * 2 - 1)
                self.situar_linea(l1, cx - r, cy - r, cx - r + 2 * r * p1, cy - r + 2 * r * p1)
                self.situar_linea(l2, cx + r, cy - r, cx + r - 2 * r * p2, cy - r + 2 * r * p2)
                if k < pasos:
                    self.despues(16, lambda: paso(k + 1))
                else:
                    listo()
        else:
            arcos = [self.c.create_arc(cx - r, cy - r, cx + r, cy + r, start=90, extent=-1,
                                       style="arc", width=g + extra,
                                       outline=mezclar(COL_CASILLA, COLOR_O, alfa), tags="marca")
                     for extra, alfa in self.CAPAS]

            def paso(k):
                if k < pasos:
                    t = 1 - (1 - k / pasos) ** 2
                    for a in arcos:
                        self.c.itemconfig(a, extent=-360 * t)
                    self.despues(16, lambda: paso(k + 1))
                else:
                    for a in arcos:
                        self.c.delete(a)
                    self.circulo_brillo(cx, cy, r, g, COLOR_O, COL_CASILLA, "marca")
                    listo()
        paso(1)

    def animar_linea(self, linea):
        x1, y1 = self.centro(linea[0])
        x2, y2 = self.centro(linea[2])
        dx, dy = x2 - x1, y2 - y1
        largo = math.hypot(dx, dy)
        ux, uy = dx / largo, dy / largo
        x1, y1, x2, y2 = x1 - ux * 45, y1 - uy * 45, x2 + ux * 45, y2 + uy * 45

        for i in linea:
            self.c.itemconfig(self.rects[i], fill=mezclar(COL_CASILLA, DORADO, 0.06),
                              outline=mezclar(BORDE, DORADO, 0.6))

        trazo = self.linea_brillo(x1, y1, x1, y1, 7, DORADO, mezclar(COL_CASILLA, DORADO, 0.06), "linea")
        pasos = 16

        def paso(k):
            t = 1 - (1 - k / pasos) ** 2
            self.situar_linea(trazo, x1, y1, x1 + (x2 - x1) * t, y1 + (y2 - y1) * t)
            if k < pasos:
                self.despues(16, lambda: paso(k + 1))
            else:
                self.bloqueado = False
                if self.celebrar:
                    self.confeti()
        paso(1)

    def confeti(self):
        color = COLOR_X if self.resultado == "X" else COLOR_O
        paleta = [color, DORADO, TEXTO, color, DORADO]
        self.piezas = []
        for _ in range(80):
            w, h = random.uniform(5, 10), random.uniform(3, 6)
            p = {"x": random.uniform(40, 480), "y": random.uniform(-60, 20),
                 "vx": random.uniform(-1.4, 1.4), "vy": random.uniform(1.0, 3.2),
                 "w": w, "h": h}
            p["id"] = self.c.create_rectangle(p["x"], p["y"], p["x"] + w, p["y"] + h,
                                              fill=random.choice(paleta), outline="", tags="confeti")
            self.piezas.append(p)
        self.caer_confeti(0)

    def caer_confeti(self, k):
        for p in self.piezas:
            p["vy"] += 0.12
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            self.c.coords(p["id"], p["x"], p["y"], p["x"] + p["w"], p["y"] + p["h"])
        if k < 110:
            self.despues(16, lambda: self.caer_confeti(k + 1))
        else:
            self.c.delete("confeti")

    def actualizar_panel(self):
        c = self.c
        c.delete("panel")

        if self.modo == "cpu":
            nombres = {"X": "TÚ", "O": "MÁQUINA"}
        else:
            nombres = {"X": "JUGADOR 1", "O": "JUGADOR 2"}

        tarjetas = [("X", COLOR_X, nombres["X"]),
                    ("=", APAGADO, "EMPATES"),
                    ("O", COLOR_O, nombres["O"])]
        for i, (clave, color, nombre) in enumerate(tarjetas):
            x1 = 40 + i * 152
            x2 = x1 + 136
            activa = (not self.terminada) and clave == self.turno
            rect_redondeado(c, x1, 102, x2, 192, 16,
                            fill=mezclar(PANEL, color, 0.09) if activa else PANEL,
                            outline=color if activa else BORDE, width=2, tags="panel")
            c.create_rectangle((x1 + x2) / 2 - 16, 112, (x1 + x2) / 2 + 16, 115,
                               fill=color, outline="", tags="panel")
            c.create_text((x1 + x2) / 2, 134, text=nombre, font=self.fuente(9, True),
                          fill=color if clave != "=" else APAGADO, tags="panel")
            c.create_text((x1 + x2) / 2, 168, text=str(self.puntos[clave]),
                          font=self.fuente(28, True), fill=TEXTO, tags="panel")

        if self.terminada:
            if self.resultado == "=":
                msg, col = "Empate", APAGADO
            elif self.modo == "cpu":
                msg, col = (("¡Ganaste esta ronda!", COLOR_X) if self.resultado == "X"
                            else ("Esta se la lleva la máquina", COLOR_O))
            else:
                n = 1 if self.resultado == "X" else 2
                msg, col = f"¡Gana el jugador {n}!", (COLOR_X if n == 1 else COLOR_O)
            self.pastilla(260, 232, msg, col, 15, "panel", alfa=0.16)
            c.create_text(260, 266, text="Toca el tablero para otra ronda",
                          font=self.fuente(10), fill=APAGADO, tags="panel")
        else:
            if self.modo == "cpu":
                msg = "Tu turno" if self.turno == "X" else "La máquina está pensando…"
            else:
                msg = f"Turno del jugador {1 if self.turno == 'X' else 2}"
            col = COLOR_X if self.turno == "X" else COLOR_O
            self.pastilla(260, 232, msg, col, 15, "panel", alfa=0.16)

    def al_mover(self, e):
        b = self.boton_en(e.x, e.y)
        if b is not self.boton_activo:
            if self.boton_activo is not None:
                self.c.itemconfig(self.boton_activo["rect"], fill=self.boton_activo["base"])
            if b is not None:
                self.c.itemconfig(b["rect"], fill=b["hover"])
            self.boton_activo = b
        if b is not None:
            self.poner_cursor("hand2")
        elif self.pantalla == "juego":
            self.mover_en_tablero(e)
        else:
            self.poner_cursor("")

    def mover_en_tablero(self, e):
        i = self.casilla_en(e.x, e.y)
        if self.terminada:
            self.poner_cursor("hand2" if i is not None and not self.bloqueado else "")
            return
        jugable = i is not None and not self.tablero[i] and not self.bloqueado
        self.poner_cursor("hand2" if jugable else "")
        clave = i if jugable else None
        if clave == self.hover:
            return
        self.hover = clave
        self.c.delete("fantasma")
        self.reiniciar_casillas()
        if not jugable:
            return
        color = COLOR_X if self.turno == "X" else COLOR_O
        self.c.itemconfig(self.rects[i], fill=COL_CASILLA_HOVER,
                          outline=mezclar(BORDE, color, 0.7))
        cx, cy = self.centro(i)
        tenue = mezclar(COL_CASILLA_HOVER, color, 0.3)
        if self.turno == "X":
            self.c.create_line(cx - 32, cy - 32, cx + 32, cy + 32, width=12, fill=tenue,
                               capstyle="round", tags="fantasma")
            self.c.create_line(cx + 32, cy - 32, cx - 32, cy + 32, width=12, fill=tenue,
                               capstyle="round", tags="fantasma")
        else:
            self.c.create_oval(cx - 32, cy - 32, cx + 32, cy + 32, width=12,
                               outline=tenue, tags="fantasma")

    def al_hacer_clic(self, e):
        b = self.boton_en(e.x, e.y)
        if b is not None:
            b["comando"]()
            return
        if self.pantalla != "juego":
            return
        i = self.casilla_en(e.x, e.y)
        if self.terminada:
            if not self.bloqueado and i is not None:
                self.nueva_ronda()
            return
        if self.bloqueado or i is None or self.tablero[i]:
            return
        self.colocar(i)


def main():
    ventana = tk.Tk()
    Triki(ventana)
    ventana.update_idletasks()
    x = (ventana.winfo_screenwidth() - Triki.ANCHO) // 2
    y = max(0, (ventana.winfo_screenheight() - Triki.ALTO) // 2 - 20)
    ventana.geometry(f"{Triki.ANCHO}x{Triki.ALTO}+{x}+{y}")
    ventana.mainloop()


if __name__ == "__main__":
    main()
