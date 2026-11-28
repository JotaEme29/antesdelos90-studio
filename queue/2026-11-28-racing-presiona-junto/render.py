"""Levante 1-3 Racing (LaLiga, jornada 14, viernes 27-11-2026). Formato PIZARRA con la voz de Miguel.
Una idea: presionar arriba sin el bloque detrás es abrirse; el Racing remontó cuando presionó y defendió JUNTO.
Base: ejemplos/pizarra-celta/render.py. Uso: python queue/<slug>/render.py salida.mp4 [--sheet t1 t2 ...]"""
import sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "engine"))
from PIL import Image
from flat import W2, H2, BG, YEL, WHT, ease, lerp2, finish
import cine as C

ROOT = os.path.join(HERE, "..", "..")
RAC = (22, 156, 92); LEV = (30, 86, 176); GREY = C.GREY

# ---------------- GUION (la primera frase es el gancho). ~110 palabras.
SCRIPT = [
    "¿Por qué el Racing presionaba arriba y le pasaban por encima?",
    "Ayer perdía uno a cero en Valencia al descanso.",
    "Con Ryan sacando desde atrás, llegaban tarde a presionar y muy abiertos.",
    "Juego directo, y a los que presionaban les costaba volver.",
    "En la segunda parte, triple cambio y otra energía: atacar juntos y defender juntos.",
    "La idea: si salta uno, sube el bloque entero. Y remontó: uno a tres.",
    "Así lo entrenamos: seis contra seis con porteros, el campo en tres franjas.",
    "Si robas arriba y marcas, vale doble. Pero solo con todos los de campo en las dos franjas de arriba.",
    "¿Tu equipo presiona junto o presiona solo?",
]
KEYS = ["tarde", "abiertos", "directo,", "volver", "juntos", "entero", "remontó"]
V = C.voice_clock(SCRIPT)
T_HOOK, T_CTX, T_SALTAN, T_LARGO, T_JUNTOS, T_SALTA, T_TAREA, T_PREG = (V.at(p) for p in (
    "¿Por qué el Racing", "Ayer perdía uno", "Con Ryan sacando", "Juego directo", "En la segunda parte", "La idea: si salta",
    "Así lo entrenamos", "¿Tu equipo presiona"))
T_REM = V.at("Y remontó")
END = T_PREG - .1; TOTAL = max(END + 3.4, V.dur + V.OFF + .8)

def clauses(maxw=9):
    from render_spec import norm
    keys = {norm(k) for k in KEYS}; out, cur = [], []
    for i, w in enumerate(V.sw):
        cur.append(i)
        if w[-1:] in ".,:;?!" or len(cur) >= maxw or i == len(V.sw) - 1:
            txt = " ".join(("*" + V.sw[j] + "*") if norm(V.sw[j]) in keys else V.sw[j] for j in cur)
            out.append((V.OFF + V.T[cur[0]][0], txt)); cur = []
    return [(a, (out[k + 1][0] if k + 1 < len(out) else END), x) for k, (a, x) in enumerate(out)]
# subtítulos por frase entera (no por cláusula corta): menos cambios, se lee mejor
def sentences():
    from render_spec import norm
    keys = {norm(k) for k in KEYS}; out, cur = [], []
    for i, w in enumerate(V.sw):
        cur.append(i)
        if w[-1:] in ".?!" or (w[-1:] in ",:" and len(cur) >= 5) or i == len(V.sw) - 1:
            txt = " ".join(("*" + V.sw[j] + "*") if norm(V.sw[j]) in keys else V.sw[j] for j in cur)
            out.append((V.OFF + V.T[cur[0]][0], txt)); cur = []
    return [(a, (out[k + 1][0] if k + 1 < len(out) else END), x) for k, (a, x) in enumerate(out)]
SUBS = [c for c in sentences() if T_CTX - .1 <= c[0] < T_TAREA]

# ---------------- posiciones (x: -34..34; z: 0 portería del Levante → 105 la del Racing). El Levante sale desde abajo.
LEV0 = {"Ryan": (0, 4), "lc1": (-11, 11), "lc2": (11, 11), "llb": (-27, 24), "lrb": (27, 24), "lpv": (0, 22),
        "lm1": (-11, 34), "lm2": (11, 35), "llw": (-25, 48), "lrw": (25, 48), "lst": (0, 55)}
RAC0 = {"rgk": (0, 101), "rcb1": (-9, 68), "rcb2": (9, 68), "rlb": (-25, 64), "rrb": (25, 64), "rm1": (-8, 51), "rm2": (8, 51),
        "rlm": (-24, 46), "rrm": (24, 46), "rf1": (-7, 28), "rf2": (8, 28)}
def sh(d, dx=0, dz=0, only=None, **over):
    out = {k: ((v[0] + dx, v[1] + dz) if (only is None or k in only) else v) for k, v in d.items()}; out.update(over); return out
