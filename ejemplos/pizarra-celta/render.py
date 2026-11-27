"""PLANTILLA del formato PIZARRA (desde el 27-11-2026). Muestra con Celta 1-2 Bournemouth (Europa League, 26-11-2026).
Reglas del formato (ver CLAUDE.md): UNA idea, voz de Miguel, 25–40 s, plano cenital que cambia poco (cada 6–8 s),
una frase en pantalla cada vez (la de la voz), solo en color los 4–6 jugadores que importan (el resto en gris),
nombres en 2 como mucho, una flecha cada vez, y cierre con la tarea integrada «Antes de los 90» + pregunta.
Los tiempos salen de la voz: V.at("frase"). Sin grabación, tiempos estimados (2,6 palabras/s) para previsualizar.
Uso: python ejemplos/pizarra-celta/render.py salida.mp4 [--sheet t1 t2 ...]"""
import sys, os, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "engine"))
from PIL import Image, ImageDraw
from flat import W2, H2, BG, YEL, WHT, ease, lerp2, finish
import cine as C

ROOT = os.path.join(HERE, "..", "..")
CEL = (138, 194, 236); BOU = (214, 28, 44); GREY = C.GREY

# ---------------- GUION (la primera frase es el gancho). 80–100 palabras ≈ 30–38 s.
SCRIPT = [
    "¿Cómo pierdes jugando 67 minutos con uno más?",
    "Le pasó al Celta ayer contra el Bournemouth.",
    "Tuvo el balón, pero atacó con prisa: siempre al choque.",
    "Y el que defiende con diez solo tiene que juntarse y esperar el error.",
    "Con uno más no hay que correr: hay que mover.",
    "A un lado, al otro, y cuando bascula, cambias.",
    "Así lo entrenamos: seis contra cinco con porteros, tres pasillos, y el gol solo vale si antes has cambiado el balón de pasillo.",
    "¿Tu equipo sabe jugar con uno más?",
]
KEYS = ["67", "prisa", "choque", "juntarse", "mover", "cambias", "pasillos", "pasillo"]
V = C.voice_clock(SCRIPT)
T_HOOK, T_CTX, T_PRISA, T_JUNTA, T_MOVER, T_LADO, T_TAREA, T_PREG = (V.at(p) for p in (
    "¿Cómo pierdes jugando", "Le pasó al Celta", "Tuvo el balón", "Y el que defiende", "Con uno más no hay", "A un lado", "Así lo entrenamos", "¿Tu equipo sabe"))
END = T_PREG - .1; TOTAL = max(END + 3.4, V.dur + V.OFF + .8)
def clauses(maxw=9):
    """subtítulos por frase/cláusula (corta en la puntuación, máx. maxw palabras): cada uno se queda hasta el siguiente."""
    from render_spec import norm
    keys = {norm(k) for k in KEYS}; out, cur = [], []
    for i, w in enumerate(V.sw):
        cur.append(i)
        if w[-1:] in ".,:;?!" or len(cur) >= maxw or i == len(V.sw) - 1:
            txt = " ".join(("*" + V.sw[j] + "*") if norm(V.sw[j]) in keys else V.sw[j] for j in cur)
            out.append((V.OFF + V.T[cur[0]][0], txt)); cur = []
    return [(a, (out[k + 1][0] if k + 1 < len(out) else END), x) for k, (a, x) in enumerate(out)]
SUBS = [c for c in clauses() if T_CTX - .1 <= c[0] < T_TAREA]

# ---------------- posiciones (x: -34..34, z: 0 portería del Celta → 105 la del Bournemouth; el Celta ataca hacia arriba)
BASE_C = {"Radu": (0, 8), "cb1": (-10, 40), "cb2": (10, 40), "lb": (-26, 56), "rb": (26, 56), "m1": (-5, 52), "m2": (7, 54),
          "m3": (-10, 66), "Aspas": (1, 74), "lw": (-22, 72), "rw": (22, 72)}
BASE_B = {"gk": (0, 101), "bcb1": (-7, 88), "bcb2": (7, 88), "brb": (-19, 86), "blb": (19, 86), "bm1": (-5, 79), "bm2": (5, 79),
          "bw1": (-15, 80), "bw2": (15, 80), "bf": (0, 66)}
def sh(d, dx=0, dz=0, only=None, **over):
    out = {k: ((v[0] + dx, v[1] + dz) if (only is None or k in only) else v) for k, v in d.items()}; out.update(over); return out
