"""Estilo 'cine' (v3): cámara 3D que se mueve entre planos, campo oscuro, jugadores en 3D con nombre,
titular que cambia en cada bloque, subtítulos que entran palabra a palabra y efectos de sonido.
Inspirado en lo que funciona en los canales grandes de táctica (planos cambiantes, historia real con nombres,
gancho provocador), no en una plantilla fija."""
import math, os, subprocess, wave, random
import numpy as np
from PIL import Image, ImageDraw
from flat import (W, H, FPS, SS, W2, H2, BG, YEL, WHT, NAVY, font, ease, back, lerp2, FOC, PL, PW, arc, _mark)

# ------------------------------------------------------------------ cámara con objetivo libre (x, z)
class Cam:
    def __init__(s, el=50, d=150, tx=0.0, tz=52.5, az=0.0, cy=900, roll=0.0):
        s.cy = cy; a, e = math.radians(az), math.radians(el)
        tgt = np.array([tx, 0.0, tz])
        s.pos = tgt + np.array([d * math.sin(a) * math.cos(e), d * math.sin(e), -d * math.cos(a) * math.cos(e)])
        f = tgt - s.pos; s.f = f / np.linalg.norm(f)
        r = np.cross([0, 1, 0], s.f); s.r = r / np.linalg.norm(r); s.u = np.cross(s.f, s.r)
    def P(s, x, z, y=0.0):
        v = np.array([x, y, z]) - s.pos; dz = max(.5, v @ s.f)
        return ((W / 2 + FOC * (v @ s.r) / dz) * SS, (s.cy - FOC * (v @ s.u) / dz) * SS, FOC / dz)

def camkeys(keys, t):
    """keys: [(t, dict(el, d, tx, tz, az, cy)), ...] interpolación suave entre planos."""
    if t <= keys[0][0]: return Cam(**keys[0][1])
    for (t0, a), (t1, b) in zip(keys, keys[1:]):
        if t0 <= t <= t1:
            e = ease((t - t0) / max(1e-6, t1 - t0)); return Cam(**{k: a[k] + (b[k] - a[k]) * e for k in a})
    return Cam(**keys[-1][1])

# ------------------------------------------------------------------ campo oscuro
LINE = (120, 132, 146, 200)
def pitch(b, cam):
    d = ImageDraw.Draw(b, "RGBA"); hx = PW / 2
    def poly(pts, fill): d.polygon([cam.P(x, z)[:2] for x, z in pts], fill=fill)
    def pl(pts, col=LINE, w=2.6): d.line([cam.P(x, z)[:2] for x, z in pts], fill=col, width=int(w * SS), joint="curve")
    poly([(-hx - 4, -4), (hx + 4, -4), (hx + 4, PL + 4), (-hx - 4, PL + 4)], (20, 25, 30, 255))
    for i in range(14):
        z0, z1 = PL * i / 14, PL * (i + 1) / 14
        poly([(-hx, z0), (hx, z0), (hx, z1), (-hx, z1)], (24, 30, 36, 255) if i % 2 else (28, 35, 42, 255))
    pl([(-hx, 0), (hx, 0), (hx, PL), (-hx, PL), (-hx, 0)]); pl([(-hx, PL / 2), (hx, PL / 2)])
    pl(arc(0, PL / 2, 9.15, 0, 360, 72))
    for zs, sg in ((0, 1), (PL, -1)):
        pl([(-20.15, zs), (-20.15, zs + sg * 16.5), (20.15, zs + sg * 16.5), (20.15, zs)])
        pl([(-9.15, zs), (-9.15, zs + sg * 5.5), (9.15, zs + sg * 5.5), (9.15, zs)])
        pl(arc(0, zs + sg * 11, 9.15, 37, 143, 24) if sg > 0 else arc(0, zs + sg * 11, 9.15, 217, 323, 24))
        # portería en 3D
        g = [cam.P(x, zs, y)[:2] for x, y in ((-3.66, 0), (-3.66, 2.44), (3.66, 2.44), (3.66, 0))]
        d.line(g, fill=(230, 236, 242, 230), width=int(3 * SS), joint="curve")

def zone(b, cam, pts, col, a=1.0, fill=55):
    if a <= .02: return
    d = ImageDraw.Draw(b, "RGBA"); q = [cam.P(x, z)[:2] for x, z in pts]
    d.polygon(q, fill=(*col, int(fill * a))); d.line(q + [q[0]], fill=(*col, int(220 * a)), width=int(3 * SS), joint="curve")

