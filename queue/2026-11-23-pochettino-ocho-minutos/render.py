"""Cine: 'Cambió la defensa y duró 8 minutos' — Liverpool 4-0 Manchester United, debut de Pochettino
(Premier League, jornada 11, Anfield, 22-11-2026). Tres claves tácticas; los goles al final. Fuentes en meta.json.
Uso: python queue/2026-11-23-pochettino-ocho-minutos/render.py salida.mp4 [--sheet t1 t2 ...]
Nota: las posiciones en el campo son una recreación ilustrativa; solo se rotula lo que está en las fuentes.
Nuevo en el motor (v3.4): heatmap (mapa de calor de toques) y redcard (tarjeta roja que gira)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "engine"))
from PIL import Image, ImageDraw, ImageFilter
from flat import W2, H2, BG, YEL, WHT, ease, lerp2, finish
import cine as C

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
LIV = (200, 16, 46); MUN = (240, 242, 246); RED = (230, 40, 50); BLU = (40, 120, 230)
END = 48.2; TOTAL = END + 3.6

def track(keys, t):
    if t <= keys[0][0]: return keys[0][1]
    for (t0, a), (t1, b) in zip(keys, keys[1:]):
        if t0 <= t <= t1: return lerp2(a, b, ease((t - t0) / max(1e-6, t1 - t0)))
    return keys[-1][1]
def P(*k): return list(k)
def S(x, z): return P((0, (x, z)))

# x: -34..34 · z: 0 portería del Liverpool (Alisson), 105 portería del United (Lammens).
# El Liverpool ataca hacia z=105. Lado x>0: Dalot (lateral derecho del United) contra Ngumoha.
# Lado x<0: L. Martínez (lateral izquierdo del United) contra Barcola.

# ---------------- A · 0–8,5: el United de Pochettino, con De Ligt y Yoro de centrales
AU = {"Lammens": S(0, 102), "Dalot": P((0, (23, 86)), (8.5, (24, 84))), "Yoro": P((0, (8, 88)), (8.5, (7, 86))),
      "De Ligt": P((0, (-7, 88)), (8.5, (-6, 86))), "L. Martínez": P((0, (-23, 86)), (8.5, (-24, 84))),
      "Tielemans": P((0, (3, 76)), (8.5, (4, 73))), "Mainoo": P((0, (-6, 74)), (8.5, (-5, 71))),
      "Mbeumo": P((0, (22, 66)), (8.5, (23, 62))), "Fernandes": P((0, (0, 64)), (8.5, (1, 60))),
      "Dorgu": P((0, (-22, 64)), (8.5, (-23, 61))), "Cunha": P((0, (0, 54)), (8.5, (-1, 51)))}
AL = {"Alisson": S(0, 6), "Araujo": P((0, (-24, 24)), (8.5, (-24, 30))), "Van Dijk": P((0, (6, 20)), (8.5, (7, 26))),
      "Jacquet": P((0, (-7, 20)), (8.5, (-6, 26))), "Kerkez": P((0, (24, 24)), (8.5, (24, 30))),
      "Szoboszlai": P((0, (5, 36)), (8.5, (6, 41))), "Mac Allister": P((0, (-5, 34)), (8.5, (-4, 39))),
      "Wirtz": P((0, (1, 46)), (8.5, (2, 50))), "Ngumoha": P((0, (25, 44)), (8.5, (26, 50))),
      "Barcola": P((0, (-25, 44)), (8.5, (-26, 50))), "Isak": P((0, (0, 52)), (8.5, (0, 56)))}
BA = [(0, "Van Dijk"), (0.8, "Van Dijk"), (1.9, "Jacquet"), (2.9, "Jacquet"), (4.0, "Mac Allister"),
      (5.0, "Mac Allister"), (6.2, "Szoboszlai"), (9, "Szoboszlai")]

# ---------------- B · 8,5–15,5: balón largo al centro, De Ligt no lo gana, Isak se escapa y Yoro le hace falta (8')
BU = {"Lammens": S(0, 101), "Dalot": P((0, (22, 84)), (7, (21, 86))),
      "Yoro": P((0, (8, 80)), (2.6, (6, 83)), (4.0, (2, 88)), (4.6, (0.8, 89.6)), (7, (0.8, 89.6))),
      "De Ligt": P((0, (-5, 76)), (2.0, (-2.5, 78)), (2.9, (-1.2, 78.6)), (4.2, (-3, 81)), (7, (-4, 82))),
      "L. Martínez": P((0, (-22, 82)), (7, (-21, 84))), "Tielemans": P((0, (2, 66)), (7, (3, 70))),
      "Mainoo": P((0, (-7, 64)), (7, (-6, 68))), "Fernandes": S(0, 56), "Mbeumo": S(20, 58), "Dorgu": S(-20, 56),
      "Cunha": S(0, 48)}
BL = {"Isak": P((0, (2, 62)), (2.2, (1, 73)), (3.0, (0.6, 79)), (4.0, (0.2, 86)), (4.6, (0.1, 89)), (7, (0.1, 89))),
      "araujo": S(-24, 42), "vandijk": S(6, 40), "Szoboszlai": S(4, 52), "Mac Allister": S(-6, 50),
      "Wirtz": S(-2, 58), "Ngumoha": S(25, 56), "Barcola": S(-25, 56)}
BB = [(0, "araujo"), (0.7, "araujo"), (2.3, (0, 79)), (3.1, (0.4, 83)), (4.0, "Isak"), (4.5, "Isak"),
      (4.75, (1.6, 92)), (7, (1.8, 93))]

# ---------------- C · 15,5–28,5: con diez, entra Maguire (22') y el United se mete atrás con cinco
CU = {"Lammens": S(0, 101), "Dorgu": P((0, (-20, 88)), (13, (-19, 90))), "L. Martínez": P((0, (-9, 90)), (13, (-9, 92))),
      "Maguire": P((0, (0, 91)), (13, (0, 93))), "De Ligt": P((0, (9, 90)), (13, (9, 92))),
      "Dalot": P((0, (20, 88)), (13, (20, 90))), "Mainoo": P((0, (-7, 80)), (13, (-6, 84))),
      "Tielemans": P((0, (2, 80)), (13, (2, 84))), "Fernandes": P((0, (11, 78)), (13, (10, 82))),
      "Cunha": P((0, (0, 68)), (13, (-1, 74)))}
CL = {"Van Dijk": P((0, (2, 52)), (13, (2, 58))), "Jacquet": P((0, (-10, 52)), (13, (-10, 58))),
      "Araujo": P((0, (-21, 64)), (13, (-22, 70))), "Kerkez": P((0, (21, 64)), (13, (22, 70))),
      "Szoboszlai": P((0, (4, 70)), (13, (5, 76))), "Mac Allister": P((0, (-5, 68)), (13, (-4, 74))),
      "Wirtz": P((0, (1, 80)), (13, (0, 84))), "Barcola": P((0, (-25, 78)), (13, (-26, 82))),
      "Ngumoha": P((0, (25, 78)), (13, (26, 82))), "Isak": P((0, (0, 86)), (13, (0, 88)))}
BC = [(0, "Szoboszlai"), (0.8, "Szoboszlai"), (2.0, "Kerkez"), (3.2, "Kerkez"), (4.4, "Ngumoha"), (5.4, "Ngumoha"),
      (6.6, "Wirtz"), (7.6, "Wirtz"), (8.8, "Mac Allister"), (9.8, "Mac Allister"), (11.0, "Barcola"), (14, "Barcola")]
HEAT = [(-16, 92, 6, .7), (-8, 96, 7, 1.0), (0, 99, 7, 1.0), (7, 95, 7, .9), (15, 91, 6, .7), (-2, 88, 6, .6),
        (10, 101, 5, .6), (-12, 100, 5, .6), (18, 97, 5, .5)]

# ---------------- D · 28,5–33,5: Ngumoha desborda a Dalot y centra raso para Wirtz (2-0, 13')
DU = {"Lammens": P((0, (0, 101)), (5, (-1.2, 101.5))), "Dalot": P((0, (22, 78)), (1.6, (23, 84)), (2.6, (22, 88)), (5, (21, 90))),
      "Maguire": P((0, (4, 92)), (3.0, (1, 95)), (5, (0, 96))), "De Ligt": P((0, (12, 90)), (3.0, (8, 94)), (5, (7, 95))),
      "L. Martínez": P((0, (-8, 90)), (5, (-6, 94))), "Dorgu": P((0, (-19, 88)), (5, (-17, 91))),
      "Tielemans": P((0, (6, 82)), (5, (4, 88))), "Mainoo": P((0, (-6, 82)), (5, (-5, 87)))}
DL = {"Ngumoha": P((0, (26, 72)), (1.4, (26, 80)), (2.4, (24.5, 86)), (3.2, (23, 89.5)), (5, (22, 91))),
      "Wirtz": P((0, (2, 80)), (3.2, (0, 92)), (3.8, (-0.6, 96.2)), (5, (-1, 97))),
      "Isak": P((0, (-2, 86)), (5, (-4, 93))), "Szoboszlai": P((0, (6, 76)), (5, (6, 84))),
      "Kerkez": P((0, (24, 64)), (5, (24, 74))), "Barcola": P((0, (-24, 76)), (5, (-24, 84)))}
BD = [(0, "Ngumoha"), (2.6, "Ngumoha"), (3.3, (12, 93)), (3.75, "Wirtz"), (3.9, "Wirtz"), (4.2, (-1, 105.3))]

# ---------------- E · 33,5–37,5: Barcola gana la carrera a L. Martínez y la pone para Ngumoha (3-0, 66')
EU = {"Lammens": P((0, (0, 101)), (4, (-1, 100.5))), "L. Martínez": P((0, (-24, 74)), (1.4, (-23, 80)), (2.6, (-20, 86)), (4, (-18, 89))),
      "Maguire": P((0, (-4, 86)), (2.8, (-2, 92)), (4, (-1, 94))), "De Ligt": P((0, (6, 86)), (2.8, (4, 92)), (4, (3, 94))),
      "Dalot": P((0, (18, 84)), (4, (16, 90))), "Dorgu": P((0, (-16, 80)), (4, (-14, 86))),
      "Tielemans": P((0, (-2, 76)), (4, (-3, 84))), "Mainoo": P((0, (4, 76)), (4, (3, 84)))}
EL = {"Barcola": P((0, (-26, 66)), (1.4, (-25, 76)), (2.4, (-22, 84)), (3.0, (-20, 88)), (4, (-19, 89))),
      "Ngumoha": P((0, (22, 76)), (2.4, (12, 88)), (3.2, (3, 93)), (3.6, (1, 95)), (4, (0.6, 96))),
      "Isak": P((0, (0, 84)), (4, (-2, 92))), "Wirtz": P((0, (4, 78)), (4, (5, 86))), "Szoboszlai": P((0, (-6, 72)), (4, (-6, 80)))}
BE = [(0, "Barcola"), (3.0, "Barcola"), (3.45, "Ngumoha"), (3.6, "Ngumoha"), (3.9, (0.4, 105.3))]

# ---------------- F · 37,5–: plano general de fondo para los goles, el dato, la cita y la clasificación
FU = {k: S(*v) for k, v in {"Lammens": (0, 101), "Dorgu": (-20, 89), "L. Martínez": (-9, 91), "Maguire": (0, 92),
      "De Ligt": (9, 91), "Dalot": (20, 89), "Mainoo": (-7, 82), "Tielemans": (2, 82), "Fernandes": (11, 80),
      "Cunha": (0, 70)}.items()}
FL = {k: S(*v) for k, v in {"Alisson": (0, 14), "Araujo": (-21, 62), "Van Dijk": (2, 52), "Jacquet": (-10, 52),
      "Kerkez": (21, 62), "Szoboszlai": (4, 70), "Mac Allister": (-5, 68), "Wirtz": (1, 78), "Barcola": (-25, 76),
      "Ngumoha": (25, 76), "Isak": (0, 84)}.items()}
BF = [(0, (0, 52.5))]

# (t0, t1, jugadores United, jugadores Liverpool, balón); tiempo local = tiempo de escena - t0
SEG = [(0.0, 8.5, AU, AL, BA), (8.5, 15.5, BU, BL, BB), (15.5, 28.5, CU, CL, BC), (28.5, 33.5, DU, DL, BD),
       (33.5, 37.5, EU, EL, BE), (37.5, 99.0, FU, FL, BF)]

CAMK = [
    (0.0,  dict(el=12, d=55,  tx=0,   tz=58, az=-30, cy=940)),
    (2.5,  dict(el=20, d=85,  tx=0,   tz=62, az=-10, cy=930)),
    (3.2,  dict(el=50, d=170, tx=0,   tz=70, az=4,   cy=900)),
    (6.4,  dict(el=44, d=140, tx=0,   tz=78, az=16,  cy=905)),
    (8.5,  dict(el=40, d=120, tx=0,   tz=70, az=-20, cy=915)),
    (11.6, dict(el=30, d=80,  tx=0,   tz=80, az=-6,  cy=925)),
    (13.3, dict(el=22, d=52,  tx=0,   tz=88, az=8,   cy=940)),
    (15.4, dict(el=24, d=56,  tx=0,   tz=88, az=18,  cy=938)),
    (15.5, dict(el=52, d=165, tx=0,   tz=80, az=0,   cy=900)),
    (19.0, dict(el=46, d=130, tx=0,   tz=86, az=-14, cy=905)),
    (22.5, dict(el=36, d=100, tx=0,   tz=90, az=10,  cy=915)),
    (28.4, dict(el=40, d=115, tx=0,   tz=88, az=24,  cy=910)),
    (28.5, dict(el=26, d=62,  tx=16,  tz=80, az=48,  cy=930)),
    (31.2, dict(el=22, d=50,  tx=8,   tz=92, az=26,  cy=940)),
    (33.4, dict(el=24, d=54,  tx=4,   tz=94, az=14,  cy=938)),
    (33.5, dict(el=28, d=66,  tx=-14, tz=74, az=-44, cy=928)),
    (36.0, dict(el=22, d=48,  tx=-4,  tz=90, az=-20, cy=940)),
    (37.4, dict(el=24, d=52,  tx=0,   tz=92, az=-8,  cy=938)),
    (37.5, dict(el=56, d=180, tx=0,   tz=60, az=-10, cy=900)),
    (END,  dict(el=50, d=160, tx=0,   tz=62, az=10,  cy=900)),
]
HEAD = [
    (2.6,  "LIVERPOOL 4-0 UNITED · 22 NOV", "El debut de", "Pochettino"),
    (8.5,  "CLAVE 1 · LA DECISIÓN", "De Ligt y Yoro,", "pareja nueva"),
    (15.5, "CLAVE 2 · CON DIEZ", "Cinco atrás", "y sin salida"),
    (28.5, "CLAVE 3 · LOS COSTADOS", "Uno contra uno", "en las bandas"),
    (37.5, "LOS GOLES", "Cuatro del Liverpool,", "cero del United"),
]
SUBS = [
    (0.5, 2.6, "…en el primer partido de *Pochettino*"),
    (2.8, 5.4, "Maguire, *al banquillo*"),
    (5.4, 8.3, "Centrales: *De Ligt* y *Yoro*"),
    (8.7, 11.0, "De Ligt no era titular en Premier *desde 2025*"),
    (11.0, 13.2, "Un balón largo y *Isak se escapa*"),
    (13.4, 15.3, "*Roja* a Yoro en el *minuto 8*"),
    (15.7, 18.2, "Entra Maguire: *cinco atrás*"),
    (18.2, 21.0, "El United *no pasa del medio campo*"),
    (21.0, 24.3, "*28* remates del Liverpool · *10* del United"),
    (28.7, 31.0, "Ngumoha, 18 años, *desborda a Dalot*"),
    (31.0, 33.3, "Centro de Ngumoha y *Wirtz, de volea: 2-0*"),
    (33.7, 35.7, "*Barcola* gana la carrera a L. Martínez"),
    (35.7, 37.3, "*Ngumoha* la empuja: *3-0*"),
]
SHOW = [((5.4, 8.3), {"De Ligt", "Yoro"}), ((8.8, 10.9), {"De Ligt"}), ((11.0, 13.2), {"Isak"}),
        ((13.2, 15.0), {"Yoro"}), ((16.0, 18.4), {"Maguire"}), ((28.8, 31.3), {"Ngumoha", "Dalot"}),
        ((31.3, 33.3), {"Wirtz"}), ((33.8, 35.8), {"Barcola", "L. Martínez"}), ((35.8, 37.3), {"Ngumoha"})]
FOCUS = [(8.8, 10.7, {"De Ligt"}), (11.6, 13.2, {"Isak"}), (29.5, 31.2, {"Ngumoha"}), (34.0, 35.7, {"Barcola"}),
         (36.4, 37.3, {"Ngumoha"})]
TAGS = [(13.2, 14.6, "Yoro", "ROJA", RED), (16.6, 18.6, "Maguire", "ENTRA · 22'", BLU)]
LOWER = [(3.2, 8.2, "Mauricio Pochettino", "Su primer partido en el United", None, 1210),
         (16.0, 19.0, "Harry Maguire", "Entra en el minuto 22", None, 1210),
         (29.0, 31.6, "Rio Ngumoha", "Extremo del Liverpool", "18 años", 1210)]
GOAL1, GOAL2 = 32.45, 37.2
SCORE = [(28.7, GOAL1, 1, 0, "13'"), (GOAL1, 33.5, 2, 0, "13'"), (33.6, GOAL2, 2, 0, "66'"), (GOAL2, 37.5, 3, 0, "66'")]
GOALS = [(GOAL1, "2-0", "Wirtz · 13'"), (GOAL2, "3-0", "Ngumoha · 66'")]
GOALLIST = [("10'", "Szoboszlai, de falta directa"), ("13'", "Wirtz, de volea, centro de Ngumoha"),
            ("66'", "Ngumoha, asistencia de Barcola"), ("82'", "Muñoz, de Wirtz")]
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
            return lerp2(pa, pb, ease(u) if not far else u), .25 + (5.5 if far else 0) * u * (1 - u)
    h = B[-1][1]; return at(h, lt), .25
def cspeed(t, dt=1 / 30):
    a = C.camkeys(CAMK, t); b = C.camkeys(CAMK, max(0, t - dt))
    k = -a.pos[1] / a.f[1]; g = a.pos + a.f * k
    pa = a.P(g[0], g[2]); pb = b.P(g[0], g[2])
    return math.hypot(pa[0] - pb[0], pa[1] - pb[1]) / 2 / 40
def alpha_of(s, n, t):
    if s is SEG[2] and n == "Maguire": return ease((t - 16.3) / .7)          # entra en el 22'
    if s is SEG[1] and n == "Yoro": return 1 - ease((t - 14.7) / .7)         # se va expulsado
    return 1.0

def compose(t): return scene(t, t)

def scene(t, r):
    global VIG
    if VIG is None: VIG = C.vignette()
    b = Image.new("RGBA", (W2, H2), (*BG, 255)); cam = C.camkeys(CAMK, min(t, END))
    C.pitch(b, cam)
    s = seg_at(t); t0s, t1s = s[0], s[1]; lt = t - t0s
    fade = (ease(lt / .2) if t0s > 0 else 1.0) * (1 - ease((t - t1s + .2) / .2) if t1s < 99 else 1.0)
    if s is SEG[1] and 10.9 < t < 13.3:                                       # la espalda de la pareja de centrales
        C.zone(b, cam, [(-12, 80), (12, 80), (12, 96), (-12, 96)], (240, 72, 72),
               ease((t - 10.9) / .4) * (1 - ease((t - 13.0) / .3)), 28)
    if s is SEG[2] and 15.9 < t < 20.5:                                       # el United, metido en su último tercio
        C.zone(b, cam, [(-34, 84), (34, 84), (34, 105), (-34, 105)], YEL, ease((t - 15.9) / .4) * (1 - ease((t - 20.2) / .3)), 20)
    if s is SEG[2] and 20.7 < t < 24.4:                                       # NUEVO: mapa de calor de toques en el área
        C.heatmap(b, cam, HEAT, (255, 96, 56), ease((t - 20.7) / .5) * (1 - ease((t - 24.1) / .35)))
    if s is SEG[0] and 5.4 < t < 8.4:                                         # la pareja de centrales, sin referencias
        C.link(b, cam, posx(s, "De Ligt", lt), posx(s, "Yoro", lt), YEL, ease((t - 5.6) / .5), (1 - ease((t - 8.1) / .3)) * fade)
    if s is SEG[1] and 9.3 < t < 11.3:                                        # el balón largo al centro
        C.arrow(b, cam, (-24, 42), (0, 79), YEL, ease((t - 9.3) / .6), 1 - ease((t - 10.9) / .3))
    if s is SEG[3] and 31.4 < t < 32.5:                                       # el centro raso de Ngumoha
        C.arrow(b, cam, (22.5, 89.5), (-0.4, 96), YEL, ease((t - 31.4) / .5), 1 - ease((t - 32.2) / .3))
    if s is SEG[4] and 36.2 < t < 37.3:                                       # el pase de Barcola
        C.arrow(b, cam, (-20, 88), (1, 95), YEL, ease((t - 36.2) / .4), 1 - ease((t - 37.0) / .25))
    people = [(n, MUN, True) for n in s[2]] + [(n, LIV, False) for n in s[3]]
    def depth(p): x, z = posx(s, p[0], lt); return -(cam.P(x, z)[2])
    for n, col, dark in people:
        pts = [posx(s, n, max(0.0, lt - .07 * k)) for k in range(9, -1, -1)]
        if abs(pts[0][0] - pts[-1][0]) + abs(pts[0][1] - pts[-1][1]) > 1.6:
            C.trail(b, cam, pts, col, a=fade * alpha_of(s, n, t))
    for f0, f1, names in FOCUS:
        if f0 <= t < f1:
            for n in names:
                if n in s[2] or n in s[3]:
                    x, z = posx(s, n, lt); C.glow_ring(b, cam, x, z, 2.6 + .3 * math.sin(t * 6), YEL, fade * alpha_of(s, n, t))
    for n, col, dark in sorted(people, key=depth):
        x, z = posx(s, n, lt); na = 0.0
        for (s0, s1), names in SHOW:
            if s0 <= t < s1 and n in names: na = ease((t - s0) / .3) * (1 - ease((t - s1 + .3) / .3))
        nm = n if n[0].isupper() else None
        a = fade * alpha_of(s, n, t)
        C.player(b, cam, x, z, col, None, nm, a, 0.0, dark, na * a)
    for t0, t1, n, txt, col in TAGS:
        if t0 <= t < t1 and (n in s[2] or n in s[3]):
            x, z = posx(s, n, lt)
            C.tag3d(b, cam, x, z, txt, col, ease((t - t0) / .25) * (1 - ease((t - t1 + .25) / .25)) * alpha_of(s, n, t))
    bts = [ball_at(s, max(0.0, lt - .04 * k)) for k in range(8, -1, -1)]
    if abs(bts[0][0][0] - bts[-1][0][0]) + abs(bts[0][0][1] - bts[-1][0][1]) > 2:
        C.ball_trail(b, cam, [(p[0], p[1], y) for p, y in bts], fade)
    (bx, bz), by = ball_at(s, lt)
    if fade > .5 and t < 37.5: C.ballp(b, cam, bx, bz, by)
    b = C.motion_blur(b, cspeed(min(t, END)) if t < END else 0)
    b.alpha_composite(VIG)
    if t < 2.6:
        sh_ = Image.new("RGBA", b.size, (0, 0, 0, 0)); a_ = int(150 * (1 - ease((t - 2.2) / .4)))
        ImageDraw.Draw(sh_).rectangle((0, 640 * 2, W2, 1080 * 2), fill=(*BG, a_)); b.alpha_composite(sh_.filter(ImageFilter.GaussianBlur(60)))
    C.bigtitle(b, t, 2.6, "Cambió la defensa", "y duró 8 minutos")
    if 2.4 < t < 39.9: C.headline(b, t, HEAD)
    if t < 37.4: C.subs(b, t, SUBS)
    for l in LOWER: C.lower_third(b, t, *l)
    for t0, t1, h, a, mn in SCORE: C.scoreboard(b, t, t0, t1, "LIV", "MUN", h, a, mn)
    for tg, txt, sub in GOALS: C.flash(b, t, tg, txt, sub)
    b = b.convert("RGB").convert("RGBA")
    for tw in [g[0] for g in GOALS] + [13.3]: C.white_flash(b, t, tw)
    C.redcard(b, t, 13.3, 1.9, "ROJA EN EL 8'", "Yoro, último defensor")
    C.statbars(b, t, 24.5, 28.5, "LO QUE NO DICE EL MARCADOR", "LIVERPOOL", "UNITED", LIV, MUN,
               [("Remates", 28, 10, "28", "10"), ("Tiros a puerta", 11, 3, "11", "3"),
                ("Posesión", 64, 36, "64 %", "36 %")])
    C.factlist(b, t, 37.6, 40.6, "LOS CUATRO GOLES", GOALLIST, y=560)
    C.counter(b, t, 40.6, 43.4, 34, "goles · todas las competiciones", 42.4, "peor de las 5 grandes ligas")
    C.quote(b, t, 43.4, 45.8, "Para mí fue una situación completamente injusta.", "MAURICIO POCHETTINO")
    C.table(b, t, 45.8, END, [(4, "Liverpool", 21, False), (19, "Man. United", 8, True)], "PREMIER · TRAS LA JORNADA 11")
    if t >= END: C.endcard(b, t - END, "¿Era el día", "de sentar a Maguire?", "Te leo en comentarios")
    for tw in [g[0] for g in GOALS] + [13.3]: b = C.shake(b, t, tw)
    return finish(b.convert("RGB"))

if __name__ == "__main__":
    out = sys.argv[1]
    if "--sheet" in sys.argv:
        ts = [float(x) for x in sys.argv[sys.argv.index("--sheet") + 1:]]
        ims = [scene(t, t).resize((540, 960)) for t in ts]
        sh = Image.new("RGB", (540 * len(ims), 960)); [sh.paste(im, (540 * i, 0)) for i, im in enumerate(ims)]; sh.save(out, quality=85)
    else:
        sfx = out + ".sfx.wav"
        C.sfx_track(sfx, TOTAL, whooshes=[2.5, 3.2, 6.4, 8.5, 11.6, 15.4, 15.5, 19.0, 24.4, 28.4, 28.5, 33.4, 33.5, 37.5, 40.5, 43.3, 45.7, 48.1],
                    hits=[13.3, GOAL1, GOAL2, 42.4])
        C.encode(compose, TOTAL, out, os.path.join(ROOT, "music", "okay_for_now-televisions.mp3"), sfx)