# formaciones por momento (se interpolan entre sí)
F = [
    (T_HOOK,  BASE_C, BASE_B),
    (T_PRISA, BASE_C, BASE_B),
    (T_PRISA + 1.6, sh(BASE_C, 0, 4, m1=(-4, 62)), BASE_B),
    (T_PRISA + 2.6, sh(BASE_C, 0, 6, Aspas=(1, 78)), sh(BASE_B, bm1=(-1.6, 79.6), bm2=(2.6, 80.2), bcb1=(-.4, 82.6))),
    (T_JUNTA, sh(BASE_C, 0, 6, Aspas=(1, 78)), sh(BASE_B, bm1=(-1.6, 79.6), bm2=(2.6, 80.2), bcb1=(-.4, 82.6))),
    (T_JUNTA + 1.4, BASE_C, sh(BASE_B, 0, 0, None, bw1=(-12, 81), bw2=(12, 81), brb=(-16, 87), blb=(16, 87), bf=(0, 70))),
    (T_LADO, sh(BASE_C, lb=(-27, 64)), sh(BASE_B, 0, 0, None, bw1=(-12, 81), bw2=(12, 81), brb=(-16, 87), blb=(16, 87), bf=(0, 70))),
    (T_LADO + 1.4, sh(BASE_C, lb=(-27, 64)), sh(BASE_B, -7, 0, None, bf=(-6, 70), gk=(-2, 101))),
    (T_LADO + 3.2, sh(BASE_C, lb=(-27, 64), rb=(28, 70)), sh(BASE_B, -7, 0, None, bf=(-6, 70), gk=(-2, 101))),
    (T_TAREA, sh(BASE_C, lb=(-27, 64), rb=(28, 76)), sh(BASE_B, -3, 0, None, gk=(-1, 101))),
]
# balón: (t, poseedor o punto)
BALL = [(T_HOOK, "cb1"), (T_PRISA + .3, "cb1"), (T_PRISA + 1.4, "m1"), (T_PRISA + 1.9, "m1"), (T_PRISA + 2.6, "Aspas"),
        (T_PRISA + 2.9, "bm2"), (T_JUNTA + 1.0, "bm2"), (T_JUNTA + 1.6, "cb1"), (T_LADO, "cb1"), (T_LADO + .9, "lb"),
        (T_LADO + 1.9, "lb"), (T_LADO + 3.2, "rb"), (T_TAREA, "rb")]
LOSS = T_PRISA + 2.9

# quién va en color en cada momento (el resto, gris): lo que cuenta la voz y nada más
COLOR = [(T_HOOK, T_PRISA, None),                                         # gancho: todos (11 contra 10)
         (T_PRISA, T_JUNTA, {"m1", "Aspas", "bm1", "bm2", "bcb1"}),
         (T_JUNTA, T_MOVER, set(BASE_B)),                                 # el bloque de 10
         (T_MOVER, T_TAREA, set(BASE_B) | {"lb", "rb"})]
NAMES = [(T_PRISA + 1.8, T_JUNTA, {"Aspas"})]
CAMK = [
    (0.0,           dict(el=64, d=128, tx=0, tz=70, az=0,  cy=960)),     # gancho: los 21 de un vistazo
    (T_PRISA - .4,  dict(el=66, d=124, tx=0, tz=70, az=4,  cy=960)),
    (T_PRISA + .6,  dict(el=60, d=96,  tx=-2, tz=72, az=-8, cy=960)),    # acerca a la zona del choque
    (T_JUNTA,       dict(el=58, d=94,  tx=0, tz=76, az=-10, cy=960)),
    (T_JUNTA + 1.5, dict(el=66, d=112, tx=0, tz=78, az=0,  cy=960)),     # el bloque entero
    (T_MOVER,       dict(el=66, d=124, tx=0, tz=74, az=0,  cy=960)),
    (T_LADO + 1.0,  dict(el=46, d=118, tx=0, tz=72, az=14, cy=960)),    # el único momento en 3D: el cambio de orientación
    (T_TAREA,       dict(el=48, d=118, tx=4, tz=74, az=20, cy=960)),
]

def track(keys, t):
    if t <= keys[0][0]: return keys[0][1]
    for (t0, a), (t1, b) in zip(keys, keys[1:]):
        if t0 <= t <= t1: return lerp2(a, b, ease((t - t0) / max(1e-6, t1 - t0)))
    return keys[-1][1]