def ring(b, cam, x, z, r, col, a=1.0, w=4):
    if a <= .02: return
    d = ImageDraw.Draw(b, "RGBA"); q = [cam.P(px, pz)[:2] for px, pz in arc(x, z, r, 0, 360, 40)]
    d.line(q, fill=(*col, int(235 * a)), width=int(w * SS), joint="curve")

def link(b, cam, p, q, col, e=1.0, a=1.0, w=4.5):
    """línea discontinua a ras de suelo (marcaje)."""
    if e <= .01 or a <= .02: return
    d = ImageDraw.Draw(b, "RGBA"); n = 14
    for i in range(n):
        if i % 2: continue
        u0, u1 = i / n * e, min(e, (i + 1) / n * e)
        d.line([cam.P(*lerp2(p, q, u0))[:2], cam.P(*lerp2(p, q, u1))[:2]], fill=(*col, int(235 * a)), width=int(w * SS))

def arrow(b, cam, p, q, col, e=1.0, a=1.0, w=6, y=0.0):
    if e <= .01 or a <= .02: return
    d = ImageDraw.Draw(b, "RGBA"); m = lerp2(p, q, e)
    pts = [cam.P(*lerp2(p, m, i / 20), y + 0)[:2] for i in range(21)]
    d.line(pts, fill=(*col, int(240 * a)), width=int(w * SS), joint="curve")
    (x1, y1), (x0, y0) = pts[-1], pts[-3]; ang = math.atan2(y1 - y0, x1 - x0); s = 20 * SS
    d.polygon([(x1, y1), (x1 - s * math.cos(ang - .5), y1 - s * math.sin(ang - .5)), (x1 - s * math.cos(ang + .5), y1 - s * math.sin(ang + .5))], fill=(*col, int(240 * a)))

# ------------------------------------------------------------------ jugadores en 3D
def player(b, cam, x, z, col, num=None, name=None, a=1.0, hi=0.0, dark=False, name_a=None, below=False):
    """Figura: sombra, cuerpo vertical, cabeza con dorsal; 'hi' (0..1) resalta con anillo; nombre encima."""
    if a <= .02: return
    d = ImageDraw.Draw(b, "RGBA"); gx, gy, sc = cam.P(x, z)
    _, hy, _ = cam.P(x, z, 2.5); _, my, _ = cam.P(x, z, 1.2)
    r = 1.05 * sc * SS
    d.ellipse((gx - r * 1.6, gy - r * .55, gx + r * 1.6, gy + r * .55), fill=(0, 0, 0, int(120 * a)))
    if hi > .02:
        rr = r * (2.6 + .4 * math.sin(hi * 6)); d.ellipse((gx - rr, gy - rr * .42, gx + rr, gy + rr * .42), outline=(*YEL, int(230 * a * min(1, hi * 3))), width=int(4 * SS))
    bw = max(r * 1.15, 3.5 * SS)
    d.rounded_rectangle((gx - bw, min(my, gy - 1), gx + bw, gy), radius=bw * .9, fill=(*[int(c * .78) for c in col], int(255 * a)))
    hr = max(r * 1.25, 9 * SS)
    d.ellipse((gx - hr, hy - hr, gx + hr, hy + hr), fill=(*col, int(255 * a)), outline=(*NAVY, int(255 * a)), width=int(2.5 * SS))
    if num is not None:
        d.text((gx, hy + 1), str(num), font=font(hr / SS * 1.05, "Black"), fill=((*WHT, int(255 * a)) if dark else (*NAVY, int(255 * a))), anchor="mm")
    na = a if name_a is None else name_a
    if name and na > .02:
        f = font(max(22, min(34, hr / SS * 1.5)), "Bold"); ty = (gy + r * .55 + 26 * SS) if below else (hy - hr - 22 * SS)
        tw = d.textlength(name, font=f)
        d.rounded_rectangle((gx - tw / 2 - 10 * SS, ty - 19 * SS, gx + tw / 2 + 10 * SS, ty + 17 * SS), radius=10 * SS, fill=(0, 0, 0, int(170 * na)))
        d.text((gx, ty), name, font=f, fill=(*WHT, int(255 * na)), anchor="mm")

