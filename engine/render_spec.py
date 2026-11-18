#!/usr/bin/env python3
"""Renderiza un vídeo vertical a partir de un spec JSON (estilo flat de @antesdelos90).

Uso:
  python engine/render_spec.py queue/<slug>/spec.json out.mp4      # vídeo completo
  python engine/render_spec.py queue/<slug>/spec.json hoja.jpg --sheet 1 5 9   # fotogramas sueltos

Formato del spec (todas las posiciones en metros: x = ancho (-34..34), z = largo (0..105), atacamos hacia +z):
{
  "kicker": "4-2-3-1 · SISTEMAS DE JUEGO", "title": ["Línea 1", "Línea 2"],
  "music": "music/archivo.mp3", "end": 28.0,                 # segundos de contenido; luego tarjeta final
  "endcard": {"q1": "¿Lo usarías", "q2": "en tu equipo?", "dur": 3.0},
  "team":   {"nums": [...11], "base": [[x,z]...11], "moves": [{"t": 3, "dur": 1.8, "to": {"1": [x,z], "4": [x,z]}}]},
  "rivals": {"show": 13.0, "base": [[x,z]...], "moves": [...]},       # opcional
  "ball":   [[t, i], ...]   # i = índice del jugador que la tiene desde t (pase de 0,55 s); o [t, [x,z]]
  "captions": [[t, "Texto con *clave*|segunda línea"], ...],
  "hook": {"text": "¿Te presionan con dos|y no sales?", "t1": 2.0},   # gancho grande en el primer segundo (obligatorio)
  "events": [ {"type": "lines"|"count"|"arrow"|"zone"|"pill"|"ring"|"card", "t0": .., "t1": .., ...} ]
  card: {"type": "card", "t0": .., "t1": .., "items": [{"name": "INTER", "sub": "Simone Inzaghi", "colors": ["#0068A8", "#111111"]}]}
        fichas de equipo/entrenador: escudo GENÉRICO con los colores del club (nunca el escudo oficial ni fotos)
}

VÍDEO CON VOZ (Miguel graba el guion):
  "voice": true, "script": ["párrafo 1", ...], "keywords": ["4-4-2", "Simeone", ...], "captions": "auto", "end": "auto"
  Cualquier tiempo puede ser una frase del guion: "@los laterales suben" (inicio de esa frase en la voz),
  con desfase opcional: "@los laterales suben+0.4". Los subtítulos salen solos de la transcripción.
  Necesita build/<slug>/voice.wav y words.json (los crea engine/voice.py).
"""
import json, math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from flat import *
COL = {"yellow": YEL, "white": WHT, "green": GRN, "red": RED, "navy": NAVY, "grey": GREY}
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

import re, unicodedata, subprocess
def norm(w):
    w = unicodedata.normalize("NFD", w.lower()); w = "".join(c for c in w if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9%\-]", "", w)

