"""Estilo 'flat' v2: fondo negro, campo grande casi cenital, fichas planas, líneas entre unidades,
título fijo arriba, subtítulo con palabras clave. Supersampling x2 para bordes limpios."""
import math, os, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
W, H, FPS, SS = 1080, 1920, 30, 2
W2, H2 = W * SS, H * SS
BG = (11, 13, 15); YEL = (255, 204, 0); WHT = (244, 246, 248); NAVY = (14, 22, 34); RIVC = (222, 228, 236)
GRN = (52, 211, 120); RED = (240, 72, 72); GREY = (150, 158, 166)
FD = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts") + "/"
_F = {}
def font(size, w="Black"):
    k = (size, w)
    if k not in _F: _F[k] = ImageFont.truetype(FD + f"InterDisplay-{w}.otf", int(size * SS))
    return _F[k]
def ease(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
def back(x):
    x = max(0.0, min(1.0, x)); c = 1.7; return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2
def lerp2(a, b, e): return (a[0] + (b[0] - a[0]) * e, a[1] + (b[1] - a[1]) * e)
# ---------------------------------------------------------------- cámara casi cenital
FOC = 1700.0
class Cam:
    def __init__(s, el=66, d=150, tz=54.0, az=0.0, cy=1010):
        s.cy = cy; az, el = math.radians(az), math.radians(el)
        s.pos = np.array([d * math.sin(az) * math.cos(el), d * math.sin(el), tz - d * math.cos(az) * math.cos(el)])
        f = np.array([0, 0.0, tz]) - s.pos; s.f = f / np.linalg.norm(f)
        r = np.cross([0, 1, 0], s.f); s.r = r / np.linalg.norm(r); s.u = np.cross(s.f, s.r)
    def P(s, x, z, y=0.0):
        v = np.array([x, y, z]) - s.pos; dz = v @ s.f
        return ((W / 2 + FOC * (v @ s.r) / dz) * SS, (s.cy - FOC * (v @ s.u) / dz) * SS, FOC / dz)
PL, PW = 105.0, 68.0
def poly(d, cam, pts, fill=None, outline=None, w=0):
    q = [cam.P(x, z)[:2] for x, z in pts]; d.polygon(q, fill=fill)
    if outline: d.line(q + [q[0]], fill=outline, width=int(w * SS), joint="curve")
def pline(d, cam, pts, col, w):
    d.line([cam.P(x, z)[:2] for x, z in pts], fill=col, width=int(w * SS), joint="curve")
def arc(cx, cz, r, a0, a1, n=48): return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)), cz + r * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]
def pitch(b, cam):
    d = ImageDraw.Draw(b, "RGBA"); hx = PW / 2
    poly(d, cam, [(-hx - 3, -3), (hx + 3, -3), (hx + 3, PL + 3), (-hx - 3, PL + 3)], (30, 112, 58, 255))
    for i in range(12):
        z0, z1 = PL * i / 12, PL * (i + 1) / 12
        poly(d, cam, [(-hx, z0), (hx, z0), (hx, z1), (-hx, z1)], (38, 136, 70, 255) if i % 2 == 0 else (44, 148, 78, 255))
    L = (236, 244, 238, 220); w = 3.2
    pline(d, cam, [(-hx, 0), (hx, 0), (hx, PL), (-hx, PL), (-hx, 0)], L, w); pline(d, cam, [(-hx, PL / 2), (hx, PL / 2)], L, w)
    pline(d, cam, arc(0, PL / 2, 9.15, 0, 360, 64), L, w)
    for zs, sg in ((0, 1), (PL, -1)):
        pline(d, cam, [(-20.15, zs), (-20.15, zs + sg * 16.5), (20.15, zs + sg * 16.5), (20.15, zs)], L, w)
        pline(d, cam, [(-9.15, zs), (-9.15, zs + sg * 5.5), (9.15, zs + sg * 5.5), (9.15, zs)], L, w)
        pline(d, cam, arc(0, zs + sg * 11, 9.15, 37, 143, 24) if sg > 0 else arc(0, zs + sg * 11, 9.15, 217, 323, 24), L, w)
        poly(d, cam, [(-3.66, zs), (3.66, zs), (3.66, zs - sg * 1.6), (-3.66, zs - sg * 1.6)], (255, 255, 255, 170))
