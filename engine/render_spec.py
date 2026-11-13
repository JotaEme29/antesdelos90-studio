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
  "events": [ {"type": "lines"|"count"|"arrow"|"zone"|"pill"|"ring", "t0": .., "t1": .., ...} ]
}
"""
import json, math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from flat import *
COL = {"yellow": YEL, "white": WHT, "green": GRN, "red": RED, "navy": NAVY, "grey": GREY}
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class Spec:
    def __init__(s, path):
        s.d = json.load(open(path)); d = s.d
        s.end = float(d["end"]); s.ec = d.get("endcard", {}); s.total = s.end + float(s.ec.get("dur", 3.0))
        s.team = d["team"]; s.riv = d.get("rivals"); s.cam = Cam(56, 166, 52.5, 0, 850)
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
        if s.riv and t >= s.riv.get("show", 0):                        # capa 2: rivales
            k = ease((t - s.riv.get("show", 0)) / .5); R_ = s.positions(s.riv, t)
            for x, z in sorted(R_, key=lambda p: -p[1]): disc(b, cam, x, z, RIVC, None, r=2.7, a=k)
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
        for i in sorted(range(len(P)), key=lambda i: -P[i][1]): disc(b, cam, P[i][0], P[i][1], YEL, nums[i], r=3.0, ring=rings.get(i))
        bp = s.ball(t, P)
        if bp: ball(b, cam, *bp)
        for e in E:                                                    # capa 4: etiquetas
            if e["type"] == "pill":
                fg = WHT if e.get("col") in ("red",) else NAVY
                pill(b, cam, e["at"][0], e["at"][1], e["text"], COL[e.get("col", "yellow")], fg, e.get("size", 34), t, e["t0"], (e["t1"] - e["t0"] - .3) if "t1" in e else None)
        title(b, s.d.get("kicker", ""), *(s.d["title"] + [None])[:2], t, 0); handle(b, s.d.get("handle", "@antesdelos90")); progress(b, t, s.end)
        cur = None
        for t0, txt in s.caps:
            if t >= t0: cur = (t0, txt)
        if cur and t < s.end: caption(b, cur[1], t, cur[0])
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
    else: encode(sp.compose, sp.total, out, os.path.join(ROOT, sp.d["music"]), sp.d.get("music_gain", -5))