def ballp(b, cam, x, z, y=0.25):
    d = ImageDraw.Draw(b, "RGBA"); gx, gy, sc = cam.P(x, z); bx, by, _ = cam.P(x, z, y)
    r = max(.55 * sc * SS, 6 * SS)
    d.ellipse((gx - r, gy - r * .35, gx + r, gy + r * .35), fill=(0, 0, 0, 110))
    d.ellipse((bx - r, by - r, bx + r, by + r), fill=(255, 255, 255, 255), outline=(*NAVY, 255), width=int(2 * SS))

# ------------------------------------------------------------------ texto
def headline(b, t, beats, top=236):
    """beats: [(t0, kicker, linea1, linea2|None)]; entra deslizando, el anterior sale."""
    cur = None
    for bt in beats:
        if t >= bt[0]: cur = bt
    if not cur: return
    d = ImageDraw.Draw(b, "RGBA"); k = ease((t - cur[0]) / .35); dx = (1 - k) * 60 * SS
    x0 = 64 * SS + dx
    d.rectangle((x0, (top - 14) * SS, x0 + 8 * SS, (top + 128) * SS), fill=(*YEL, int(255 * k)))
    d.text((x0 + 26 * SS, top * SS), cur[1], font=font(28, "Bold"), fill=(*YEL, int(255 * k)), anchor="lm")
    d.text((x0 + 26 * SS, (top + 52) * SS), cur[2], font=font(60, "Black"), fill=(*WHT, int(255 * k)), anchor="lm")
    if cur[3]: d.text((x0 + 26 * SS, (top + 112) * SS), cur[3], font=font(60, "Black"), fill=(*YEL, int(255 * k)), anchor="lm")

def subs(b, t, items, y=1420):
    """items: [(t0, t1, 'texto con *clave*')]: palabras que entran una a una con salto."""
    cur = None
    for it in items:
        if it[0] <= t < it[1]: cur = it
    if not cur: return
    d = ImageDraw.Draw(b, "RGBA"); f = font(56, "Black"); words = cur[2].split()
    plain = [w.strip("*") for w in words]; sp = d.textlength(" ", font=f)
    widths = [d.textlength(w, font=f) for w in plain]
    lines, ln, lw = [], [], 0
    for i, w in enumerate(widths):
        if ln and lw + sp + w > 900 * SS: lines.append(ln); ln, lw = [], 0
        ln.append(i); lw += (sp if len(ln) > 1 else 0) + w
    lines.append(ln)
    per = min(.12, (cur[1] - cur[0]) * .4 / max(1, len(words)))
    for j, ln in enumerate(lines):
        tw = sum(widths[i] for i in ln) + sp * (len(ln) - 1); x = W2 / 2 - tw / 2; yy = (y + 72 * j) * SS
        for i in ln:
            k = back((t - cur[0] - i * per) / .22); key = words[i].startswith("*")
            if k > .02:
                fk = font(56 * (.6 + .4 * min(1.2, k)), "Black")
                d.text((x + widths[i] / 2 + 3 * SS, yy + 4 * SS), plain[i], font=fk, fill=(0, 0, 0, int(190 * min(1, k))), anchor="mm")
                d.text((x + widths[i] / 2, yy), plain[i], font=fk, fill=(*(YEL if key else WHT), int(255 * min(1, k))), anchor="mm")
            x += widths[i] + sp

def bigtitle(b, t, t1, l1, l2):
    """gancho: dos líneas enormes en el centro durante el primer par de segundos."""
    if t >= t1: return
    d = ImageDraw.Draw(b, "RGBA"); k = back(t / .3) if t < .3 else 1.0; a = 1 - ease((t - t1 + .35) / .35)
    for j, (txt, col) in enumerate(((l1, WHT), (l2, YEL))):
        f = font(104 * (.85 + .15 * k), "Black"); y = (800 + 118 * j) * SS
        d.text((W2 / 2 + 5 * SS, y + 6 * SS), txt, font=f, fill=(0, 0, 0, int(200 * a)), anchor="mm")
        d.text((W2 / 2, y), txt, font=f, fill=(*col, int(255 * a)), anchor="mm")