def pos(n, t):
    side = 1 if n in BASE_C else 2
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
    if t < T_PRISA:                                                        # el hueco del expulsado
        C.ghost(b, cam, -21, 89, BOU, "Diakité", ease((t - T_CTX) / .4), t, tag="ROJA 23'")
    if T_PRISA <= t < T_JUNTA:
        C.passline(b, cam, BASE_C["cb1"], (-4, 62), t, T_PRISA + .3, 1.1, YEL, 1.0, 1.2)
        C.passline(b, cam, (-4, 62), (1, 78), t, T_PRISA + 1.9, .7, YEL, 1.0, 1.4)
        pa = ease((t - T_PRISA - 2.4) / .3)
        for n in ("bm1", "bm2", "bcb1"): C.pressure(b, cam, pos(n, t), pos("Aspas", t), BOU, pa)
    if T_JUNTA + .8 <= t < T_MOVER:                                        # el bloque de 10, junto
        a = ease((t - T_JUNTA - .8) / .4)
        C.zone(b, cam, [(-17, 77), (17, 77), (17, 90), (-17, 90)], BOU, a, 34)
    if T_LADO <= t < T_TAREA:
        C.passline(b, cam, (-10, 40), (-27, 64), t, T_LADO, .9, YEL, 1.0, 1.0)
        C.arrow(b, cam, (-26, 66), (27, 72), YEL, ease((t - T_LADO - 1.9) / 1.3), 1.0, w=8)
        C.zone(b, cam, [(20, 62), (34, 62), (34, 86), (20, 86)], YEL, ease((t - T_LADO - 1.5) / .4), 40)
    names = set().union(*[s for t0, t1, s in NAMES if t0 <= t < t1]) if NAMES else set()
    people = [(n, CEL) for n in BASE_C] + [(n, BOU) for n in BASE_B]
    for n, col in sorted(people, key=lambda p: -cam.P(*pos(p[0], t))[2]):
        x, z = pos(n, t); on = colored(n, t)
        C.player(b, cam, x, z, col if on else GREY, None, n if n in names else None, 1.0 if on else .55, 0.0, col == BOU, 1.0 if n in names else 0.0)
    if T_LADO + 3.0 <= t < T_TAREA:
        x, z = pos("rb", t); C.tag3d(b, cam, x, z, "LIBRE", YEL, ease((t - T_LADO - 3.0) / .3), fg=(14, 22, 34))
    bx, bz = ball(t)
    if t < T_TAREA: C.ballp(b, cam, bx, bz)
    C.spark(b, cam, 1, 79, t, LOSS, col=BOU)
    b.alpha_composite(VIG)
    C.bigtitle(b, t, T_CTX + .2, "¿Cómo pierdes con", "uno más 67 minutos?")
    C.question_top(b, t, T_CTX + .2, "67 minutos con uno más", "y perdió. ¿Por qué?", "CELTA 1-2 BOURNEMOUTH · EUROPA LEAGUE")
    if T_CTX + .2 < t < T_TAREA: C.rec_tag(b, y=470)
    if t < T_TAREA: C.caption(b, t, SUBS)
    C.drillboard(b, t, T_TAREA, END, "ANTES DE LOS 90 · ASÍ SE ENTRENA", "Superioridad con cerebro",
                 ["*6 contra 5* + porteros", "*3 pasillos*", "Gol solo tras *cambiar de pasillo*"], CEL, BOU)
    if t >= END: C.endcard(b, t - END, "¿Tu equipo sabe", "jugar con uno más?", "Te leo en comentarios")
    return finish(b.convert("RGB"))

def compose(t): return scene(t)

if __name__ == "__main__":
    out = sys.argv[1]
    if "--sheet" in sys.argv:
        ts = [float(x) for x in sys.argv[sys.argv.index("--sheet") + 1:]]
        C.sheet(scene, ts, out)
    else:
        sfx = out + ".sfx.wav"
        C.sfx_track(sfx, TOTAL, whooshes=[T_TAREA - .2, END - .1], hits=[LOSS])
        music = os.environ.get("MUSIC", os.path.join(ROOT, "music", "okay_for_now-televisions.mp3"))
        C.encode(compose, TOTAL, out, music, sfx, gain=-14 if V.wav else -8, voice=V.wav)
        os.path.exists(sfx) and os.remove(sfx)