# ---------------------------------------------------------------- piezas
def disc(b, cam, x, z, col, num=None, r=1.9, a=1.0, ring=None, numcol=NAVY):
    if a <= .02: return
    d = ImageDraw.Draw(b, "RGBA"); cx, cy, sc = cam.P(x, z)
    rx = r * sc * SS; ry = rx * .80
    d.ellipse((cx - rx * 1.05, cy - ry * .55, cx + rx * 1.05, cy + ry * 1.25), fill=(0, 0, 0, int(80 * a)))    # sombra
    if ring: d.ellipse((cx - rx * 1.55, cy - ry * 1.55, cx + rx * 1.55, cy + ry * 1.55), outline=(*ring, int(230 * a)), width=int(4 * SS))
    d.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), fill=(*col, int(255 * a)), outline=(*NAVY, int(255 * a)), width=int(3 * SS))
    if num is not None:
        f = font(rx / SS * 1.05, "Black"); d.text((cx, cy + 1), str(num), font=f, fill=(*numcol, int(255 * a)), anchor="mm")
def ball(b, cam, x, z):
    d = ImageDraw.Draw(b, "RGBA"); cx, cy, sc = cam.P(x + 2.9, z - 2.2); r = .95 * sc * SS
    d.ellipse((cx - r, cy - r * .8, cx + r, cy + r * .8), fill=(255, 255, 255, 255), outline=(*NAVY, 255), width=int(2 * SS))
def seg(b, cam, a, c, col, e=1.0, w=5, alpha=210):
    if e <= .01: return
    d = ImageDraw.Draw(b, "RGBA"); p = cam.P(*a)[:2]; q = cam.P(*lerp2(a, c, e))[:2]
    d.line([p, q], fill=(*col, alpha), width=int(w * SS))
    for pt in (p, q): r = w * SS / 2; d.ellipse((pt[0] - r, pt[1] - r, pt[0] + r, pt[1] + r), fill=(*col, alpha))
def chain(b, cam, pts, col, e=1.0, w=5):
    n = len(pts) - 1
    for i in range(n): seg(b, cam, pts[i], pts[i + 1], col, ease(e * n - i), w)
def arrow(b, cam, a, c, col, e, w=5, dash=True):
    if e <= .01: return
    d = ImageDraw.Draw(b, "RGBA"); m = lerp2(a, c, e); p = cam.P(*a)[:2]; q = cam.P(*m)[:2]
    L = math.hypot(q[0] - p[0], q[1] - p[1]); n = max(1, int(L / (26 * SS)))
    for i in range(n):
        if dash and i % 2: continue
        u0, u1 = i / n, min(1, (i + 1) / n)
        d.line([(p[0] + (q[0] - p[0]) * u0, p[1] + (q[1] - p[1]) * u0), (p[0] + (q[0] - p[0]) * u1, p[1] + (q[1] - p[1]) * u1)], fill=(*col, 235), width=int(w * SS))
    ang = math.atan2(q[1] - p[1], q[0] - p[0]); s = 16 * SS
    d.polygon([q, (q[0] - s * math.cos(ang - .5), q[1] - s * math.sin(ang - .5)), (q[0] - s * math.cos(ang + .5), q[1] - s * math.sin(ang + .5))], fill=(*col, 235))
def zone(b, cam, x0, z0, x1, z1, col, a=1.0, fill=60):
    if a <= .02: return
    d = ImageDraw.Draw(b, "RGBA"); poly(d, cam, [(x0, z0), (x1, z0), (x1, z1), (x0, z1)], (*col, int(fill * a)), (*col, int(230 * a)), 3)