def flash(b, t, t0, txt, sub=None):
    """golpe de texto enorme (GOL, 2 contra 1...)."""
    u = t - t0
    if u < 0 or u > 1.4: return
    d = ImageDraw.Draw(b, "RGBA"); k = max(.05, back(u / .25)); a = 1 - ease((u - 1.0) / .4)
    d.text((W2 / 2 + 6 * SS, 640 * SS + 8 * SS), txt, font=font(190 * k, "Black"), fill=(0, 0, 0, int(200 * a)), anchor="mm")
    d.text((W2 / 2, 640 * SS), txt, font=font(190 * k, "Black"), fill=(*YEL, int(255 * a)), anchor="mm")
    if sub: d.text((W2 / 2, 770 * SS), sub, font=font(48, "Bold"), fill=(*WHT, int(255 * a)), anchor="mm")

def vignette():
    y, x = np.mgrid[0:H2:8, 0:W2:8]; r = np.hypot((x - W2 / 2) / (W2 / 2), (y - H2 * .46) / (H2 / 2))
    a = np.clip((r - .55) * 1.4, 0, 1) * 200
    m = Image.fromarray(a.astype(np.uint8), "L").resize((W2, H2), Image.BILINEAR)
    v = Image.new("RGBA", (W2, H2), (*BG, 255)); v.putalpha(m); return v

def endcard(b, u, q1, q2, extra=None):
    d = ImageDraw.Draw(b, "RGBA"); d.rectangle((0, 0, W2, H2), fill=(*BG, int(238 * ease(u / .35))))
    m = _mark(); k0 = back((u - .05) / .4)
    if m and k0 > .05:
        w = int(260 * SS * k0); h = int(w * m.height / m.width); mm = m.resize((w, h), Image.LANCZOS)
        b.paste(mm, (int(W2 / 2 - w / 2), int(560 * SS - h / 2)), mm)
    k = back((u - .1) / .4)
    if k > .05:
        d.text((W2 / 2, 790 * SS), q1, font=font(80 * k, "Black"), fill=WHT, anchor="mm")
        d.text((W2 / 2, 885 * SS), q2, font=font(80 * k, "Black"), fill=YEL, anchor="mm")
    k2 = back((u - .35) / .4)
    if k2 > .05:
        w, h = 620 * SS * k2, 110 * SS * k2; d.rounded_rectangle((W2 / 2 - w / 2, 1040 * SS - h / 2, W2 / 2 + w / 2, 1040 * SS + h / 2), radius=h / 2, fill=YEL)
        d.text((W2 / 2, 1040 * SS), "@antesdelos90", font=font(54 * k2, "Black"), fill=NAVY, anchor="mm")
    if extra: d.text((W2 / 2, 1160 * SS), extra, font=font(34, "SemiBold"), fill=(200, 206, 212, int(255 * ease((u - .6) / .4))), anchor="mm")

# ------------------------------------------------------------------ sonido: whoosh e impacto sintetizados (sin licencias)
def sfx_track(path, total, whooshes=(), hits=(), sr=44100):
    n = int(total * sr); out = np.zeros(n, np.float32); rng = np.random.default_rng(7)
    for t0 in whooshes:
        L = int(.55 * sr); noise = rng.standard_normal(L).astype(np.float32)
        env = np.sin(np.linspace(0, math.pi, L)) ** 2
        # filtro paso-banda que barre (whoosh): suavizado variable
        y = np.zeros(L, np.float32); s = 0.0
        for i in range(L):
            a = .02 + .25 * (i / L); s += a * (noise[i] - s); y[i] = s
        y = y / (np.abs(y).max() + 1e-6) * env * .35
        i0 = int(t0 * sr); j = min(n, i0 + L); out[i0:j] += y[:j - i0]
    for t0 in hits:
        L = int(.6 * sr); tt = np.arange(L) / sr
        y = (np.sin(2 * math.pi * 55 * tt) * np.exp(-tt * 7) * .9 + rng.standard_normal(L) * np.exp(-tt * 30) * .25).astype(np.float32)
        i0 = int(t0 * sr); j = min(n, i0 + L); out[i0:j] += y[:j - i0]
    out = np.clip(out, -1, 1); pcm = (out * 32000).astype(np.int16)
    with wave.open(path, "wb") as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes(pcm.tobytes())

