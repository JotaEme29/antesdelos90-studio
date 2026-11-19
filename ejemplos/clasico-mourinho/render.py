"""Prototipo formato v3: 'Así ganó Mourinho el Clásico' (Barça 1-2 Real Madrid, 25-10-2026).
Fuentes: Coaches' Voice (análisis táctico), Claro Sports (previa), crónicas del partido. Ver meta en README del ejemplo.
Uso: python ejemplos/clasico-mourinho/render.py salida.mp4 [--sheet t1 t2 ...]"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "engine"))
from PIL import Image
from flat import W2, H2, BG, YEL, WHT, ease, lerp2, finish
import cine as C

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
MAD = (255, 204, 0); BAR = (196, 46, 82)
TOTAL = 37.5; END = 33.2

def track(keys, t):
    if t <= keys[0][0]: return keys[0][1]
    for (t0, a), (t1, b) in zip(keys, keys[1:]):
        if t0 <= t <= t1: return lerp2(a, b, ease((t - t0) / max(1e-6, t1 - t0)))
    return keys[-1][1]

# ---------------- posiciones (x: -34..34 · z: 0 portería del Madrid, 105 portería del Barça)
# Madrid defendiendo la salida del Barça (4-2-3-1 con marcas por dentro)
MADRID = {
    "Courtois":   [(0, (0, 6))],
    "Valverde":   [(0, (22, 34))],
    "cent1":      [(0, (8, 30))],
    "cent2":      [(0, (-8, 30))],
    "Cucurella":  [(0, (-22, 36)), (20.2, (-22, 36)), (21.2, (-27, 54)), (25, (-27, 54)), (25.6, (-20, 40))],
    "Tchouaméni": [(0, (2, 44)), (11.0, (2, 44)), (11.9, (-3, 54)), (25, (1, 52)), (25.6, (0, 40))],
    "Bernardo":   [(0, (8, 58)), (9.4, (8, 58)), (10.3, (12, 68)), (25, (8, 66)), (25.6, (14, 50))],
    "Bellingham": [(0, (-4, 62)), (7.8, (-4, 62)), (8.7, (-8, 72)), (25, (-4, 70)), (25.6, (-6, 44)), (26.8, (-4, 54))],
    "Güler":      [(0, (16, 66)), (15.4, (16, 66)), (16.6, (9, 70)), (25, (9, 70)), (25.6, (14, 54)), (27.2, (13, 60)), (28.4, (10, 74))],
    "Diomandé":   [(0, (-16, 66)), (15.4, (-16, 66)), (16.6, (-9, 70)), (19.8, (-9, 70)), (21.0, (-23, 62)), (25, (-23, 62)), (25.6, (-22, 58)), (29, (-16, 80))],
    "Mbappé":     [(0, (-4, 82)), (25, (-4, 82)), (25.6, (6, 74)), (29.6, (4, 92)), (30.6, (3, 97))],
    "Camavinga":  [(0, (40, 40))] , # entra en el min 79: aparece solo en la jugada del gol
}
CAMA = [(0, (2, 58)), (27.0, (2, 62)), (29.0, (-5, 91))]
BARCA = {
    "porB":    [(0, (0, 100))],
    "Martín":  [(0, (11, 89)), (25, (11, 89)), (25.6, (8, 86)), (30, (5, 95))],
    "centB":   [(0, (-11, 89)), (25, (-11, 89)), (25.6, (-7, 86)), (30, (-3, 95))],
    "latD":    [(0, (-28, 80)), (25, (-28, 80)), (25.6, (-24, 70)), (30, (-14, 88))],
    "latI":    [(0, (28, 80)), (25, (28, 80)), (25.6, (24, 68)), (30, (14, 88))],
    "Rodri":   [(0, (-4, 74)), (25, (-4, 74)), (25.6, (-2, 50)), (30, (2, 74))],
    "Pedri":   [(0, (8, 70)), (25, (8, 70)), (25.6, (10, 56)), (30, (8, 80))],
    "Fermín":  [(0, (0, 56)), (25, (0, 56)), (25.6, (-6, 50)), (30, (-6, 70))],
    "Lamine":  [(0, (-29, 58)), (25, (-29, 58)), (25.6, (-26, 46)), (30, (-20, 66))],
    "Gordon":  [(0, (29, 58)), (25, (29, 58)), (25.6, (26, 46)), (30, (22, 64))],
    "Raphinha":[(0, (1, 46)), (25, (1, 46)), (25.6, (-2, 38)), (30, (-2, 56))],
}
NAMED = {"Bellingham", "Bernardo", "Tchouaméni", "Rodri", "Pedri", "Fermín", "Güler", "Diomandé", "Cucurella", "Lamine", "Mbappé", "Martín", "Camavinga"}

# balón: (t, poseedor o punto)
BALL = [(0, "Martín"), (16.0, "Martín"), (16.8, "centB"), (17.6, "centB"), (18.8, "Lamine"), (25.0, "Lamine"),
        (25.5, "Bellingham"), (26.8, "Bellingham"), (27.4, "Güler"), (28.4, "Güler"), (29.1, "Camavinga"), (30.1, "Camavinga"), (30.6, "Mbappé"), (30.85, (0.5, 105.8))]

CAMK = [
    (0.0,  dict(el=16, d=78,  tx=0,   tz=62, az=38,  cy=930)),
    (2.4,  dict(el=24, d=96,  tx=0,   tz=62, az=14,  cy=930)),
    (3.4,  dict(el=50, d=172, tx=0,   tz=60, az=0,   cy=900)),
    (7.0,  dict(el=50, d=172, tx=0,   tz=60, az=0,   cy=900)),
    (8.0,  dict(el=34, d=92,  tx=2,   tz=64, az=-14, cy=900)),
    (14.6, dict(el=36, d=96,  tx=2,   tz=62, az=-6,  cy=900)),
    (15.6, dict(el=48, d=150, tx=0,   tz=70, az=8,   cy=880)),
    (19.6, dict(el=48, d=150, tx=-4,  tz=68, az=8,   cy=880)),
    (20.6, dict(el=34, d=80,  tx=-20, tz=58, az=-28, cy=900)),
    (24.8, dict(el=34, d=84,  tx=-20, tz=58, az=-22, cy=900)),
    (25.8, dict(el=30, d=95,  tx=0,   tz=50, az=16,  cy=920)),
    (28.0, dict(el=34, d=100, tx=6,   tz=72, az=12,  cy=920)),
    (30.2, dict(el=36, d=92,  tx=2,   tz=92, az=4,   cy=920)),
    (32.2, dict(el=32, d=84,  tx=0,   tz=95, az=-6,  cy=920)),
]
HEAD = [
    (0.0,  "BARÇA 1-2 MADRID · 25 OCT", "Así ganó Mourinho", "el Clásico"),
    (3.0,  "EL BARÇA DE FLICK", "Construye por dentro:", "Rodri, Pedri y Fermín"),
    (7.6,  "EL PLAN DE MOURINHO", "Marcaje al hombre", "por dentro"),
    (15.2, "CENTRO CERRADO", "Güler y Diomandé", "tapan las líneas de pase"),
    (20.2, "LA TRAMPA", "Lamine recibe…", "contra dos"),
    (25.2, "MINUTO 87", "Robo, transición", "y gol"),
]
SUBS = [
    (0.3, 2.6, "Le *quitó el centro* al Barça"),
    (3.6, 7.4, "El Barça sale con sus *tres medios* por dentro"),
    (8.0, 9.6, "*Bellingham* se pega a Rodri"),
    (9.6, 11.2, "*Bernardo* a Pedri"),
    (11.2, 14.8, "y *Tchouaméni* a Fermín"),
    (15.4, 19.8, "Sin pase por dentro, el balón *se va a la banda*"),
    (20.4, 24.8, "*Cucurella* encima y *Diomandé* ayuda: *2 contra 1*"),
    (25.4, 27.2, "*Bellingham* supera la presión"),
    (27.2, 29.0, "*Güler* conduce"),
    (29.0, 30.4, "*Camavinga* entra al área…"),
]
LINKS = [(8.2, "Bellingham", "Rodri"), (9.8, "Bernardo", "Pedri"), (11.4, "Tchouaméni", "Fermín")]
FOCUS = [(3.4, 7.4, {"Rodri", "Pedri", "Fermín"}), (20.6, 24.8, {"Lamine"}), (25.4, 31.5, None)]
VIG = None

def pos(name, t):
    if name == "Camavinga": return track(CAMA, t)
    return track(MADRID[name] if name in MADRID else BARCA[name], t)

def ball_at(t):
    prev = BALL[0]
    for i, (t0, h) in enumerate(BALL):
        if t < t0:
            a = prev[1]; pa = pos(a, prev[0]) if isinstance(a, str) else a
            pb = pos(h, t0) if isinstance(h, str) else h
            if isinstance(a, str) and a == h: return pos(a, t), 0.25
            u = (t - prev[0]) / max(1e-6, t0 - prev[0])
            if isinstance(a, str): pa = pos(a, prev[0])
            return lerp2(pa, pb, ease(u)), .25 + 2.2 * u * (1 - u) * (1 if (abs(pa[0] - pb[0]) + abs(pa[1] - pb[1])) > 18 else 0)
        prev = (t0, h)
    h = BALL[-1][1]; return (pos(h, t) if isinstance(h, str) else h), .25

def compose(t):
    global VIG
    if VIG is None: VIG = C.vignette()
    b = Image.new("RGBA", (W2, H2), (*BG, 255)); cam = C.camkeys(CAMK, min(t, END))
    C.pitch(b, cam)
    # zonas
    if 15.6 < t < 20.2:
        a = ease((t - 16.4) / .5) * (1 - ease((t - 19.7) / .4))
        C.zone(b, cam, [(-8, 62), (8, 62), (8, 84), (-8, 84)], (240, 72, 72), a, 45)
    if 20.8 < t < 25.0:
        a = ease((t - 21.2) / .4) * (1 - ease((t - 24.6) / .4))
        C.ring(b, cam, -26, 57, 7.5, YEL, a)
    # marcajes
    for t0, m, r in LINKS:
        if t0 <= t < 24.8:
            e = ease((t - t0) / .5); a = 1 - ease((t - 24.4) / .4)
            C.link(b, cam, pos(m, t), pos(r, t), YEL, e, a)
    # líneas de pase cerradas por Güler y Diomandé
    if 16.4 < t < 20.0:
        a = ease((t - 16.6) / .4) * (1 - ease((t - 19.6) / .4))
        C.arrow(b, cam, pos("Martín", t), (2, 66), (240, 72, 72), ease((t - 16.4) / .5), a)
    # jugadores (ordenados por profundidad: los lejanos primero)
    people = []
    for n in BARCA: people.append((n, BAR, True))
    for n in MADRID:
        if n != "Camavinga": people.append((n, MAD, False))
    if t >= 25.4: people.append(("Camavinga", MAD, False))
    focus = None
    for f0, f1, s in FOCUS:
        if f0 <= t < f1: focus = s
    def depth(p): x, z = pos(p[0], t); return -(cam.P(x, z)[2])
    for n, col, dark in sorted(people, key=depth):
        x, z = pos(n, t); hi = 0.0; nm = n if n in NAMED else None; na = None
        if focus and n in focus: hi = (t % 1.0)
        # nombres: solo los que importan en cada momento
        show = {(3.4, 7.4): {"Rodri", "Pedri", "Fermín"}, (7.6, 15.0): {"Bellingham", "Rodri", "Bernardo", "Pedri", "Tchouaméni", "Fermín"},
                (15.4, 20.2): {"Güler", "Diomandé", "Martín"}, (20.4, 25.0): {"Lamine", "Cucurella", "Diomandé"},
                (25.4, 31.6): {"Bellingham", "Güler", "Camavinga", "Mbappé"}}
        na = 0.0
        for (s0, s1), names in show.items():
            if s0 <= t < s1 and n in names: na = ease((t - s0) / .3) * (1 - ease((t - s1 + .3) / .3))
        a = 1.0
        if n == "Camavinga": a = ease((t - 25.4) / .3)
        C.player(b, cam, x, z, col, None, nm, a, hi, dark, na, below=(col == MAD))
    bx, bz = ball_at(t)[0]; C.ballp(b, cam, bx, bz, ball_at(t)[1])
    b.alpha_composite(VIG)
    C.bigtitle(b, t, 2.6, "Así ganó Mourinho", "el Clásico")
    C.headline(b, t, HEAD) if 2.4 < t < END else None
    C.subs(b, t, SUBS) if t < END else None
    C.flash(b, t, 21.4, "2 vs 1")
    C.flash(b, t, 30.95, "GOL", "Mbappé · Barça 1-2 Madrid")
    if t >= END: C.endcard(b, t - END, "¿Plan de Mourinho", "o fallo del Barça?", "Cuéntamelo en comentarios")
    return finish(b.convert("RGB"))

if __name__ == "__main__":
    out = sys.argv[1]
    if "--sheet" in sys.argv:
        ts = [float(x) for x in sys.argv[sys.argv.index("--sheet") + 1:]]
        ims = [compose(t).resize((540, 960)) for t in ts]
        sh = Image.new("RGB", (540 * len(ims), 960)); [sh.paste(im, (540 * i, 0)) for i, im in enumerate(ims)]; sh.save(out, quality=85)
    else:
        sfx = out + ".sfx.wav"
        C.sfx_track(sfx, TOTAL, whooshes=[2.5, 7.4, 15.0, 20.0, 25.0, 33.0], hits=[21.4, 30.95])
        C.encode(compose, TOTAL, out, os.path.join(ROOT, "music", "okay_for_now-televisions.mp3"), sfx)