def label(b, cam, x, z, txt, size=40, col=WHT, a=1.0, t=None, t0=None):
    if a <= .02: return
    k = back((t - t0) / .35) if t is not None else 1
    cx, cy, _ = cam.P(x, z); f = font(size * max(.05, k), "Black"); d = ImageDraw.Draw(b, "RGBA")
    d.text((cx + 3 * SS, cy + 4 * SS), txt, font=f, fill=(0, 0, 0, int(150 * a)), anchor="mm")
    d.text((cx, cy), txt, font=f, fill=(*col, int(255 * a)), anchor="mm")
def pill(b, cam, x, z, txt, col, fg=NAVY, size=34, t=0, t0=0, dur=None):
    if t < t0 or (dur is not None and t > t0 + dur + .3): return
    k = back((t - t0) / .3); a = 1 if dur is None else 1 - ease((t - t0 - dur) / .3)
    if k <= .03 or a <= .02: return
    cx, cy, _ = cam.P(x, z); f = font(size * k, "Bold"); d = ImageDraw.Draw(b, "RGBA")
    bb = d.textbbox((0, 0), txt, font=f); w = bb[2] - bb[0] + 34 * SS * k; h = bb[3] - bb[1] + 22 * SS * k
    d.rounded_rectangle((cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2), radius=h / 2, fill=(*col, int(245 * a)))
    d.text((cx, cy), txt, font=f, fill=(*fg, int(255 * a)), anchor="mm")
# ---------------------------------------------------------------- texto de pantalla
# Zona segura: YouTube Shorts y TikTok tapan ~220 px arriba, ~420 px abajo y la columna de botones a la derecha.
CAP_Y, PROG_Y, CARD_Y = 1408, 1362, 496
def hexcol(h): h = h.lstrip("#"); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
def card(b, items, t, t0, t1=None):
    """Fichas de equipo/entrenador en la franja entre título y campo.
    items: [{"name": "INTER", "sub": "Simone Inzaghi", "colors": ["#0068A8", "#111111"]}, ...] (escudo genérico con los colores, no el oficial)"""
    d = ImageDraw.Draw(b, "RGBA"); k = back((t - t0) / .45)
    if t1 is not None: k *= 1 - ease((t - t1 + .3) / .3)
    if k <= .02: return
    fN, fS = font(38, "Black"), font(26, "SemiBold"); gap = 22 * SS; hgt = 96 * SS
    ws = [max(d.textlength(i["name"], font=fN), d.textlength(i.get("sub", ""), font=fS)) + (hgt if i.get("colors") else 30 * SS) + 34 * SS for i in items]
    x = W2 / 2 - (sum(ws) + gap * (len(ws) - 1)) / 2; y = CARD_Y * SS + (1 - k) * 30 * SS; a = int(255 * min(1, k))
    for i, w in zip(items, ws):
        d.rounded_rectangle((x, y - hgt / 2, x + w, y + hgt / 2), radius=18 * SS, fill=(24, 28, 34, int(235 * min(1, k))), outline=(255, 255, 255, int(40 * min(1, k))), width=int(2 * SS))
        tx = x + 26 * SS
        if i.get("colors"):                                            # escudo genérico: dos franjas con los colores del club
            c1, c2 = hexcol(i["colors"][0]), hexcol(i["colors"][-1]); sx, sw_, sh = x + 20 * SS, 44 * SS, 54 * SS; sy = y - sh / 2
            sh_pts = [(sx, sy), (sx + sw_, sy), (sx + sw_, sy + sh * .55), (sx + sw_ / 2, sy + sh), (sx, sy + sh * .55)]
            m = Image.new("L", b.size, 0); ImageDraw.Draw(m).polygon(sh_pts, fill=a)
            st = Image.new("RGBA", b.size, (*c1, 255)); ImageDraw.Draw(st).rectangle((sx + sw_ / 2, sy, sx + sw_, sy + sh), fill=(*c2, 255))
            b.paste(st, (0, 0), m); d.line(sh_pts + [sh_pts[0]], fill=(255, 255, 255, int(200 * min(1, k))), width=int(2.5 * SS), joint="curve")
            tx = x + 82 * SS
        if i.get("sub"):
            d.text((tx, y - 14 * SS), i["name"], font=fN, fill=(*WHT, a), anchor="lm"); d.text((tx, y + 22 * SS), i["sub"], font=fS, fill=(*YEL, a), anchor="lm")
        else: d.text((tx, y), i["name"], font=fN, fill=(*WHT, a), anchor="lm")
        x += w + gap
