"""Edición de vídeos a cámara de Miguel (@soymigueldelfutbol): subtítulos palabra a palabra, zooms de ritmo,
tarjetas animadas sobre el pecho (no tapan la cara), rótulo superior, cierre con pregunta y música baja.
Uso: python engine/talk.py edit.json salida.mp4 [--sheet t1 t2 ...]
edit.json: {"video": ..., "words": [[ini, fin, "texto"], ...], "fix": {"idx": "palabra"}, "keys": [...],
            "top": [[t0, t1, "rótulo"]], "cards": [[t0, t1, tipo, {...}]], "zooms": [t...], "end": {...}, "music": ...}"""
import sys, os, json, math, subprocess
import numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from flat import font as _font, ease, back, YEL, WHT, NAVY, BG, SS
def font(px, w="Black"): return _font(max(1, px / SS), w)   # flat.font escala por SS; aquí trabajamos a 1080x1920

W, H, FPS = 1080, 1920, 30

def norm(s): return "".join(c for c in s.lower() if c.isalnum())

def frames(path, t0=0):
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", str(t0), "-i", path, "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-"], stdout=subprocess.PIPE)
    while True:
        b = p.stdout.read(W * H * 3)
        if len(b) < W * H * 3: break
        yield Image.frombytes("RGB", (W, H), b)

def zoom_at(t, zs):
    """pequeños 'punch-in' (1.0→1.07) en los cambios de frase; se mantienen y vuelven suaves."""
    z = 1.0
    for i, t0 in enumerate(zs):
        if t >= t0: z = 1.0 + (.07 if i % 2 == 0 else 0.0) * ease((t - t0) / .18) + (.0 if i % 2 == 0 else .07 * (1 - ease((t - t0) / .25)))
    return z

def apply_zoom(im, z, cy=.36):
    if z <= 1.001: return im
    w, h = int(W / z), int(H / z); x0 = (W - w) // 2; y0 = int((H - h) * cy / .5 * .5)
    return im.crop((x0, y0, x0 + w, y0 + h)).resize((W, H), Image.BILINEAR)

def subtitle_clean(d, words, t, y):
    """subtítulo limpio: 2–3 palabras, blanco con contorno, la que suena en amarillo; sin cajas."""
    groups, cur = [], []
    for w in words:
        cur.append(w)
        if len(cur) >= 3 or w[2].endswith((".", ",", "?", "!")): groups.append(cur); cur = []
    if cur: groups.append(cur)
    g = None
    for gr in groups:
        if gr[0][0] - .05 <= t: g = gr
    if not g or t > g[-1][1] + .5: return
    f = font(70, "Black"); sp = d.textlength(" ", font=f)
    ws = [d.textlength(w[2], font=f) for w in g]; x = W / 2 - (sum(ws) + sp * (len(ws) - 1)) / 2
    k = min(1, back((t - g[0][0]) / .15))
    for (a, b, s, key), ww in zip(g, ws):
        on = a <= t < max(b, a + .1)
        d.text((x, y + (1 - k) * 10), s, font=f, fill=(*(YEL if on else WHT), 255), stroke_width=6, stroke_fill=(0, 0, 0, 230), anchor="lm")
        x += ww + sp

def subtitle(d, words, t, y=1440):
    """frase actual (bloques de ~4 palabras), palabra que suena en caja amarilla."""
    groups, cur = [], []
    for w in words:
        cur.append(w)
        if len(cur) >= 3 or w[2].endswith((".", ",", "?", "!")): groups.append(cur); cur = []
    if cur: groups.append(cur)
    g = None
    for gr in groups:
        if gr[0][0] - .05 <= t: g = gr
    if not g or t > g[-1][1] + .6: return
    f = font(80, "Black"); sp = d.textlength(" ", font=f) + 18
    txt = [w[2] for w in g]; ws = [d.textlength(x, font=f) for x in txt]
    x = W / 2 - (sum(ws) + sp * (len(ws) - 1)) / 2
    k = back((t - g[0][0]) / .18)
    for (a, b, s, key), ww in zip(g, ws):
        on = a <= t < max(b, a + .1)
        yy = y + (1 - min(1, k)) * 14
        if on:
            d.rounded_rectangle((x - 10, yy - 50, x + ww + 10, yy + 48), radius=16, fill=YEL)
            d.text((x, yy), s, font=f, fill=NAVY, anchor="lm")
        else:
            d.text((x + 3, yy + 4), s, font=f, fill=(0, 0, 0, 200), anchor="lm")
            d.text((x, yy), s, font=f, fill=(*(YEL if key else WHT), 255 if t >= a else 150), stroke_width=3, stroke_fill=(0, 0, 0), anchor="lm")
        x += ww + sp

