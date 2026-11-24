"""Cine: 'Antes de la roja, ya ganaba 2-0' — Brentford 4-0 Everton (Premier League, lunes 23-11-2026,
Gtech Community Stadium). La noche del récord de Moyes (593 partidos en el Everton). Tres claves; los goles, al final.
Uso: python queue/2026-11-24-brentford-everton/render.py salida.mp4 [--sheet t1 t2 ...]
Experimento de la semana: ≤ 42 s y la jugada clave en movimiento desde el primer fotograma (sin título sobre campo vacío).
Nota: las posiciones son una recreación ilustrativa (chip 'Recreación'); solo se rotula lo que está en las fuentes.
Nuevo en el motor (v3.5): stopwatch (cronómetro de 90' que corre de un minuto a otro) y spark (chispazo del desvío)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "engine"))
from PIL import Image, ImageDraw, ImageFilter
from flat import W2, H2, BG, YEL, WHT, ease, lerp2, finish
import cine as C

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
BRE = (214, 28, 38); EVE = (28, 74, 178); RED = (230, 40, 50)
END = 38.4; TOTAL = END + 3.6

def track(keys, t):
    if t <= keys[0][0]: return keys[0][1]
    for (t0, a), (t1, b) in zip(keys, keys[1:]):
        if t0 <= t <= t1: return lerp2(a, b, ease((t - t0) / max(1e-6, t1 - t0)))
    return keys[-1][1]
def P(*k): return list(k)
def S(x, z): return P((0, (x, z)))

# x: -34..34 · z: 0 portería del Brentford (Kelleher), 105 portería del Everton (Pickford). El Brentford ataca hacia z=105.
# Nombres en minúscula = jugador sin rotular (no se nombra a quien las fuentes no citan).

# ---------------- A · 0–10: 23' · balón a la espalda, Everton no lo despeja, Anthony raso, Lewis-Potter, desvío en Branthwaite
AB = {"medio": P((0, (4, 52)), (1.0, (4, 55)), (10, (6, 66))), "Anthony": P((0, (-22, 72)), (1.2, (-20, 80)), (2.4, (-17, 87.5)), (5.4, (-15, 90.5)), (10, (-14, 92))),
      "Lewis-Potter": P((0, (6, 74)), (2.4, (5, 82)), (5.4, (0, 90)), (6.1, (-1.8, 93.2)), (10, (-2, 95))),
      "Wilson": P((0, (-4, 76)), (2.4, (-5, 84)), (5.4, (-6, 92)), (10, (-6, 95))),
      "Damsgaard": P((0, (16, 66)), (10, (14, 80))), "Kayode": P((0, (27, 60)), (10, (26, 72))),
      "b1": P((0, (-10, 56)), (10, (-10, 64)))}
AE = {"Pickford": P((0, (0, 102)), (6.4, (-0.8, 102.5)), (7.0, (3.5, 103)), (10, (5, 103.4))),
      "Tarkowski": P((0, (-6, 80)), (1.6, (-11, 84)), (2.3, (-15, 87)), (5.4, (-13, 90)), (10, (-11, 93))),
      "Branthwaite": P((0, (5, 80)), (2.4, (3, 87)), (5.4, (2, 94)), (6.3, (1.8, 96.6)), (10, (-0.8, 97.6))),
      "O'Brien": P((0, (-20, 78)), (2.4, (-19, 85)), (5.4, (-18, 89)), (10, (-17, 91))),
      "e1": P((0, (20, 78)), (5.4, (12, 90)), (10, (10, 93))), "Barry": P((0, (2, 58)), (10, (1, 70))),
      "Dewsbury-Hall": P((0, (-6, 66)), (10, (-4, 80))), "e2": P((0, (10, 66)), (10, (8, 82))),
      "e3": P((0, (-18, 64)), (10, (-16, 78))), "e4": P((0, (22, 64)), (10, (20, 78)))}
BA = [(0, "medio"), (0.85, "medio"), (2.4, (-17, 88)), (2.5, "Anthony"), (5.5, "Anthony"), (6.1, "Lewis-Potter"),
      (6.25, "Lewis-Potter"), (6.5, (1.2, 96.3)), (6.95, (-1.6, 105.3)), (10, (-1.8, 105.6))]
SHOT1, DEF1, GOAL1 = 6.25, 6.5, 6.95

# ---------------- B · 10–19,5: 25' · falta de Damsgaard al área, primer remate bloqueado, rechace, desvío en Barry
BB_ = {"Damsgaard": S(-22, 76), "Lewis-Potter": P((0, (-2, 88)), (2.6, (-1, 88)), (3.3, (1.5, 93)), (4.3, (1.6, 92)), (9.5, (1.5, 93))),
       "Wilson": P((0, (4, 88)), (3.3, (5, 95)), (9.5, (5, 96))), "Janelt": P((0, (-8, 87)), (3.3, (-6, 94)), (9.5, (-6, 95))),
       "Yarmoliuk": P((0, (9, 86)), (3.3, (9, 93)), (9.5, (9, 94))), "Anthony": P((0, (-14, 86)), (9.5, (-13, 90))),
       "b2": S(14, 70)}
BE_ = {"Pickford": P((0, (0, 103)), (4.2, (-1, 103)), (4.7, (2.5, 103.4)), (9.5, (2.5, 103.4))),
       "Tarkowski": P((0, (4, 91)), (3.3, (3.4, 95)), (3.6, (3.2, 95.2)), (9.5, (3.2, 96))),
       "Barry": P((0, (-3, 92)), (4.0, (-1.6, 95.4)), (4.35, (-1.4, 96.4)), (9.5, (-1.4, 96.5))),
       "Branthwaite": P((0, (6, 91)), (3.3, (6, 95)), (9.5, (6, 96))), "O'Brien": P((0, (-5, 91)), (3.3, (-4, 95)), (9.5, (-4, 96))),
       "e1": P((0, (-9, 91)), (9.5, (-8, 95))), "e2": P((0, (10, 90)), (9.5, (10, 94))),
       "Dewsbury-Hall": P((0, (-17, 82)), (9.5, (-15, 86))), "e3": S(-20, 80), "e4": S(2, 80)}
BB = [(0, "Damsgaard"), (2.0, "Damsgaard"), (3.15, "Lewis-Potter"), (3.3, "Lewis-Potter"), (3.55, (2.6, 94.8)),
      (4.2, "Lewis-Potter"), (4.3, "Lewis-Potter"), (4.45, (-1.0, 96.1)), (4.85, (-3.0, 105.3)), (9.5, (-3.2, 105.6))]
FK, BLOCK, SHOT2, DEF2, GOAL2 = 2.0, 3.55, 4.3, 4.45, 4.85

# ---------------- C · 19,5–29,5: 40' Tarkowski expulsado (VAR) · con diez, Janelt desde lejos (67')
CB = {"Yarmoliuk": P((0, (-4, 50)), (1.0, (-4.2, 54)), (1.25, (-4.0, 54.6)), (4.0, (-4.0, 54.6))),
      "Damsgaard": S(12, 50), "Lewis-Potter": S(-24, 56), "Kayode": S(26, 50), "Wilson": S(-3, 64), "Janelt": S(-10, 44), "b2": S(8, 38)}
CE = {"Tarkowski": P((0, (4, 58)), (1.0, (-1.4, 55.0)), (4.0, (2.6, 56.0))), "Barry": S(-4, 46), "Dewsbury-Hall": S(-12, 54),
      "Branthwaite": S(-8, 62), "O'Brien": S(-22, 60), "e1": S(14, 60), "e2": S(8, 52), "e3": S(-20, 50), "e4": S(22, 52)}
CB2 = {"Janelt": P((0, (-12, 64)), (2.4, (-6, 70)), (3.6, (-3.5, 73)), (6, (-3, 74))), "Damsgaard": P((0, (12, 78)), (6, (10, 80))),
       "Lewis-Potter": P((0, (-24, 84)), (6, (-23, 88))), "Kayode": P((0, (26, 80)), (6, (25, 84))),
       "Wilson": P((0, (0, 92)), (6, (-1, 94))), "Anthony": P((0, (-16, 76)), (6, (-14, 82))), "Yarmoliuk": P((0, (4, 66)), (6, (5, 70)))}
CE2 = {"Pickford": P((0, (0, 103)), (3.9, (0.2, 103)), (4.4, (2.2, 103.5)), (6, (2.2, 103.5))),
       "Branthwaite": P((0, (-4, 94)), (6, (-3, 95))), "O'Brien": P((0, (-14, 93)), (6, (-13, 94))),
       "e1": P((0, (6, 94)), (6, (5, 95))), "e5": P((0, (16, 93)), (6, (15, 94))),
       "Dewsbury-Hall": P((0, (-8, 84)), (6, (-6, 86))), "e2": P((0, (2, 85)), (6, (2, 87))),
       "e3": P((0, (-20, 86)), (6, (-19, 88))), "e4": P((0, (20, 86)), (6, (19, 88))), "Barry": P((0, (8, 80)), (6, (7, 84)))}
BC = [(0, "Yarmoliuk"), (1.2, "Yarmoliuk"), (4, "Yarmoliuk")]
BC2 = [(0, "Damsgaard"), (0.9, "Damsgaard"), (2.3, "Anthony"), (2.6, "Anthony"), (3.55, "Janelt"), (3.75, "Janelt"),
       (4.5, (2.0, 105.3)), (6, (2.2, 105.6))]
SHOT3, GOAL3 = 23.5 + 3.75, 23.5 + 4.5

# ---------------- D · 29,5–: plano general para los goles, el dato y la clasificación
DB = {k: S(*v) for k, v in {"Kelleher": (0, 4), "Kayode": (24, 30), "b3": (6, 22), "b4": (-6, 22), "Lewis-Potter": (-24, 32),
      "Janelt": (-6, 42), "Yarmoliuk": (6, 44), "Damsgaard": (14, 56), "Anthony": (-16, 58), "Wilson": (0, 66), "Carvalho": (8, 64)}.items()}
DE = {k: S(*v) for k, v in {"Pickford": (0, 101), "e1": (-18, 86), "Branthwaite": (-6, 88), "O'Brien": (6, 88), "e5": (18, 86),
      "Dewsbury-Hall": (-10, 76), "e2": (0, 74), "e3": (10, 76), "Grealish": (-16, 64), "Barry": (2, 62)}.items()}

# (t0, t1, Brentford, Everton, balón)
SEG = [(0.0, 10.0, AB, AE, BA), (10.0, 19.5, BB_, BE_, BB), (19.5, 23.5, CB, CE, BC), (23.5, 29.5, CB2, CE2, BC2),
       (29.5, 99.0, DB, DE, [(0, (0, 52.5))])]

CAMK = [
    (0.0,  dict(el=26, d=66,  tx=-4,  tz=72, az=-14, cy=1180)),   # baja, detrás del pase largo, girando
    (2.3,  dict(el=28, d=72,  tx=-10, tz=82, az=-24, cy=1150)),
    (2.5,  dict(el=48, d=150, tx=-4,  tz=86, az=-8,  cy=900)),   # general: la espalda de la línea
    (5.3,  dict(el=40, d=118, tx=-6,  tz=90, az=-20, cy=910)),
    (5.6,  dict(el=44, d=46,  tx=-1,  tz=94, az=-12, cy=900)),   # a pie de área, lateral, para el desvío
    (9.9,  dict(el=46, d=50,  tx=-1,  tz=95, az=8,   cy=900)),
    (10.0, dict(el=55, d=170, tx=0,   tz=82, az=6,   cy=900)),
    (11.9, dict(el=50, d=150, tx=-4,  tz=86, az=-6,  cy=900)),
    (12.0, dict(el=30, d=78,  tx=-8,  tz=88, az=-44, cy=920)),   # desde detrás del lanzador
    (13.2, dict(el=46, d=48,  tx=0,   tz=94, az=-6,  cy=900)),
    (15.0, dict(el=44, d=46,  tx=0,   tz=95, az=10,  cy=900)),   # contraplano del rechace
    (19.4, dict(el=46, d=52,  tx=0,   tz=95, az=18,  cy=900)),
    (19.5, dict(el=24, d=58,  tx=0,   tz=55, az=12,  cy=935)),   # zoom a la entrada de Tarkowski
    (23.4, dict(el=28, d=60,  tx=0,   tz=56, az=10,  cy=930)),
    (23.5, dict(el=52, d=160, tx=0,   tz=82, az=-4,  cy=900)),   # con diez: todo el bloque
    (26.0, dict(el=36, d=96,  tx=-2,  tz=82, az=-18, cy=915)),
    (27.4, dict(el=40, d=56,  tx=-1,  tz=90, az=10,  cy=900)),   # cámara baja hacia la portería: el disparo llega
    (29.4, dict(el=32, d=58,  tx=0,   tz=96, az=18,  cy=900)),
    (29.5, dict(el=56, d=180, tx=0,   tz=58, az=-10, cy=900)),
    (END,  dict(el=50, d=160, tx=0,   tz=62, az=12,  cy=900)),
]
HEAD = [
    (2.4,  "BRENTFORD 4-0 EVERTON · LUNES 23", "Clave 1:", "la espalda"),
    (10.0, "CLAVE 2 · 2 MINUTOS DESPUÉS", "El balón", "parado"),
    (19.5, "CLAVE 3 · MINUTO 40", "Con diez", "y 2-0 abajo"),
    (29.5, "LA CONSECUENCIA", "La noche del récord", "de Moyes"),
]
SUBS = [
    (2.6, 4.2, "Balón a la *espalda de la línea*"),
    (4.2, 5.7, "Y el Everton *no lo despeja*"),
    (5.7, 7.3, "*Anthony*, raso y de primeras"),
    (7.3, 9.8, "Remata *Lewis-Potter*: desvío en *Branthwaite*"),
    (12.0, 13.7, "Balón parado: *Damsgaard* la mete al área"),
    (13.7, 15.1, "Primer remate, *bloqueado*"),
    (15.1, 17.4, "Nadie saca el *rechace*: desvío en *Barry*"),
    (17.4, 19.3, "*Lewis-Potter*, otra vez: *2-0*"),
    (19.7, 21.6, "Entrada de *Tarkowski* a *Yarmoliuk*"),
    (21.6, 23.3, "El *VAR* cambia la amarilla *por roja*"),
    (23.7, 26.2, "Con diez, el Everton *se hunde*"),
    (26.2, 27.6, "y *Janelt* tira *desde muy lejos*"),
    (27.8, 29.3, "A la escuadra: *3-0*"),
]
SHOW = [((2.6, 5.6), {"Anthony", "Tarkowski"}), ((5.4, 6.45), {"Lewis-Potter"}),
        ((7.2, 9.8), {"Branthwaite"}), ((12.0, 13.6), {"Damsgaard"}), ((13.6, 15.0), {"Lewis-Potter"}),
        ((16.1, 17.6), {"Barry"}), ((19.6, 21.4), {"Tarkowski"}), ((25.6, 28.0), {"Janelt"})]
FOCUS = [(2.4, 5.5, {"Anthony"}), (5.9, 6.6, {"Lewis-Potter"}), (12.0, 12.8, {"Damsgaard"}), (13.2, 14.4, {"Lewis-Potter"}),
         (25.8, 27.3, {"Janelt"})]
TAGS = [(21.4, 23.3, "Tarkowski", "VAR · ROJA", RED)]
LOWER = []
SCORE = [(7.6, 10.0, 1, 0, "23'"), (12.0, 10 + GOAL2, 1, 0, "25'"), (10 + GOAL2, 19.5, 2, 0, "25'"),
         (24.0, GOAL3, 2, 0, "67'"), (GOAL3, 29.5, 3, 0, "67'")]
GOALS = [(GOAL1, "1-0", "Lewis-Potter · 23'"), (10 + GOAL2, "2-0", "Lewis-Potter · 25'"), (GOAL3, "3-0", "Janelt · 67'")]
GOALLIST = [("23'", "Lewis-Potter: pase raso de Anthony y desvío en Branthwaite"),
            ("25'", "Lewis-Potter: balón parado, rechace y desvío en Barry"),
            ("67'", "Janelt, desde lejos, a la escuadra (ya 11 contra 10)"),
            ("90'", "Carvalho, que salió del banquillo, tras un córner")]
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
            if s is SEG[3] and t0 == 3.75: y = .3 + 2.0 * u                 # el disparo de Janelt sube a la escuadra
            if s is SEG[1] and t0 == 2.0: y = .25 + 4.0 * u * (1 - u)       # la falta, bombeada al área
            return lerp2(pa, pb, ease(u) if not far else u), y
    h = B[-1][1]; return at(h, lt), (2.3 if s is SEG[3] else .25)
def cspeed(t, dt=1 / 30):
    a = C.camkeys(CAMK, t); b = C.camkeys(CAMK, max(0, t - dt))
    k = -a.pos[1] / a.f[1]; g = a.pos + a.f * k
    pa = a.P(g[0], g[2]); pb = b.P(g[0], g[2])
    return math.hypot(pa[0] - pb[0], pa[1] - pb[1]) / 2 / 40
def alpha_of(s, n, t):
    if s is SEG[2] and n == "Tarkowski": return 1 - ease((t - 23.0) / .45)   # se va expulsado
    return 1.0

def compose(t): return scene(t, t)

def scene(t, r):
    global VIG
    if VIG is None: VIG = C.vignette()
    b = Image.new("RGBA", (W2, H2), (*BG, 255)); cam = C.camkeys(CAMK, min(t, END))
    C.pitch(b, cam)
    s = seg_at(t); t0s, t1s = s[0], s[1]; lt = t - t0s
    fade = (ease(lt / .2) if t0s > 0 else 1.0) * (1 - ease((t - t1s + .2) / .2) if t1s < 99 else 1.0)
    if s is SEG[0] and 1.0 < t < 5.6:                                         # la espalda de la línea del Everton
        C.zone(b, cam, [(-24, 83), (8, 83), (8, 96), (-24, 96)], (240, 72, 72), ease((t - 1.0) / .4) * (1 - ease((t - 5.3) / .3)), 30)
    if s is SEG[0] and 0.6 < t < 2.6:                                         # el pase largo
        C.arrow(b, cam, (4, 55), (-17, 88), YEL, ease((t - 0.6) / .6), 1 - ease((t - 2.3) / .3))
    if s is SEG[0] and 5.0 < t < 6.2:                                         # el pase raso de Anthony
        C.arrow(b, cam, (-15, 90.5), (-1.8, 93.2), YEL, ease((t - 5.0) / .4), 1 - ease((t - 5.9) / .3))
    if s is SEG[1] and 11.0 < t < 12.4:                                       # la falta, antes de sacarla
        C.arrow(b, cam, (-22, 76), (1.5, 93), YEL, ease((t - 11.0) / .6), 1 - ease((t - 12.1) / .3), y=0)
    if s is SEG[1] and 14.0 < t < 15.6:                                       # el rechace que nadie despeja
        C.zone(b, cam, [(-4, 89), (6, 89), (6, 97), (-4, 97)], (240, 72, 72), ease((t - 14.0) / .3) * (1 - ease((t - 15.3) / .3)), 34)
    if s is SEG[3] and 24.2 < t < 27.4:                                       # la frontal, libre con diez
        C.zone(b, cam, [(-12, 70), (10, 70), (10, 80), (-12, 80)], YEL, ease((t - 24.2) / .4) * (1 - ease((t - 27.1) / .3)), 26)
    people = [(n, BRE, False) for n in s[2]] + [(n, EVE, True) for n in s[3]]
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
    if fade > .5 and t < 29.5: C.ballp(b, cam, bx, bz, by)
    C.spark(b, cam, 1.2, 96.3, t, DEF1)                                      # NUEVO: el desvío en Branthwaite
    C.spark(b, cam, 2.6, 94.8, t, 10 + BLOCK, col=WHT)                       # el primer remate, bloqueado
    C.spark(b, cam, -1.0, 96.1, t, 10 + DEF2)                                 # el desvío en Barry
    b = C.motion_blur(b, cspeed(min(t, END)) if t < END else 0)
    b.alpha_composite(VIG)
    if t < 2.4:
        sh_ = Image.new("RGBA", b.size, (0, 0, 0, 0)); a_ = int(130 * (1 - ease((t - 2.0) / .4)))
        ImageDraw.Draw(sh_).rectangle((0, 640 * 2, W2, 1080 * 2), fill=(*BG, a_)); b.alpha_composite(sh_.filter(ImageFilter.GaussianBlur(60)))
    C.bigtitle(b, t, 2.4, "Antes de la roja,", "ya ganaba 2-0")
    if 0.1 < t < 29.4: C.rec_tag(b, a=ease((t - 0.1) / .3) * (1 - ease((t - 29.1) / .3)) * (0 if 10.0 <= t < 11.95 else 1))
    if 2.2 < t < 38.0: C.headline(b, t, HEAD)
    if t < 29.4: C.subs(b, t, SUBS)
    for l in LOWER: C.lower_third(b, t, *l)
    for t0, t1, h, a, mn in SCORE: C.scoreboard(b, t, t0, t1, "BRE", "EVE", h, a, mn)
    for tg, txt, sub in GOALS: C.flash(b, t, tg, txt, sub)
    C.stopwatch(b, t, 10.0, 12.0, 23, 25, "2 MINUTOS", "del 1-0 al 2-0")   # NUEVO: cronómetro de partido
    b = b.convert("RGB").convert("RGBA")
    for tw in [g[0] for g in GOALS] + [21.4]: C.white_flash(b, t, tw)
    C.factlist(b, t, 29.5, 33.2, "LOS CUATRO GOLES", GOALLIST, y=560)
    C.counter(b, t, 33.2, 36.2, 593, "partidos: récord en el Everton", 35.15, "y acabó 4-0")
    C.table(b, t, 36.2, END, [(6, "Brentford", 17, True), (9, "Everton", 16, False)], "PREMIER · TRAS LA JORNADA 11")
    if t >= END: C.endcard(b, t - END, "¿Lo decidió la roja", "o el minuto 25?", "Te leo en comentarios")
    for tw in [g[0] for g in GOALS] + [21.4]: b = C.shake(b, t, tw)
    return finish(b.convert("RGB"))

if __name__ == "__main__":
    out = sys.argv[1]
    if "--sheet" in sys.argv:
        ts = [float(x) for x in sys.argv[sys.argv.index("--sheet") + 1:]]
        ims = [scene(t, t).resize((540, 960)) for t in ts]
        sh = Image.new("RGB", (540 * len(ims), 960)); [sh.paste(im, (540 * i, 0)) for i, im in enumerate(ims)]; sh.save(out, quality=85)
    else:
        sfx = out + ".sfx.wav"
        C.sfx_track(sfx, TOTAL, whooshes=[2.4, 5.6, 10.0, 12.0, 15.0, 19.5, 23.5, 27.4, 29.5, 33.2, 36.2, 38.3],
                    hits=[GOAL1, 10 + GOAL2, GOAL3, 21.4, 35.15])
        C.encode(compose, TOTAL, out, os.path.join(ROOT, "music", "got_it-cory_barker.mp3"), sfx)
