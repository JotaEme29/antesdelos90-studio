"""Cine: 'Con 10 desde el 23' y ganó en Balaídos' — Celta 1-2 Bournemouth (Europa League, J5, jueves 26-11-2026).
Contexto: Aspas adelanta al Celta (19'); roja a Diakité por una entrada a Driouech (23'). 67 minutos de 11 contra 10.
Clave 1: el Celta con uno más tiene el balón (≈64 %) y tira 20 veces, pero ataca precipitado y va al contacto
          (Giráldez: «Hemos atacado muy precipitados»).
Clave 2: al descanso Rose mete a Adams por Kluivert; en la primera acción de la 2.ª parte, centro de Adli y cabezazo
          de Álvaro Rodríguez (47'). Giráldez: «Estamos cuatro en el área contra tres de ellos».
Clave 3: los que salen del banquillo: Truffert roba y corre, Tavernier la da de cara y Rayan marca (78').
Antes de los 90: tarea de superioridad con cerebro (propuesta de entrenador).
Uso: python queue/2026-11-27-bournemouth-diez-balaidos/render.py salida.mp4 [--sheet t1 t2 ...]
Experimento de la semana: ≤ 42 s y la jugada clave (la contra del 1-2) en movimiento desde el fotograma 0.
Nota: posiciones = recreación ilustrativa (chip 'Recreación'); solo se rotula a quien citan las fuentes.
Nuevo en el motor (v3.8): outnumber (contador 11 v 10 con el muñeco que se apaga) y drillboard (pizarra de la tarea)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "engine"))
from PIL import Image, ImageDraw, ImageFilter
from flat import W2, H2, BG, YEL, WHT, ease, lerp2, finish
import cine as C

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
CEL = (138, 194, 236); BOU = (214, 28, 44); RED = (230, 40, 50)
END = 38.6; TOTAL = END + 3.4

def track(keys, t):
    if t <= keys[0][0]: return keys[0][1]
    for (t0, a), (t1, b) in zip(keys, keys[1:]):
        if t0 <= t <= t1: return lerp2(a, b, ease((t - t0) / max(1e-6, t1 - t0)))
    return keys[-1][1]
def P(*k): return list(k)
def S(x, z): return P((0, (x, z)))

# x: -34..34 · z: 0 portería del Celta (Radu), 105 portería del Bournemouth (Di Gregorio). El Celta ataca hacia z=105.
# Izquierda del Celta = x<0; izquierda del Bournemouth (que ataca hacia z=0) = x>0.

# ---------------- H · 0–2,4: gancho · la contra del 1-2 ya en marcha
HB = {"Truffert": P((0, (19, 44)), (2.4, (14, 27))), "Tavernier": P((0, (9, 34)), (2.4, (7, 19))), "Rayan": P((0, (-6, 36)), (2.4, (-3, 17)))}
HC = {"c1": P((0, (12, 30)), (2.4, (9, 18))), "c2": P((0, (-2, 28)), (2.4, (-1, 15))), "c3": P((0, (22, 52)), (2.4, (19, 36))),
      "c4": P((0, (-14, 48)), (2.4, (-10, 32))), "Radu": P((0, (0, 3)), (2.4, (0, 4)))}
BH = [(0, "Truffert"), (2.4, "Truffert")]

# ---------------- A · 2,4–6,6: la entrada de Diakité a Driouech y el Bournemouth se queda con 10
AC = {"Radu": S(0, 4), "c_cb1": S(-9, 44), "c_cb2": S(9, 44), "c_lb": P((0, (-26, 58)), (4.2, (-26, 62))), "c_rb": S(26, 58),
      "c_m1": S(-6, 58), "c_m2": S(8, 56), "Aspas": S(2, 76), "c_w2": S(22, 74), "c_m3": S(-8, 70),
      "Driouech": P((0, (-20, 70)), (.7, (-22, 77)), (1.0, (-21.6, 78)), (1.6, (-20.4, 78.6)), (4.2, (-20, 78.6)))}
AB = {"Di Gregorio": S(0, 101), "b_cb1": S(-8, 89), "b_cb2": S(8, 89), "b_lb": P((0, (23, 87)), (2.0, (23, 87)), (3.2, (22, 88))),
      "Diakité": P((0, (-15, 82)), (.7, (-20.6, 78.2)), (4.2, (-20.6, 78.2))),
      "b_m1": P((0, (-6, 76)), (2.0, (-6, 76)), (3.2, (-7, 80))), "b_m2": P((0, (6, 76)), (2.0, (6, 76)), (3.2, (5, 80))),
      "b_w1": P((0, (-18, 74)), (2.0, (-18, 74)), (3.2, (-17, 84))), "b_w2": P((0, (18, 74)), (2.0, (18, 74)), (3.2, (17, 79))),
      "b_f1": P((0, (-3, 60)), (2.0, (-3, 60)), (3.2, (-1, 66))), "Á. Rodríguez": P((0, (5, 62)), (2.0, (5, 62)), (3.2, (3, 64)))}
BA = [(0, (-21, 72)), (.7, "Driouech"), (1.0, (-21, 80)), (4.2, (-20.5, 80.2))]
DIAK_GHOST = (-20, 87)

# ---------------- B · 6,6–13,8: el Celta con uno más: mucho balón, pero precipitado y al contacto
BC = {"Radu": S(0, 8), "c_cb1": P((0, (-10, 44)), (7.2, (-10, 50))), "c_cb2": P((0, (10, 44)), (7.2, (10, 50))),
      "c_lb": P((0, (-26, 58)), (7.2, (-26, 66))), "c_rb": P((0, (26, 58)), (7.2, (26, 66))),
      "c_m1": P((0, (-5, 56)), (2.0, (-4, 62)), (7.2, (-4, 66))), "c_m2": P((0, (8, 56)), (7.2, (8, 64))),
      "Aspas": P((0, (2, 74)), (2.6, (0, 76)), (3.4, (-3, 79)), (7.2, (-3, 80))), "Driouech": P((0, (-22, 72)), (3.0, (-20, 76)), (7.2, (-19, 78))),
      "c_w2": P((0, (22, 74)), (7.2, (20, 80))), "c_m3": P((0, (-8, 66)), (7.2, (-9, 72)))}
BB = {"Di Gregorio": S(0, 101), "b_cb1": S(-7, 88), "b_cb2": S(7, 88), "b_rb": S(-19, 87), "b_lb": S(20, 87),
      "b_m1": P((0, (-6, 80)), (3.2, (-3.6, 79)), (7.2, (-3, 78))), "b_m2": P((0, (6, 80)), (3.2, (1, 80.4)), (7.2, (0, 78))),
      "b_w1": P((0, (-16, 82)), (3.0, (-11, 80)), (7.2, (-10, 80))), "b_w2": P((0, (16, 80)), (7.2, (14, 80))),
      "Á. Rodríguez": P((0, (2, 66)), (2.6, (-1, 70)), (7.2, (-1, 70))), "b_f1": P((0, (-6, 70)), (7.2, (-6, 72)))}
BBL = [(0, "c_cb1"), (.6, "c_cb1"), (1.2, "c_m1"), (1.7, "c_m1"), (2.4, "Driouech"), (2.8, "Driouech"), (3.3, "Aspas"), (3.5, (-3, 79.6)),
       (3.9, "b_m1"), (4.4, "b_m1"), (5.2, "Á. Rodríguez"), (7.2, "Á. Rodríguez")]
B0 = 6.6; LOSS = B0 + 3.6

# ---------------- C · 13,8–20,6: descanso (Adams por Kluivert) y el 1-1: centro de Adli, cabeza de Álvaro Rodríguez (47')
CB_ = {"Adli": P((0, (24, 34)), (1.6, (25, 24)), (6.8, (26, 21))), "Á. Rodríguez": P((0, (2, 24)), (1.6, (0, 13)), (2.4, (.6, 7)), (6.8, (1, 6))),
       "b_a2": P((0, (-6, 24)), (2.4, (-5, 10)), (6.8, (-5, 9))), "b_a3": P((0, (8, 22)), (2.4, (7, 11)), (6.8, (7, 10))),
       "Adams": S(4, 38), "b_m": S(-10, 40)}
CC = {"Radu": P((0, (0, 3)), (2.2, (1.2, 3)), (2.8, (2.8, 1.8)), (6.8, (3, 1.6))), "c_d1": P((0, (-2, 14)), (2.4, (-1.4, 8.4)), (6.8, (-1.4, 8))),
      "c_d2": P((0, (5, 14)), (2.4, (3.6, 9.8)), (6.8, (3.4, 9.6))), "c_d3": P((0, (-9, 13)), (2.4, (-6, 8.6)), (6.8, (-6, 8.6))),
      "c_d4": P((0, (12, 14)), (2.4, (9, 12)), (6.8, (9, 12))), "c_rb": P((0, (20, 28)), (1.6, (22, 25)), (6.8, (22, 24))),
      "c_m1": S(-4, 30), "c_m2": S(10, 34)}
BCL = [(0, (10, 46)), (.6, "Adli"), (1.6, "Adli"), (2.3, "Á. Rodríguez"), (2.4, "Á. Rodríguez"), (2.75, (-1.6, -.3)), (6.8, (-1.8, -.6))]
C0 = 13.8; XC0 = C0 + 1.6; GOAL1 = C0 + 2.75

# ---------------- D · 20,6–28,2: el banquillo decide: Truffert roba y corre, Tavernier de cara, Rayan (78')
DC = {"Radu": P((0, (0, 4)), (5.4, (0, 4)), (6.2, (-1.4, 3)), (7.6, (-1.6, 3))),
      "c_lw": P((0, (24, 70)), (.8, (21, 72)), (7.6, (18, 52))), "c_m1": P((0, (6, 64)), (7.6, (6, 40))), "c_m2": P((0, (-10, 66)), (7.6, (-8, 44))),
      "c_cb1": P((0, (-6, 50)), (2.4, (-5, 38)), (4.6, (-5, 22)), (5.8, (-8.5, 16)), (7.6, (-9.5, 15.5))),
      "c_cb2": P((0, (8, 50)), (2.4, (9, 36)), (4.6, (6, 25)), (5.6, (3, 21)), (7.6, (2, 20))),
      "Aspas": P((0, (-2, 80)), (7.6, (-2, 60))), "c_rb": P((0, (-22, 66)), (7.6, (-14, 46)))}
DB = {"Truffert": P((0, (22, 76)), (.8, (21.4, 72.6)), (2.4, (18, 52)), (3.6, (14, 34)), (7.6, (13, 28))),
      "Tavernier": P((0, (12, 64)), (2.4, (10, 42)), (3.6, (8, 24)), (4.4, (7.4, 18)), (7.6, (9, 15))),
      "Rayan": P((0, (-8, 62)), (2.4, (-7, 40)), (4.4, (-4, 20)), (5.4, (-3, 12)), (7.6, (-2.6, 10))),
      "b_x": P((0, (4, 80)), (7.6, (2, 62)))}
BDL = [(0, (24, 72)), (.8, "Truffert"), (3.6, "Truffert"), (4.4, "Tavernier"), (4.6, "Tavernier"), (5.4, "Rayan"), (5.5, "Rayan"),
       (5.95, (-1.4, -.3)), (7.6, (-1.6, -.6))]
D0 = 20.6; STEAL, GOAL2 = D0 + .8, D0 + 5.95

# ---------------- E · 28,2–: plano general para los datos, la tarea y la pregunta
EC = {k: S(*v) for k, v in {"Radu": (0, 6), "c_cb1": (-9, 40), "c_cb2": (9, 40), "c_lb": (-24, 52), "c_rb": (24, 52), "c_m1": (-6, 54),
      "c_m2": (8, 54), "Aspas": (0, 72), "Driouech": (-20, 70), "c_w2": (20, 70), "c_m3": (-8, 64)}.items()}
EB = {k: S(*v) for k, v in {"Di Gregorio": (0, 101), "b_cb1": (-7, 88), "b_cb2": (7, 88), "b_rb": (-19, 87), "b_lb": (19, 87),
      "b_m1": (-5, 79), "b_m2": (5, 79), "b_w1": (-15, 80), "b_w2": (15, 80), "Á. Rodríguez": (0, 68)}.items()}

# (t0, t1, Celta, Bournemouth, balón)
SEG = [(0.0, 2.4, HC, HB, BH), (2.4, 6.6, AC, AB, BA), (6.6, 13.8, BC, BB, BBL), (13.8, 20.6, CC, CB_, BCL),
       (20.6, 28.2, DC, DB, BDL), (28.2, 99.0, EC, EB, [(0, (0, 60))])]

CAMK = [
    (0.0,  dict(el=26, d=64,  tx=6,  tz=26, az=150, cy=1180)),   # gancho: a ras, detrás de Truffert
    (2.3,  dict(el=28, d=58,  tx=3,  tz=18, az=164, cy=1190)),
    (2.4,  dict(el=30, d=60,  tx=-20, tz=79, az=-80, cy=1030)),  # la entrada: lateral, a pie de banda
    (4.1,  dict(el=36, d=72,  tx=-16, tz=81, az=-100, cy=980)),
    (4.2,  dict(el=62, d=150, tx=0,  tz=74, az=180, cy=880)),    # 11 v 10: general desde detrás del Bournemouth
    (6.5,  dict(el=56, d=140, tx=-2, tz=76, az=196, cy=880)),
    (6.6,  dict(el=48, d=120, tx=-4, tz=66, az=-10, cy=900)),    # clave 1: desde detrás del Celta
    (9.9,  dict(el=40, d=92,  tx=-4, tz=74, az=-28, cy=920)),
    (10.0, dict(el=30, d=58,  tx=-3, tz=79, az=-120, cy=1000)),  # el choque: zoom a la zona, contraplano
    (13.7, dict(el=34, d=66,  tx=-2, tz=76, az=-140, cy=980)),
    (13.8, dict(el=58, d=130, tx=4,  tz=26, az=176, cy=880)),    # 2.ª parte: general
    (15.3, dict(el=46, d=96,  tx=12, tz=22, az=150, cy=900)),
    (15.4, dict(el=32, d=68,  tx=15, tz=15, az=-25, cy=1000)),   # el centro: detrás de la portería del Celta
    (17.0, dict(el=26, d=52,  tx=6,  tz=12, az=-15, cy=1030)),
    (17.1, dict(el=34, d=46,  tx=0,  tz=6,  az=-30, cy=1000)),   # contraplano del cabezazo
    (20.5, dict(el=40, d=56,  tx=0,  tz=9,  az=-12, cy=980)),
    (20.6, dict(el=34, d=70,  tx=20, tz=70, az=120, cy=980)),    # el robo de Truffert: lateral
    (22.4, dict(el=42, d=110, tx=14, tz=56, az=160, cy=900)),
    (22.5, dict(el=40, d=100, tx=10, tz=44, az=190, cy=900)),    # la carrera: le sigue la cámara
    (24.9, dict(el=30, d=64,  tx=6,  tz=22, az=200, cy=960)),
    (25.0, dict(el=20, d=40,  tx=-1, tz=8,  az=20,  cy=1070)),   # el remate: a ras de portería, contraplano
    (28.1, dict(el=24, d=44,  tx=-1, tz=7,  az=4,   cy=1060)),
    (28.2, dict(el=56, d=180, tx=0,  tz=56, az=-10, cy=900)),
    (END,  dict(el=50, d=160, tx=0,  tz=58, az=12,  cy=900)),
]
HEAD = [
    (2.4,  "CELTA 1-2 BOURNEMOUTH · EUROPA LEAGUE", "Roja en", "el minuto 23"),
    (6.6,  "CLAVE 1 · EL CELTA, CON UNO MÁS", "Mucho balón,", "poca pausa"),
    (13.8, "CLAVE 2 · EL ÁREA", "Un centro", "y 1-1"),
    (20.6, "CLAVE 3 · EL BANQUILLO", "Tres que entran", "y deciden"),
    (28.2, "LA CONSECUENCIA", "5 de 5", "en Europa"),
]
SUBS = [
    (2.6, 4.1, "*Diakité* entra a *Driouech*: roja"),
    (6.8, 9.8, "En el partido: *64 %* del balón y *20 tiros*"),
    (10.0, 13.6, "Pero *precipitado*: siempre *al contacto*"),
    (15.6, 17.0, "*Adli* la pone al área…"),
    (17.1, 18.2, "y *Álvaro Rodríguez* empata de cabeza"),
    (20.8, 22.4, "*Truffert* roba… y *corre*"),
    (22.5, 24.9, "*Tavernier* la da de cara…"),
    (25.0, 28.0, "y *Rayan*, desde el banquillo"),
]
SHOW = [((2.5, 4.1), {"Diakité"}), ((6.8, 9.9), {"Aspas", "Driouech"}), ((10.0, 13.6), {"Aspas", "Á. Rodríguez"}),
        ((15.5, 17.0), {"Adli"}), ((17.9, 20.4), {"Á. Rodríguez"}), ((20.7, 22.4), {"Truffert"}), ((22.5, 24.9), {"Truffert", "Tavernier"}),
        ((24.9, 28.0), {"Rayan", "Tavernier"}), ((0.2, 2.3), {"Truffert", "Rayan"})]
FOCUS = [(2.5, 3.6, {"Diakité"}), (10.2, 11.4, {"Aspas"}), (15.6, 17.0, {"Adli"}), (17.0, 18.6, {"Á. Rodríguez"}),
         (20.7, 22.3, {"Truffert"}), (25.0, 26.8, {"Rayan"})]
TAGS = [(15.5, 16.5, "c_d4", "4 CONTRA 3", YEL), (22.6, 23.7, "Tavernier", "ENTRÓ", (60, 200, 110)), (25.0, 25.9, "Rayan", "ENTRÓ", (60, 200, 110))]
SCORE = [(2.6, 6.4, 1, 0, "23'"), (6.8, 13.6, 1, 0, "1.ª P"), (14.0, GOAL1, 1, 0, "47'"), (GOAL1, 20.4, 1, 1, "47'"),
         (20.8, GOAL2, 1, 1, "78'"), (GOAL2, 28.1, 1, 2, "78'")]
GOALS = [(GOAL1, "1-1", "Álvaro Rodríguez · 47'"), (GOAL2, "1-2", "Rayan · 78'")]
FACTS = [("5/5", "1.º equipo inglés que gana sus 5 primeros partidos europeos"), ("15", "puntos: líder de la Europa League"),
         ("3", "puntos del Celta tras 5 jornadas")]
DRILL = ["40×30 m · *6 contra 5* + porteros", "Gol solo tras *cambiar de pasillo*", "Si roba el de 5: *6 s* para marcar", "Se busca: *pausa*, *girar* y *cerrar el área*"]
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
    if s is SEG[1] and t >= 4.2:                                              # el hueco de Diakité
        C.ghost(b, cam, *DIAK_GHOST, BOU, "Diakité", ease((t - 4.4) / .3) * fade, t, tag="ROJA")
    if s is SEG[2]:
        blk = ease((t - 7.0) / .5) * (1 - ease((t - 9.8) / .3)) * fade         # el bloque de 10, junto
        C.zone(b, cam, [(-20, 77), (21, 77), (21, 89), (-20, 89)], BOU, blk * .8, 30)
        C.passline(b, cam, (-10, 50), (-4, 62), t, B0 + .6, .5, CEL, fade, .7)
        C.passline(b, cam, (-4, 62), (-20, 76), t, B0 + 1.7, .6, CEL, fade, .7)
        C.passline(b, cam, (-20, 76), (-3, 79), t, B0 + 2.8, .5, YEL, fade, 1.6)
        if t > LOSS - .5:                                                     # tres contra uno: el choque
            pa_ = ease((t - LOSS + .5) / .3) * (1 - ease((t - 12.6) / .4)) * fade
            for pr in ("b_m1", "b_m2", "b_w1"):
                C.pressure(b, cam, posx(s, pr, lt), posx(s, "Aspas", lt), BOU, pa_)
    if s is SEG[3]:
        C.passline(b, cam, (25, 24), (.6, 7.4), t, XC0, .7, YEL, fade, 1.2)
        za = ease((t - 15.6) / .3) * (1 - ease((t - 18.0) / .3)) * fade
        C.zone(b, cam, [(-20.15, 0), (20.15, 0), (20.15, 16.5), (-20.15, 16.5)], YEL, za * .7, 22)
    if s is SEG[4]:
        C.arrow(b, cam, (21, 70), (14, 36), YEL, ease((t - STEAL - .2) / 1.6), 1 - ease((t - D0 - 3.4) / .3))
        C.passline(b, cam, (14, 34), (7.4, 18), t, D0 + 3.6, .8, YEL, fade, .8)
        C.passline(b, cam, (7.4, 18), (-3, 12), t, D0 + 4.6, .8, YEL, fade, 1.0)
        # los del Celta que vuelven tarde: líneas de carrera
        for n in ("c_m1", "c_m2", "Aspas"):
            C.link(b, cam, posx(s, n, lt), posx(s, n, 0), CEL, 1.0, ease((t - D0 - 1.0) / .4) * (1 - ease((t - D0 - 4.6) / .4)) * .6)
    people = [(n, CEL, False) for n in s[2]] + [(n, BOU, True) for n in s[3]]
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
        if s is SEG[1] and n == "Diakité" and t >= 4.2: continue             # expulsado: ya solo queda su hueco
        x, z = posx(s, n, lt); na = 0.0
        for (s0, s1), names in SHOW:
            if s0 <= t < s1 and n in names: na = ease((t - s0) / .3) * (1 - ease((t - s1 + .3) / .3))
        if any(t0 <= t < t1 and tn == n for t0, t1, tn, _, _ in TAGS): na = 0.0      # la etiqueta flotante manda
        nm = n if n[0].isupper() else None
        C.player(b, cam, x, z, col, None, nm, fade, 0.0, dark, na * fade)
    for t0, t1, n, txt, col in TAGS:
        if t0 <= t < t1 and (n in s[2] or n in s[3]):
            x, z = posx(s, n, lt)
            C.tag3d(b, cam, x, z, txt, col, ease((t - t0) / .25) * (1 - ease((t - t1 + .25) / .25)), fg=((14, 22, 34) if col == YEL else WHT), h=(4.2 if col == YEL else 6.4))
    bts = [ball_at(s, max(0.0, lt - .04 * k)) for k in range(8, -1, -1)]
    if abs(bts[0][0][0] - bts[-1][0][0]) + abs(bts[0][0][1] - bts[-1][0][1]) > 2:
        C.ball_trail(b, cam, [(p[0], p[1], y) for p, y in bts], fade)
    (bx, bz), by = ball_at(s, lt)
    if fade > .5 and t < 28.2: C.ballp(b, cam, bx, bz, by)
    C.spark(b, cam, -20.8, 78.4, t, 2.4 + .72, col=RED)                       # la entrada
    C.spark(b, cam, -3, 79.6, t, LOSS, col=BOU)                               # el choque: pérdida
    C.spark(b, cam, 21.4, 72.6, t, STEAL, col=YEL)                            # el robo de Truffert
    b = C.motion_blur(b, cspeed(min(t, END)) if t < END else 0)
    b.alpha_composite(VIG)
    if t < 2.4:
        sh_ = Image.new("RGBA", b.size, (0, 0, 0, 0)); a_ = int(130 * (1 - ease((t - 2.0) / .4)))
        ImageDraw.Draw(sh_).rectangle((0, 640 * 2, W2, 1080 * 2), fill=(*BG, a_)); b.alpha_composite(sh_.filter(ImageFilter.GaussianBlur(60)))
    C.bigtitle(b, t, 2.4, "Con 10 desde el 23'", "y ganó en Balaídos")
    if 0.1 < t < 28.1: C.rec_tag(b, a=ease((t - 0.1) / .3) * (1 - ease((t - 27.8) / .3)))
    if 2.2 < t < 37.9: C.headline(b, t, HEAD)
    if t < 28.1: C.subs(b, t, SUBS, y=1395)
    C.redcard(b, t, 3.25, 1.0, "ROJA · 23'", "Diakité", y=700)
    C.outnumber(b, t, 4.3, 6.5, 11, 10, CEL, BOU, "CELTA", "BOURNE.", out_at=4.9, y=560)   # NUEVO (v3.8)
    C.lower_third(b, t, 10.4, 13.6, "«Hemos atacado muy precipitados»", "GIRÁLDEZ, ENTRENADOR DEL CELTA")
    C.subboard(b, t, 13.8, 15.3, ["Kluivert"], ["Adams"], "DESCANSO · BOURNEMOUTH", y=800)
    C.lower_third(b, t, 20.8, 22.4, "Marco Rose", "ENTRENADOR DEL BOURNEMOUTH", "mueve el banquillo")
    for t0, t1, h, a, mn in SCORE: C.scoreboard(b, t, t0, t1, "CEL", "BOU", h, a, mn)
    for tg, txt, sub in GOALS: C.flash(b, t, tg, txt, sub)
    C.quote(b, t, 18.0, 20.5, "Estamos cuatro en el área contra tres de ellos", "GIRÁLDEZ, SOBRE EL 1-1")
    b = b.convert("RGB").convert("RGBA")
    for tw in [g[0] for g in GOALS]: C.white_flash(b, t, tw)
    C.statbars(b, t, 28.2, 30.4, "EN TODO EL PARTIDO", "CELTA", "BOURNE.", CEL, BOU,
               [("Posesión", 64, 36, "64 %", "36 %"), ("Tiros", 20, 10, "20", "10")], y=600)
    C.factlist(b, t, 30.4, 33.2, "CELTA 1-2 BOURNEMOUTH", FACTS, y=540)
    C.drillboard(b, t, 33.2, END, "ANTES DE LOS 90 · ASÍ SE ENTRENA", "Superioridad con cerebro", DRILL, CEL, BOU)   # NUEVO (v3.8)
    if t >= END: C.endcard(b, t - END, "¿Falló el Celta", "o lo ganó Rose?", "Te leo en comentarios")
    for tw in [g[0] for g in GOALS] + [3.1]: b = C.shake(b, t, tw)
    return finish(b.convert("RGB"))

if __name__ == "__main__":
    out = sys.argv[1]
    if "--sheet" in sys.argv:
        ts = [float(x) for x in sys.argv[sys.argv.index("--sheet") + 1:]]
        ims = [scene(t, t).resize((540, 960)) for t in ts]
        sh = Image.new("RGB", (540 * len(ims), 960)); [sh.paste(im, (540 * i, 0)) for i, im in enumerate(ims)]; sh.save(out, quality=85)
    else:
        sfx = out + ".sfx.wav"
        C.sfx_track(sfx, TOTAL, whooshes=[2.4, 4.2, 6.6, 10.0, 13.8, 15.4, 17.1, 20.6, 22.5, 25.0, 28.2, 30.4, 33.2, 38.5],
                    hits=[3.1, 4.9, LOSS, GOAL1, STEAL, GOAL2])
        C.encode(compose, TOTAL, out, os.path.join(ROOT, "music", "okay_for_now-televisions.mp3"), sfx)
