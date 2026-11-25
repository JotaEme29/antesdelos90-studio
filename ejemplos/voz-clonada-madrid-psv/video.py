import sys, json
sys.path.insert(0, "/tmp/claude-0/an"); sys.path.insert(0, "/home/claude/antesdelos90-studio/engine")
from PIL import Image, ImageDraw
import anim as A, cine as C, talk as T
from flat import W2, H2, BG, YEL, WHT, NAVY, ease, back, font, finish
OFF = 0.3
marks = json.load(open("/tmp/claude-0/tts/marks.json"))
REAL = ["Al descanso el Madrid perdía…", "y Mourinho no cambió jugadores: cambió el partido.",
 "En la primera parte el PSV le dio un baño: presionaba arriba y salía a la contra.", "El propio Mourinho lo reconoció: no conseguían robar.",
 "Al descanso, tres cambios de golpe.", "Fuera Militão, Rüdiger y Tchouaméni, dos de ellos con amarilla.", "Dentro Konaté, Huijsen y Bellingham.",
 "Primera clave: con centrales rápidos, la defensa sube y el Madrid presiona arriba.", "Se acabaron las contras del PSV.",
 "Segunda: Bernardo y Güler en el centro.", "Güler empieza a mandar: tacón para el 1-1 y pase para el 3-1.",
 "Tercera: Bellingham entre líneas.", "Gol y asistencia.", "Y el propio Mourinho lo admitió: se equivocó dejando a Jude en el banquillo.",
 "Yo como entrenador me quedo con esto: a veces el cambio no es meter más delanteros, es mover las piezas.", "¿Qué cambio fue el clave para ti?", "Te leo."]
KEYS = {T.norm(k) for k in ["Mourinho", "PSV", "Militão,", "Rüdiger", "Tchouaméni,", "Konaté,", "Huijsen", "Bellingham.", "Bellingham", "Güler", "Bernardo", "1-1", "3-1", "Jude", "piezas.", "amarilla."]}
WORDS = []
for m, txt in zip(marks, REAL):
    ws = txt.split(); a, b = m["t0"] + OFF, min(m["t1"], 55.6) + OFF
    if m is marks[-1]: b = a + .9
    L = sum(len(w) + 2 for w in ws); t = a
    for w in ws:
        d = (b - a) * (len(w) + 2) / L; WORDS.append((t, t + d, w, T.norm(w) in KEYS)); t += d
def S(i): return marks[i]["t0"] + OFF
END = S(15) - .1; TOTAL = 57.2
def subs_board(b, t):
    """Cambios del descanso: sale / entra."""
    d = ImageDraw.Draw(b, "RGBA"); k = ease((t - S(4)) / .3) * (1 - ease((t - S(7) + .3) / .3))
    d.rectangle((0, 0, W2, H2), fill=(*BG, int(215 * k)))
    d.text((W2 / 2, 620 * 2), "CAMBIOS AL DESCANSO", font=font(42, "Bold"), fill=(*YEL, int(255 * k)), anchor="mm")
    rows = [("Militão", "Konaté", False), ("Rüdiger", "Huijsen", True), ("Tchouaméni", "Bellingham", True)]
    for i, (o, n, yel) in enumerate(rows):
        u = ease((t - S(5) - i * .9) / .35) * k; y = (760 + i * 150) * 2
        if u <= .02: continue
        d.rounded_rectangle((110 * 2, y - 58 * 2, (1080 - 110) * 2, y + 58 * 2), radius=36, fill=(28, 34, 40, int(240 * u)))
        d.text((170 * 2, y), o, font=font(46, "Black"), fill=(235, 80, 90, int(255 * u)), anchor="lm")
        if yel and t > S(5) + 2.6: d.rounded_rectangle((170 * 2 + d.textlength(o, font=font(46, "Black")) + 20, y - 34, 170 * 2 + d.textlength(o, font=font(46, "Black")) + 66, y + 34), radius=6, fill=(255, 210, 0, int(255 * u)))
        d.text((540 * 2, y), "→", font=font(46, "Black"), fill=(*WHT, int(255 * u)), anchor="mm")
        v = ease((t - S(6) - i * .5) / .35) * k
        if v > .02: d.text((910 * 2, y), n, font=font(46 * (.8 + .2 * min(1, back((t - S(6) - i * .5) / .35))), "Black"), fill=(*YEL, int(255 * v)), anchor="rm")