def encode(compose, total, out, music, sfx, gain=-6, voice=None, voice_off=0.35):
    """vídeo + música (+ voz con la música agachada debajo) + efectos."""
    n = int(round(total * FPS)); tmp = out + ".part.mp4"
    ins = ["-i", music, "-i", sfx] + (["-i", voice] if voice else [])
    if voice:
        ms = int(voice_off * 1000)
        fc = (f"[1:a]atrim=0:{total:.2f},volume={gain - 4}dB,afade=t=in:d=0.2,afade=t=out:st={total - 1.5:.2f}:d=1.5[m0];"
              f"[3:a]adelay={ms}|{ms},apad,atrim=0:{total:.2f},asplit=2[v][k];[m0][k]sidechaincompress=threshold=0.03:ratio=5:attack=20:release=300[m];"
              f"[2:a]volume=1dB[s];[v][m][s]amix=inputs=3:normalize=0,aresample=44100,loudnorm=I=-14:TP=-1.5[a]")
    else:
        fc = (f"[1:a]atrim=0:{total:.2f},volume={gain}dB,afade=t=in:d=0.2,afade=t=out:st={total - 1.5:.2f}:d=1.5[m];"
              f"[2:a]volume=3dB[s];[m][s]amix=inputs=2:normalize=0,aresample=44100,loudnorm=I=-14:TP=-1.5[a]")
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-framerate", str(FPS), "-i", "-",
                            *ins, "-filter_complex", fc, "-map", "0:v", "-map", "[a]", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                            "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-t", f"{total:.3f}", "-movflags", "+faststart", tmp], stdin=subprocess.PIPE)
    for k in range(n):
        enc.stdin.write(compose(k / FPS).tobytes())
        if k % 150 == 0: print("frame", k, "/", n, flush=True)
    enc.stdin.close()
    if enc.wait() == 0: os.replace(tmp, out); print("OK", out, round(total, 1), "s")
    else: raise SystemExit("ffmpeg falló")

def voice_clock(script):
    """Para vídeos con voz: tiempos reales de cada frase del guion (VOICE_DIR = build/<slug> tras engine/voice.py).
    Sin grabación todavía, tiempos estimados (solo para previsualizar). Devuelve un objeto con .at('frase'), .dur, .wav, .captions(keys)."""
    from render_spec import Voice
    return Voice(os.environ.get("VOICE_DIR", "/nonexistent"), script)

def sheet(scene_fn, ts, out, real=lambda t: t):
    ims = [scene_fn(t, real(t)).resize((540, 960)) for t in ts]
    sh = Image.new("RGB", (540 * len(ims), 960)); [sh.paste(im, (540 * i, 0)) for i, im in enumerate(ims)]; sh.save(out, quality=85)

# ------------------------------------------------------------------ efectos avanzados (v3.1)
from PIL import ImageFilter

def trail(b, cam, pts, col, w=7, a=1.0):
    """estela de carrera: pts = posiciones pasadas (más antigua primero)."""
    if len(pts) < 2 or a <= .02: return
    d = ImageDraw.Draw(b, "RGBA"); n = len(pts)
    for i in range(n - 1):
        k = (i + 1) / n
        d.line([cam.P(*pts[i])[:2], cam.P(*pts[i + 1])[:2]], fill=(*col, int(170 * a * k * k)), width=max(1, int(w * SS * k)))

def ball_trail(b, cam, pts, a=1.0):
    """estela luminosa del balón (pts con altura: (x, z, y))."""
    if len(pts) < 2: return
    layer = Image.new("RGBA", b.size, (0, 0, 0, 0)); d = ImageDraw.Draw(layer); n = len(pts)
    for i in range(n - 1):
        k = (i + 1) / n
        d.line([cam.P(*pts[i])[:2], cam.P(*pts[i + 1])[:2]], fill=(255, 236, 140, int(230 * a * k)), width=max(2, int(9 * SS * k)))
    glow = layer.filter(ImageFilter.GaussianBlur(10 * SS)); b.alpha_composite(glow); b.alpha_composite(layer)