JUMP = dict(rf1=(-2, 9), rf2=(9, 14), rrm=(21, 28))                     # los tres que saltan; el resto se queda
LONG_L = sh(LEV0, 0, 0, None, lst=(-3, 44), llw=(-24, 54), lrw=(24, 54))
RAC_J = {"rgk": (0, 86), "rcb1": (-8, 41), "rcb2": (8, 41), "rlb": (-23, 39), "rrb": (23, 39), "rm1": (-7, 28), "rm2": (7, 28),
         "rlm": (-20, 22), "rrm": (20, 23), "rf1": (-5, 13), "rf2": (8, 15)}
LEV_J = sh(LEV0, lst=(0, 47), llw=(-25, 44), lrw=(25, 44), lm1=(-10, 31), lm2=(10, 32))
F = [
    (0.0,            LEV0, RAC0),
    (T_SALTAN,       LEV0, RAC0),
    (T_SALTAN + 1.6, LEV0, sh(RAC0, **JUMP)),
    (T_LARGO,        LEV0, sh(RAC0, **JUMP)),
    (T_LARGO + 1.4,  LONG_L, sh(RAC0, **JUMP)),
    (T_LARGO + 3.0,  sh(LONG_L, lst=(-5, 50)), sh(RAC0, **dict(JUMP, rf1=(-3, 13), rf2=(8, 17)))),   # se gira; arriba no vuelven
    (T_JUNTOS,       LEV_J, sh(RAC0, **dict(JUMP, rf1=(-3, 13), rf2=(8, 17)))),
    (T_JUNTOS + 1.8, LEV_J, RAC_J),
    (T_SALTA,        LEV_J, RAC_J),
    (T_SALTA + 1.4,  LEV_J, sh(RAC_J, 0, -5, None, rf1=(-3, 9), rf2=(6, 12), rgk=(0, 82))),
    (T_SALTA + 3.0,  sh(LEV_J, lst=(-2, 40)), sh(RAC_J, 0, -5, None, rf1=(-3, 9), rf2=(6, 12), rcb1=(-4, 38), rgk=(0, 82))),
    (T_TAREA,        sh(LEV_J, lst=(-2, 40)), sh(RAC_J, 0, -5, None, rf1=(-3, 9), rf2=(6, 12), rcb1=(-4, 38), rgk=(0, 82))),
]
BALL = [(0.0, "Ryan"), (T_LARGO + .2, "Ryan"), (T_LARGO + 1.3, "lst"), (T_JUNTOS, "lst"), (T_JUNTOS + .6, "Ryan"),
        (T_SALTA + 1.3, "Ryan"), (T_SALTA + 2.4, "rcb1"), (T_TAREA, "rcb1")]
ROBO = T_SALTA + 2.4
PRESS = {"rf1", "rf2", "rrm"}
COLOR = [(0.0, T_SALTAN, None),                                         # gancho: todos
         (T_SALTAN, T_LARGO, PRESS | {"rm1", "rm2", "Ryan"}),            # saltan tres; los medios, lejos
         (T_LARGO, T_JUNTOS, PRESS | {"Ryan", "lst"}),                  # balón largo; los de arriba no vuelven
         (T_JUNTOS, T_TAREA, {"rf1", "rf2", "rm1", "rm2", "rcb1", "rcb2"})]  # el eje del bloque: punta, medios, centrales
NAMES = [(T_SALTAN, T_LARGO + 1.6, {"Ryan"})]
CAMK = [                                                                 # pocos planos, estables
    (0.0,            dict(el=64, d=124, tx=0, tz=42, az=0, cy=760)),    # gancho: los 22
    (T_SALTAN - .2,  dict(el=64, d=124, tx=0, tz=42, az=0, cy=760)),
    (T_SALTAN + 1.0, dict(el=62, d=106, tx=-2, tz=33, az=0, cy=760)),   # el hueco entre los que saltan y los medios
    (T_JUNTOS,       dict(el=62, d=106, tx=-2, tz=33, az=0, cy=760)),
    (T_JUNTOS + 1.2, dict(el=64, d=108, tx=-1, tz=28, az=0, cy=760)),   # el bloque, corto
    (T_SALTA,        dict(el=64, d=108, tx=-1, tz=28, az=0, cy=760)),
    (T_SALTA + 1.0,  dict(el=48, d=108, tx=0, tz=26, az=14, cy=760)),   # el único momento en 3D: sube el bloque
    (T_TAREA,        dict(el=50, d=108, tx=0, tz=26, az=16, cy=760)),
]

def track(keys, t):
    if t <= keys[0][0]: return keys[0][1]
    for (t0, a), (t1, b) in zip(keys, keys[1:]):
        if t0 <= t <= t1: return lerp2(a, b, ease((t - t0) / max(1e-6, t1 - t0)))
    return keys[-1][1]
