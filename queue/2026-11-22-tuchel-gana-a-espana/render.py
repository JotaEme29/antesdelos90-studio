"""Cine: 'Así se le gana a la campeona del mundo' — España 2-3 Inglaterra (Nations League, Metropolitano, 15-11-2026)
y el cruce de cuartos con la Francia de Zidane (sorteo del 20-11-2026). Fuentes en meta.json.
Uso: python queue/2026-11-22-tuchel-gana-a-espana/render.py salida.mp4 [--sheet t1 t2 ...]"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "engine"))
from PIL import Image
from flat import W2, H2, BG, YEL, WHT, ease, lerp2, finish
import cine as C

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
ESP = (200, 16, 46); ENG = (236, 239, 244); FRA = (24, 52, 140)
SLOW0, SLOW1, SLOWF = 23.0, 24.2, 0.4
END = 45.5; SCENE_TOTAL = 49.5
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

# x: -34..34 (+x a la derecha con az=0) · z: 0 portería de Inglaterra, 105 portería de España.
# España ataca hacia z=0 (su banda derecha es x<0); Inglaterra ataca hacia z=105.
def P(*k): return list(k)

# ---------------- S1 · 0–20.6: salida de España y presión al hombre de Inglaterra (primeros minutos)
S1E = {
    "Simón":     P((0, (0, 101))),
    "Cubarsí":   P((0, (-10, 95)), (1.2, (-12, 93)), (6, (-13, 93))),
    "Laporte":   P((0, (10, 95)), (7.0, (13, 92)), (12, (12, 91))),
    "latD":      P((0, (-27, 86)), (8, (-28, 82))),
    "Cucurella": P((0, (27, 86)), (8, (28, 80))),
    "Zubimendi": P((0, (-5, 84)), (10.8, (-3, 83)), (12.4, (2, 80)), (14.0, (2, 80)), (15.0, (0, 82))),
    "Fabián":    P((0, (8, 78)), (11, (9, 77)), (13, (9, 76))),
    "Merino":    P((0, (-2, 68)), (12, (-3, 70)), (15, (0, 74))),
    "Lamine":    P((0, (-28, 62)), (12, (-27, 64)), (15, (-24, 70))),
    "Baena":     P((0, (26, 62)), (12, (25, 64)), (15, (22, 70))),
    "Oyarzabal": P((0, (0, 56)), (14, (0, 58)), (16, (-2, 64))),
}
S1I = {
    "Trafford":  P((0, (0, 7))),
    "Kane":      P((0, (1, 87)), (7.6, (2, 88)), (9.4, (8, 90)), (12, (9, 89)), (14.4, (6, 86))),
    "Rice":      P((0, (-1, 79)), (10.8, (1, 78)), (12.4, (6, 76.5)), (13.4, (4.4, 79)), (14.2, (3.6, 79.6)), (15, (3, 78))),
    "Anderson":  P((0, (12, 74)), (11, (13, 73.5)), (13, (12, 75)), (14.6, (10, 74))),
    "Bellingham":P((0, (-7, 72)), (12.6, (-6, 74)), (13.8, (-1.6, 80.6)), (15, (-2, 80))),
    "der":       P((0, (19, 82)), (9.4, (20, 84)), (14, (22, 84))),
    "izq":       P((0, (-19, 84)), (9.4, (-20, 84)), (14, (-18, 86))),
    "White":     P((0, (24, 58)), (14, (25, 60))),
    "Konsa":     P((0, (8, 52)), (14, (7, 54))),
    "Quansah":   P((0, (-8, 52)), (14, (-7, 54))),
    "Hall":      P((0, (-25, 58)), (12, (-25, 60)), (15, (-23, 66))),
}
B1 = [(0, "Simón"), (0.5, "Simón"), (1.3, "Cubarsí"), (3.6, "Cubarsí"), (4.4, "Simón"), (7.2, "Simón"), (8.4, "Laporte"),
      (11.6, "Laporte"), (12.5, "Zubimendi"), (13.9, "Zubimendi"), (14.2, "Rice")]

# ---------------- S2 · 20.6–27: minuto 45, pase largo de Anderson, Kane a la espalda, penalti
S2E = {
    "Simón":     P((0, (0, 101)), (24.3, (0, 104.4)), (25.4, (0, 104.4)), (25.75, (-2.2, 104.4))),
    "Cubarsí":   P((0, (-6, 64)), (21.6, (-6, 66)), (23.1, (-4.4, 86.5)), (23.5, (-5.6, 88.4)), (24.3, (-7, 87.5))),
    "Laporte":   P((0, (8, 64)), (23.2, (5, 84)), (24.3, (6, 88))),
    "latD":      P((0, (-26, 60)), (23.2, (-21, 76)), (24.3, (-14, 87))),
    "Cucurella": P((0, (26, 60)), (23.2, (19, 77)), (24.3, (13, 87.5))),
    "Zubimendi": P((0, (-2, 52)), (23.2, (-2, 68)), (24.3, (-4, 86))),
    "Fabián":    P((0, (6, 50)), (23.2, (5, 66)), (24.3, (4, 86))),
    "Merino":    P((0, (0, 42)), (24.3, (1, 84))),
    "Lamine":    P((0, (-24, 42)), (24.3, (-22, 82))),
    "Baena":     P((0, (22, 44)), (24.3, (21, 84))),
    "Oyarzabal": P((0, (2, 34)), (24.3, (-3, 80))),
}
S2I = {
    "Trafford":  P((0, (0, 6))),
    "Kane":      P((0, (-1, 62)), (21.6, (-2, 72)), (23.1, (-2, 88)), (23.5, (-2, 91)), (24.3, (0, 92.4)), (25.3, (0, 92.4)), (25.6, (0, 93.6))),
    "Anderson":  P((0, (4, 42)), (24.3, (6, 82))),
    "Rice":      P((0, (-6, 40)), (24.3, (-8, 83))),
    "Bellingham":P((0, (8, 56)), (23.2, (9, 74)), (24.3, (9, 86.5))),
    "der":       P((0, (20, 60)), (23.2, (20, 78)), (24.3, (17, 86.5))),
    "izq":       P((0, (-20, 60)), (23.2, (-17, 79)), (24.3, (-10, 87))),
    "White":     P((0, (24, 30)), (24.3, (24, 78))),
    "Konsa":     P((0, (8, 20)), (24.3, (10, 70))),
    "Quansah":   P((0, (-8, 20)), (24.3, (-10, 70))),
    "Hall":      P((0, (-24, 34)), (24.3, (-24, 76))),
}
B2 = [(20.6, "Anderson"), (21.6, "Anderson"), (23.1, (-2, 88.6)), (23.5, "Kane"), (23.9, (-2.5, 93)), (24.3, (0, 94)), (25.4, (0, 94)), (25.8, (-2.8, 105.3))]

# ---------------- S3a · 27–30.2: minuto 53, córner de Rice y cabezazo de Konsa
def box_def(dx=0):
    return {"Simón": P((0, (0, 104))), "d1": P((0, (-4 + dx, 99))), "d2": P((0, (3 + dx, 100.5))), "d3": P((0, (-9 + dx, 96))),
            "d4": P((0, (9 + dx, 97))), "d5": P((0, (0 + dx, 94))), "d6": P((0, (-14 + dx, 92))), "d7": P((0, (14 + dx, 91))),
            "d8": P((0, (-3, 82))), "d9": P((0, (8, 80))), "Oyarzabal": P((0, (0, 66)))}
S3E = box_def()
S3E["d2"] = P((0, (3, 100.5)), (28.2, (4, 100)))
S3I = {
    "Trafford": P((0, (0, 10))),
    "Rice":     P((0, (34, 105.6))),
    "Konsa":    P((0, (7, 91)), (27.6, (7, 92)), (28.5, (1.2, 99.6)), (29.4, (0.5, 101))),
    "Kane":     P((0, (-5, 95)), (28.5, (-4, 98))),
    "Bellingham": P((0, (-11, 92)), (28.5, (-9, 95))),
    "Quansah":  P((0, (4, 95)), (28.5, (6, 98))),
    "der":      P((0, (12, 88)), (28.5, (13, 93))),
    "izq":      P((0, (-17, 89))),
    "Anderson": P((0, (2, 80))),
    "White":    P((0, (22, 60))),
    "Hall":     P((0, (-22, 62))),
}
B3 = [(27.0, (33.4, 105.0)), (27.5, (33.4, 105.0)), (28.5, (1.2, 99.9)), (28.9, (-1.4, 105.3))]

# ---------------- S3b · 30.2–33: minuto 57, Bellingham al segundo palo y gol de White
S3bE = box_def(-2)
S3bE["d4"] = P((0, (7, 97)), (31.5, (8, 99)))
S3bI = {
    "Trafford": P((0, (0, 10))),
    "Bellingham": P((0, (-11, 88)), (30.9, (-10, 90))),
    "White":    P((0, (17, 88)), (31.5, (7, 99)), (32.4, (5, 101))),
    "Kane":     P((0, (-3, 95)), (31.4, (-2, 98))),
    "Konsa":    P((0, (-6, 82))),
    "izq":      P((0, (-24, 88))),
    "der":      P((0, (6, 92)), (31.4, (3, 96))),
    "Rice":     P((0, (2, 78))),
    "Anderson": P((0, (10, 80))),
    "Quansah":  P((0, (-4, 60))),
    "Hall":     P((0, (-20, 64))),
}
B3b = [(30.2, "Bellingham"), (30.95, "Bellingham"), (31.5, "White"), (31.6, "White"), (31.95, (2.6, 105.3))]

# ---------------- S4 · 33–45.5: con diez, Inglaterra atrás; Lamine a la espalda y gol de Nico Williams (75')
S4E = {
    "Simón":     P((0, (0, 100))),
    "Huijsen":   P((0, (-8, 62)), (37, (-8, 56))),
    "Laporte":   P((0, (10, 62)), (37, (10, 56))),
    "latD":      P((0, (-26, 44)), (37, (-24, 36))),
    "Cucurella": P((0, (26, 42)), (37, (24, 34))),
    "Pedri":     P((0, (4, 40)), (37, (3, 30))),
    "Fermín":    P((0, (-6, 38)), (36, (-7, 30))),
    "Lamine":    P((0, (-27, 33)), (34.8, (-25, 29)), (35.9, (-19, 13)), (37.2, (-17, 11))),
    "Nico":      P((0, (8, 26)), (35.2, (6, 18)), (36.5, (-1.5, 8)), (37.3, (-1, 5))),
    "Oyarzabal": P((0, (0, 18)), (35.6, (1, 12)), (36.5, (4, 9))),
    "Baena":     P((0, (16, 30)), (36.5, (14, 20))),
}
S4I = {
    "Trafford":  P((0, (0, 2)), (36.5, (-0.8, 2.6))),
    "Konsa":     P((0, (6, 13)), (36.4, (2, 9.5))),
    "Quansah":   P((0, (-6, 13)), (36.2, (-6, 10))),
    "White":     P((0, (17, 15)), (36.5, (12, 12))),
    "Hall":      P((0, (-21, 26)), (34.8, (-22, 24)), (36.0, (-18, 15.5))),
    "Rice":      P((0, (-4, 24)), (36.5, (-3, 17))),
    "Bellingham":P((0, (6, 25)), (36.5, (5, 18))),
    "der":       P((0, (16, 30)), (36.5, (15, 22))),
    "izq":       P((0, (-14, 28)), (36.5, (-12, 20))),
    "Kane":      P((0, (1, 42)), (37, (1, 34))),
}
B4 = [(33.0, "Fermín"), (34.1, "Fermín"), (34.9, "Lamine"), (35.95, "Lamine"), (36.5, "Nico"), (36.6, "Nico"), (36.95, (1.6, -0.4))]

SEG = [(0.0, 20.6, S1E, S1I, B1), (20.6, 27.0, S2E, S2I, B2), (27.0, 30.2, S3E, S3I, B3), (30.2, 33.0, S3bE, S3bI, B3b), (33.0, 99, S4E, S4I, B4)]
NAME = {"Simón": "Unai Simón", "Nico": "Nico Williams", "Lamine": "Lamine"}

CAMK = [
    (0.0,  dict(el=13, d=66,  tx=0,   tz=88, az=-32, cy=930)),
    (2.5,  dict(el=22, d=92,  tx=0,   tz=86, az=-12, cy=930)),
    (3.4,  dict(el=52, d=165, tx=0,   tz=76, az=0,   cy=900)),
    (6.8,  dict(el=52, d=160, tx=0,   tz=76, az=6,   cy=900)),
    (7.6,  dict(el=40, d=66,  tx=3,   tz=82, az=-58, cy=930)),
    (12.4, dict(el=40, d=60,  tx=3,   tz=80, az=-48, cy=930)),
    (13.1, dict(el=34, d=48,  tx=2,   tz=79, az=-70, cy=940)),
    (20.5, dict(el=36, d=52,  tx=2,   tz=79, az=-80, cy=940)),
    (20.6, dict(el=40, d=135, tx=0,   tz=62, az=-8,  cy=900)),
    (22.0, dict(el=34, d=105, tx=-2,  tz=76, az=-4,  cy=900)),
    (23.1, dict(el=42, d=62,  tx=-2,  tz=88, az=-38, cy=930)),
    (24.2, dict(el=42, d=58,  tx=-2,  tz=89, az=-44, cy=930)),
    (24.5, dict(el=34, d=50,  tx=0,   tz=98, az=-38, cy=940)),
    (26.9, dict(el=32, d=44,  tx=0,   tz=99, az=-30, cy=940)),
    (27.0, dict(el=30, d=72,  tx=10,  tz=96, az=-42, cy=920)),
    (28.6, dict(el=25, d=56,  tx=2,   tz=98, az=-30, cy=930)),
    (30.1, dict(el=24, d=54,  tx=2,   tz=98, az=-26, cy=930)),
    (30.3, dict(el=36, d=82,  tx=-2,  tz=94, az=22,  cy=920)),
    (32.9, dict(el=32, d=72,  tx=0,   tz=96, az=28,  cy=920)),
    (33.0, dict(el=46, d=130, tx=-6,  tz=30, az=180, cy=900)),
    (34.6, dict(el=34, d=96,  tx=-20, tz=22, az=198, cy=910)),
    (36.3, dict(el=26, d=66,  tx=-11, tz=10, az=190, cy=930)),
    (38.4, dict(el=30, d=82,  tx=-4,  tz=12, az=184, cy=920)),
    (45.5, dict(el=40, d=120, tx=0,   tz=24, az=170, cy=900)),
]
HEAD = [
    (2.6,  "ESPAÑA 2-3 INGLATERRA · 15 NOV", "43 partidos invicta…", "…hasta Tuchel"),
    (7.0,  "EL PLAN DE TUCHEL", "Presión arriba", "con parejas al hombre"),
    (12.6, "LA SALIDA DE ESPAÑA", "Cada pase,", "un rival encima"),
    (20.6, "MINUTO 45", "Pase largo de Anderson", "y Kane a la espalda"),
    (27.0, "SEGUNDA PARTE", "Dos goles en 4 minutos", "y 0-3 en el 57'"),
    (33.0, "LA REACCIÓN", "Inglaterra, con diez…", "España se queda a uno"),
]
SUBS = [
    (0.3, 2.6, "La *campeona del mundo*"),
    (2.8, 4.8, "*43 partidos* seguidos sin perder"),
    (4.8, 6.9, "hasta que llegó *Tuchel*"),
    (7.2, 9.6, "Inglaterra presiona *arriba*"),
    (9.6, 11.0, "*Rice* encima de Zubimendi"),
    (11.0, 12.6, "*Anderson* encima de Fabián"),
    (12.8, 14.2, "Cada pase, *un rival encima*"),
    (14.2, 16.9, "…y *robo* en campo de España"),
    (20.8, 22.2, "Pase largo de *Anderson*"),
    (22.2, 23.0, "*Kane* a la espalda"),
    (23.0, 24.3, "*Penalti* de *Cubarsí* sobre *Kane*"),
    (24.5, 25.8, "*Kane* no falla"),
    (27.2, 29.0, "Córner de *Rice* y cabezazo de *Konsa*"),
    (30.3, 32.0, "*Bellingham* al segundo palo: *White*"),
    (32.0, 33.0, "*0-3*"),
    (33.1, 34.5, "Roja a *Anderson* y penalti de *Oyarzabal*"),
    (34.5, 36.9, "*Lamine* gana la espalda…"),
    (36.9, 38.4, "*Nico Williams*: *2-3*"),
]
SHOW = [((7.6, 12.4), {"Rice", "Zubimendi", "Anderson", "Fabián"}),
        ((12.6, 16.9), {"Rice", "Zubimendi"}), ((20.7, 21.9), {"Anderson"}), ((21.9, 23.0), {"Kane", "Cubarsí"}),
        ((23.0, 24.3), {"Kane", "Cubarsí"}), ((24.5, 26.9), {"Kane", "Simón"}), ((27.6, 29.6), {"Konsa"}),
        ((30.3, 32.8), {"Bellingham", "White"}), ((34.4, 38.4), {"Lamine", "Nico"})]
PRESS = [(9.6, 14.0, "Rice", "Zubimendi"), (11.0, 14.0, "Anderson", "Fabián")]
FOCUS = [(12.6, 14.4, {"Zubimendi"}), (22.0, 23.6, {"Kane"}), (27.6, 28.9, {"Konsa"}), (30.9, 31.9, {"White"}), (34.8, 36.5, {"Lamine"})]
LOWER = [(9.7, 12.4, "Declan Rice", "Mediocentro", "→ marca a Zubimendi"), (20.9, 22.9, "Elliot Anderson", "Mediocentro", "→ pase largo"),
         (34.7, 36.8, "Lamine Yamal", "Extremo derecho", "→ asistencia")]
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
    """velocidad aparente de la cámara medida en el punto del suelo al que mira (no en el centro del campo)."""
    a = C.camkeys(CAMK, t); b = C.camkeys(CAMK, max(0, t - dt))
    k = -a.pos[1] / a.f[1]; g = a.pos + a.f * k
    pa = a.P(g[0], g[2]); pb = b.P(g[0], g[2])
    return math.hypot(pa[0] - pb[0], pa[1] - pb[1]) / 2 / 40

def compose(r): return scene(scene_t(r), r)

def scene(t, r):
    global VIG
    if VIG is None: VIG = C.vignette()
    b = Image.new("RGBA", (W2, H2), (*BG, 255)); cam = C.camkeys(CAMK, min(t, END))
    C.pitch(b, cam)
    s = seg_at(t); t0s, t1s = s[0], s[1]
    fade = (ease((t - t0s) / .2) if t0s > 0 else 1.0) * (1 - ease((t - t1s + .2) / .2) if t1s < 99 else 1.0)
    # zona de penalti marcada en la jugada de Kane
    if 22.6 < t < 24.4:
        C.zone(b, cam, [(-20.15, 88.5), (20.15, 88.5), (20.15, 105), (-20.15, 105)], (240, 72, 72), ease((t - 22.6) / .3) * (1 - ease((t - 24.1) / .3)), 16)
    for p0, p1, a_, q_ in PRESS:                                   # conos de presión (nuevo)
        if p0 <= t < p1 and s is SEG[0]:
            C.pressure(b, cam, posx(s, a_, t), posx(s, q_, t), (240, 72, 72), ease((t - p0) / .4) * (1 - ease((t - p1 + .3) / .3)))
    if 21.4 < t < 23.3 and s is SEG[1]:
        C.arrow(b, cam, posx(s, "Kane", 21.6), (-2, 88), YEL, ease((t - 21.4) / .5), 1 - ease((t - 23.0) / .3))
    people = [(n, ESP, True, True) for n in s[2]] + [(n, ENG, False, False) for n in s[3]]
    if s is SEG[-1]: people = [p for p in people if p[0] != "Anderson"]
    def depth(p): x, z = posx(s, p[0], t); return -(cam.P(x, z)[2])
    for n, col, dark, below in people:                             # estelas
        pts = [posx(s, n, max(t0s, t - .07 * k)) for k in range(9, -1, -1)]
        if abs(pts[0][0] - pts[-1][0]) + abs(pts[0][1] - pts[-1][1]) > 1.6: C.trail(b, cam, pts, col, a=fade)
    for f0, f1, names in FOCUS:
        if f0 <= t < f1:
            for n in names:
                x, z = posx(s, n, t); C.glow_ring(b, cam, x, z, 2.6 + .3 * math.sin(t * 6), YEL, fade)
    for n, col, dark, below in sorted(people, key=depth):
        x, z = posx(s, n, t); na = 0.0
        for (s0, s1), names in SHOW:
            if s0 <= t < s1 and n in names: na = ease((t - s0) / .3) * (1 - ease((t - s1 + .3) / .3))
        nm = NAME.get(n, n) if n[0].isupper() and n not in ("Simón",) or n == "Simón" else None
        if n in ("latD", "der", "izq") or n[:1] == "d" and n[1:].isdigit(): nm = None
        C.player(b, cam, x, z, col, None, nm, fade, 0.0, dark, na * fade, below=below)
    bts = [ball_at(s, max(t0s, t - .04 * k)) for k in range(8, -1, -1)]
    if abs(bts[0][0][0] - bts[-1][0][0]) + abs(bts[0][0][1] - bts[-1][0][1]) > 2: C.ball_trail(b, cam, [(p[0], p[1], y) for p, y in bts], fade)
    (bx, bz), by = ball_at(s, t)
    if fade > .5: C.ballp(b, cam, bx, bz, by)
    b = C.motion_blur(b, cspeed(min(t, END)) if t < END else 0)
    b.alpha_composite(VIG)
    if t < 2.6:                                                      # fondo oscuro tras el gancho para que se lea
        sh_ = Image.new("RGBA", b.size, (0, 0, 0, 0)); a_ = int(150 * (1 - ease((t - 2.2) / .4)))
        from PIL import ImageDraw as _D; _D.Draw(sh_).rectangle((0, 640 * 2, W2, 1080 * 2), fill=(*BG, a_))
        from PIL import ImageFilter as _F; b.alpha_composite(sh_.filter(_F.GaussianBlur(60)))
    C.bigtitle(b, t, 2.6, "¿Cómo ganar", "a España?")
    if 2.4 < t < 38.4: C.headline(b, t, HEAD)
    if t < 38.4: C.subs(b, t, SUBS)
    for l in LOWER: C.lower_third(b, t, *l)
    C.counter(b, t, 2.7, 6.9, 43, "PARTIDOS SIN PERDER", broken_at=5.0, broken_txt="ROTA EN MADRID")
    C.scoreboard(b, t, 20.8, 25.85, "ESP", "ING", 0, 0, "45'"); C.scoreboard(b, t, 25.85, 27.0, "ESP", "ING", 0, 1, "45'")
    C.scoreboard(b, t, 27.1, 28.95, "ESP", "ING", 0, 1, "53'"); C.scoreboard(b, t, 28.95, 30.2, "ESP", "ING", 0, 2, "53'")
    C.scoreboard(b, t, 30.3, 31.95, "ESP", "ING", 0, 2, "57'"); C.scoreboard(b, t, 31.95, 33.0, "ESP", "ING", 0, 3, "57'")
    C.scoreboard(b, t, 33.1, 34.5, "ESP", "ING", 1, 3, "65'"); C.scoreboard(b, t, 34.5, 36.95, "ESP", "ING", 1, 3, "75'")
    C.scoreboard(b, t, 36.95, 38.4, "ESP", "ING", 2, 3, "75'")
    C.flash(b, t, 14.15, "ROBO")
    C.flash(b, t, 23.5, "PENALTI")
    C.flash(b, t, 25.8, "GOL", "Kane (pen.) · 45'")
    C.flash(b, t, 28.9, "0-2", "Konsa · 53'")
    C.flash(b, t, 31.95, "0-3", "White · 57'")
    C.flash(b, t, 36.95, "2-3", "Nico Williams · 75'")
    b = b.convert("RGB").convert("RGBA")
    for tw in (23.5, 25.8, 28.9, 31.95, 36.95): C.white_flash(b, r, real_t(tw))
    C.quote(b, t, 17.0, 20.6, "En los primeros treinta minutos nos han desbordado…", "LUIS DE LA FUENTE, tras el partido")
    C.table(b, t, 38.4, 42.0, [(1, "Inglaterra", 15, False), (2, "España", 15, True)], "GRUPO A3 · EMPATE A 15: MANDA LA DIFERENCIA")
    C.versus(b, t, 42.0, END, "ESPAÑA", "FRANCIA", ESP, FRA, "CUARTOS DE LA NATIONS LEAGUE", "Campeona del mundo", "de Zidane", "Ida en España · marzo de 2027")
    if t >= END: C.endcard(b, t - END, "¿Copiará Zidane", "el plan de Tuchel?", "Cuéntamelo en comentarios")
    for tw in (5.0, 25.8, 28.9, 31.95, 36.95): b = C.shake(b, r, real_t(tw))
    return finish(b.convert("RGB"))

if __name__ == "__main__":
    out = sys.argv[1]
    if "--sheet" in sys.argv:
        ts = [float(x) for x in sys.argv[sys.argv.index("--sheet") + 1:]]
        ims = [scene(t, real_t(t)).resize((540, 960)) for t in ts]
        sh = Image.new("RGB", (540 * len(ims), 960)); [sh.paste(im, (540 * i, 0)) for i, im in enumerate(ims)]; sh.save(out, quality=85)
    else:
        sfx = out + ".sfx.wav"
        C.sfx_track(sfx, TOTAL, whooshes=[real_t(x) for x in (2.5, 6.9, 12.5, 16.9, 20.5, 26.9, 30.1, 32.9, 38.3, 41.9, 45.4)],
                    hits=[5.0, 14.15, real_t(23.5), real_t(25.8), real_t(28.9), real_t(31.95), real_t(36.95)])
        C.encode(compose, TOTAL, out, os.path.join(ROOT, "music", "dance_with_you-everet_almond.mp3"), sfx)