def glow_ring(b, cam, x, z, r, col, a=1.0):
    """anillo con brillo bajo un jugador clave."""
    if a <= .02: return
    layer = Image.new("RGBA", b.size, (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    q = [cam.P(px, pz)[:2] for px, pz in arc(x, z, r, 0, 360, 40)]
    d.line(q, fill=(*col, int(255 * a)), width=int(6 * SS), joint="curve")
    b.alpha_composite(layer.filter(ImageFilter.GaussianBlur(8 * SS))); b.alpha_composite(layer)

def motion_blur(img, amount):
    """desenfoque de movimiento cuando la cámara gira rápido (amount 0..1)."""
    if amount < .08: return img
    return img.filter(ImageFilter.GaussianBlur(min(10, amount * 10) * SS))

def shake(img, t, t0, dur=.45, amp=22):
    u = t - t0
    if u < 0 or u > dur: return img
    k = (1 - u / dur) ** 2; dx = int(amp * SS * k * math.sin(u * 90)); dy = int(amp * SS * k * math.cos(u * 70))
    out = Image.new("RGBA", img.size, (*BG, 255)); out.paste(img, (dx, dy)); return out

def white_flash(b, t, t0, dur=.25):
    u = t - t0
    if 0 <= u <= dur:
        # sobre RGBA, ImageDraw sustituye el píxel en vez de mezclar: se compone una capa para que sea un destello, no un fotograma blanco
        b.alpha_composite(Image.new("RGBA", b.size, (255, 255, 255, int(140 * (1 - u / dur)))))

def lower_third(b, t, t0, t1, name, role, extra=None, y=1210):
    """ficha tipo retransmisión: barra amarilla + nombre + rol."""
    if not (t0 <= t < t1): return
    d = ImageDraw.Draw(b, "RGBA"); k = ease((t - t0) / .3) * (1 - ease((t - t1 + .3) / .3))
    if k <= .02: return
    x0 = (64 - (1 - k) * 120) * SS; fN = font(44, "Black"); fR = font(28, "SemiBold")
    w = max(d.textlength(name, font=fN), d.textlength(role, font=fR) + (d.textlength(extra, font=fR) + 30 * SS if extra else 0)) + 60 * SS
    d.rectangle((x0, (y - 52) * SS, x0 + w, (y + 50) * SS), fill=(14, 18, 22, int(235 * k)))
    d.rectangle((x0, (y - 52) * SS, x0 + 10 * SS, (y + 50) * SS), fill=(*YEL, int(255 * k)))
    d.text((x0 + 30 * SS, (y - 16) * SS), name.upper(), font=fN, fill=(*WHT, int(255 * k)), anchor="lm")
    d.text((x0 + 30 * SS, (y + 26) * SS), role, font=fR, fill=(*YEL, int(255 * k)), anchor="lm")
    if extra: d.text((x0 + 30 * SS + d.textlength(role, font=fR) + 30 * SS, (y + 26) * SS), extra, font=fR, fill=(200, 206, 212, int(255 * k)), anchor="lm")

def scoreboard(b, t, t0, t1, home, away, sh, sa, minute):
    if not (t0 <= t < t1): return
    d = ImageDraw.Draw(b, "RGBA"); k = ease((t - t0) / .3) * (1 - ease((t - t1 + .3) / .3))
    f = font(34, "Black"); fm = font(28, "Bold"); y = 470 * SS; x1 = W2 - 64 * SS
    txt = f"{home}  {sh} - {sa}  {away}"; tw = d.textlength(txt, font=f)
    x0 = x1 - tw - 150 * SS
    d.rounded_rectangle((x0, y - 34 * SS, x1, y + 34 * SS), radius=12 * SS, fill=(14, 18, 22, int(235 * k)))
    d.rounded_rectangle((x1 - 110 * SS, y - 34 * SS, x1, y + 34 * SS), radius=12 * SS, fill=(*YEL, int(255 * k)))
    d.text((x0 + 22 * SS, y), txt, font=f, fill=(*WHT, int(255 * k)), anchor="lm")
    d.text((x1 - 55 * SS, y), minute, font=fm, fill=(*NAVY, int(255 * k)), anchor="mm")

def quote(b, t, t0, t1, text, who):
    """cita del entrenador a pantalla completa sobre el campo desenfocado."""
    if not (t0 <= t < t1): return
    d = ImageDraw.Draw(b, "RGBA"); k = ease((t - t0) / .35) * (1 - ease((t - t1 + .3) / .3))
    d.rectangle((0, 0, W2, H2), fill=(*BG, int(200 * k)))
    f = font(66, "Black"); words = text.split(); lines, cur = [], ""
    for w in words:
        if d.textlength(cur + " " + w, font=f) > 880 * SS and cur: lines.append(cur); cur = w
        else: cur = (cur + " " + w).strip()
    lines.append(cur); y0 = (860 - 40 * len(lines)) * SS
    d.text((W2 / 2, y0 - 100 * SS), "“", font=font(180, "Black"), fill=(*YEL, int(255 * k)), anchor="mm")
    for j, l in enumerate(lines):
        d.text((W2 / 2, y0 + j * 84 * SS), l, font=f, fill=(*WHT, int(255 * k)), anchor="mm")
    d.text((W2 / 2, y0 + len(lines) * 84 * SS + 40 * SS), who, font=font(34, "Bold"), fill=(*YEL, int(255 * k)), anchor="mm")

def table(b, t, t0, t1, rows, title):
    """mini clasificación animada: rows = [(pos, equipo, pts, destacado)]."""
    if not (t0 <= t < t1): return
    d = ImageDraw.Draw(b, "RGBA"); k = ease((t - t0) / .35) * (1 - ease((t - t1 + .3) / .3))
    d.rectangle((0, 0, W2, H2), fill=(*BG, int(210 * k)))
    d.text((W2 / 2, 600 * SS), title, font=font(40, "Bold"), fill=(*YEL, int(255 * k)), anchor="mm")
    for i, (p, team, pts, hi) in enumerate(rows):
        u = ease((t - t0 - .25 - i * .15) / .3) * k; y = (700 + i * 112) * SS; x0 = (140 + (1 - u) * 80) * SS; x1 = W2 - 140 * SS
        d.rounded_rectangle((x0, y - 44 * SS, x1, y + 44 * SS), radius=16 * SS, fill=((*YEL, int(255 * u)) if hi else (30, 36, 42, int(240 * u))))
        c = NAVY if hi else WHT
        d.text((x0 + 40 * SS, y), str(p), font=font(44, "Black"), fill=(*c, int(255 * u)), anchor="lm")
        d.text((x0 + 120 * SS, y), team, font=font(44, "Black"), fill=(*c, int(255 * u)), anchor="lm")
        d.text((x1 - 40 * SS, y), f"{pts} pts", font=font(40, "Bold"), fill=(*c, int(255 * u)), anchor="rm")

def cam_speed(keys, t, dt=1 / 30):
    """velocidad de la cámara (para el desenfoque): cambio de un punto del centro de la imagen."""
    a = camkeys(keys, t); b = camkeys(keys, max(0, t - dt))
    pa = a.P(0, 52.5); pb = b.P(0, 52.5)
    return math.hypot(pa[0] - pb[0], pa[1] - pb[1]) / SS / 40

# ------------------------------------------------------------------ efectos nuevos (v3.2, semana 16–22 nov)
def counter(b, t, t0, t1, n, label, broken_at=None, broken_txt=None, y=820):
    """contador de datos: el número sube de 0 a n; si broken_at, una raya roja lo 'rompe' y aparece broken_txt."""
    if not (t0 <= t < t1): return
    d = ImageDraw.Draw(b, "RGBA"); k = ease((t - t0) / .3) * (1 - ease((t - t1 + .3) / .3))
    d.rectangle((0, (y - 260) * SS, W2, (y + 250) * SS), fill=(*BG, int(170 * k)))
    u = ease((t - t0 - .15) / 1.5); val = int(round(n * u))
    pop = 1.0 + .08 * math.sin(min(1, max(0, (t - t0 - 1.65) / .3)) * math.pi)
    jit = 0
    if broken_at is not None and t >= broken_at:
        e = t - broken_at; jit = int(14 * SS * max(0, 1 - e / .35) * math.sin(e * 80))
    f = font(300 * pop, "Black"); cx = W2 / 2 + jit; cy = (y - 40) * SS
    d.text((cx + 8 * SS, cy + 10 * SS), str(val), font=f, fill=(0, 0, 0, int(200 * k)), anchor="mm")
    d.text((cx, cy), str(val), font=f, fill=(*YEL, int(255 * k)), anchor="mm")
    d.text((W2 / 2, (y + 150) * SS), label, font=font(52, "Black"), fill=(*WHT, int(255 * k)), anchor="mm")
    if broken_at is not None and t >= broken_at:
        e = ease((t - broken_at) / .22); x0, y0 = W2 / 2 - 300 * SS, cy + 120 * SS; x1, y1 = W2 / 2 + 300 * SS, cy - 130 * SS
        d.line((x0, y0, x0 + (x1 - x0) * e, y0 + (y1 - y0) * e), fill=(230, 40, 50, int(255 * k)), width=int(26 * SS))
        if broken_txt:
            kk = back((t - broken_at - .15) / .3)
            if kk > .05:
                fb = font(64 * kk, "Black"); tw = d.textlength(broken_txt, font=fb)
                d.rounded_rectangle((W2 / 2 - tw / 2 - 30 * SS, (y + 230) * SS - 50 * SS * kk, W2 / 2 + tw / 2 + 30 * SS, (y + 230) * SS + 50 * SS * kk),
                                    radius=18 * SS, fill=(230, 40, 50, int(255 * k)))
                d.text((W2 / 2, (y + 230) * SS), broken_txt, font=fb, fill=(*WHT, int(255 * k)), anchor="mm")

def pressure(b, cam, p, q, col, a=1.0, width=4.5):
    """cono de presión a ras de suelo: del que presiona (p) al que recibe (q), se estrecha hacia el objetivo."""
    if a <= .02: return
    layer = Image.new("RGBA", b.size, (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    dx, dz = q[0] - p[0], q[1] - p[1]; L = math.hypot(dx, dz) or 1; nx, nz = -dz / L, dx / L
    for i in range(6):
        u0, u1 = i / 6, (i + 1) / 6
        w0, w1 = width * (1 - u0 * .8), width * (1 - u1 * .8)
        pts = [(p[0] + dx * u0 + nx * w0, p[1] + dz * u0 + nz * w0), (p[0] + dx * u1 + nx * w1, p[1] + dz * u1 + nz * w1),
               (p[0] + dx * u1 - nx * w1, p[1] + dz * u1 - nz * w1), (p[0] + dx * u0 - nx * w0, p[1] + dz * u0 - nz * w0)]
        d.polygon([cam.P(*pt)[:2] for pt in pts], fill=(*col, int((60 + 25 * i) * a)))
    b.alpha_composite(layer.filter(ImageFilter.GaussianBlur(3 * SS)))

def versus(b, t, t0, t1, left, right, colL, colR, kicker, subL=None, subR=None, foot=None):
    """cartel de cruce: pantalla partida en diagonal con los dos equipos (colores del club, sin escudos)."""
    if not (t0 <= t < t1): return
    d = ImageDraw.Draw(b, "RGBA"); k = ease((t - t0) / .35) * (1 - ease((t - t1 + .3) / .3))
    s = ease((t - t0) / .45); off = (1 - s) * 700 * SS
    yA, yB = 520 * SS, 1330 * SS
    d.polygon([(-off, yA), (W2 / 2 + 90 * SS - off, yA), (W2 / 2 - 90 * SS - off, yB), (-off, yB)], fill=(*colL, int(235 * k)))
    d.polygon([(W2 / 2 + 90 * SS + off, yA), (W2 + off, yA), (W2 + off, yB), (W2 / 2 - 90 * SS + off, yB)], fill=(*colR, int(235 * k)))
    d.text((W2 / 2, 440 * SS), kicker, font=font(40, "Bold"), fill=(*YEL, int(255 * k)), anchor="mm")
    kk = back((t - t0 - .3) / .35)
    if kk > .05:
        for txt, sub, cx, cy in ((left, subL, W2 * .27, 820 * SS), (right, subR, W2 * .70, 1030 * SS)):
            f = font(84 * kk, "Black")
            d.text((cx + 5 * SS, cy + 6 * SS), txt, font=f, fill=(0, 0, 0, int(160 * k)), anchor="mm")
            d.text((cx, cy), txt, font=f, fill=(*WHT, int(255 * k)), anchor="mm")
            if sub: d.text((cx, cy + 80 * SS), sub, font=font(34, "Bold"), fill=(*WHT, int(235 * k)), anchor="mm")
        kv = back((t - t0 - .5) / .3)
        if kv > .05:
            r = 70 * SS * kv; cx, cy = W2 / 2, 925 * SS
            d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(*YEL, int(255 * k))); d.text((cx, cy), "VS", font=font(58 * kv, "Black"), fill=(*NAVY, int(255 * k)), anchor="mm")
    if foot: d.text((W2 / 2, 1410 * SS), foot, font=font(40, "Bold"), fill=(*WHT, int(255 * k * ease((t - t0 - .6) / .3))), anchor="mm")
