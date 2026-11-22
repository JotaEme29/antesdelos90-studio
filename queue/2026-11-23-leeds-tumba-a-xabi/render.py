"""Cine: 'El Leeds corrió 6 km más' — Chelsea 1-4 Leeds (Premier League, jornada 11, Stamford Bridge, 21-11-2026).
Fuentes en meta.json. Uso: python queue/2026-11-23-leeds-tumba-a-xabi/render.py salida.mp4 [--sheet t1 t2 ...]
Nota: las posiciones en el campo son una recreación ilustrativa; solo se rotula lo que está en las fuentes."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "engine"))
from PIL import Image, ImageDraw, ImageFilter
from flat import W2, H2, BG, YEL, WHT, ease, lerp2, finish
import cine as C

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
CHE = (10, 72, 160); LEE = (238, 240, 244); RED = (230, 40, 50)
SLOW0, SLOW1, SLOWF = 31.7, 32.9, 0.4
END = 49.3; SCENE_TOTAL = END + 3.6
EXTRA = (SLOW1 - SLOW0) / SLOWF - (SLOW1 - SLOW0); TOTAL = SCENE_TOTAL + EXTRA
def scene_t(r):
    if r < SLOW0: return r
    if r < SLOW0 + (SLOW1 - SLOW0) / SLOWF: return SLOW0 + (r - SLOW0) * SLOWF
    return r - EXTRA
def real_t(sc): return sc if sc < SLOW0 else (SLOW0 + (sc - SLOW0) / SLOWF if sc < SLOW1 else sc + EXTRA)

def track(keys, t):
    if t <= keys[0][0]: return keys[0][1]
    for (t0, a), (t1, b) in zip(keys, keys[1:]):
        if t0 <= t <= t1: return lerp2(a, b, ease((t - t0) / max(1e-6, t1 - t0)))
    return keys[-1][1]
def P(*k): return list(k)
def S(x, z): return P((0, (x, z)))

# x: -34..34 · z: 0 portería del Leeds (Trafford), 105 portería del Chelsea (Martínez).
# El Leeds ataca hacia z=105 (su derecha es x>0: Bogle); el Chelsea ataca hacia z=0 (su derecha es x<0: Estêvão).

# ---------------- A · 0–9: el Chelsea saca desde atrás y el Leeds aprieta arriba
AC = {"Martínez": S(0, 103), "Fofana": P((0, (-10, 95)), (2, (-12, 93))), "Colwill": P((0, (10, 95)), (4.5, (13, 92))),
      "l1": S(-26, 86), "l2": P((0, (26, 86)), (6, (27, 82))), "Caicedo": P((0, (-3, 82)), (6.4, (-1, 79))), "Lavia": S(7, 78),
      "Palmer": P((0, (-2, 66)), (7, (-3, 70))), "Estêvão": S(-25, 62), "Rogers": S(23, 63), "Emegha": S(0, 55)}
AL = {"Trafford": S(0, 8), "Calvert-Lewin": P((0, (1, 84)), (1.6, (-5, 89)), (4.4, (2, 89)), (5.6, (9, 90.5))),
      "Okafor": P((0, (-6, 82)), (2.2, (-9, 88)), (6, (-7, 86))), "Tanaka": P((0, (-4, 74)), (6.6, (-2, 78))),
      "Longstaff": P((0, (14, 78)), (5.4, (19, 82))), "Ampadu": P((0, (3, 66)), (7, (4, 70))), "Bogle": P((0, (24, 66)), (6, (25, 72))),
      "Gudmundsson": P((0, (-24, 66)), (6, (-25, 70))), "Justin": P((0, (10, 50)), (7, (11, 55))), "Elvedi": P((0, (0, 48)), (7, (0, 53))),
      "Muharemović": P((0, (-10, 50)), (7, (-10, 55)))}
BA = [(0, "Martínez"), (0.6, "Martínez"), (1.4, "Fofana"), (2.6, "Fofana"), (3.4, "Martínez"), (4.4, "Martínez"), (5.3, "Colwill"),
      (6.3, "Colwill"), (7.2, "Caicedo"), (9, "Caicedo")]

# ---------------- B · 9–17: se lesiona Caicedo, entra Henderson; Rogers conduce y Emegha marca (25')
BC = {"Martínez": S(0, 100), "Fofana": S(-9, 62), "Colwill": S(9, 62), "l1": P((0, (-24, 50)), (14, (-22, 44))), "l2": P((0, (24, 52)), (14, (22, 46))),
      "Caicedo": S(0, 54), "Henderson": P((0, (33, 56)), (11.0, (33, 56)), (12.3, (1, 52))), "Lavia": P((0, (6, 47)), (11.6, (5, 46))),
      "Palmer": P((0, (-4, 38)), (14, (-5, 30))), "Estêvão": P((0, (-22, 32)), (14, (-20, 22))),
      "Rogers": P((0, (12, 42)), (11.6, (11, 40)), (13.6, (6, 29)), (14.4, (5, 27))),
      "Emegha": P((0, (2, 30)), (13.2, (1, 26)), (14.3, (-1, 15.5)), (14.8, (-1.3, 13.6)))}
BL = {"Trafford": P((0, (0, 2.5)), (14.8, (-0.6, 3.2))), "Justin": P((0, (10, 20)), (14.3, (6, 16))), "Elvedi": P((0, (0, 19)), (14.4, (1.8, 14.5))),
      "Muharemović": P((0, (-10, 20)), (14.4, (-7, 15))), "Bogle": P((0, (24, 28)), (14, (21, 24))), "Gudmundsson": P((0, (-24, 28)), (14, (-22, 22))),
      "Ampadu": P((0, (2, 36)), (13.6, (4, 31))), "Tanaka": P((0, (-6, 38)), (14, (-5, 32))), "Longstaff": P((0, (12, 38)), (13, (10, 34))),
      "Calvert-Lewin": S(2, 52), "Okafor": S(-8, 50)}
BB = [(9.0, "Lavia"), (10.6, "Lavia"), (11.6, "Rogers"), (13.6, "Rogers"), (14.3, (-0.8, 15.8)), (14.5, "Emegha"), (14.8, "Emegha"), (15.3, (-2.6, -0.4))]

# ---------------- C · 17–21: balón suelto en el área y Okafor empata (28')
CC = {"Martínez": P((0, (0, 103.5)), (18.8, (-1.4, 103.6))), "Fofana": P((0, (-6, 97)), (18.6, (-5, 96))), "Colwill": P((0, (3, 98)), (17.9, (4, 97.5))),
      "l1": S(-14, 95), "l2": P((0, (13, 95)), (17.5, (16, 94))), "Henderson": P((0, (0, 87)), (18.6, (-2, 89))), "Lavia": S(7, 86), "Rogers": S(-20, 84)}
CL = {"Okafor": P((0, (-8, 86)), (17.4, (-7, 87.5)), (18.5, (-4.2, 92))), "Calvert-Lewin": P((0, (0, 92)), (17.9, (-1, 92.6))), "Bogle": P((0, (20, 91)), (17.2, (21, 92))),
      "Longstaff": S(10, 89), "Tanaka": S(-2, 79), "Ampadu": S(4, 72), "Gudmundsson": S(-22, 82)}
BCb = [(17.0, "Okafor"), (17.4, "Okafor"), (17.9, "Calvert-Lewin"), (18.0, "Calvert-Lewin"), (18.5, (-4, 92.6)), (18.7, "Okafor"), (18.85, "Okafor"), (19.2, (-3, 105.3))]

# ---------------- D · 21–25.8: la presión del Leeds en campo del Chelsea (robo y 9 recuperaciones en el último tercio)
DC = {"Martínez": S(0, 103), "Fofana": P((0, (-10, 95)), (23, (-13, 93))), "Colwill": P((0, (10, 95)), (22, (13, 93))),
      "l1": S(-25, 86), "l2": S(25, 86), "Henderson": P((0, (-2, 82)), (23.2, (0, 85)), (24.2, (0.6, 85.4))), "Lavia": S(7, 78),
      "Palmer": P((0, (-2, 66)), (24.2, (-2, 72))), "Estêvão": S(-24, 64), "Rogers": S(22, 64), "Emegha": S(0, 56)}
DL = {"Trafford": S(0, 10), "Calvert-Lewin": P((0, (2, 84)), (22.4, (10, 90.6))), "Okafor": P((0, (-6, 84)), (23.4, (-9, 90)), (25, (-4, 92))),
      "Tanaka": P((0, (-4, 74)), (23.4, (-1.2, 83)), (24.0, (0, 84)), (24.8, (-1, 87.5))), "Longstaff": P((0, (14, 78)), (23, (17, 85))),
      "Bogle": P((0, (24, 70)), (23, (24, 80))), "Gudmundsson": P((0, (-24, 70)), (23, (-24, 80))), "Ampadu": P((0, (2, 64)), (24, (2, 74))),
      "Justin": P((0, (10, 52)), (24, (10, 60))), "Elvedi": P((0, (0, 50)), (24, (0, 58))), "Muharemović": P((0, (-10, 52)), (24, (-10, 60)))}
BD = [(21.0, "Martínez"), (21.4, "Martínez"), (22.0, "Colwill"), (22.7, "Colwill"), (23.5, "Henderson"), (23.9, "Henderson"),
      (24.05, "Tanaka"), (24.8, "Tanaka"), (25.3, "Okafor"), (26, "Okafor")]

# ---------------- E · 30.5–33.8: disparo de Bogle, le da en el brazo a Rogers (53')
EC = {"Martínez": S(0, 104), "Fofana": S(-3, 97), "Colwill": S(4, 98), "l1": S(-11, 96), "l2": P((0, (15, 95)), (31.6, (14, 94))),
      "Rogers": P((0, (6, 90)), (31.7, (8.6, 91.6))), "Henderson": P((0, (0, 87)), (31.5, (2, 88))), "Lavia": S(-6, 89)}
EL = {"Bogle": P((0, (17, 83)), (31.2, (14.6, 86.6)), (31.75, (13.4, 87.6))), "Tanaka": P((0, (1, 82)), (31, (0, 83))),
      "Calvert-Lewin": S(-2, 98), "Okafor": S(-9, 94), "Longstaff": S(20, 92), "Ampadu": S(4, 76)}
BE = [(30.5, "Tanaka"), (30.6, "Tanaka"), (31.3, "Bogle"), (31.75, "Bogle"), (32.15, (9.2, 91.9)), (32.7, (11.5, 89.5)), (34, (12, 89))]

# ---------------- E2 · 33.8–37.5: penalti de Calvert-Lewin (1-2)
E2C = {"Martínez": P((0, (0, 104.4)), (35.35, (0, 104.4)), (35.7, (-2.4, 104.4))), "Colwill": S(-9, 87.5), "Fofana": S(7, 87.8), "Henderson": S(-3, 86),
       "Rogers": S(13, 86)}
E2L = {"Calvert-Lewin": P((0, (-1.5, 90.5)), (34.6, (-1.5, 90.5)), (35.25, (-0.3, 93.4))), "Okafor": S(-6, 87), "Bogle": S(10, 87.2), "Tanaka": S(2, 85.6)}
BE2 = [(33.8, (0, 94)), (35.3, (0, 94)), (35.7, (2.7, 105.3))]

# ---------------- F · 37.5–39.6: centro raso y Okafor repite (58')
FC = {"Martínez": P((0, (0, 104)), (38.6, (0.8, 104))), "Fofana": P((0, (2, 99)), (38.3, (4, 98.5))), "Colwill": P((0, (-6, 97)), (38.4, (-4, 96))),
      "l2": P((0, (16, 98)), (37.8, (20, 99.5))), "Henderson": P((0, (-5, 88)), (38.5, (-4, 91))), "l1": S(-14, 95)}
FL = {"cen": P((0, (23, 100)), (37.8, (24, 101))), "Okafor": P((0, (-5, 87)), (38.45, (-2.2, 93))), "Calvert-Lewin": P((0, (2, 96)), (38.3, (4, 99.5))),
      "Longstaff": S(10, 90)}
BF = [(37.5, "cen"), (37.85, "cen"), (38.15, (11, 97)), (38.5, "Okafor"), (38.62, "Okafor"), (38.95, (1.8, 105.3))]

# ---------------- F2 · 39.6–41.8: en el descuento, Aaronson ante Martínez (1-4)
F2C = {"Martínez": P((0, (0, 104)), (40.6, (0.4, 99.5))), "Colwill": P((0, (-7, 74)), (41.2, (-3, 92))), "Fofana": P((0, (9, 78)), (41.2, (5, 94))),
       "l1": P((0, (-18, 76)), (41.2, (-12, 88)))}
F2L = {"Aaronson": P((0, (-14, 74)), (40.3, (-7, 86)), (40.9, (0.8, 95.2))), "pas": S(-6, 68), "Calvert-Lewin": P((0, (-10, 76)), (41.2, (-8, 88)))}
BF2 = [(39.6, "pas"), (39.75, "pas"), (40.35, "Aaronson"), (40.9, "Aaronson"), (41.35, (0.6, 105.3))]

# ---------------- G · 41.8–: plano general de fondo para cita y consecuencias
GC = {k: S(*v) for k, v in {"Martínez": (0, 103), "Fofana": (-10, 92), "Colwill": (10, 92), "l1": (-25, 84), "l2": (25, 84), "Henderson": (-3, 76),
      "Lavia": (6, 74), "Palmer": (-2, 62), "Estêvão": (-24, 58), "Rogers": (22, 58), "Emegha": (0, 54)}.items()}
GL = {k: S(*v) for k, v in {"Trafford": (0, 4), "Justin": (10, 20), "Elvedi": (0, 18), "Muharemović": (-10, 20), "Bogle": (24, 32), "Gudmundsson": (-24, 32),
      "Ampadu": (3, 34), "Tanaka": (-6, 38), "Longstaff": (12, 40), "Calvert-Lewin": (2, 48), "Okafor": (-8, 46)}.items()}
BG_ = [(41.8, (0, 52.5))]

SEG = [(0.0, 9.0, AC, AL, BA), (9.0, 17.0, BC, BL, BB), (17.0, 21.0, CC, CL, BCb), (21.0, 30.5, DC, DL, BD), (30.5, 33.8, EC, EL, BE),
       (33.8, 37.5, E2C, E2L, BE2), (37.5, 39.6, FC, FL, BF), (39.6, 41.8, F2C, F2L, BF2), (41.8, 99, GC, GL, BG_)]
NAME = {"Calvert-Lewin": "Calvert-Lewin", "Martínez": "E. Martínez"}

CAMK = [
    (0.0,  dict(el=12, d=60,  tx=0,  tz=92, az=-34, cy=930)),
    (2.5,  dict(el=22, d=90,  tx=0,  tz=88, az=-14, cy=930)),
    (3.2,  dict(el=50, d=165, tx=0,  tz=72, az=0,   cy=900)),
    (6.0,  dict(el=50, d=158, tx=0,  tz=74, az=8,   cy=900)),
    (6.6,  dict(el=36, d=78,  tx=-2, tz=84, az=-52, cy=930)),
    (8.9,  dict(el=36, d=72,  tx=-2, tz=83, az=-44, cy=930)),
    (9.0,  dict(el=42, d=96,  tx=4,  tz=52, az=196, cy=910)),
    (11.8, dict(el=38, d=80,  tx=4,  tz=50, az=186, cy=910)),
    (12.4, dict(el=30, d=72,  tx=2,  tz=28, az=168, cy=930)),
    (14.6, dict(el=24, d=52,  tx=0,  tz=16, az=158, cy=940)),
    (16.9, dict(el=24, d=48,  tx=0,  tz=12, az=150, cy=940)),
    (17.0, dict(el=28, d=60,  tx=2,  tz=94, az=-26, cy=930)),
    (20.9, dict(el=26, d=52,  tx=0,  tz=97, az=-42, cy=935)),
    (21.0, dict(el=48, d=150, tx=0,  tz=78, az=0,   cy=900)),
    (22.6, dict(el=40, d=96,  tx=2,  tz=84, az=24,  cy=910)),
    (25.8, dict(el=38, d=88,  tx=0,  tz=86, az=34,  cy=910)),
    (30.4, dict(el=38, d=88,  tx=0,  tz=86, az=40,  cy=910)),
    (30.5, dict(el=34, d=70,  tx=8,  tz=90, az=58,  cy=930)),
    (31.7, dict(el=28, d=46,  tx=10, tz=90, az=70,  cy=940)),
    (32.9, dict(el=26, d=42,  tx=10, tz=90, az=78,  cy=940)),
    (33.7, dict(el=26, d=42,  tx=10, tz=90, az=80,  cy=940)),
    (33.8, dict(el=22, d=44,  tx=0,  tz=98, az=38,  cy=940)),
    (37.4, dict(el=20, d=40,  tx=0,  tz=99, az=24,  cy=945)),
    (37.5, dict(el=36, d=74,  tx=6,  tz=94, az=42,  cy=925)),
    (39.5, dict(el=32, d=62,  tx=4,  tz=96, az=30,  cy=930)),
    (39.6, dict(el=30, d=92,  tx=0,  tz=82, az=-16, cy=920)),
    (41.7, dict(el=26, d=60,  tx=0,  tz=95, az=-24, cy=935)),
    (41.8, dict(el=56, d=175, tx=0,  tz=56, az=-12, cy=900)),
    (END,  dict(el=50, d=165, tx=0,  tz=56, az=12,  cy=900)),
]
HEAD = [
    (2.6,  "CHELSEA 1-4 LEEDS · 21 NOV", "El Leeds gana allí", "por primera vez desde 1999"),
    (9.0,  "PRIMERA PARTE", "Se lesiona Caicedo…", "…y aun así, 1-0"),
    (17.0, "MINUTO 28", "Tres minutos después,", "el empate"),
    (21.0, "LA CLAVE", "El Leeds aprieta", "en campo del Chelsea"),
    (30.5, "MINUTO 53", "Disparo de Bogle", "y mano de Rogers"),
    (37.5, "SE DESMORONA", "Okafor repite", "y Aaronson cierra"),
]
SUBS = [
    (0.5, 2.6, "…que el Chelsea de *Xabi Alonso*"),
    (2.8, 5.0, "*1-4* en Stamford Bridge"),
    (5.0, 7.0, "El Leeds no ganaba allí *desde 1999*"),
    (7.0, 8.9, "Xabi: «la primera *media hora* fue buena»"),
    (9.2, 11.6, "*Caicedo* se lesiona y se va"),
    (12.4, 14.4, "*Rogers* conduce y filtra…"),
    (14.4, 16.9, "*Emegha:* *1-0*"),
    (17.2, 18.6, "Pared con *Calvert-Lewin…*"),
    (18.6, 20.9, "*Okafor:* *1-1*"),
    (21.2, 23.0, "El Leeds presiona *arriba*"),
    (23.0, 25.6, "…y roba en *campo del Chelsea*"),
    (30.6, 31.75, "Disparo de *Bogle…*"),
    (31.75, 33.7, "…al brazo de *Rogers*"),
    (33.9, 35.6, "Penalti tras revisar el *VAR*"),
    (35.7, 37.4, "*Calvert-Lewin:* *1-2*"),
    (37.6, 39.5, "*Okafor* repite: *1-3*"),
    (39.7, 41.7, "En el descuento, *Aaronson:* *1-4*"),
]
SHOW = [((0.6, 8.8), {"Calvert-Lewin", "Okafor"}), ((11.4, 12.4), {"Henderson"}), ((12.4, 15.3), {"Rogers", "Emegha"}),
        ((17.2, 19.2), {"Okafor", "Calvert-Lewin"}),
        ((30.6, 33.7), {"Bogle", "Rogers"}), ((33.9, 35.7), {"Calvert-Lewin", "Martínez"}), ((37.6, 38.95), {"Okafor"}),
        ((39.7, 41.35), {"Aaronson", "Martínez"})]
PRESS = [(1.2, 3.0, "Calvert-Lewin", "Fofana"), (4.6, 6.6, "Calvert-Lewin", "Colwill"),
         (21.6, 23.0, "Calvert-Lewin", "Colwill"), (22.9, 24.1, "Tanaka", "Henderson"), (22.9, 24.1, "Okafor", "Fofana")]
FOCUS = [(9.4, 11.0, {"Caicedo"}), (12.4, 14.3, {"Rogers"}), (14.3, 15.3, {"Emegha"}), (18.5, 19.2, {"Okafor"}),
         (31.6, 33.7, {"Rogers"}), (34.6, 35.7, {"Calvert-Lewin"}), (38.3, 38.95, {"Okafor"}), (40.4, 41.35, {"Aaronson"})]
TAGS = [(9.5, 11.4, "Caicedo", "LESIÓN", RED), (32.15, 33.7, "Rogers", "MANO", RED)]
LOWER = [(5.0, 8.8, "Xabi Alonso", "Entrenador del Chelsea", None, 1210), (12.5, 14.4, "Emmanuel Emegha", "Delantero del Chelsea", "· primera titularidad", 1300),
         (21.2, 23.4, "Daniel Farke", "Entrenador del Leeds", None, 1210)]
SCORE = [(12.4, 15.3, 0, 0, "25'"), (15.3, 17.0, 1, 0, "25'"), (17.0, 19.2, 1, 0, "28'"), (19.2, 21.0, 1, 1, "28'"),
         (30.5, 35.7, 1, 1, "53'"), (35.7, 37.5, 1, 2, "53'"), (37.5, 38.95, 1, 2, "58'"), (38.95, 39.6, 1, 3, "58'"),
         (39.6, 41.35, 1, 3, "90+'"), (41.35, 41.8, 1, 4, "90+'")]
GOALS = [(15.3, "1-0", "Emegha · 25'"), (19.2, "1-1", "Okafor · 28'"), (35.7, "1-2", "Calvert-Lewin (pen.) · 53'"),
         (38.95, "1-3", "Okafor · 58'"), (41.35, "1-4", "Aaronson · descuento")]
VIG = None

def seg_at(t):
    for s in SEG:
        if s[0] <= t < s[1]: return s
    return SEG[-1]
def posx(s, name, t):
    d = s[2] if name in s[2] else s[3]; return track(d[name], t)
def ball_at(s, t):
    B = s[4]
    def at(h, tt): return posx(s, h, tt) if isinstance(h, str) else h
    if t <= B[0][0]: return at(B[0][1], t), .25
    for (t0, a), (t1, h) in zip(B, B[1:]):
        if t0 <= t < t1:
            if isinstance(a, str) and a == h: return posx(s, a, t), .25
            pa, pb = at(a, t0), at(h, t1); u = (t - t0) / max(1e-6, t1 - t0)
            far = (abs(pa[0] - pb[0]) + abs(pa[1] - pb[1])) > 18
            return lerp2(pa, pb, ease(u) if not far else u), .25 + (5.5 if far else 0) * u * (1 - u)
    h = B[-1][1]; return at(h, t), .25
def cspeed(t, dt=1 / 30):
    a = C.camkeys(CAMK, t); b = C.camkeys(CAMK, max(0, t - dt))
    k = -a.pos[1] / a.f[1]; g = a.pos + a.f * k
    pa = a.P(g[0], g[2]); pb = b.P(g[0], g[2])
    return math.hypot(pa[0] - pb[0], pa[1] - pb[1]) / 2 / 40
def alpha_of(s, n, t):
    if s is SEG[1] and n == "Caicedo": return 1 - ease((t - 10.9) / .8)
    if s is SEG[1] and n == "Henderson": return ease((t - 10.9) / .6)
    return 1.0

def compose(r): return scene(scene_t(r), r)

def scene(t, r):
    global VIG
    if VIG is None: VIG = C.vignette()
    b = Image.new("RGBA", (W2, H2), (*BG, 255)); cam = C.camkeys(CAMK, min(t, END))
    C.pitch(b, cam)
    s = seg_at(t); t0s, t1s = s[0], s[1]
    fade = (ease((t - t0s) / .2) if t0s > 0 else 1.0) * (1 - ease((t - t1s + .2) / .2) if t1s < 99 else 1.0)
    if 21.2 < t < 25.8:                                              # último tercio del Chelsea
        C.zone(b, cam, [(-34, 70), (34, 70), (34, 105), (-34, 105)], YEL, ease((t - 21.2) / .4) * (1 - ease((t - 25.5) / .3)), 22)
    if 33.9 < t < 35.8:
        C.zone(b, cam, [(-20.15, 88.5), (20.15, 88.5), (20.15, 105), (-20.15, 105)], (240, 72, 72), ease((t - 33.9) / .3) * (1 - ease((t - 35.5) / .3)), 16)
    for p0, p1, a_, q_ in PRESS:
        if p0 <= t < p1 and a_ in s[3] and q_ in s[2]:
            C.pressure(b, cam, posx(s, a_, t), posx(s, q_, t), (240, 72, 72), ease((t - p0) / .4) * (1 - ease((t - p1 + .3) / .3)))
    if s is SEG[1] and 11.8 < t < 13.8:                              # conducción de Rogers
        C.arrow(b, cam, posx(s, "Rogers", 11.7), (6, 29), YEL, ease((t - 11.8) / .7), 1 - ease((t - 13.5) / .3))
    if s is SEG[7] and 39.6 < t < 40.5:
        C.arrow(b, cam, (-14, 74), (-7, 86), YEL, ease((t - 39.6) / .5), 1 - ease((t - 40.2) / .3))
    people = [(n, CHE, True, False) for n in s[2]] + [(n, LEE, False, False) for n in s[3]]
    def depth(p): x, z = posx(s, p[0], t); return -(cam.P(x, z)[2])
    for n, col, dark, below in people:
        pts = [posx(s, n, max(t0s, t - .07 * k)) for k in range(9, -1, -1)]
        if abs(pts[0][0] - pts[-1][0]) + abs(pts[0][1] - pts[-1][1]) > 1.6: C.trail(b, cam, pts, col, a=fade * alpha_of(s, n, t))
    for f0, f1, names in FOCUS:
        if f0 <= t < f1:
            for n in names:
                if n in s[2] or n in s[3]:
                    x, z = posx(s, n, t); C.glow_ring(b, cam, x, z, 2.6 + .3 * math.sin(t * 6), YEL, fade * alpha_of(s, n, t))
    for n, col, dark, below in sorted(people, key=depth):
        x, z = posx(s, n, t); na = 0.0
        for (s0, s1), names in SHOW:
            if s0 <= t < s1 and n in names: na = ease((t - s0) / .3) * (1 - ease((t - s1 + .3) / .3))
        nm = NAME.get(n, n) if n[0].isupper() else None
        a = fade * alpha_of(s, n, t)
        C.player(b, cam, x, z, col, None, nm, a, 0.0, dark, na * a, below=below)
    for t0, t1, n, txt, col in TAGS:
        if t0 <= t < t1 and (n in s[2] or n in s[3]):
            x, z = posx(s, n, t); C.tag3d(b, cam, x, z, txt, col, ease((t - t0) / .25) * (1 - ease((t - t1 + .25) / .25)) * alpha_of(s, n, t))
    bts = [ball_at(s, max(t0s, t - .04 * k)) for k in range(8, -1, -1)]
    if abs(bts[0][0][0] - bts[-1][0][0]) + abs(bts[0][0][1] - bts[-1][0][1]) > 2: C.ball_trail(b, cam, [(p[0], p[1], y) for p, y in bts], fade)
    (bx, bz), by = ball_at(s, t)
    if fade > .5 and t < 41.8: C.ballp(b, cam, bx, bz, by)
    b = C.motion_blur(b, cspeed(min(t, END)) if t < END else 0)
    b.alpha_composite(VIG)
    if t < 2.6:
        sh_ = Image.new("RGBA", b.size, (0, 0, 0, 0)); a_ = int(150 * (1 - ease((t - 2.2) / .4)))
        ImageDraw.Draw(sh_).rectangle((0, 640 * 2, W2, 1080 * 2), fill=(*BG, a_)); b.alpha_composite(sh_.filter(ImageFilter.GaussianBlur(60)))
    C.bigtitle(b, t, 2.6, "El Leeds corrió", "6 km más…")
    if 2.4 < t < 41.8: C.headline(b, t, HEAD)
    if t < 41.8: C.subs(b, t, SUBS)
    for l in LOWER: C.lower_third(b, t, *l)
    for t0, t1, h, a, mn in SCORE: C.scoreboard(b, t, t0, t1, "CHE", "LEE", h, a, mn)
    C.flash(b, t, 24.05, "ROBO")
    C.flash(b, t, 33.0, "PENALTI", "tras revisión del VAR")
    for tg, txt, sub in GOALS: C.flash(b, t, tg, txt, sub)
    b = b.convert("RGB").convert("RGBA")
    for tw in [g[0] for g in GOALS] + [33.0]: C.white_flash(b, r, real_t(tw))
    C.statbars(b, t, 25.8, 30.5, "LO QUE NO DICE EL MARCADOR", "LEEDS", "CHELSEA", LEE, CHE,
               [("Recuperaciones en el último tercio", 9, 1, "9", "1"), ("Distancia recorrida", 6, 0, "+6 km", "")])
    C.quote(b, t, 41.9, 45.4, "Estamos en un momento frágil.", "XABI ALONSO, tras el partido")
    C.factlist(b, t, 45.4, END, "LA RESACA EN EL CHELSEA", [("8.º", "Cae a la octava plaza de la Premier"),
               ("3 de 4", "Tres derrotas en sus últimos cuatro partidos de liga"), ("20", "goles encajados en 11 jornadas")])
    if t >= END: C.endcard(b, t - END, "¿Culpa de Xabi", "o de la plantilla?", "Te leo en comentarios")
    for tw in [g[0] for g in GOALS] + [33.0]: b = C.shake(b, r, real_t(tw))
    return finish(b.convert("RGB"))

if __name__ == "__main__":
    out = sys.argv[1]
    if "--sheet" in sys.argv:
        ts = [float(x) for x in sys.argv[sys.argv.index("--sheet") + 1:]]
        ims = [scene(t, real_t(t)).resize((540, 960)) for t in ts]
        sh = Image.new("RGB", (540 * len(ims), 960)); [sh.paste(im, (540 * i, 0)) for i, im in enumerate(ims)]; sh.save(out, quality=85)
    else:
        sfx = out + ".sfx.wav"
        C.sfx_track(sfx, TOTAL, whooshes=[real_t(x) for x in (2.5, 6.4, 8.9, 12.3, 16.9, 20.9, 25.7, 30.4, 33.7, 37.4, 39.5, 41.7, 45.3, 49.2)],
                    hits=[15.3, 19.2, 24.05, real_t(33.0), real_t(35.7), real_t(38.95), real_t(41.35)])
        C.encode(compose, TOTAL, out, os.path.join(ROOT, "music", "glitter_and_gold-patrick_patrikios.mp3"), sfx)
