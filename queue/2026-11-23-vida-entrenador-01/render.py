"""Serie 'La vida del entrenador' · Ep. 1: 'Siete fuera cada semana' (lo que no se ve antes de la sesión).
Formato cine CON VOZ de Miguel (primera persona) + PLANOS DE VÍDEO (suyos o generados con IA) + animación.
Los clips van en clips/ con los nombres de CLIPS (ver clips/LEEME.md). Si falta alguno, la hoja de previsualización
pinta un marcador; el render completo se para (no se publica un vídeo con huecos).
Uso: python queue/2026-11-23-vida-entrenador-01/render.py salida.mp4 [--sheet t1 t2 ...]"""
import sys, os, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "engine")); sys.path.insert(0, HERE)
from PIL import Image, ImageDraw
from flat import W2, H2, BG, YEL, WHT, ease, finish
import cine as C
import planos

ROOT = os.path.join(HERE, "..", "..")
SCRIPT = [
    "Cada semana dejo a siete chavales fuera de la convocatoria.",
    "Y nadie ve lo que hay detrás.",
    "El lunes empieza mucho antes del entrenamiento: planificar la semana, pensar cada tarea, que el balón no pare y que todos aprendan algo.",
    "Luego llega la convocatoria. Siete nombres que no salen. Y cada uno es un chaval que esa tarde llega triste a casa.",
    "Entonces llegan los mensajes. El padre que no entiende por qué su hijo no va. El padre que te explica cómo tendrías que jugar.",
    "Y el chico que está convencido de que tienes algo personal contra él.",
    "No es personal. Nunca lo es. Es una decisión de una semana, no sobre una persona.",
    "Y aun así, el sábado el equipo sale, se ayuda y compite. Eso es lo que no se ve.",
    "Entrenador, ¿cómo le dices tú a un chaval que no va convocado?",
]
KEYS = ["siete", "convocatoria", "detrás", "planificar", "tarea", "triste", "mensajes", "padre", "personal", "sábado", "compite", "convocado"]
V = C.voice_clock(SCRIPT)
PLANTILLA = 21                                   # ajustar al número real de la plantilla de Miguel
FUERA = (3, 8, 11, 14, 17, 19, 21)               # dorsales genéricos: nunca nombres (son menores)

def cp(name, label, ia=False, **kw):
    return dict(clip=C.Clip(os.path.join(HERE, "clips", name), label, **kw), ia=ia)
# (frase donde empieza el plano, plano). Un plano dura hasta que empieza el siguiente.
SHOTS = [
    ("Cada semana dejo",            cp("01-miguel-habla.jpg", "Foto de Miguel hablando al equipo", zoom=(1.0, 1.10))),
    ("Y nadie ve",                  cp("02-espaldas-luz.jpg", "Foto de Miguel de espaldas (U.D. Mortadelo)", zoom=(1.12, 1.0))),
    ("El lunes empieza",            dict(anim="mesa", clip_alt=os.path.join(HERE, "clips", "03-mesa-planificar.mp4"))),
    ("pensar cada tarea",           dict(anim="rondo")),
    ("que el balón no pare",        dict(anim="conos", clip_alt=os.path.join(HERE, "clips", "04-conos-balones.mp4"))),
    ("Luego llega la convocatoria", cp("05-banda-perfil.jpg", "Foto de Miguel en la banda", zoom=(1.04, 1.12))),
    ("Y cada uno es un chaval",     dict(anim="calle", clip_alt=os.path.join(HERE, "clips", "06-chico-mochila.mp4"))),
    ("Entonces llegan los mensajes", dict(anim="movil", clip_alt=os.path.join(HERE, "clips", "07-movil-mesa.mp4"))),
    ("El padre que te explica",     dict(anim="grada", clip_alt=os.path.join(HERE, "clips", "08-padre-grada.mp4"))),
    ("Y el chico que está",         dict(anim="banquillo", clip_alt=os.path.join(HERE, "clips", "09-chico-banquillo.mp4"))),
    ("No es personal",              cp("10-espaldas-partido.jpg", "Foto de Miguel de espaldas mirando el partido", zoom=(1.0, 1.10))),
    ("Y aun así, el sábado",        cp("11-equipo-pina.jpg", "Foto de la piña del equipo (caras difuminadas)", zoom=(1.0, 1.05))),
    ("Eso es lo que no se ve",      cp("12-agachado-banda.jpg", "Foto de Miguel agachado en la banda", zoom=(1.10, 1.0))),
    ("Entrenador, ¿cómo le dices",  dict(end=True)),
]
for _k, (_p, _s) in enumerate(SHOTS):                       # si llega el clip real o de IA, sustituye al plano dibujado
    if "clip_alt" in _s:
        _c = C.Clip(_s["clip_alt"], "")
        if _c.ok: SHOTS[_k] = (_p, dict(clip=_c, ia=True))
T = [V.at(p) for p, _ in SHOTS]
END = T[-1] - .15; TOTAL = max(END + 3.4, V.dur + V.OFF + 1.0)
CAPS = V.captions(KEYS)
SUBS = [(c[0], (CAPS[i + 1][0] if i + 1 < len(CAPS) else END), c[1]) for i, c in enumerate(CAPS) if c[0] < END]
HEAD = [(V.at("Cada semana dejo") + 2.4, "LA VIDA DEL ENTRENADOR · EP. 1", "Lo que", "no se ve"),
        (V.at("El lunes empieza"), "ANTES DE LA SESIÓN", "Planificar", "cada tarea"),
        (V.at("Luego llega la convocatoria"), "LA CONVOCATORIA", "Siete", "fuera"),
        (V.at("Entonces llegan los mensajes"), "DESPUÉS", "Los mensajes", "y la grada"),
        (V.at("No es personal"), "LA DECISIÓN", "Una semana,", "no una persona"),
        (V.at("Y aun así, el sábado"), "EL SÁBADO", "Y el equipo", "compite")]