class Voice:
    """Alinea el GUION con la voz grabada: cada palabra del guion recibe su tiempo.
    Los subtítulos salen del guion (no de la transcripción, que puede equivocarse)."""
    OFF = 0.35
    def __init__(s, build_dir, script):
        import difflib
        s.sw = " ".join(script).split()                              # palabras del guion, tal cual
        wj = os.path.join(build_dir, "words.json"); s.wav = os.path.join(build_dir, "voice.wav")
        if not os.path.isfile(wj):                                   # aún sin grabación: tiempos estimados (solo para previsualizar)
            rate = 2.6; s.W = [{"w": w, "s": i / rate, "e": (i + .85) / rate} for i, w in enumerate(s.sw)]; s.dur = len(s.sw) / rate; s.wav = None
        else:
            s.W = json.load(open(wj))
            s.dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", s.wav], capture_output=True, text=True).stdout)
        a = [norm(w) for w in s.sw]; b = [norm(w["w"]) for w in s.W]
        T = [None] * len(a)
        for m in difflib.SequenceMatcher(None, a, b, autojunk=False).get_matching_blocks():
            for k in range(m.size): T[m.a + k] = (s.W[m.b + k]["s"], s.W[m.b + k]["e"])
        known = [i for i, x in enumerate(T) if x]                    # interpolar las que no casan
        if not known: T = [(s.dur * i / len(a), s.dur * (i + 1) / len(a)) for i in range(len(a))]
        else:
            for i in range(len(a)):
                if T[i]: continue
                lo = max([k for k in known if k < i], default=None); hi = min([k for k in known if k > i], default=None)
                t0 = T[lo][1] if lo is not None else 0.0; t1 = T[hi][0] if hi is not None else s.dur
                n0 = lo if lo is not None else -1; n1 = hi if hi is not None else len(a)
                f0 = (i - n0) / (n1 - n0); f1 = (i + 1 - n0) / (n1 - n0); T[i] = (t0 + (t1 - t0) * f0 - .0, t0 + (t1 - t0) * f1)
        s.T = T; s.na = a
    def at(s, phrase):
        q = [norm(x) for x in phrase.split() if norm(x)]
        for i in range(len(s.na) - len(q) + 1):
            if s.na[i:i + len(q)] == q: return s.OFF + s.T[i][0]
        best, bi = 0, None
        for i in range(len(s.na)):
            k = sum(1 for j, t in enumerate(q) if i + j < len(s.na) and s.na[i + j] == t)
            if k > best: best, bi = k, i
        if bi is None or best < max(1, int(len(q) * .6)): raise SystemExit(f"Frase no encontrada en el guion: {phrase!r}")
        return s.OFF + s.T[bi][0]
    def captions(s, keywords):
        keys = {norm(k) for k in keywords}; out, cur, c0 = [], [], None
        for i, w in enumerate(s.sw):
            if c0 is None: c0 = s.T[i][0]
            cur.append(w); gap = (s.T[i + 1][0] - s.T[i][1]) if i + 1 < len(s.sw) else 9
            if len(" ".join(cur)) > 26 or w[-1:] in ".,;:?!" or gap > .35 or i == len(s.sw) - 1:
                txt = " ".join(("*" + x + "*") if norm(x) in keys else x for x in cur).replace("* *", " ")
                ws = [(x, s.OFF + s.T[i - len(cur) + 1 + j][0], s.OFF + s.T[i - len(cur) + 1 + j][1], norm(x) in keys) for j, x in enumerate(cur)]
                out.append([s.OFF + c0, txt, ws]); cur, c0 = [], None
        return out

