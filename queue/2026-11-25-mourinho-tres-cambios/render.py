"""Cine: 'Tres cambios al descanso y de 0-1 a 5-1' — Real Madrid 5-1 PSV (Champions, J5, martes 24-11-2026, Bernabéu).
Clave 1: el PSV apretaba arriba y el Madrid no salía (penalti de Tchouaméni, Perišić 32').
Clave 2: triple cambio al descanso (Militão, Rüdiger, Tchouaméni → Huijsen, Konaté, Bellingham).
Clave 3: Güler baja junto a Bernardo, la línea sube y el Madrid presiona arriba: robo de Güler y 3-1 de Mbappé.
Uso: python queue/2026-11-25-mourinho-tres-cambios/render.py salida.mp4 [--sheet t1 t2 ...]
Experimento de la semana: ≤ 42 s y la jugada en movimiento desde el fotograma 0 (la presión alta de la 2.ª parte bajo el gancho).
Nota: posiciones = recreación ilustrativa (chip 'Recreación'); solo se rotula a quien citan las fuentes.
Nuevo en el motor (v3.6): subboard (cartel LED del cuarto árbitro) y lineband (la línea defensiva que sube, con su huella)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "engine"))
from PIL import Image, ImageDraw, ImageFilter
from flat import W2, H2, BG, YEL, WHT, ease, lerp2, finish
import cine as C

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
RMA = (236, 236, 242); PSV = (222, 30, 44); RED = (230, 40, 50)
END = 38.0; TOTAL = END + 3.6

def track(keys, t):
    if t <= keys[0][0]: return keys[0][1]
    for (t0, a), (t1, b) in zip(keys, keys[1:]):
        if t0 <= t <= t1: return lerp2(a, b, ease((t - t0) / max(1e-6, t1 - t0)))
    return keys[-1][1]
def P(*k): return list(k)
def S(x, z): return P((0, (x, z)))

# x: -34..34 · z: 0 portería del Madrid (Courtois), 105 portería del PSV (Kovář). El Madrid ataca hacia z=105.
# Nombres en minúscula = jugador sin rotular.

# ---------------- H · 0–2,4: gancho · la presión alta de la segunda parte, ya en movimiento
HM = {"Mbappé": P((0, (-4, 78)), (2.4, (-1, 89))), "Vinícius": P((0, (-22, 80)), (2.4, (-15, 90))),
      "Bellingham": P((0, (8, 70)), (2.4, (6, 84))), "Güler": P((0, (14, 68)), (2.4, (12, 80))),
      "Valverde": P((0, (24, 66)), (2.4, (22, 78))), "Bernardo": P((0, (0, 60)), (2.4, (0, 70))),
      "Huijsen": P((0, (-8, 44)), (2.4, (-8, 56))), "Konaté": P((0, (8, 44)), (2.4, (8, 56))),
      "m1": P((0, (-24, 48)), (2.4, (-24, 60))), "m2": P((0, (24, 48)), (2.4, (24, 60)))}
HP = {"p1": P((0, (2, 93)), (2.4, (4, 95))), "p2": S(-12, 92), "p3": S(14, 92), "p4": S(-25, 86), "p5": S(25, 86),
      "p6": P((0, (0, 84)), (2.4, (1, 87))), "p7": S(-8, 78), "p8": S(10, 78), "gk": S(0, 103)}
BH = [(0, "p1"), (2.4, "p1")]

# ---------------- A1 · 2,4–6,0: primera parte · el PSV aprieta la salida
A1M = {"Courtois": S(0, 3), "Militão": P((0, (-10, 12)), (3.6, (-11, 13))), "Rüdiger": P((0, (10, 12)), (3.6, (11, 13))),
       "Tchouaméni": P((0, (0, 22)), (3.6, (-2, 20))), "Bernardo": P((0, (-9, 32)), (3.6, (-9, 30))),
       "Güler": P((0, (3, 42)), (3.6, (3, 40))), "Valverde": S(22, 34), "m1": S(-24, 26), "m2": S(24, 24),
       "Vinícius": S(-22, 55), "Mbappé": S(2, 60)}
A1P = {"pa": P((0, (-5, 26)), (1.6, (-8.5, 15.5)), (3.6, (-9, 15))), "pb": P((0, (6, 26)), (1.3, (9, 15.5)), (3.6, (9.5, 15))),
       "Mijnans": P((0, (2, 32)), (1.6, (0, 24.5)), (3.6, (-1, 23.5))), "pc": P((0, (-14, 38)), (3.6, (-11, 33))),
       "pd": P((0, (14, 38)), (3.6, (13, 35))), "pe": P((0, (22, 44)), (3.6, (22, 38))), "pf": P((0, (-22, 46)), (3.6, (-22, 40))),
       "pg": S(-12, 60), "ph": S(0, 62), "pi": S(12, 60)}
BA1 = [(0, "Courtois"), (0.5, "Courtois"), (1.1, "Rüdiger"), (1.9, "Rüdiger"), (2.6, "Courtois"), (3.6, "Courtois")]

# ---------------- A2 · 6,0–9,2: el penalti · Tchouaméni sobre Mijnans (VAR), Perišić 32'
A2M = {"Courtois": P((0, (0, 2)), (3.2, (-1, 2))), "Tchouaméni": P((0, (-7, 22)), (1.0, (-4.6, 14.8)), (3.2, (-4.4, 14.6))),
       "Militão": S(-10, 10), "Rüdiger": S(8, 11), "m1": S(-20, 18), "Bernardo": S(4, 24), "Valverde": S(16, 26)}
A2P = {"Mijnans": P((0, (-10, 24)), (1.0, (-5, 14.2)), (3.2, (-5.2, 13.8))), "Perišić": P((0, (14, 22)), (3.2, (10, 18))),
       "pc": S(2, 31), "pd": P((0, (-21, 31)), (3.2, (-19, 29)))}
BA2 = [(0, "pd"), (0.45, "pd"), (0.9, "Mijnans"), (1.0, "Mijnans"), (1.25, (-4, 11.5)), (3.2, (-4, 11.5))]
FOUL = 6.0 + 1.0

# ---------------- B · 9,2–17,6: el triple cambio · Huijsen saca el balón y Bellingham conduce
BM = {"Courtois": S(0, 3), "Huijsen": P((0, (-10, 12)), (2.8, (-10, 12)), (4.4, (-8, 22)), (8.4, (-8, 24))),
      "Konaté": P((0, (10, 12)), (8.4, (10, 18))), "Bernardo": P((0, (-2, 28)), (8.4, (-2, 34))),
      "Güler": P((0, (8, 30)), (8.4, (8, 38))), "Bellingham": P((0, (6, 44)), (5.0, (4, 47)), (7.6, (2, 57)), (8.4, (2, 58))),
      "Valverde": P((0, (22, 40)), (8.4, (22, 54))), "m1": P((0, (-24, 30)), (8.4, (-24, 42))), "m2": P((0, (24, 26)), (8.4, (24, 38))),
      "Vinícius": P((0, (-22, 58)), (8.4, (-20, 68))), "Mbappé": P((0, (2, 64)), (8.4, (4, 74)))}
BP = {"pa": P((0, (-6, 36)), (8.4, (-6, 33))), "pb": P((0, (6, 36)), (8.4, (8, 34))), "Mijnans": P((0, (-9, 46)), (8.4, (-10, 47))),
      "pc": P((0, (-14, 48)), (8.4, (-13, 50))), "pd": P((0, (14, 52)), (8.4, (12, 54))), "pe": P((0, (-7, 56)), (8.4, (-6, 61))),
      "pg": S(-14, 68), "ph": S(-4, 70), "pi": S(6, 70), "pj": S(17, 68)}
BB = [(0, "Huijsen"), (4.5, "Huijsen"), (5.05, "Bellingham"), (8.4, "Bellingham")]

# ---------------- C1 · 17,6–20,6: Güler baja junto a Bernardo y monta el juego
C1M = {"Courtois": S(0, 3), "Huijsen": S(-10, 18), "Konaté": S(10, 18), "Bernardo": P((0, (-6, 34)), (3, (-7, 34))),
       "Güler": P((0, (6, 47)), (2.0, (1, 34.5)), (3, (1, 35))), "Bellingham": P((0, (2, 52)), (3, (4, 56))),
       "Valverde": S(22, 50), "m1": S(-24, 36), "m2": S(24, 34), "Vinícius": S(-20, 66), "Mbappé": S(2, 72)}
C1P = {"pa": S(-6, 44), "pb": S(7, 44), "Mijnans": P((0, (2, 52)), (3, (1, 48))), "pc": S(-14, 54), "pd": S(14, 56),
       "pe": S(-2, 62), "pg": S(-14, 70), "ph": S(-4, 72), "pi": S(6, 72), "pj": S(17, 70)}
BC1 = [(0, "Huijsen"), (1.9, "Huijsen"), (2.5, "Güler"), (3, "Güler")]

# ---------------- C2 · 20,6–27,0: la línea sube, presión arriba, robo de Güler y 3-1 de Mbappé (64')
LINE0, LINE1 = 30.0, 50.0
def lz(dz): return P((0, (0, LINE0 + dz)), (2.4, (0, LINE1 + dz)))
def mv(x, z0, z1, t1=2.4): return P((0, (x, z0)), (t1, (x, z1)))
C2M = {"Huijsen": mv(-9, LINE0, LINE1), "Konaté": mv(9, LINE0, LINE1), "m1": mv(-24, LINE0 + 2, LINE1 + 3), "m2": mv(24, LINE0 + 2, LINE1 + 3),
       "Bernardo": mv(-4, 52, 64), "Bellingham": P((0, (8, 64)), (2.4, (9, 76)), (6.4, (8, 82))),
       "Güler": P((0, (4, 58)), (2.4, (5, 71)), (3.4, (7.2, 77.0)), (3.8, (7.6, 78.0)), (6.4, (8, 80))),
       "Valverde": mv(22, 62, 74), "Vinícius": P((0, (-20, 70)), (2.4, (-16, 80)), (6.4, (-12, 90))),
       "Mbappé": P((0, (0, 72)), (2.4, (2, 83)), (3.9, (1, 88)), (4.6, (0.5, 91)), (6.4, (0, 93)))}
C2P = {"gk": P((0, (0, 103)), (4.7, (-0.5, 102.6)), (5.0, (-3.2, 103)), (6.4, (-3.6, 103.2))),
       "pg": S(-14, 92), "ph": P((0, (-1, 95)), (6.4, (0, 94))), "pi": P((0, (10, 93)), (6.4, (6, 94))),
       "pj": S(23, 86), "pk": S(-24, 84), "pl": P((0, (11, 74)), (2.2, (8, 79)), (3.2, (7.6, 77.6)), (6.4, (9, 80))),
       "pc": S(-8, 80), "pd": P((0, (16, 72)), (6.4, (14, 82))), "pe": P((0, (-4, 74)), (6.4, (-3, 84)))}
BC2 = [(0, "ph"), (2.3, "ph"), (3.2, "pl"), (3.35, "pl"), (3.5, "Güler"), (3.65, "Güler"), (4.05, "Mbappé"), (4.55, "Mbappé"),
       (4.95, (-1.8, 105.3)), (6.4, (-2.0, 105.6))]
STEAL, SHOT, GOAL3 = 20.6 + 3.4, 20.6 + 4.55, 20.6 + 4.95

# ---------------- D · 27–: plano general para los goles, la cita y el dato
DM = {k: S(*v) for k, v in {"Courtois": (0, 4), "Huijsen": (-9, 30), "Konaté": (9, 30), "m1": (-24, 38), "m2": (24, 38),
      "Bernardo": (-4, 46), "Güler": (6, 50), "Bellingham": (2, 62), "Valverde": (20, 60), "Vinícius": (-20, 72), "Mbappé": (0, 78)}.items()}
DP = {k: S(*v) for k, v in {"gk": (0, 101), "pg": (-18, 88), "ph": (-6, 90), "pi": (6, 90), "pj": (18, 88),
      "pc": (-10, 76), "pe": (0, 74), "pd": (10, 76), "pk": (-18, 64), "Mijnans": (2, 64)}.items()}

# (t0, t1, Madrid, PSV, balón)
SEG = [(0.0, 2.4, HM, HP, BH), (2.4, 6.0, A1M, A1P, BA1), (6.0, 9.2, A2M, A2P, BA2), (9.2, 17.6, BM, BP, BB),
       (17.6, 20.6, C1M, C1P, BC1), (20.6, 27.0, C2M, C2P, BC2), (27.0, 99.0, DM, DP, [(0, (0, 52.5))])]

CAMK = [
    (0.0,  dict(el=22, d=64,  tx=-2, tz=84, az=-16, cy=1200)),   # gancho: baja, a ras de la presión
    (2.3,  dict(el=26, d=70,  tx=0,  tz=88, az=10,  cy=1180)),
    (2.4,  dict(el=50, d=120, tx=0,  tz=24, az=180, cy=900)),    # primera parte: desde detrás del PSV que presiona
    (4.2,  dict(el=40, d=92,  tx=0,  tz=20, az=196, cy=900)),
    (5.9,  dict(el=36, d=84,  tx=-2, tz=18, az=204, cy=900)),
    (6.0,  dict(el=30, d=52,  tx=-5, tz=16, az=128, cy=1060)),    # el penalti: lateral, a pie de área
    (9.1,  dict(el=34, d=56,  tx=-5, tz=15, az=110, cy=1050)),
    (9.2,  dict(el=62, d=175, tx=0,  tz=40, az=0,   cy=900)),    # descanso: general detrás del cartel
    (11.8, dict(el=56, d=160, tx=0,  tz=38, az=-6,  cy=900)),
    (11.9, dict(el=30, d=70,  tx=-8, tz=18, az=-30, cy=960)),    # baja, detrás de Huijsen
    (14.2, dict(el=34, d=86,  tx=-4, tz=34, az=-12, cy=930)),
    (14.3, dict(el=38, d=66,  tx=4,  tz=52, az=26,  cy=920)),    # gira a Bellingham
    (17.5, dict(el=40, d=78,  tx=2,  tz=58, az=12,  cy=910)),
    (17.6, dict(el=64, d=110, tx=0,  tz=44, az=0,   cy=860)),    # cenital: Güler cae al lado de Bernardo
    (20.5, dict(el=58, d=118, tx=-2, tz=44, az=-14, cy=860)),
    (20.6, dict(el=30, d=150, tx=0,  tz=56, az=90,  cy=900)),    # de lado: se ve subir la línea
    (23.2, dict(el=34, d=140, tx=0,  tz=64, az=78,  cy=900)),
    (23.3, dict(el=36, d=64,  tx=4,  tz=82, az=-20, cy=860)),    # zoom al robo y al remate
    (25.5, dict(el=40, d=60,  tx=1,  tz=94, az=-6,  cy=900)),
    (26.9, dict(el=34, d=58,  tx=0,  tz=96, az=14,  cy=900)),
    (27.0, dict(el=56, d=180, tx=0,  tz=58, az=-10, cy=900)),
    (END,  dict(el=50, d=160, tx=0,  tz=62, az=12,  cy=900)),
]
HEAD = [
    (2.4,  "REAL MADRID 5-1 PSV · CHAMPIONS", "Clave 1:", "el PSV apretaba"),
    (9.2,  "CLAVE 2 · EL DESCANSO", "Tres cambios", "a la vez"),
    (17.6, "CLAVE 3 · LA SEGUNDA PARTE", "Güler baja,", "la línea sube"),
    (27.0, "LA CONSECUENCIA", "Del 0-1", "al 5-1"),
]
SUBS = [
    (2.6, 4.3, "Primera parte: el PSV *aprieta arriba*"),
    (4.3, 5.9, "y el Madrid *no sale limpio*"),
    (6.1, 7.8, "Penalti de *Tchouaméni* sobre *Mijnans*"),
    (12.0, 14.2, "*Huijsen* saca el balón desde atrás"),
    (14.3, 17.4, "y *Bellingham* conduce: el Madrid *ya avanza*"),
    (17.8, 20.5, "*Güler* baja junto a *Bernardo* y monta el juego"),
    (20.8, 23.2, "La defensa *se adelanta*: presión *arriba*"),
    (23.4, 25.0, "*Güler* roba y asiste a *Mbappé*"),
]
SHOW = [((2.6, 5.9), {"Militão", "Rüdiger", "Tchouaméni"}), ((6.1, 6.85), {"Mijnans"}), ((6.85, 7.3), {"Tchouaméni"}),
        ((12.0, 14.2), {"Huijsen", "Konaté"}), ((14.3, 17.5), {"Bellingham"}), ((17.8, 20.5), {"Güler", "Bernardo"}),
        ((23.4, 25.0), {"Güler"})]
FOCUS = [(3.0, 4.4, {"Rüdiger"}), (12.0, 14.0, {"Huijsen"}), (14.6, 17.0, {"Bellingham"}), (18.0, 20.4, {"Güler"}),
         (23.3, 24.4, {"Güler"}), (24.4, 25.2, {"Mbappé"})]
TAGS = [(7.3, 8.0, "Tchouaméni", "VAR · PENALTI", RED)]
SCORE = [(2.6, 5.9, 0, 0, "1.ª P"), (6.1, 7.9, 0, 0, "32'"), (7.9, 9.2, 0, 1, "32'"),
         (20.8, GOAL3, 2, 1, "64'"), (GOAL3, 27.0, 3, 1, "64'")]
GOALS = [(7.9, "0-1", "Perišić, de penalti · 32'"), (GOAL3, "3-1", "Mbappé · 64'")]
GOALLIST = [("50'", "Valverde, tras un taconazo de Güler"),
            ("60'", "Bellingham, desde fuera del área"),
            ("64'", "Mbappé, tras el robo de Güler"),
            ("84'", "Mbappé otra vez, pase de Brahim"),
            ("87'", "Vinícius cierra el 5-1")]
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
    if s is SEG[1]:                                                           # conos de presión del PSV sobre la salida
        pa_ = ease((t - 2.8) / .4) * (1 - ease((t - 5.6) / .3)) * fade
        for pr, tg in (("pa", "Militão"), ("pb", "Rüdiger"), ("Mijnans", "Tchouaméni")):
            C.pressure(b, cam, posx(s, pr, lt), posx(s, tg, lt), PSV, pa_)
    if s is SEG[3] and 12.4 < t < 14.2:                                       # la conducción de Huijsen
        C.arrow(b, cam, (-10, 13), (-8, 22), YEL, ease((t - 12.4) / .6), 1 - ease((t - 13.9) / .3))
    if s is SEG[3] and 13.4 < t < 15.2:                                       # el pase a Bellingham
        C.arrow(b, cam, (-8, 22.5), (4, 46), YEL, ease((t - 13.4) / .5), 1 - ease((t - 14.9) / .3))
    if s is SEG[4]:                                                           # Güler cae a la altura de Bernardo
        C.arrow(b, cam, (6, 46), (1.5, 36.5), YEL, ease((t - 17.9) / .9), 1 - ease((t - 20.2) / .3))
        C.zone(b, cam, [(-11, 30), (5, 30), (5, 39), (-11, 39)], YEL, ease((t - 19.2) / .4) * (1 - ease((t - 20.3) / .3)), 30)
    if s is SEG[5] and t < 23.4:                                              # NUEVO: la línea defensiva que sube
        u = ease((t - 20.8) / 2.0); zl = LINE0 + (LINE1 - LINE0) * u
        C.lineband(b, cam, zl, YEL, ease((t - 20.8) / .3) * (1 - ease((t - 23.0) / .3)), "LÍNEA ALTA" if u > .5 else None, zfrom=LINE0)
    people = [(n, RMA, False) for n in s[2]] + [(n, PSV, True) for n in s[3]]
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
            C.tag3d(b, cam, x, z, txt, col, ease((t - t0) / .25) * (1 - ease((t - t1 + .25) / .25)))
    bts = [ball_at(s, max(0.0, lt - .04 * k)) for k in range(8, -1, -1)]
    if abs(bts[0][0][0] - bts[-1][0][0]) + abs(bts[0][0][1] - bts[-1][0][1]) > 2:
        C.ball_trail(b, cam, [(p[0], p[1], y) for p, y in bts], fade)
    (bx, bz), by = ball_at(s, lt)
    if fade > .5 and t < 27.0: C.ballp(b, cam, bx, bz, by)
    C.spark(b, cam, -4.8, 14.5, t, FOUL, col=RED)                            # la falta en el área
    C.spark(b, cam, 7.4, 77.6, t, STEAL)                                       # el robo de Güler
    b = C.motion_blur(b, cspeed(min(t, END)) if t < END else 0)
    b.alpha_composite(VIG)
    if t < 2.4:
        sh_ = Image.new("RGBA", b.size, (0, 0, 0, 0)); a_ = int(130 * (1 - ease((t - 2.0) / .4)))
        ImageDraw.Draw(sh_).rectangle((0, 640 * 2, W2, 1080 * 2), fill=(*BG, a_)); b.alpha_composite(sh_.filter(ImageFilter.GaussianBlur(60)))
    C.bigtitle(b, t, 2.4, "Tres cambios", "y del 0-1 al 5-1")
    if 0.1 < t < 26.9: C.rec_tag(b, a=ease((t - 0.1) / .3) * (1 - ease((t - 26.6) / .3)) * (0 if 9.2 <= t < 11.9 else 1))
    if 2.2 < t < 37.6: C.headline(b, t, HEAD)
    if t < 26.9: C.subs(b, t, SUBS)
    C.lower_third(b, t, 20.9, 23.3, "«Hemos presionado alto»", "MOURINHO")
    for t0, t1, h, a, mn in SCORE: C.scoreboard(b, t, t0, t1, "RMA", "PSV", h, a, mn)
    for tg, txt, sub in GOALS: C.flash(b, t, tg, txt, sub)
    C.subboard(b, t, 9.2, 11.95, ["Militão", "Rüdiger", "Tchouaméni"], ["Huijsen", "Konaté", "Bellingham"], "DESCANSO · 0-1")   # NUEVO
    b = b.convert("RGB").convert("RGBA")
    for tw in [g[0] for g in GOALS] + [FOUL]: C.white_flash(b, t, tw)
    C.factlist(b, t, 27.0, 31.8, "DEL 0-1 AL 5-1", GOALLIST, y=470)
    C.quote(b, t, 31.8, 35.0, "He pensado, quizás mal, que podía ganar sin él", "MOURINHO, SOBRE BELLINGHAM")
    C.counter(b, t, 35.0, END, 10, "victorias seguidas del Madrid")
    if t >= END: C.endcard(b, t - END, "¿Lo cambió la mentalidad", "o los tres cambios?", "Te leo en comentarios")
    for tw in [g[0] for g in GOALS] + [FOUL]: b = C.shake(b, t, tw)
    return finish(b.convert("RGB"))

if __name__ == "__main__":
    out = sys.argv[1]
    if "--sheet" in sys.argv:
        ts = [float(x) for x in sys.argv[sys.argv.index("--sheet") + 1:]]
        ims = [scene(t, t).resize((540, 960)) for t in ts]
        sh = Image.new("RGB", (540 * len(ims), 960)); [sh.paste(im, (540 * i, 0)) for i, im in enumerate(ims)]; sh.save(out, quality=85)
    else:
        sfx = out + ".sfx.wav"
        C.sfx_track(sfx, TOTAL, whooshes=[2.4, 6.0, 9.2, 11.9, 14.3, 17.6, 20.6, 23.3, 27.0, 31.8, 35.0, 37.9],
                    hits=[FOUL, 7.9, 9.9, 10.35, 10.8, GOAL3, 36.6])
        C.encode(compose, TOTAL, out, os.path.join(ROOT, "music", "dance_with_you-everet_almond.mp3"), sfx)