def caption_words(b, words, t, y=CAP_Y):
    """Subtítulo palabra a palabra: la que suena va en caja amarilla; las clave, en amarillo."""
    d = ImageDraw.Draw(b, "RGBA"); f = font(52, "Black"); sp = d.textlength(" ", font=f); maxw = 860 * SS
    lines, cur, cw = [], [], 0
    for w in words:
        ww = d.textlength(w[0], font=f)
        if cur and cw + sp + ww > maxw: lines.append(cur); cur, cw = [], 0
        cur.append((w, ww)); cw += (sp if len(cur) > 1 else 0) + ww
    if cur: lines.append(cur)
    k = ease((t - words[0][1]) / .2)
    for j, ln in enumerate(lines[:2]):
        tw = sum(ww for _, ww in ln) + sp * (len(ln) - 1); x = W2 / 2 - tw / 2; yy = (y + 70 * j + (1 - k) * 12) * SS
        for (w, ts, te, key), ww in ln:
            on = ts <= t < max(te, ts + .12)
            if on:
                d.rounded_rectangle((x - 10 * SS, yy - 36 * SS, x + ww + 10 * SS, yy + 34 * SS), radius=12 * SS, fill=(*YEL, int(255 * k)))
                d.text((x, yy), w, font=f, fill=(*NAVY, int(255 * k)), anchor="lm")
            else:
                d.text((x + 2 * SS, yy + 3 * SS), w, font=f, fill=(0, 0, 0, int(170 * k)), anchor="lm")
                d.text((x, yy), w, font=f, fill=(*(YEL if key else WHT), int(255 * k * (1 if t >= ts else .55))), anchor="lm")
            x += ww + sp
def title(b, kicker, l1, l2=None, t=9, t0=0):
    d = ImageDraw.Draw(b, "RGBA"); k = ease((t - t0) / .4)
    d.text((W2 / 2, 240 * SS), kicker, font=font(30, "Bold"), fill=(*YEL, int(255 * k)), anchor="mm")
    d.text((W2 / 2, 302 * SS), l1, font=font(64, "Black"), fill=(*WHT, int(255 * k)), anchor="mm")
    if l2: d.text((W2 / 2, 374 * SS), l2, font=font(64, "Black"), fill=(*WHT, int(255 * k)), anchor="mm")
def caption(b, txt, t, t0, y=CAP_Y):
    """txt con *clave* en amarillo; '|' separa líneas."""
    k = ease((t - t0) / .25); d = ImageDraw.Draw(b, "RGBA"); f = font(50, "Bold")
    for j, line in enumerate(txt.split("|")):
        parts = line.split("*"); widths = [d.textlength(p, font=f) for p in parts]; x = W2 / 2 - sum(widths) / 2
        yy = (y + 68 * j + (1 - k) * 14) * SS
        for i, p in enumerate(parts):
            col = YEL if i % 2 else WHT
            d.text((x + 2 * SS, yy + 3 * SS), p, font=f, fill=(0, 0, 0, int(180 * k)), anchor="lm")
            d.text((x, yy), p, font=f, fill=(*col, int(255 * k)), anchor="lm"); x += widths[i]