MSGS = [("¿Por qué no va mi hijo este fin de semana?", "Mensaje de un padre · recreación"),
        ("Yo jugaría con dos arriba, se ve clarísimo…", "Otro padre · recreación")]
VIG = None

def shot_at(t):
    i = max([k for k, t0 in enumerate(T) if t0 <= t], default=0); return i, T[i], (T[i + 1] if i + 1 < len(T) else TOTAL)

# ---- animación del rondo (pensar cada tarea): 4 contra 2 en un cuadrado, el balón circula
RONDO = [(-9, 47), (9, 47), (9, 61), (-9, 61)]
CAM_R = dict(el=58, d=70, tx=0, tz=54, az=-18, cy=930)
def rondo(b, lt):
    cam = C.Cam(**{**CAM_R, "az": -18 + 10 * min(1, lt / 4)}); C.pitch(b, cam)
    C.zone(b, cam, [(-11, 45), (11, 45), (11, 63), (-11, 63)], YEL, min(1, lt / .4), 18)
    seq = [0, 1, 3, 2, 0, 2, 1]; k = int(lt / .7) % (len(seq) - 1); u = ease((lt % .7) / .7)
    a, c = RONDO[seq[k]], RONDO[seq[k + 1]]; bx, bz = a[0] + (c[0] - a[0]) * u, a[1] + (c[1] - a[1]) * u
    d1 = (bx * .55 - 2, bz * .55 + 54 * .45); d2 = (bx * .35 + 3, bz * .35 + 54 * .65 + 1)
    for x, z in RONDO: C.player(b, cam, x, z, YEL, None, None, 1.0)
    for x, z in (d1, d2): C.player(b, cam, x, z, (240, 242, 246), None, None, 1.0, dark=True)
    C.arrow(b, cam, a, c, WHT, u, .7, w=4); C.ballp(b, cam, bx, bz)

def scene(t):
    global VIG
    if VIG is None: VIG = C.vignette()
    i, t0, t1 = shot_at(min(t, END - .01)); sh = SHOTS[i][1]; lt = t - t0
    b = Image.new("RGBA", (W2, H2), (*BG, 255))
    if sh.get("anim") == "rondo": rondo(b, lt)
    elif sh.get("anim") in planos.FN: planos.FN[sh["anim"]](b, lt, t1 - t0)
    elif "clip" in sh: b = sh["clip"].frame(lt, min(1, lt / max(.5, t1 - t0)))
    if i > 0 and lt < .18:                                  # corte con un fundido muy corto desde el plano anterior
        pv = SHOTS[i - 1][1]
        if "clip" in pv:
            prev = pv["clip"].frame(t - T[i - 1], 1.0); b = Image.blend(prev, b, ease(lt / .18))
    b.alpha_composite(VIG)
    if sh.get("ia"): C.rec_tag(b, "Recreación con IA", a=ease(lt / .3))
    if t < 2.4:                                             # banda oscura detrás del gancho para que se lea sobre la foto
        from PIL import ImageFilter
        sh_ = Image.new("RGBA", b.size, (0, 0, 0, 0)); a_ = int(170 * (1 - ease((t - 2.0) / .4)))
        ImageDraw.Draw(sh_).rectangle((0, 700 * 2, W2, 1020 * 2), fill=(*BG, a_)); b.alpha_composite(sh_.filter(ImageFilter.GaussianBlur(60)))
    C.bigtitle(b, t, 2.4, "Cada semana dejo", "a 7 fuera")
    if 2.2 < t < END: C.headline(b, t, HEAD)
    C.roster(b, t, V.at("Luego llega la convocatoria") + .1, V.at("Y cada uno es un chaval") - .05, PLANTILLA, FUERA,
             V.at("Siete nombres que no salen"), "CONVOCATORIA · SÁBADO")
    C.chat(b, t, V.at("Entonces llegan los mensajes") + .5, V.at("El padre que te explica") + .2, MSGS)
    C.flash(b, t, V.at("No es personal"), "NO ES PERSONAL", None, size=100)
    if t < END and not (V.at("Luego llega la convocatoria") < t < V.at("Y cada uno es un chaval")) and t > 2.4: C.subs(b, t, SUBS)
    if t >= END: C.endcard(b, t - END, "¿Cómo le dices a un chaval", "que no va convocado?", "Entrenadores: os leo")
    return finish(b.convert("RGB"))

if __name__ == "__main__":
    out = sys.argv[1]
    if "--sheet" in sys.argv:
        ts = [float(x) for x in sys.argv[sys.argv.index("--sheet") + 1:]]
        ims = [scene(t).resize((540, 960)) for t in ts]
        s = Image.new("RGB", (540 * len(ims), 960)); [s.paste(im, (540 * k, 0)) for k, im in enumerate(ims)]; s.save(out, quality=85)
    else:
        missing = [x[1]["clip"].path for x in SHOTS if "clip" in x[1] and not x[1]["clip"].ok]
        if missing: raise SystemExit("Faltan planos de vídeo en clips/: " + ", ".join(os.path.basename(m) for m in missing))
        sfx = out + ".sfx.wav"
        C.sfx_track(sfx, TOTAL, whooshes=[x - .05 for x in T[1:]], hits=[V.at("Siete nombres que no salen"), V.at("No es personal")])
        C.encode(lambda t: scene(t), TOTAL, out, os.path.join(ROOT, "music", "dance_with_you-everet_almond.mp3"), sfx, gain=-10, voice=V.wav)