def pos(n, t):
    side = 1 if n in LEV0 else 2
    return track([(f[0], f[side][n]) for f in F], t)
def ball(t):
    def at(h, tt): return pos(h, tt) if isinstance(h, str) else h
    if t <= BALL[0][0]: return at(BALL[0][1], t)
    for (t0, a), (t1, h) in zip(BALL, BALL[1:]):
        if t0 <= t < t1:
            if a == h: return at(a, t)
            return lerp2(at(a, t0), at(h, t1), ease((t - t0) / max(1e-6, t1 - t0)))
    return at(BALL[-1][1], t)
def colored(n, t):
    for t0, t1, s in COLOR:
        if t0 <= t < t1: return s is None or n in s
    return True

VIG = None
def scene(t, r=None):
    global VIG
    if VIG is None: VIG = C.vignette()
    b = Image.new("RGBA", (W2, H2), (*BG, 255)); cam = C.camkeys(CAMK, min(t, END)); C.pitch(b, cam)
    # --- dibujo táctico: una cosa cada vez
    if T_SALTAN + 1.2 <= t < T_LARGO:                                   # el hueco: de los que saltan a los medios
        C.gap(b, cam, -30, 13, 50, YEL, 1.0, "HUECO", ease((t - T_SALTAN - 1.2) / .8), label_z=34)
    if T_LARGO <= t < T_JUNTOS:
        C.passline(b, cam, LEV0["Ryan"], (-3, 44), t, T_LARGO + .2, 1.1, YEL, 1.0, 1.6)
    if T_JUNTOS + 1.6 <= t < T_SALTA:                                   # el mismo hueco, ahora corto
        C.gap(b, cam, -29, 13, 28, YEL, 1.0, "JUNTOS", ease((t - T_JUNTOS - 1.6) / .6), label_z=34)
    if T_SALTA <= t < T_TAREA:                                          # sube el bloque entero
        a = ease((t - T_SALTA - .2) / .4) * (1 - ease((t - T_REM + .2) / .3))
        C.lineband(b, cam, 36, YEL, a, None, zfrom=41)
    people = [(n, LEV) for n in LEV0] + [(n, RAC) for n in RAC0]
    names = set().union(*[s for t0, t1, s in NAMES if t0 <= t < t1])
    for n, col in sorted(people, key=lambda p: -cam.P(*pos(p[0], t))[2]):
        x, z = pos(n, t); on = colored(n, t)
        C.player(b, cam, x, z, col if on else GREY, None, n if n in names else None, 1.0 if on else .55, 0.0, col == LEV, 1.0 if n in names else 0.0)
    if T_LARGO + 1.8 <= t < T_JUNTOS:
        x, z = pos("rf1", t); C.tag3d(b, cam, x, z, "LES CUESTA VOLVER", (230, 60, 60), ease((t - T_LARGO - 1.8) / .3))
    bx, bz = ball(t)
    if t < T_TAREA: C.ballp(b, cam, bx, bz)
    C.spark(b, cam, -4, 38, t, ROBO, col=RAC)
    b.alpha_composite(VIG)
    C.bigtitle(b, t, T_CTX + .2, "¿Por qué el Racing", "presionaba solo?")
    C.question_top(b, t, T_CTX + .2, "¿Por qué le pasaban", "por encima al Racing?", "LEVANTE 1-3 RACING · LALIGA")
    if T_CTX + .2 < t < T_TAREA: C.rec_tag(b, y=470)
    if t < T_TAREA: C.caption(b, t, SUBS)
    C.drillboard_press(b, t, T_TAREA, END, "ANTES DE LOS 90 · ASÍ SE ENTRENA", "Presionar juntos",
                       ["*6 contra 6* + porteros", "Campo en *3 franjas*", "Robo arriba y gol: *vale doble*", "…si los 6 están en *2 franjas*"], RAC, LEV)
    if t >= END: C.endcard(b, t - END, "¿Tu equipo presiona", "junto o solo?", "Te leo en comentarios")
    return finish(b.convert("RGB"))

def compose(t): return scene(t)

if __name__ == "__main__":
    out = sys.argv[1]
    if "--sheet" in sys.argv:
        ts = [float(x) for x in sys.argv[sys.argv.index("--sheet") + 1:]]
        C.sheet(scene, ts, out)
    else:
        sfx = out + ".sfx.wav"
        C.sfx_track(sfx, TOTAL, whooshes=[T_TAREA - .2, END - .1], hits=[ROBO])
        music = os.environ.get("MUSIC", os.path.join(ROOT, "music", "mixkit", "135-mixkit.mp3"))
        C.encode(compose, TOTAL, out, music, sfx, gain=-14 if V.wav else -8, voice=V.wav)
        os.path.exists(sfx) and os.remove(sfx)