class Spec:
    def __init__(s, path):
        s.d = json.load(open(path)); d = s.d; s.voice = None
        if d.get("voice"):
            slug = os.path.basename(os.path.dirname(os.path.abspath(path)))
            s.voice = Voice(os.path.join(ROOT, "build", slug), d.get("script", []))
            def res(v):
                if isinstance(v, str) and v.startswith("@"):
                    m = re.match(r"@(.*?)([+-]\d+(?:\.\d+)?)?$", v); return s.voice.at(m.group(1).strip()) + float(m.group(2) or 0)
                return v
            def walk(o):
                if isinstance(o, dict): return {k: (res(v) if k in ("t", "t0", "t1", "show", "hide") else walk(v)) for k, v in o.items()}
                if isinstance(o, list): return [walk(x) for x in o]
                return o
            d = s.d = walk(d)
            d["ball"] = [[res(t), h] for t, h in d.get("ball", [])]
            s.vend = s.voice.dur + Voice.OFF + 0.4
            if d.get("end", "auto") == "auto":                  # si el guion acaba en pregunta, la tarjeta final sale mientras Miguel la dice (no se repite)
                last = d.get("script", [""])[-1].strip()
                if last.endswith("?") or "comentarios" in last.lower():
                    d["end"] = s.voice.OFF + s.voice.T[len(s.voice.sw) - len(last.split())][0] - 0.15
                    q = last.split("?")[0].strip() + "?"; ws_ = q.split(); h = (len(ws_) + 1) // 2
                    d.setdefault("endcard", {}).setdefault("q1", " ".join(ws_[:h])); d["endcard"].setdefault("q2", " ".join(ws_[h:]))
                else: d["end"] = s.vend
            if d.get("captions") == "auto": d["captions"] = s.voice.captions(d.get("keywords", []))
            else: d["captions"] = [[res(t), c] for t, c in d.get("captions", [])]
        s.end = float(d["end"]); s.ec = d.get("endcard", {}); s.total = max(s.end + float(s.ec.get("dur", 3.0)), getattr(s, "vend", 0) + 1.2)
        s.team = d["team"]; Spec._team = s.team; s.riv = d.get("rivals"); s.cam = Cam(56, 200, 52.5, 0, 900)
        s.caps = sorted(d.get("captions", []), key=lambda c: c[0]); s.ev = d.get("events", [])
        s.ballseq = d.get("ball", [])
    # posiciones: cada movimiento interpola desde donde estaba el jugador al empezar
    @staticmethod
    def positions(group, t, wobble=True):
        P = [tuple(p) for p in group["base"]]
        for m in sorted(group.get("moves", []), key=lambda m: m["t"]):
            if t <= m["t"]: break
            e = ease((t - m["t"]) / max(.05, m.get("dur", 1.0))); st = m.get("stagger", 0.0)
            for k, (i, tgt) in enumerate(sorted(m["to"].items(), key=lambda kv: int(kv[0]))):
                i = int(i); ek = ease((t - m["t"] - st * k) / max(.05, m.get("dur", 1.0))) if st else e
                P[i] = lerp2(P[i], tuple(tgt), ek)
        if group is getattr(Spec, "_team", None) and t < 1.1:          # entrada: el equipo se abre desde el centro en el primer segundo
            e = ease(t / 1.1); P = [lerp2((x * .78, 52.5 + (z - 52.5) * .82), (x, z), e) for x, z in P]
        if wobble: P = [(x + .35 * math.sin(t * 2.2 + i * 1.7), z + .35 * math.cos(t * 1.9 + i * 2.3)) for i, (x, z) in enumerate(P)]
        return P
    def ball(s, t, P):
        if not s.ballseq: return None
        def at(h): return P[h] if isinstance(h, int) else tuple(h)
        cur = at(s.ballseq[0][1])
        for k in range(1, len(s.ballseq)):
            tp, h = s.ballseq[k]
            if t < tp: return cur
            e = ease((t - tp) / .55); cur = lerp2(at(s.ballseq[k - 1][1]), at(h), e) if e < 1 else at(h)
        return cur
    def active(s, e, t): return e.get("t0", 0) <= t < e.get("t1", 1e9)
    def fade(s, e, t, fin=.35):
        a = ease((t - e.get("t0", 0)) / fin)
        if "t1" in e: a *= 1 - ease((t - e["t1"] + .3) / .3)
        return a
    def compose(s, t):
        b = Image.new("RGB", (W2, H2), BG); cam = s.cam; pitch(b, cam)
        P = s.positions(s.team, t); E = [e for e in s.ev if s.active(e, t)]
        for e in E:                                                    # capa 1: zonas
            if e["type"] == "zone":
                a = s.fade(e, t) * ((.75 + .25 * math.sin(t * 6)) if e.get("pulse") else 1)
                zone(b, cam, *e["rect"], COL[e.get("col", "yellow")], a)
        if s.riv and s.riv.get("show", 0) <= t < s.riv.get("hide", 1e9):                        # capa 2: rivales
            k = ease((t - s.riv.get("show", 0)) / .5); R_ = s.positions(s.riv, t)
            for x, z in sorted(R_, key=lambda p: -p[1]): disc(b, cam, x, z, RIVC, None, r=3.0, a=k)
        for e in E:                                                    # capa 3: líneas, flechas
            c = COL[e.get("col", "yellow")]
            if e["type"] == "lines":
                prog = ease((t - e["t0"]) / e.get("draw", 1.0)) * s.fade(e, t, .01)
                for g in e["groups"]: chain(b, cam, [P[i] for i in g], c, prog, e.get("w", 6))
            elif e["type"] == "arrow":
                arrow(b, cam, tuple(e["from"]), tuple(e["to"]), c, ease((t - e["t0"]) / e.get("draw", 1.4)) * s.fade(e, t, .01), 5, e.get("dash", True))
            elif e["type"] == "count":
                label(b, cam, e["at"][0], e["at"][1], e["text"], e.get("size", 64), c, s.fade(e, t, .01), t, e["t0"])
        rings = {}
        for e in E:
            if e["type"] == "ring":
                for i in e["players"]: rings[i] = COL[e.get("col", "white")]
        nums = s.team["nums"]
        for i in sorted(range(len(P)), key=lambda i: -P[i][1]): disc(b, cam, P[i][0], P[i][1], YEL, nums[i], r=3.35, ring=rings.get(i))
        bp = s.ball(t, P)
        if bp: ball(b, cam, *bp)
        for e in E:                                                    # capa 4: etiquetas
            if e["type"] == "pill":
                fg = WHT if e.get("col") in ("red",) else NAVY
                pill(b, cam, e["at"][0], e["at"][1], e["text"], COL[e.get("col", "yellow")], fg, e.get("size", 34), t, e["t0"], (e["t1"] - e["t0"] - .3) if "t1" in e else None)
        title(b, s.d.get("kicker", ""), *(s.d["title"] + [None])[:2], t, 0); handle(b, s.d.get("handle", "@antesdelos90")); progress(b, t, s.end)
        for e in E:
            if e["type"] == "card": card(b, e["items"], t, e["t0"], e.get("t1"))
        hk = s.d.get("hook")
        hk_on = bool(hk) and t < float(hk.get("t1", 2.0))
        if hk_on: hook(b, hk["text"], t, float(hk.get("t1", 2.0)))
        cur = None
        for c in s.caps:
            if t >= c[0]: cur = c
        if cur and t < s.end and not hk_on:
            if len(cur) > 2 and cur[2]: caption_words(b, cur[2], t)
            else: caption(b, cur[1], t, cur[0])
        if t >= s.end: endcard(b, t - s.end, s.ec.get("q1", "¿Y tu equipo?"), s.ec.get("q2", ""))
        return finish(b)