def final_score(b, t, t0, t1):
    d = ImageDraw.Draw(b, "RGBA"); k = ease((t - t0) / .3) * (1 - ease((t - t1 + .3) / .3))
    d.rectangle((0, 0, W2, H2), fill=(*BG, int(220 * k)))
    d.text((W2 / 2, 720 * 2), "REAL MADRID 5-1 PSV", font=font(66 * (.85 + .15 * min(1, back((t - t0) / .35))), "Black"), fill=(*WHT, int(255 * k)), anchor="mm")
    goals = ["Valverde 50'", "Bellingham 60'", "Mbappé 64' y 84'", "Vinícius 87'"]
    for i, g in enumerate(goals):
        u = ease((t - t0 - .4 - i * .35) / .3) * k
        d.text((W2 / 2, (840 + i * 80) * 2), g, font=font(42, "Bold"), fill=(*YEL, int(255 * u)), anchor="mm")
    d.text((W2 / 2, (840 + 4 * 80 + 30) * 2), "Los 5 goles, en la 2ª parte", font=font(34, "SemiBold"), fill=(200, 206, 212, int(255 * k)), anchor="mm")
def endcard(b, u):
    d = ImageDraw.Draw(b, "RGBA"); d.rectangle((0, 0, W2, H2), fill=(*BG, int(235 * ease(u / .3))))
    k = back((u - .05) / .4)
    if k > .05:
        d.text((W2 / 2, 820 * 2), "¿Qué cambio", font=font(84 * k, "Black"), fill=WHT, anchor="mm")
        d.text((W2 / 2, 920 * 2), "fue la clave?", font=font(84 * k, "Black"), fill=YEL, anchor="mm")
    k2 = back((u - .3) / .4)
    if k2 > .05:
        w, h = 700 * 2 * k2, 110 * 2 * k2; d.rounded_rectangle((W2 / 2 - w / 2, 1090 * 2 - h / 2, W2 / 2 + w / 2, 1090 * 2 + h / 2), radius=h / 2, fill=YEL)
        d.text((W2 / 2, 1090 * 2), "@soymigueldelfutbol", font=font(54 * k2, "Black"), fill=NAVY, anchor="mm")
def base(t):
    if t < S(2): return A.scene_cambio(min(2.9, t * .4)), None          # gancho y 1ª parte
    if t < S(3): return A.scene_cambio(min(2.9, 1.2 + (t - S(2)) * .3)), None
    if t < S(4): return A.scene_cambio(2.9), "quote1"
    if t < S(7): return A.scene_cambio(2.9), "subs"
    if t < S(9): return A.scene_presion(min(5.99, (t - S(7)) * 6 / (S(9) - S(7)))), None
    if t < S(10): return A.scene_cambio(min(6.9, 3.2 + (t - S(9)))), None
    if t < S(11): return A.scene_gol(min(6.39, (t - S(10)) * 6.4 / (S(11) - S(10)))), None
    if t < S(13): return A.scene_cambio(6.9), "belli"
    if t < S(14): return A.scene_cambio(6.9), "quote2"
    if t < END: return A.scene_cambio(6.9), "score"
    return A.scene_cambio(6.9), "end"
def compose(t):
    im, mode = base(t); b = im.resize((W2, H2)).convert("RGBA")
    if t < 2.6: C.bigtitle(b, t, 2.6, "Perdía 0-1", "al descanso")
    if mode == "quote1": C.quote(b, t, S(3), S(4), "Hemos tenido mucha dificultad para robar el balón.", "JOSÉ MOURINHO")
    if mode == "subs": subs_board(b, t)
    if mode == "belli": C.lower_third(b, t, S(11), S(13), "Jude Bellingham", "Entra al descanso", "Gol y asistencia")
    if mode == "quote2": C.quote(b, t, S(13), S(14), "Pensaba que podía ganar sin Bellingham… quizá lo pensé de forma equivocada.", "JOSÉ MOURINHO")
    if mode == "score": final_score(b, t, S(14), END)
    if mode == "end": endcard(b, t - END)
    out = finish(b.convert("RGB")).convert("RGBA"); d = ImageDraw.Draw(out)
    if t < END and mode not in ("quote1", "quote2", "subs", "score"): T.subtitle_clean(d, WORDS, t, 1430)
    return out.convert("RGB")
if __name__ == "__main__":
    o = sys.argv[1]
    if "--sheet" in sys.argv:
        ts = [float(x) for x in sys.argv[sys.argv.index("--sheet") + 1:]]
        ims = [compose(t).resize((360, 640)) for t in ts]; sh = Image.new("RGB", (360 * len(ims), 640)); [sh.paste(im, (360 * i, 0)) for i, im in enumerate(ims)]; sh.save(o)
    else:
        sfx = o + ".wav"; C.sfx_track(sfx, TOTAL, whooshes=[S(4) - .2, S(7) - .2, S(9) - .2, S(10) - .2, S(13) - .2, S(14) - .2, END - .2], hits=[S(10) + 3.6 * (S(11) - S(10)) / 6.4])
        C.encode(compose, TOTAL, o, "/home/claude/antesdelos90-studio/music/glitter_and_gold-patrick_patrikios.mp3", sfx, gain=-12, voice="/tmp/claude-0/tts/voz_final.wav", voice_off=OFF)
