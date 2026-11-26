"""Cine: 'Ganaba el Bayern y cayó en 3 minutos' — Lille 2-1 Bayern (Champions, J5, miércoles 25-11-2026).
Contexto: sin Kane, Olise, Neuer, Davies ni Gnabry; Laimer, de delantero improvisado.
Clave 1: primera parte del Bayern: presión arriba y 0-1 de Upamecano de cabeza (córner de Bischof, 15').
Clave 2: en la segunda parte el Bayern deja de presionar arriba; pase de Ngoy a la espalda y Ueda empata (62').
Clave 3: tres minutos después, contra tras una contra que lanza Özer: André lanza a Ethan Mbappé,
          palo y el rechace lo mete Pavlović en propia puerta (65').
Uso: python queue/2026-11-26-lille-tumba-al-bayern/render.py salida.mp4 [--sheet t1 t2 ...]
Experimento de la semana: ≤ 42 s y la jugada clave (la contra del 2-1) en movimiento desde el fotograma 0.
Nota: posiciones = recreación ilustrativa (chip 'Recreación'); solo se rotula a quien citan las fuentes.
Nuevo en el motor (v3.7): ghost (las bajas, como siluetas huecas en su sitio del once) y passline (pase que se dibuja)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "engine"))
from PIL import Image, ImageDraw, ImageFilter
from flat import W2, H2, BG, YEL, WHT, ease, lerp2, finish
import cine as C

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
FCB = (220, 16, 48); LIL = (44, 78, 178); RED = (230, 40, 50)
END = 38.0; TOTAL = END + 3.6

def track(keys, t):
    if t <= keys[0][0]: return keys[0][1]
    for (t0, a), (t1, b) in zip(keys, keys[1:]):
        if t0 <= t <= t1: return lerp2(a, b, ease((t - t0) / max(1e-6, t1 - t0)))
    return keys[-1][1]
def P(*k): return list(k)
def S(x, z): return P((0, (x, z)))

# x: -34..34 · z: 0 portería del Lille (Özer), 105 portería del Bayern (Urbig). El Lille ataca hacia z=105.
# Nombres en minúscula = jugador sin rotular.

# ---------------- H · 0–2,4: gancho · la contra del 2-1 ya en marcha
HL = {"E. Mbappé": P((0, (11, 70)), (2.4, (7, 90))), "Ueda": P((0, (-13, 64)), (2.4, (-9, 84))), "l3": P((0, (-24, 54)), (2.4, (-22, 70)))}
HB = {"Pavlović": P((0, (3, 63)), (2.4, (3.5, 85))), "Urbig": P((0, (0, 103)), (2.4, (1.5, 100))),
      "b2": P((0, (17, 55)), (2.4, (14, 74))), "b3": P((0, (-5, 52)), (2.4, (-5, 70))), "b4": P((0, (-19, 48)), (2.4, (-17, 66)))}
BH = [(0, "E. Mbappé"), (2.4, "E. Mbappé")]

# ---------------- A · 2,4–7,0: las bajas · Laimer ocupa el sitio de Kane
GH = [("Kane", (0, 47)), ("Olise", (-16, 61)), ("Gnabry", (16, 61)), ("Davies", (18, 88)), ("Neuer", (0, 103))]
AB = {"Urbig": P((0, (9, 97)), (1.4, (9, 97)), (2.6, (0.2, 102.6))), "Upamecano": S(-8, 92), "Kim": S(8, 92),
      "b_rb": S(-24, 86), "Ito": P((0, (18, 92)), (1.4, (18, 92)), (2.6, (17.6, 88.4))),
      "Kimmich": S(-6, 77), "Bischof": S(6, 77), "Pavlović": S(0, 66),
      "Karl": P((0, (-14, 70)), (1.4, (-14, 70)), (2.6, (-15.6, 61.6))), "b_w": P((0, (14, 70)), (1.4, (14, 70)), (2.6, (15.6, 61.6))),
      "Laimer": P((0, (8, 64)), (1.4, (8, 64)), (2.8, (0.4, 47.6)))}
AL = {"Özer": S(0, 3), "l_cb1": S(-8, 14), "l_cb2": S(8, 14), "l_lb": S(-24, 18), "l_rb": S(24, 18), "André": S(0, 26),
      "l_m1": S(-12, 32), "l_m2": S(12, 32), "l_w1": S(-24, 34), "Ueda": S(5, 36), "E. Mbappé": S(24, 34)}
BA = [(0, "Kimmich"), (4.6, "Kimmich")]

# ---------------- B1 · 7,0–10,4: primera parte · el Bayern aprieta la salida del Lille
B1L = {"Özer": S(0, 3), "l_cb1": P((0, (-10, 10)), (3.4, (-12, 10))), "l_cb2": P((0, (10, 10)), (3.4, (12, 11))),
       "André": P((0, (0, 20)), (3.4, (-2, 19))), "l_lb": S(-26, 18), "l_rb": S(26, 18), "l_m1": S(-12, 30), "l_m2": S(12, 30),
       "l_w1": S(-24, 44), "Ueda": S(0, 48), "E. Mbappé": S(24, 44)}
B1B = {"Laimer": P((0, (-2, 26)), (1.4, (-8, 15)), (3.4, (-10, 13))), "Karl": P((0, (-18, 30)), (3.4, (-22, 22))),
       "b_w": P((0, (18, 30)), (1.6, (13, 16)), (3.4, (13, 14))), "Pavlović": P((0, (2, 32)), (1.6, (0, 24)), (3.4, (-1, 22))),
       "Kimmich": S(-8, 42), "Bischof": S(8, 42), "Upamecano": S(-9, 58), "Kim": S(9, 58), "b_rb": S(-24, 52), "Ito": S(24, 52)}
BB1 = [(0, "Özer"), (0.5, "Özer"), (1.0, "l_cb2"), (1.7, "l_cb2"), (2.3, "Özer"), (2.6, "Özer"), (3.4, (4, 52))]

# ---------------- B2 · 10,4–13,0: el córner de Bischof y el cabezazo de Upamecano (15')
B2B = {"Bischof": S(-33.5, 0.6), "Upamecano": P((0, (8, 12)), (1.0, (4.6, 5.6)), (2.6, (4.4, 5.2))), "Kim": P((0, (-4, 11)), (2.6, (-3, 7))),
       "Laimer": P((0, (-1, 9)), (2.6, (0, 6))), "Kimmich": S(-10, 18), "Pavlović": S(6, 17)}
B2L = {"Özer": P((0, (0, 1.2)), (1.2, (1.4, 1.0)), (2.6, (2.0, 1.0))), "l_cb1": P((0, (-3, 6)), (2.6, (-2.4, 5.8))),
       "l_cb2": P((0, (6, 7)), (1.0, (5.6, 6.6)), (2.6, (5.2, 6.4))), "André": S(2, 10), "l_m1": S(-8, 12), "l_m2": S(10, 13), "Ueda": S(-16, 22)}
BB2 = [(0, "Bischof"), (0.25, "Bischof"), (1.0, "Upamecano"), (1.05, "Upamecano"), (1.45, (2.6, -0.4)), (2.6, (2.6, -0.6))]
GOAL1 = 10.4 + 1.45

# ---------------- C · 13,0–21,0: segunda parte · la presión llega tarde, Ngoy a la espalda y Ueda empata (62')
LINEZ = 56.0
C_L = {"Özer": S(0, 3), "l_cb1": P((0, (-10, 12)), (8, (-10, 14))), "Ngoy": P((0, (-14, 16)), (2.2, (-20, 26)), (3.8, (-21, 32)), (8, (-20, 36))),
       "André": P((0, (0, 22)), (8, (0, 34))), "l_m1": P((0, (-10, 34)), (8, (-10, 44))), "l_m2": P((0, (12, 32)), (8, (12, 46))),
       "l_rb": P((0, (26, 22)), (8, (26, 40))), "E. Mbappé": P((0, (24, 46)), (8, (22, 64))),
       "Ueda": P((0, (-2, 50)), (3.6, (-3, 54)), (4.2, (-4, 56)), (5.6, (-5, 74)), (6.3, (-4.6, 80)), (8, (-4, 82)))}
C_B = {"Laimer": P((0, (-2, 34)), (2.4, (-8, 24)), (8, (-8, 26))), "Karl": P((0, (-14, 40)), (8, (-16, 34))),
       "b_w": P((0, (16, 40)), (8, (16, 36))), "Pavlović": P((0, (2, 42)), (8, (2, 46))),
       "Kimmich": P((0, (-6, 48)), (3.8, (-10, 44)), (8, (-8, 52))), "Bischof": P((0, (8, 48)), (8, (6, 54))),
       "Upamecano": P((0, (-7, LINEZ)), (4.0, (-7, LINEZ + 1)), (6.3, (-9, 74)), (8, (-9, 76))),
       "Kim": P((0, (7, LINEZ)), (4.0, (7, LINEZ + 1)), (6.3, (2, 74)), (8, (1, 77))),
       "b_rb": P((0, (-22, LINEZ - 2)), (8, (-20, 62))), "Ito": P((0, (22, LINEZ - 2)), (8, (18, 64))),
       "Urbig": P((0, (0, 102)), (6.0, (0, 100)), (6.7, (1.6, 101)), (8, (1.8, 101)))}
BC = [(0, "Özer"), (0.6, "Özer"), (1.2, "l_cb1"), (1.8, "l_cb1"), (2.4, "Ngoy"), (3.8, "Ngoy"), (4.6, (-4.4, 63)),
      (5.6, "Ueda"), (6.3, "Ueda"), (6.75, (-3.2, 105.3)), (8, (-3.4, 105.6))]
THRU0, SHOT2, GOAL2 = 13.0 + 3.8, 13.0 + 6.3, 13.0 + 6.75

# ---------------- D · 21,0–28,5: falta del Bayern arriba → contra: André, E. Mbappé al palo y Pavlović en propia (65')
D_L = {"Özer": P((0, (0, 3)), (0.6, (0, 4)), (1.4, (1, 6)), (7.5, (1, 6))), "l_cb1": S(-5, 9), "l_cb2": S(5, 10),
       "André": P((0, (4, 18)), (1.4, (4, 25)), (2.2, (4, 27)), (7.5, (4, 48))),
       "E. Mbappé": P((0, (10, 22)), (1.4, (12, 32)), (2.4, (13, 44)), (4.6, (8, 91)), (5.4, (6, 95)), (7.5, (5, 97))),
       "Ueda": P((0, (-12, 26)), (4.6, (-8, 78)), (7.5, (-6, 88))), "l_m1": S(-12, 14), "l_m2": S(14, 14)}
D_B = {"Laimer": P((0, (-2, 10)), (7.5, (-2, 34))), "Upamecano": P((0, (3, 8)), (7.5, (2, 46))), "Kim": P((0, (-6, 12)), (7.5, (-6, 50))),
       "Kimmich": P((0, (-14, 22)), (7.5, (-10, 56))), "Bischof": P((0, (14, 26)), (7.5, (12, 58))), "Karl": S(-22, 18),
       "Pavlović": P((0, (-2, 42)), (2.0, (-2, 52)), (4.8, (-1.5, 92)), (5.6, (-1.2, 100.4)), (7.5, (-1.2, 101))),
       "Urbig": P((0, (0, 102)), (4.0, (1, 99)), (4.9, (3.2, 98)), (7.5, (3.4, 98.4)))}
BD = [(0, (2, 9)), (0.6, "Özer"), (1.4, "Özer"), (2.2, "André"), (2.3, "André"), (3.1, "E. Mbappé"), (4.85, "E. Mbappé"),
      (5.2, (3.8, 104.6)), (5.6, "Pavlović"), (5.7, "Pavlović"), (6.0, (-1.4, 105.4)), (7.5, (-1.5, 105.7))]
D0 = 21.0; POST, OG, GOAL3 = D0 + 5.2, D0 + 5.7, D0 + 6.0

# ---------------- E · 28,5–: plano general para la cita, el dato y la consecuencia
EL = {k: S(*v) for k, v in {"Özer": (0, 4), "l_cb1": (-9, 22), "l_cb2": (9, 22), "l_lb": (-24, 26), "l_rb": (24, 26), "André": (0, 34),
      "l_m1": (-12, 42), "l_m2": (12, 42), "l_w1": (-22, 54), "Ueda": (0, 58), "E. Mbappé": (22, 54)}.items()}
EB = {k: S(*v) for k, v in {"Urbig": (0, 101), "Upamecano": (-8, 82), "Kim": (8, 82), "b_rb": (-22, 76), "Ito": (22, 76),
      "Kimmich": (-6, 68), "Bischof": (6, 68), "Pavlović": (0, 60), "Karl": (-18, 58), "b_w": (18, 58), "Laimer": (0, 48)}.items()}

# (t0, t1, Lille, Bayern, balón)
SEG = [(0.0, 2.4, HL, HB, BH), (2.4, 7.0, AL, AB, BA), (7.0, 10.4, B1L, B1B, BB1), (10.4, 13.0, B2L, B2B, BB2),
       (13.0, 21.0, C_L, C_B, BC), (21.0, 28.5, D_L, D_B, BD), (28.5, 99.0, EL, EB, [(0, (0, 52.5))])]

CAMK = [
    (0.0,  dict(el=26, d=66,  tx=6,  tz=82, az=56,  cy=1180)),   # gancho: a ras, detrás de E. Mbappé
    (2.3,  dict(el=28, d=62,  tx=5,  tz=90, az=44,  cy=1190)),
    (2.4,  dict(el=58, d=118, tx=0,  tz=76, az=180, cy=900)),    # las bajas: desde detrás del Bayern
    (4.6,  dict(el=50, d=104, tx=0,  tz=72, az=196, cy=900)),
    (6.9,  dict(el=46, d=96,  tx=0,  tz=66, az=206, cy=900)),
    (7.0,  dict(el=40, d=96,  tx=0,  tz=20, az=-150, cy=900)),   # 1.ª parte: la presión, desde detrás de Laimer
    (10.3, dict(el=34, d=84,  tx=-2, tz=18, az=-168, cy=900)),
    (10.4, dict(el=26, d=50,  tx=0,  tz=8,  az=-62, cy=1040)),   # el córner: lateral, a pie de área
    (12.9, dict(el=30, d=54,  tx=1,  tz=6,  az=-80, cy=1030)),
    (13.0, dict(el=60, d=150, tx=0,  tz=34, az=0,   cy=880)),    # 2.ª parte: general, la presión llega tarde
    (15.8, dict(el=52, d=140, tx=-4, tz=42, az=-12, cy=880)),
    (15.9, dict(el=34, d=110, tx=-8, tz=52, az=-70, cy=900)),    # de lado: la espalda de la defensa
    (18.4, dict(el=32, d=80,  tx=-5, tz=72, az=-44, cy=920)),
    (18.5, dict(el=24, d=52,  tx=-4, tz=92, az=-12, cy=1040)),   # remate de Ueda, a ras de portería
    (20.9, dict(el=28, d=56,  tx=-3, tz=96, az=8,   cy=1030)),
    (21.0, dict(el=56, d=130, tx=0,  tz=26, az=0,   cy=860)),    # la falta y la contra: general
    (23.0, dict(el=44, d=120, tx=6,  tz=52, az=24,  cy=880)),
    (23.1, dict(el=36, d=84,  tx=9,  tz=46, az=-20, cy=860)),    # sigue a E. Mbappé
    (25.4, dict(el=28, d=56,  tx=7,  tz=88, az=-14, cy=1020)),
    (25.5, dict(el=22, d=40,  tx=1,  tz=101, az=-150, cy=1060)), # contraplano: el palo y el rechace
    (28.4, dict(el=26, d=44,  tx=0,  tz=101, az=-166, cy=1050)),
    (28.5, dict(el=56, d=180, tx=0,  tz=56, az=-10, cy=900)),
    (END,  dict(el=50, d=160, tx=0,  tz=58, az=12,  cy=900)),
]
HEAD = [
    (2.4,  "LILLE 2-1 BAYERN · CHAMPIONS", "Cinco bajas", "de golpe"),
    (7.0,  "CLAVE 1 · LA PRIMERA PARTE", "El Bayern", "aprieta arriba"),
    (13.0, "CLAVE 2 · LA SEGUNDA PARTE", "La presión", "se apaga"),
    (21.0, "CLAVE 3 · TRES MINUTOS DESPUÉS", "Özer sale", "a la contra"),
    (28.5, "LA CONSECUENCIA", "Primera derrota", "del Bayern"),
]
SUBS = [
    (2.6, 4.7, "Sin *Kane*, *Olise*, *Neuer*, *Davies* ni *Gnabry*"),
    (4.8, 6.9, "*Laimer*, de *delantero improvisado*"),
    (7.2, 10.2, "1.ª parte: el Bayern *presiona arriba*"),
    (10.6, 12.9, "*Upamecano*, de cabeza en un córner"),
    (13.2, 15.8, "2.ª parte: la presión *ya no llega*"),
    (16.0, 18.4, "*Ngoy* la mete *a la espalda*"),
    (18.6, 20.9, "y *Ueda* empata"),
    (21.2, 23.0, "*Özer* la atrapa… y *contra*"),
    (23.1, 25.4, "*André* lanza a *E. Mbappé*"),
    (25.6, 28.3, "Al palo… y el rechace lo mete *Pavlović*"),
]
SHOW = [((7.2, 10.2), {"Laimer", "André"}), ((10.6, 12.9), {"Upamecano", "Bischof"}),
        ((16.0, 18.4), {"Ngoy"}), ((18.4, 20.9), {"Ueda"}), ((21.4, 23.0), {"Özer"}), ((23.1, 25.4), {"André", "E. Mbappé"}),
        ((25.5, 28.3), {"Pavlović"})]
FOCUS = [(4.8, 6.6, {"Laimer"}), (16.2, 17.2, {"Ngoy"}), (17.2, 19.4, {"Ueda"}), (23.3, 25.0, {"E. Mbappé"}), (26.0, 27.2, {"Pavlović"})]
TAGS = [(5.3, 6.8, "Laimer", "LAIMER · DE 9", YEL), (POST, POST + .75, "E. Mbappé", "¡AL PALO!", RED)]
SCORE = [(7.2, 10.2, 0, 0, "1.ª P"), (10.6, GOAL1, 0, 0, "15'"), (GOAL1, 13.0, 0, 1, "15'"),
         (13.2, GOAL2, 0, 1, "2.ª P"), (GOAL2, 21.0, 1, 1, "62'"), (21.2, GOAL3, 1, 1, "65'"), (GOAL3, 28.5, 2, 1, "65'")]
GOALS = [(GOAL1, "0-1", "Upamecano · 15'"), (GOAL2, "1-1", "Ueda · 62'"), (GOAL3, "2-1", "Pavlović, en propia · 65'")]
FACTS = [("1.ª", "derrota del Bayern esta temporada"), ("15.º", "con 8 puntos, a 2 del top 8"), ("1.ª", "victoria del Lille en esta Champions")]
VIG = None

def seg_at(t):
    for s in SEG:
        if s[0] <= t < s[1]: return s
    return SEG[-1]
def posx(s, name, lt):
    d = s[2] if name in s[2] else s[3]; return track(d[name], lt)
def ball_at(s, lt):
    B = s[4]
    def at(h, tt): return posx(s, h, tt) if isinstance(h, str) else h
    if lt <= B[0][0]: return at(B[0][1], lt), .25
    for (t0, a), (t1, h) in zip(B, B[1:]):
        if t0 <= lt < t1:
            if isinstance(a, str) and a == h: return posx(s, a, lt), .25
            pa, pb = at(a, t0), at(h, t1); u = (lt - t0) / max(1e-6, t1 - t0)
            far = (abs(pa[0] - pb[0]) + abs(pa[1] - pb[1])) > 18
            y = .25 + (5.5 if far else 0) * u * (1 - u)
            return lerp2(pa, pb, ease(u) if not far else u), y
    h = B[-1][1]; return at(h, lt), .25
def cspeed(t, dt=1 / 30):
    a = C.camkeys(CAMK, t); b = C.camkeys(CAMK, max(0, t - dt))
    k = -a.pos[1] / a.f[1]; g = a.pos + a.f * k
    pa = a.P(g[0], g[2]); pb = b.P(g[0], g[2])
    return math.hypot(pa[0] - pb[0], pa[1] - pb[1]) / 2 / 40

def compose(t): return scene(t, t)

def scene(t, r):
    global VIG
    if VIG is None: VIG = C.vignette()
    b = Image.new("RGBA", (W2, H2), (*BG, 255)); cam = C.camkeys(CAMK, min(t, END))
    C.pitch(b, cam)
    s = seg_at(t); t0s, t1s = s[0], s[1]; lt = t - t0s
    fade = (ease(lt / .2) if t0s > 0 else 1.0) * (1 - ease((t - t1s + .2) / .2) if t1s < 99 else 1.0)
    # --- dibujo táctico por debajo de los jugadores
    if s is SEG[1]:                                                           # NUEVO: las bajas en su sitio del once
        for i, (nm, (gx, gz)) in enumerate(GH):
            ga = ease((t - 2.6 - i * .22) / .3) * (1 - ease((t - (4.9 if nm == 'Kane' else 6.3)) / .4)) * fade
            C.ghost(b, cam, gx, gz, FCB, nm, ga, t)
        C.arrow(b, cam, (8, 63), (1, 49), YEL, ease((t - 4.9) / .7), 1 - ease((t - 6.6) / .3))
    if s is SEG[2]:                                                           # conos de presión del Bayern
        pa_ = ease((t - 7.5) / .4) * (1 - ease((t - 10.0) / .3)) * fade
        for pr, tg in (("Laimer", "l_cb1"), ("b_w", "l_cb2"), ("Pavlović", "André")):
            C.pressure(b, cam, posx(s, pr, lt), posx(s, tg, lt), FCB, pa_)
    if s is SEG[4]:
        if t < 15.8:                                                          # presión que llega tarde: conos discontinuos
            for pr, tg in (("Laimer", "l_cb1"), ("Pavlović", "André")):
                C.link(b, cam, posx(s, pr, lt), posx(s, tg, lt), FCB, 1.0, ease((t - 13.4) / .4) * (1 - ease((t - 15.5) / .3)) * .8)
        if 15.9 < t < 18.6:                                                   # la espalda de la defensa
            za = ease((t - 16.0) / .4) * (1 - ease((t - 18.3) / .3))
            C.lineband(b, cam, LINEZ + .5, YEL, za, "LA ESPALDA")
            C.zone(b, cam, [(-30, LINEZ + 2), (20, LINEZ + 2), (20, 88), (-30, 88)], YEL, za * .9, 26)
        C.passline(b, cam, (-21, 32), (-4.4, 63), t, THRU0, .8, YEL, fade, 1.4)   # NUEVO: el pase de Ngoy se dibuja
    if s is SEG[5]:
        C.passline(b, cam, (1, 6), (4, 27), t, D0 + 1.4, .8, YEL, fade, .6)
        C.passline(b, cam, (4, 27), (13, 44), t, D0 + 2.3, .8, YEL, fade, .9)
        C.arrow(b, cam, (13, 46), (8, 88), YEL, ease((t - D0 + -3.1) / 1.4), 1 - ease((t - D0 - 4.9) / .3))
    people = [(n, LIL, True) for n in s[2]] + [(n, FCB, True) for n in s[3]]
    def depth(p): x, z = posx(s, p[0], lt); return -(cam.P(x, z)[2])
    for n, col, dark in people:
        pts = [posx(s, n, max(0.0, lt - .07 * k)) for k in range(9, -1, -1)]
        if abs(pts[0][0] - pts[-1][0]) + abs(pts[0][1] - pts[-1][1]) > 1.6:
            C.trail(b, cam, pts, col, a=fade)
    for f0, f1, names in FOCUS:
        if f0 <= t < f1:
            for n in names:
                if n in s[2] or n in s[3]:
                    x, z = posx(s, n, lt); C.glow_ring(b, cam, x, z, 2.6 + .3 * math.sin(t * 6), YEL, fade)
    for n, col, dark in sorted(people, key=depth):
        x, z = posx(s, n, lt); na = 0.0
        for (s0, s1), names in SHOW:
            if s0 <= t < s1 and n in names: na = ease((t - s0) / .3) * (1 - ease((t - s1 + .3) / .3))
        nm = n if n[0].isupper() else None
        C.player(b, cam, x, z, col, None, nm, fade, 0.0, dark, na * fade)
    for t0, t1, n, txt, col in TAGS:
        if t0 <= t < t1 and (n in s[2] or n in s[3]):
            x, z = posx(s, n, lt)
            C.tag3d(b, cam, x, z, txt, col, ease((t - t0) / .25) * (1 - ease((t - t1 + .25) / .25)), fg=((14, 22, 34) if col == YEL else WHT))
    bts = [ball_at(s, max(0.0, lt - .04 * k)) for k in range(8, -1, -1)]
    if abs(bts[0][0][0] - bts[-1][0][0]) + abs(bts[0][0][1] - bts[-1][0][1]) > 2:
        C.ball_trail(b, cam, [(p[0], p[1], y) for p, y in bts], fade)
    (bx, bz), by = ball_at(s, lt)
    if fade > .5 and t < 28.5: C.ballp(b, cam, bx, bz, by)
    C.spark(b, cam, 3.8, 104.6, t, POST, col=WHT, y=1.2)                      # el palo
    C.spark(b, cam, -1.2, 100.6, t, OG, col=RED)                              # el despeje de Pavlović
    b = C.motion_blur(b, cspeed(min(t, END)) if t < END else 0)
    b.alpha_composite(VIG)
    if t < 2.4:
        sh_ = Image.new("RGBA", b.size, (0, 0, 0, 0)); a_ = int(130 * (1 - ease((t - 2.0) / .4)))
        ImageDraw.Draw(sh_).rectangle((0, 640 * 2, W2, 1080 * 2), fill=(*BG, a_)); b.alpha_composite(sh_.filter(ImageFilter.GaussianBlur(60)))
    C.bigtitle(b, t, 2.4, "Ganaba el Bayern", "y cayó en 3 minutos")
    if 0.1 < t < 28.4: C.rec_tag(b, a=ease((t - 0.1) / .3) * (1 - ease((t - 28.1) / .3)))
    if 2.2 < t < 37.6: C.headline(b, t, HEAD)
    if t < 28.4: C.subs(b, t, SUBS)
    C.lower_third(b, t, 7.6, 10.2, "«Fue una primera parte muy buena»", "KOMPANY, SOBRE LA 1.ª PARTE")
    C.lower_third(b, t, 13.4, 15.8, "«Dejamos de recuperar arriba»", "KIMMICH, SOBRE LA 2.ª PARTE")
    for t0, t1, h, a, mn in SCORE: C.scoreboard(b, t, t0, t1, "LIL", "BAY", h, a, mn)
    for tg, txt, sub in GOALS: C.flash(b, t, tg, txt, sub)
    b = b.convert("RGB").convert("RGBA")
    for tw in [g[0] for g in GOALS] + [POST]: C.white_flash(b, t, tw)
    C.quote(b, t, 28.5, 31.6, "El segundo gol no puede pasar", "KOMPANY")
    C.statbars(b, t, 31.6, 34.6, "GOLES ESPERADOS (xG)", "LILLE", "BAYERN", LIL, FCB, [("xG del partido", 2.11, 1.19, "2,1", "1,2")], y=700)
    C.factlist(b, t, 34.6, END, "LILLE 2-1 BAYERN", FACTS, y=520)
    if t >= END: C.endcard(b, t - END, "¿Le faltó Kane", "o le faltó presión?", "Te leo en comentarios")
    for tw in [g[0] for g in GOALS] + [POST]: b = C.shake(b, t, tw)
    return finish(b.convert("RGB"))

if __name__ == "__main__":
    out = sys.argv[1]
    if "--sheet" in sys.argv:
        ts = [float(x) for x in sys.argv[sys.argv.index("--sheet") + 1:]]
        ims = [scene(t, t).resize((540, 960)) for t in ts]
        sh = Image.new("RGB", (540 * len(ims), 960)); [sh.paste(im, (540 * i, 0)) for i, im in enumerate(ims)]; sh.save(out, quality=85)
    else:
        sfx = out + ".sfx.wav"
        C.sfx_track(sfx, TOTAL, whooshes=[2.4, 7.0, 10.4, 13.0, 15.9, 18.5, 21.0, 23.1, 25.5, 28.5, 31.6, 34.6, 37.9],
                    hits=[GOAL1, GOAL2, POST, GOAL3, 2.8, 3.0, 3.25, 3.5, 3.7])
        C.encode(compose, TOTAL, out, os.path.join(ROOT, "music", "glitter_and_gold-patrick_patrikios.mp3"), sfx)