def top_label(d, t, t0, t1, txt):
    if not (t0 <= t < t1): return
    k = ease((t - t0) / .3) * (1 - ease((t - t1 + .3) / .3)); f = font(46, "Black"); tw = d.textlength(txt, font=f)
    x0 = W / 2 - tw / 2 - 28; y = 262
    d.rounded_rectangle((x0, y - 42, x0 + tw + 56, y + 42), radius=42, fill=(*YEL, int(255 * k)))
    d.text((W / 2, y), txt, font=f, fill=(*NAVY, int(255 * k)), anchor="mm")

def panel(d, t, t0, t1, y0=990, y1=1330):
    k = ease((t - t0) / .3) * (1 - ease((t - t1 + .3) / .3))
    d.rounded_rectangle((60, y0 + (1 - k) * 40, W - 60, y1 + (1 - k) * 40), radius=28, fill=(14, 18, 22, int(230 * k)), outline=(*YEL, int(180 * k)), width=3)
    return k

def card(d, t, t0, t1, kind, o):
    if not (t0 <= t < t1): return
    k = panel(d, t, t0, t1); a = int(255 * k); u = t - t0
    if kind == "history":          # gran año + dos líneas
        d.text((W / 2, 1080), o["big"], font=font(170 * (.8 + .2 * min(1, back(u / .35))), "Black"), fill=(*YEL, a), anchor="mm")
        d.text((W / 2, 1200), o["l1"], font=font(50, "Black"), fill=(*WHT, a), anchor="mm")
        d.text((W / 2, 1268), o["l2"], font=font(38, "SemiBold"), fill=(200, 206, 212, a), anchor="mm")
    elif kind == "stats":          # varios contadores que suben
        n = len(o["items"]); cw = (W - 120) / n
        for i, (val, lab) in enumerate(o["items"]):
            cx = 60 + cw * (i + .5); e = ease((u - .15 - i * .25) / .6)
            v = val if isinstance(val, str) else str(int(round(val * e)))
            d.text((cx, 1120), v, font=font(150, "Black"), fill=(*YEL, int(a * min(1, e * 2))), anchor="mm")
            d.text((cx, 1250), lab, font=font(40, "Bold"), fill=(*WHT, int(a * min(1, e * 2))), anchor="mm")
    elif kind == "chips":          # dos o tres datos en filas
        for i, (ico, txt) in enumerate(o["items"]):
            e = ease((u - .1 - i * .3) / .3); y = 1090 + i * 130
            d.text((100, y), ico, font=font(64, "Black"), fill=(*YEL, int(a * e)), anchor="lm")
            d.text((175, y), txt, font=font(56, "Bold"), fill=(*WHT, int(a * e)), anchor="lm")
    elif kind == "versus":
        d.text((W / 2, 1110), o["l1"], font=font(88, "Black"), fill=(*WHT, a), anchor="mm")
        d.text((W / 2, 1220), o["l2"], font=font(56, "Black"), fill=(*YEL, a), anchor="mm")

def endcard(d, t, t0, o):
    if t < t0: return
    u = t - t0; k = ease(u / .3)
    d.rectangle((0, 0, W, H), fill=(*BG, int(150 * k)))
    kk = back(u / .35)
    if kk > .05:
        d.text((W / 2, 880), o["q1"], font=font(96 * kk, "Black"), fill=WHT, stroke_width=4, stroke_fill=(0, 0, 0), anchor="mm")
        d.text((W / 2, 980), o["q2"], font=font(96 * kk, "Black"), fill=YEL, stroke_width=4, stroke_fill=(0, 0, 0), anchor="mm")
    k2 = back((u - .25) / .35)
    if k2 > .05:
        w, h = 640 * k2, 104 * k2; d.rounded_rectangle((W / 2 - w / 2, 1130 - h / 2, W / 2 + w / 2, 1130 + h / 2), radius=h / 2, fill=YEL)
        d.text((W / 2, 1130), o["handle"], font=font(50 * k2, "Black"), fill=NAVY, anchor="mm")