def thumbnail(spec, out, t=None):
    """Portada 1080x1920 = el fotograma más 'lleno' (por defecto, 60 % del vídeo)."""
    spec.compose(t if t is not None else spec.end * .6).save(out, quality=92)

if __name__ == "__main__":
    sp = Spec(sys.argv[1]); out = sys.argv[2]
    if "--sheet" in sys.argv:
        ts = [float(x) for x in sys.argv[sys.argv.index("--sheet") + 1:]]; sheet(sp.compose, ts, out)
    elif out.endswith(".jpg"): thumbnail(sp, out)
    else:
        music = os.path.join(ROOT, sp.d["music"])
        if sp.voice:
            if not sp.voice.wav: raise SystemExit("Falta la grabación: ejecuta antes engine/voice.py (o sube voz.m4a)")
            mix = out + ".mix.wav"; T = sp.total
            fc = (f"[0:a]adelay={int(Voice.OFF * 1000)},apad,atrim=0:{T:.2f},asplit=2[v][k];"
                  f"[1:a]aloop=loop=-1:size=2e9,atrim=0:{T:.2f},volume=-9dB,afade=t=in:d=0.6,afade=t=out:st={T - 2:.2f}:d=2[m];"
                  f"[m][k]sidechaincompress=threshold=0.03:ratio=5:attack=20:release=900[d];[v][d]amix=inputs=2:normalize=0[a]")
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", sp.voice.wav, "-i", music, "-filter_complex", fc, "-map", "[a]", "-ar", "48000", mix], check=True)
            encode(sp.compose, T, out, mix, 0); os.remove(mix)
        else: encode(sp.compose, sp.total, out, music, sp.d.get("music_gain", -5))