def progress(b, t, T):
    d = ImageDraw.Draw(b, "RGBA"); x0, x1, y = 140 * SS, (W - 140) * SS, PROG_Y * SS
    d.rounded_rectangle((x0, y, x1, y + 6 * SS), radius=3 * SS, fill=(255, 255, 255, 40))
    d.rounded_rectangle((x0, y, x0 + (x1 - x0) * min(1, t / T), y + 6 * SS), radius=3 * SS, fill=(*YEL, 230))
def handle(b, txt="@antesdelos90"):
    ImageDraw.Draw(b, "RGBA").text(((W - 80) * SS, 430 * SS), txt, font=font(26, "SemiBold"), fill=(255, 255, 255, 120), anchor="rm")
_MARK = None
def _mark():
    global _MARK
    if _MARK is None:
        p = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "brand", "mark_transparente.png")
        _MARK = Image.open(p).convert("RGBA") if os.path.isfile(p) else False
    return _MARK
def endcard(b, u, q1, q2):
    d = ImageDraw.Draw(b, "RGBA"); d.rectangle((0, 0, W2, H2), fill=(*BG, int(235 * ease(u / .4))))
    m = _mark(); k0 = back((u - .05) / .4)
    if m and k0 > .05:                                     # logo del canal encima de la pregunta
        w = int(300 * SS * k0); h = int(w * m.height / m.width); mm = m.resize((w, h), Image.LANCZOS)
        b.paste(mm, (int(W2 / 2 - w / 2), int(600 * SS - h / 2)), mm)
    k = back((u - .1) / .4)
    if k > .05:
        d.text((W2 / 2, 830 * SS), q1, font=font(84 * k, "Black"), fill=WHT, anchor="mm")
        d.text((W2 / 2, 925 * SS), q2, font=font(84 * k, "Black"), fill=YEL, anchor="mm")
    k2 = back((u - .35) / .4)
    if k2 > .05:
        w, h = 620 * SS * k2, 110 * SS * k2; d.rounded_rectangle((W2 / 2 - w / 2, 1080 * SS - h / 2, W2 / 2 + w / 2, 1080 * SS + h / 2), radius=h / 2, fill=YEL)
        d.text((W2 / 2, 1080 * SS), "@antesdelos90", font=font(54 * k2, "Black"), fill=NAVY, anchor="mm")
    d.text((W2 / 2, 1200 * SS), "Sistemas de juego · cada semana", font=font(36, "SemiBold"), fill=(200, 206, 212, int(255 * ease((u - .6) / .4))), anchor="mm")
def finish(b): return b.resize((W, H), Image.LANCZOS)
def encode(compose, total, out, music, gain=-5):
    n = int(round(total * FPS)); tmp = out + ".part.mp4"
    af = f"atrim=0:{total:.2f},volume={gain}dB,afade=t=in:d=0.3,afade=t=out:st={total - 1.6:.2f}:d=1.6,aresample=44100,loudnorm=I=-15:TP=-1.5"
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-framerate", str(FPS), "-i", "-",
                            "-i", music, "-map", "0:v", "-map", "1:a", "-af", af, "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p",
                            "-c:a", "aac", "-b:a", "160k", "-t", f"{total:.3f}", "-movflags", "+faststart", tmp], stdin=subprocess.PIPE)
    for k in range(n):
        enc.stdin.write(compose(k / FPS).tobytes())
        if k % 150 == 0: print("frame", k, "/", n, flush=True)
    enc.stdin.close()
    if enc.wait() == 0: os.replace(tmp, out); print("OK", out, round(total, 1), "s")
def sheet(compose, times, out):
    ims = [compose(t).resize((W // 3, H // 3), Image.LANCZOS) for t in times]
    cols = 4; rows = math.ceil(len(ims) / cols); s = Image.new("RGB", (cols * W // 3, rows * H // 3))
    for i, im in enumerate(ims): s.paste(im, ((i % cols) * W // 3, (i // cols) * H // 3))
    s.save(out, quality=90)