def build(E):
    words = [list(w) for w in E["words"]]
    for i, s in E.get("fix", {}).items(): words[int(i)][2] = s
    keys = {norm(k) for k in E.get("keys", [])}
    W4 = [(a, b, s, norm(s) in keys) for a, b, s in words if s]
    def overlay(im, t):
        im = apply_zoom(im, zoom_at(t, E.get("zooms", [])))
        im = im.convert("RGBA"); lay = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        clean = E.get("style", "clean") == "clean"        # estilo por defecto (Miguel): limpio, la cara manda
        if not clean:
            for t0, t1, txt in E.get("top", []): top_label(d, t, t0, t1, txt)
        for t0, t1, kind, o in E.get("cards", []):
            if not clean or kind in E.get("allow", []): card(d, t, t0, t1, kind, o)
        if t < E["end"]["t"] and E.get("subs", not clean):
            yy = E.get("subs_y", 1440)
            for a, b, y2 in E.get("subs_move", []):
                if a <= t < b: yy = y2
            (subtitle_clean if E.get("sub_style") == "clean" else subtitle)(d, W4, t, yy)
        endcard(d, t, E["end"]["t"], E["end"])
        im.alpha_composite(lay); return im.convert("RGB")
    return overlay

def render(E, out):
    ov = build(E); dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", E["video"]], capture_output=True, text=True).stdout)
    total = dur + float(E["end"].get("tail", 0.0))
    if not E.get("music"):
        fc = "[1:a]anull[a]"
        enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-framerate", str(FPS), "-i", "-",
                                "-i", E["video"], "-filter_complex", fc, "-map", "0:v", "-map", "[a]", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                                "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-t", f"{total:.3f}", "-movflags", "+faststart", out], stdin=subprocess.PIPE)
        n = 0
        for im in frames(E["video"]): enc.stdin.write(ov(im, n / FPS).tobytes()); n += 1
        enc.stdin.close(); enc.wait(); print("OK", out, round(n / FPS, 1)); return
    fc = (f"[0:a]highpass=f=80,acompressor=threshold=-20dB:ratio=3,apad,atrim=0:{total:.2f},asplit=2[v][k];"
          f"[1:a]atrim=0:{total:.2f},volume={E.get('music_db', -20)}dB,afade=t=out:st={total - 1.2:.2f}:d=1.2[m0];"
          f"[m0][k]sidechaincompress=threshold=0.04:ratio=6:attack=15:release=250[m];[v][m]amix=inputs=2:normalize=0,loudnorm=I=-14:TP=-1.5[a]")
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-framerate", str(FPS), "-i", "-",
                            "-i", E["video"], "-stream_loop", "-1", "-i", E["music"], "-filter_complex", fc.replace("[0:a]", "[1:a]", 1).replace("[1:a]atrim", "[2:a]atrim"),
                            "-map", "0:v", "-map", "[a]", "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k",
                            "-t", f"{total:.3f}", "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    last = None; n = 0
    for im in frames(E["video"]):
        t = n / FPS; enc.stdin.write(ov(im, t).tobytes()); last = im; n += 1
    while n / FPS < total:                       # cola: último fotograma congelado bajo la tarjeta final
        enc.stdin.write(ov(last, n / FPS).tobytes()); n += 1
    enc.stdin.close(); enc.wait(); print("OK", out, round(total, 1))

if __name__ == "__main__":
    E = json.load(open(sys.argv[1])); out = sys.argv[2]
    if "--sheet" in sys.argv:
        ts = [float(x) for x in sys.argv[sys.argv.index("--sheet") + 1:]]; ov = build(E); ims = []
        for t in ts:
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(min(t, 33)), "-i", E["video"], "-vframes", "1", "-s", f"{W}x{H}", "/tmp/claude-0/_f.png"])
            ims.append(ov(Image.open("/tmp/claude-0/_f.png").convert("RGB"), t).resize((432, 768)))
        sh = Image.new("RGB", (432 * len(ims), 768)); [sh.paste(im, (432 * i, 0)) for i, im in enumerate(ims)]; sh.save(out, quality=85)
    else: render(E, out)
