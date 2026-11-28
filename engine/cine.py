"""Estilo 'cine' (v3.10, con modo pizarra y cota de distancia entre líneas): cámara 3D que se mueve entre planos, campo oscuro, jugadores en 3D con nombre,
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
    # sobre RGBA ImageDraw sustituye el píxel (no mezcla): se pinta en una capa y se compone, si no la zona sale opaca
    layer = Image.new("RGBA", b.size, (0, 0, 0, 0)); d = ImageDraw.Draw(layer); q = [cam.P(x, z)[:2] for x, z in pts]
    d.polygon(q, fill=(*col, int(fill * a))); d.line(q + [q[0]], fill=(*col, int(220 * a)), width=int(3 * SS), joint="curve")
    b.alpha_composite(layer)

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
    keys, on = [], False                                  # v3.5: *clave* de varias palabras y con puntuación pegada
    for w in words:
        st = on or w.startswith("*"); n = w.count("*")
        keys.append(st or n > 0); on = (on or w.startswith("*")) and not (w.rstrip(".,:;!?…").endswith("*") or (n == 1 and on and not w.startswith("*")))
        if n >= 2: on = False
    plain = [w.replace("*", "") for w in words]; sp = d.textlength(" ", font=f) * 1.4   # v3.6: más aire entre palabras
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
            k = back((t - cur[0] - i * per) / .22); key = keys[i]
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

def flash(b, t, t0, txt, sub=None, size=190):
    """golpe de texto enorme (GOL, 2 contra 1...)."""
    u = t - t0
    if u < 0 or u > 1.4: return
    d = ImageDraw.Draw(b, "RGBA"); k = max(.05, back(u / .25)); a = 1 - ease((u - 1.0) / .4)
    d.text((W2 / 2 + 6 * SS, 640 * SS + 8 * SS), txt, font=font(size * k, "Black"), fill=(0, 0, 0, int(200 * a)), anchor="mm")
    d.text((W2 / 2, 640 * SS), txt, font=font(size * k, "Black"), fill=(*YEL, int(255 * a)), anchor="mm")
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

# ------------------------------------------------------------------ efectos nuevos (v3.3, semana 23–29 nov)
def statbars(b, t, t0, t1, title, nameL, nameR, colL, colR, rows, y=640):
    """duelo de datos: barras enfrentadas que crecen desde el centro con los colores de cada club.
    rows = [(etiqueta, valorL, valorR, textoL, textoR)]; la barra del que gana brilla."""
    if not (t0 <= t < t1): return
    d = ImageDraw.Draw(b, "RGBA"); k = ease((t - t0) / .35) * (1 - ease((t - t1 + .3) / .3))
    d.rectangle((0, 0, W2, H2), fill=(*BG, int(215 * k)))
    d.text((W2 / 2, y * SS), title, font=font(40, "Bold"), fill=(*YEL, int(255 * k)), anchor="mm")
    kh = back((t - t0 - .1) / .35)
    if kh > .05:
        for txt, col, cx in ((nameL, colL, W2 * .28), (nameR, colR, W2 * .72)):
            f = font(64 * kh, "Black"); tw = d.textlength(txt, font=f)
            d.rounded_rectangle((cx - tw / 2 - 26 * SS, (y + 100) * SS - 46 * SS * kh, cx + tw / 2 + 26 * SS, (y + 100) * SS + 46 * SS * kh),
                                radius=18 * SS, fill=(*col, int(245 * k)))
            lum = sum(col) / 3; d.text((cx, (y + 100) * SS), txt, font=f, fill=((*NAVY, int(255 * k)) if lum > 150 else (*WHT, int(255 * k))), anchor="mm")
    cx = W2 / 2; half = 270 * SS
    for i, (lab, vL, vR, tL, tR) in enumerate(rows):
        yy = (y + 300 + i * 250) * SS; u = ease((t - t0 - .45 - i * .55) / .9) * k
        if u <= .01: continue
        d.text((cx, yy - 70 * SS), lab, font=font(40, "Bold"), fill=(*WHT, int(235 * u)), anchor="mm")
        m = max(vL, vR) or 1
        for v, col, sg, txt in ((vL, colL, -1, tL), (vR, colR, 1, tR)):
            L = half * (v / m) * u; win = v == m and vL != vR
            x0, x1 = (cx - L, cx - 6 * SS) if sg < 0 else (cx + 6 * SS, cx + L)
            if L > 8 * SS:
                if win:
                    g = Image.new("RGBA", b.size, (0, 0, 0, 0)); ImageDraw.Draw(g).rounded_rectangle((x0, yy - 30 * SS, x1, yy + 30 * SS), radius=14 * SS, fill=(*YEL, int(170 * u)))
                    b.alpha_composite(g.filter(ImageFilter.GaussianBlur(14 * SS))); d = ImageDraw.Draw(b, "RGBA")
                d.rounded_rectangle((x0, yy - 26 * SS, x1, yy + 26 * SS), radius=12 * SS, fill=(*col, int(250 * u)))
            val = txt if u > .97 else (txt if not str(txt).isdigit() else str(int(round(v * u))))
            tx = (cx - L - 24 * SS) if sg < 0 else (cx + L + 24 * SS)
            fv = font(64, "Black"); d.text((tx, yy), str(val), font=fv, fill=(*(YEL if win else WHT), int(255 * u)), anchor=("rm" if sg < 0 else "lm"))

def factlist(b, t, t0, t1, title, items, y=600):
    """lista de consecuencias: tarjetas que caen una a una con un número grande a la izquierda.
    items = [(numero_o_texto_corto, texto)]"""
    if not (t0 <= t < t1): return
    d = ImageDraw.Draw(b, "RGBA"); k = ease((t - t0) / .35) * (1 - ease((t - t1 + .3) / .3))
    d.rectangle((0, 0, W2, H2), fill=(*BG, int(205 * k)))
    d.text((W2 / 2, y * SS), title, font=font(44, "Black"), fill=(*YEL, int(255 * k)), anchor="mm")
    for i, (big, txt) in enumerate(items):
        u = back((t - t0 - .3 - i * .6) / .4); a = min(1, max(0, u)) * k
        if a <= .02: continue
        yy = (y + 150 + i * 190) * SS - (1 - min(1, u)) * 60 * SS; x0, x1 = 90 * SS, W2 - 150 * SS
        d.rounded_rectangle((x0, yy - 70 * SS, x1, yy + 70 * SS), radius=22 * SS, fill=(26, 31, 37, int(245 * a)))
        d.rounded_rectangle((x0, yy - 70 * SS, x0 + 210 * SS, yy + 70 * SS), radius=22 * SS, fill=(*YEL, int(255 * a)))
        d.text((x0 + 105 * SS, yy), big, font=font(70 if len(big) <= 3 else 52, "Black"), fill=(*NAVY, int(255 * a)), anchor="mm")
        f = font(40, "Bold"); words = txt.split(); lines, cur = [], ""
        for w in words:
            if d.textlength((cur + " " + w).strip(), font=f) > (x1 - x0 - 270 * SS) and cur: lines.append(cur); cur = w
            else: cur = (cur + " " + w).strip()
        lines.append(cur)
        for j, l in enumerate(lines):
            d.text((x0 + 240 * SS, yy + (j - (len(lines) - 1) / 2) * 50 * SS), l, font=f, fill=(*WHT, int(255 * a)), anchor="lm")

def tag3d(b, cam, x, z, txt, col=(230, 40, 50), a=1.0, fg=WHT, h=4.2):
    """etiqueta flotando sobre un jugador en el mundo 3D (LESIÓN, VAR, MANO...), con palito hasta la cabeza."""
    if a <= .02: return
    d = ImageDraw.Draw(b, "RGBA"); hx, hy, _ = cam.P(x, z, 2.9); tx, ty, _ = cam.P(x, z, h)
    ty = min(ty, hy - 70 * SS)
    f = font(34, "Black"); tw = d.textlength(txt, font=f)
    d.line((hx, hy, tx, ty + 24 * SS), fill=(*col, int(230 * a)), width=int(3 * SS))
    d.rounded_rectangle((tx - tw / 2 - 18 * SS, ty - 26 * SS, tx + tw / 2 + 18 * SS, ty + 26 * SS), radius=12 * SS, fill=(*col, int(245 * a)))
    d.text((tx, ty), txt, font=f, fill=(*fg, int(255 * a)), anchor="mm")

# ------------------------------------------------------------------ efectos nuevos (v3.4, semana 23–29 nov)
def heatmap(b, cam, blobs, col=(255, 96, 56), a=1.0):
    """mapa de calor a ras de suelo: blobs = [(x, z, radio, peso 0..1)]. Varias capas difuminadas se suman."""
    if a <= .02: return
    layer = Image.new("RGBA", b.size, (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    for x, z, r, w in blobs:
        for k, al in ((1.0, 34), (.62, 46), (.3, 58)):
            d.polygon([cam.P(px, pz)[:2] for px, pz in arc(x, z, max(.4, r * k), 0, 360, 26)], fill=(*col, int(al * w * a)))
    b.alpha_composite(layer.filter(ImageFilter.GaussianBlur(16 * SS)))

def redcard(b, t, t0, dur=1.7, txt="ROJA", sub=None, y=640):
    """tarjeta roja que gira hasta ponerse de frente, con el motivo debajo."""
    u = t - t0
    if u < 0 or u > dur: return
    d = ImageDraw.Draw(b, "RGBA"); out = 1 - ease((u - (dur - .4)) / .4)
    sx = abs(math.cos(min(1.0, u / .5) * 3 * math.pi / 2)) if u < .5 else 1.0
    w, h = 150 * SS * max(.05, sx), 215 * SS; cx, cy = W2 / 2, y * SS
    d.rounded_rectangle((cx - w, cy - h, cx + w, cy + h), radius=16 * SS, fill=(222, 32, 40, int(250 * out)))
    if sx > .55:
        k = min(1.0, (u - .35) / .3)
        if k > .05:
            d.text((cx, cy + h + 92 * SS), txt, font=font(104 * (.7 + .3 * k), "Black"), fill=(*WHT, int(255 * out * k)), anchor="mm")
            if sub: d.text((cx, cy + h + 182 * SS), sub, font=font(44, "Bold"), fill=(*YEL, int(255 * out * k)), anchor="mm")

# ------------------------------------------------------------------ vídeo real / IA dentro del cine (v3.4, serie "la vida del entrenador")
VID_EXT = (".mp4", ".mov", ".m4v", ".webm")
IMG_EXT = (".jpg", ".jpeg", ".png", ".webp")

class Clip:
    """Clip de vídeo (grabado por Miguel o generado con IA) como fondo a pantalla completa.
    Se lee en orden con ffmpeg (barato en el render secuencial); recorta a 9:16, hace un zoom lento
    y lo etalona al look del canal (más oscuro, algo desaturado). Si el archivo aún no existe,
    pinta un marcador con la descripción del plano para poder previsualizar el montaje."""
    def __init__(s, path, label="", zoom=(1.0, 1.08), grade=.82, sat=.85, start=0.0):
        if path and not os.path.isfile(path):                # vale cualquier formato con el mismo nombre: vídeo o foto
            import glob
            alt = sorted(glob.glob(os.path.splitext(path)[0] + ".*")); alt = [a for a in alt if a.lower().endswith(VID_EXT + IMG_EXT)]
            if alt: path = alt[0]
        s.path, s.label, s.zoom, s.grade, s.sat, s.start = path, label, zoom, grade, sat, start
        s.ok = bool(path) and os.path.isfile(path); s.p = None; s.pos = -1; s.last = None; s.img = None
        if s.ok and path.lower().endswith(IMG_EXT):          # foto: se anima con zoom lento (efecto Ken Burns)
            from PIL import ImageOps
            im = ImageOps.exif_transpose(Image.open(path)).convert("RGB")
            s.img = ImageOps.fit(im, (W, H), Image.LANCZOS); s.dur = 99.0; s.zoom = (zoom[0], max(zoom[1], 1.12))
        elif s.ok:
            r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path], capture_output=True, text=True)
            s.dur = float(r.stdout.strip() or 5)
    def _open(s, t):
        if s.p: s.p.kill()
        s.p = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", f"{s.start + t:.3f}", "-i", s.path, "-an",
                                "-vf", f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS}",
                                "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        s.pos = int(round(t * FPS)) - 1
    def raw(s, t):
        t = t % max(.5, s.dur - s.start - .05)              # si el plano dura más que el clip, vuelve a empezar
        k = int(round(t * FPS))
        if s.p is None or k <= s.pos - 1 or k > s.pos + 45: s._open(t)
        while s.pos < k:
            buf = s.p.stdout.read(W * H * 3)
            if len(buf) < W * H * 3: s._open(0); buf = s.p.stdout.read(W * H * 3)
            s.last = buf; s.pos += 1
        return Image.frombytes("RGB", (W, H), s.last)
    def frame(s, t, u):
        """t: segundos dentro del plano; u: 0..1 avance del plano (para el zoom)."""
        if not s.ok:
            im = Image.new("RGBA", (W2, H2), (24, 30, 36, 255)); d = ImageDraw.Draw(im)
            for i in range(0, W2 + H2, 120 * SS): d.line((i, 0, i - H2, H2), fill=(30, 37, 44, 255), width=int(40 * SS))
            d.text((W2 / 2, 1060 * SS), "PLANO PENDIENTE", font=font(40, "Bold"), fill=(*YEL, 255), anchor="mm")
            y = 1130 * SS
            for ln in _wrap(d, s.label, font(36, "SemiBold"), 860 * SS):
                d.text((W2 / 2, y), ln, font=font(36, "SemiBold"), fill=(*WHT, 230), anchor="mm"); y += 50 * SS
            return im
        im = s.img.copy() if s.img is not None else s.raw(t); z = s.zoom[0] + (s.zoom[1] - s.zoom[0]) * ease(u)
        if abs(z - 1) > .002:
            cw, ch = W / z, H / z; im = im.crop(((W - cw) / 2, (H - ch) / 2, (W + cw) / 2, (H + ch) / 2))
        im = im.resize((W2, H2), Image.BILINEAR)
        a = np.asarray(im).astype(np.float32); g = a.mean(axis=2, keepdims=True)
        a = (g + (a - g) * s.sat) * s.grade; a[..., 2] *= 1.04
        return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGB").convert("RGBA")

def _wrap(d, txt, f, maxw):
    out, cur = [], ""
    for w in txt.split():
        if cur and d.textlength(cur + " " + w, font=f) > maxw: out.append(cur); cur = w
        else: cur = (cur + " " + w).strip()
    return out + ([cur] if cur else [])

def rec_tag(b, txt="Recreación", y=412, a=1.0):
    """chip pequeño arriba a la izquierda: avisa de que el plano es recreación (IA) y no imagen real."""
    if a <= .02: return
    d = ImageDraw.Draw(b, "RGBA"); f = font(26, "Bold"); tw = d.textlength(txt, font=f); x0 = 64 * SS
    d.rounded_rectangle((x0, (y - 22) * SS, x0 + tw + 56 * SS, (y + 22) * SS), radius=22 * SS, fill=(14, 18, 22, int(200 * a)))
    d.ellipse((x0 + 16 * SS, (y - 6) * SS, x0 + 28 * SS, (y + 6) * SS), fill=(230, 40, 50, int(255 * a)))
    d.text((x0 + 40 * SS, y * SS), txt, font=f, fill=(*WHT, int(235 * a)), anchor="lm")

def roster(b, t, t0, t1, n=18, out=(), cross_at=None, title="CONVOCATORIA", y=560):
    """lista de dorsales (sin nombres: son menores); los de 'out' se tachan en rojo a partir de cross_at, uno tras otro."""
    if not (t0 <= t < t1): return
    d = ImageDraw.Draw(b, "RGBA"); k = ease((t - t0) / .35) * (1 - ease((t - t1 + .3) / .3))
    cols = 3; rows = math.ceil(n / cols); cw, rh = 280, 104; x0 = W2 / 2 - cols * cw * SS / 2
    d.rounded_rectangle((x0 - 30 * SS, (y - 80) * SS, W2 - x0 + 30 * SS, (y + rows * rh + 20) * SS), radius=28 * SS, fill=(246, 244, 238, int(242 * k)))
    d.text((W2 / 2, (y - 30) * SS), title, font=font(40, "Black"), fill=(*NAVY, int(255 * k)), anchor="mm")
    for i in range(n):
        u = ease((t - t0 - .15 - i * .04) / .25) * k
        cx = x0 + (i % cols + .5) * cw * SS; cy = (y + 40 + (i // cols) * rh) * SS
        dead = cross_at is not None and (i + 1) in out
        e = ease((t - cross_at - list(out).index(i + 1) * .28) / .25) if dead else 0.0
        col = tuple(int(NAVY[j] + (150 - NAVY[j]) * e) for j in range(3))
        d.text((cx, cy), f"Nº {i + 1}", font=font(46, "Black"), fill=(*col, int(255 * u)), anchor="mm")
        if dead:
            if e > .01: d.line((cx - 95 * SS, cy + 4 * SS, cx - 95 * SS + 190 * SS * e, cy - 4 * SS), fill=(222, 32, 40, int(255 * k)), width=int(9 * SS))

def chat(b, t, t0, t1, msgs, y=600):
    """burbujas de mensaje genéricas (sin app ni nombres reales) que entran una a una: msgs = [(texto, quien)]."""
    if not (t0 <= t < t1): return
    d = ImageDraw.Draw(b, "RGBA"); k = 1 - ease((t - t1 + .3) / .3); f = font(40, "SemiBold"); fw = font(26, "Bold"); yy = y * SS
    for i, (txt, who) in enumerate(msgs):
        u = back((t - t0 - i * .9) / .35); a = min(1, max(0, u)) * k
        if a <= .02: continue
        lines = _wrap(d, txt, f, 720 * SS); h = (len(lines) * 52 + 70) * SS; x0 = 90 * SS
        w = max(d.textlength(l, font=f) for l in lines) + 70 * SS
        d.rounded_rectangle((x0, yy, x0 + w, yy + h), radius=30 * SS, fill=(250, 250, 250, int(245 * a)))
        d.text((x0 + 36 * SS, yy + 30 * SS), who, font=fw, fill=(120, 126, 132, int(255 * a)), anchor="lm")
        for j, l in enumerate(lines): d.text((x0 + 36 * SS, yy + (78 + j * 52) * SS), l, font=f, fill=(*NAVY, int(255 * a)), anchor="lm")
        yy += h + 30 * SS

# ------------------------------------------------------------------ efectos nuevos (v3.5, semana 23–29 nov)
def stopwatch(b, t, t0, t1, m0, m1, label, sub=None, y=760):
    """cronómetro de partido: esfera de 90' con la aguja que corre de m0 a m1; el tramo recorrido se pinta
    en amarillo y el minuto grande va contando. Para 'dos goles en dos minutos' y similares."""
    if not (t0 <= t < t1): return
    d = ImageDraw.Draw(b, "RGBA"); k = ease((t - t0) / .3) * (1 - ease((t - t1 + .3) / .3))
    d.rectangle((0, (y - 330) * SS, W2, (y + 330) * SS), fill=(*BG, int(175 * k)))
    cx, cy, R = W2 / 2, (y - 40) * SS, 230 * SS
    u = ease((t - t0 - .35) / 1.2); m = m0 + (m1 - m0) * u
    d.ellipse((cx - R, cy - R, cx + R, cy + R), outline=(60, 68, 78, int(255 * k)), width=int(26 * SS))
    for i in range(0, 91, 5):                                         # marcas cada 5 minutos
        a = math.radians(-90 + 360 * i / 90); r0 = R - (40 if i % 15 == 0 else 26) * SS
        d.line((cx + r0 * math.cos(a), cy + r0 * math.sin(a), cx + (R - 14 * SS) * math.cos(a), cy + (R - 14 * SS) * math.sin(a)),
               fill=(*WHT, int(150 * k)), width=int((5 if i % 15 == 0 else 3) * SS))
    a0, a1 = -90 + 360 * m0 / 90, -90 + 360 * m / 90
    if a1 - a0 < 4: a1 = a0 + 4                                       # que el tramo se vea aunque sean 2 minutos
    d.arc((cx - R, cy - R, cx + R, cy + R), a0, a1, fill=(*YEL, int(255 * k)), width=int(30 * SS))
    a = math.radians(a1)
    d.line((cx, cy, cx + (R - 50 * SS) * math.cos(a), cy + (R - 50 * SS) * math.sin(a)), fill=(*YEL, int(255 * k)), width=int(9 * SS))
    d.ellipse((cx - 14 * SS, cy - 14 * SS, cx + 14 * SS, cy + 14 * SS), fill=(*YEL, int(255 * k)))
    f = font(120, "Black"); txt = f"{int(round(m))}'"
    d.text((cx + 6 * SS, cy + 6 * SS), txt, font=f, fill=(0, 0, 0, int(190 * k)), anchor="mm")
    d.text((cx, cy), txt, font=f, fill=(*WHT, int(255 * k)), anchor="mm")
    kk = back((t - t0 - 1.1) / .35)
    if kk > .05:
        fb = font(64 * min(1.0, kk), "Black"); tw = d.textlength(label, font=fb); ly = (y + 250) * SS
        d.rounded_rectangle((W2 / 2 - tw / 2 - 30 * SS, ly - 48 * SS, W2 / 2 + tw / 2 + 30 * SS, ly + 48 * SS), radius=18 * SS, fill=(*YEL, int(255 * k)))
        d.text((W2 / 2, ly), label, font=fb, fill=(*NAVY, int(255 * k)), anchor="mm")
        if sub: d.text((W2 / 2, ly + 92 * SS), sub, font=font(40, "Bold"), fill=(*WHT, int(235 * k)), anchor="mm")

def spark(b, cam, x, z, t, t0, col=(255, 204, 0), dur=.7, y=.6):
    """chispazo donde el balón toca a un defensor y cambia de dirección (desvío): rayos que salen y se apagan."""
    u = (t - t0) / dur
    if not (0 <= u < 1): return
    d = ImageDraw.Draw(b, "RGBA"); px, py, sc = cam.P(x, z, y); a = 1 - ease(u)
    r0, r1 = (6 + 30 * u) * sc * SS * .12 + 10 * SS, (14 + 70 * ease(u)) * sc * SS * .12 + 30 * SS
    for i in range(10):
        ang = math.radians(i * 36 + 12)
        d.line((px + r0 * math.cos(ang), py + r0 * math.sin(ang), px + r1 * math.cos(ang), py + r1 * math.sin(ang)),
               fill=(*col, int(255 * a)), width=int(5 * SS))
    rr = r1 * .55; d.ellipse((px - rr, py - rr, px + rr, py + rr), outline=(*WHT, int(200 * a)), width=int(3 * SS))

# ------------------------------------------------------------------ efectos nuevos (v3.6, semana 23–29 nov)
def subboard(b, t, t0, t1, outs, ins, title="DESCANSO", y=860):
    """cartel del cuarto árbitro: tablero LED que gira hasta ponerse de frente; cada fila (SALE en rojo / ENTRA en
    verde) se enciende por turnos con un barrido. outs/ins = listas de nombres del mismo tamaño."""
    if not (t0 <= t < t1): return
    d = ImageDraw.Draw(b, "RGBA"); k = ease((t - t0) / .3) * (1 - ease((t - t1 + .3) / .3))
    d.rectangle((0, 0, W2, H2), fill=(*BG, int(150 * k)))
    u = t - t0; sx = min(1.0, max(.04, abs(math.sin(min(1.0, u / .45) * math.pi / 2))))
    n = len(outs); rh = 118; hh = (130 + n * rh * 2 + 40) / 2
    cx, cy = W2 / 2, y * SS; w = 430 * SS * sx; h = hh * SS
    d.rounded_rectangle((cx - w - 14 * SS, cy - h - 14 * SS, cx + w + 14 * SS, cy + h + 14 * SS), radius=26 * SS, fill=(40, 46, 54, int(255 * k)))
    d.rounded_rectangle((cx - w, cy - h, cx + w, cy + h), radius=18 * SS, fill=(6, 8, 10, int(255 * k)))
    if sx < .9: return
    for yy in range(int(cy - h), int(cy + h), int(9 * SS)):           # rejilla LED
        d.line((cx - w, yy, cx + w, yy), fill=(255, 255, 255, int(10 * k)), width=1)
    d.text((cx, cy - h + 66 * SS), title, font=font(44, "Black"), fill=(*YEL, int(255 * k)), anchor="mm")
    RED_, GRN_ = (240, 60, 60), (60, 220, 120)
    for i in range(n):
        for j, (nm, col, tag) in enumerate(((outs[i], RED_, "SALE"), (ins[i], GRN_, "ENTRA"))):
            st = t0 + .5 + i * .45 + j * .18; e = ease((t - st) / .25)
            if e <= .02: continue
            ry = cy - h + (150 + (2 * i + j) * rh) * SS
            glow = 1 + .5 * max(0, 1 - (t - st) / .4)
            d.polygon([(cx - w + 50 * SS, ry + (-18 if j else 18) * SS), (cx - w + 86 * SS, ry + (-18 if j else 18) * SS),
                       (cx - w + 68 * SS, ry + (18 if j else -18) * SS)], fill=(*col, int(255 * k * e)))
            d.text((cx - w + 110 * SS, ry), tag, font=font(30, "Bold"), fill=(*col, int(255 * k * e)), anchor="lm")
            f = font(62, "Black"); x0 = cx - w + 230 * SS; full = d.textlength(nm, font=f)
            # barrido: el nombre se enciende de izquierda a derecha
            lay = Image.new("RGBA", b.size, (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
            ld.text((x0, ry), nm, font=f, fill=(*[min(255, int(c * glow)) for c in col], 255), anchor="lm")
            m = Image.new("L", b.size, 0); ImageDraw.Draw(m).rectangle((x0 - 4, ry - 60 * SS, x0 + full * e + 4, ry + 60 * SS), fill=int(255 * k))
            b.paste(lay, (0, 0), Image.composite(lay.getchannel("A"), Image.new("L", b.size, 0), m))
            d = ImageDraw.Draw(b, "RGBA")

def lineband(b, cam, z, col=(255, 204, 0), a=1.0, label=None, x0=-34, x1=34, zfrom=None):
    """línea defensiva luminosa de banda a banda en la altura z; si zfrom, deja la huella de dónde estaba
    y una flecha de lo que ha subido. La etiqueta va a la izquierda (fuera de la columna de iconos)."""
    if a <= .02: return
    layer = Image.new("RGBA", b.size, (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    if zfrom is not None:
        d.line([cam.P(x, zfrom)[:2] for x in (x0, x1)], fill=(255, 255, 255, int(110 * a)), width=int(4 * SS))
        d.polygon([cam.P(x, zz)[:2] for x, zz in ((x0, zfrom), (x1, zfrom), (x1, z), (x0, z))], fill=(*col, int(34 * a)))
    d.polygon([cam.P(x, zz)[:2] for x, zz in ((x0, z - .9), (x1, z - .9), (x1, z + .9), (x0, z + .9))], fill=(*col, int(150 * a)))
    b.alpha_composite(layer.filter(ImageFilter.GaussianBlur(5 * SS)))
    d = ImageDraw.Draw(b, "RGBA"); d.line([cam.P(x, z)[:2] for x in (x0, x1)], fill=(*col, int(255 * a)), width=int(5 * SS))
    if zfrom is not None and abs(z - zfrom) > 2:
        for xa in (-14, 14):
            p, q = cam.P(xa, zfrom)[:2], cam.P(xa, z - 1.2)[:2]
            d.line((p, q), fill=(*col, int(230 * a)), width=int(6 * SS))
            ang = math.atan2(q[1] - p[1], q[0] - p[0]); s = 22 * SS
            d.polygon([q, (q[0] - s * math.cos(ang - .5), q[1] - s * math.sin(ang - .5)), (q[0] - s * math.cos(ang + .5), q[1] - s * math.sin(ang + .5))], fill=(*col, int(230 * a)))
    if label:
        px, py, _ = cam.P(x0 + 6, z); px = max(px, 70 * SS); f = font(34, "Black"); tw = d.textlength(label, font=f)
        py -= 46 * SS
        d.rounded_rectangle((px, py - 26 * SS, px + tw + 36 * SS, py + 26 * SS), radius=12 * SS, fill=(*col, int(245 * a)))
        d.text((px + 18 * SS, py), label, font=f, fill=(*NAVY, int(255 * a)), anchor="lm")

# ------------------------------------------------------------------ efectos nuevos (v3.7, semana 23–29 nov)
def ghost(b, cam, x, z, col, name, a=1.0, t=0.0, tag="BAJA"):
    """jugador ausente (lesionado/baja): silueta hueca y translúcida con contorno discontinuo que respira,
    una cruz roja sobre la cabeza y su nombre con la etiqueta BAJA. Para enseñar el hueco que deja en el once."""
    if a <= .02: return
    layer = Image.new("RGBA", b.size, (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    gx, gy, sc = cam.P(x, z); _, hy, _ = cam.P(x, z, 2.5); _, my, _ = cam.P(x, z, 1.2)
    r = 1.05 * sc * SS; bw = max(r * 1.15, 3.5 * SS); hr = max(r * 1.25, 9 * SS)
    pulse = .75 + .25 * math.sin(t * 5 + x)
    d.ellipse((gx - r * 1.6, gy - r * .55, gx + r * 1.6, gy + r * .55), outline=(*col, int(150 * a)), width=int(2 * SS))
    d.rounded_rectangle((gx - bw, min(my, gy - 1), gx + bw, gy), radius=bw * .9, fill=(*col, int(55 * a * pulse)))
    n = 18                                                              # cabeza: contorno discontinuo
    for i in range(0, n, 2):
        a0, a1 = 360 * i / n + t * 40, 360 * (i + 1) / n + t * 40
        d.arc((gx - hr, hy - hr, gx + hr, hy + hr), a0, a1, fill=(*col, int(235 * a)), width=int(4 * SS))
    d.ellipse((gx - hr * .8, hy - hr * .8, gx + hr * .8, hy + hr * .8), fill=(*col, int(45 * a * pulse)))
    s = hr * .55; R_ = (240, 50, 56, int(255 * a))
    d.line((gx - s, hy - s, gx + s, hy + s), fill=R_, width=int(5 * SS)); d.line((gx - s, hy + s, gx + s, hy - s), fill=R_, width=int(5 * SS))
    b.alpha_composite(layer)
    d = ImageDraw.Draw(b, "RGBA"); f = font(max(22, min(32, hr / SS * 1.4)), "Bold"); ft = font(22, "Black")
    ty = hy - hr - 24 * SS; tw = d.textlength(name, font=f); gw = d.textlength(tag, font=ft) + 20 * SS
    x0 = gx - (tw + gw + 34 * SS) / 2
    d.rounded_rectangle((x0, ty - 20 * SS, x0 + tw + gw + 34 * SS, ty + 18 * SS), radius=10 * SS, fill=(0, 0, 0, int(175 * a)))
    d.text((x0 + 12 * SS, ty), name, font=f, fill=(*WHT, int(200 * a)), anchor="lm")
    bx = x0 + tw + 22 * SS
    d.rounded_rectangle((bx, ty - 14 * SS, bx + gw, ty + 13 * SS), radius=7 * SS, fill=(240, 50, 56, int(240 * a)))
    d.text((bx + gw / 2, ty), tag, font=ft, fill=(*WHT, int(255 * a)), anchor="mm")

def passline(b, cam, p, q, t, t0, dur=.6, col=(255, 204, 0), a=1.0, hold=1.2, w=5):
    """pase que se dibuja: trazo discontinuo que avanza de p a q mientras viaja el balón, con un aro que se
    abre en el punto de llegada y se queda marcado 'hold' segundos antes de apagarse."""
    if t < t0: return
    u = min(1.0, (t - t0) / dur); fade = a * (1 - ease((t - t0 - dur - hold) / .35))
    if fade <= .02: return
    d = ImageDraw.Draw(b, "RGBA"); n = 26
    for i in range(0, n, 2):
        u0, u1 = i / n, (i + 1) / n
        if u0 > u: break
        d.line([cam.P(*lerp2(p, q, u0))[:2], cam.P(*lerp2(p, q, min(u, u1)))[:2]], fill=(*col, int(245 * fade)), width=int(w * SS))
    hx, hy, _ = cam.P(*lerp2(p, q, u)); d.ellipse((hx - 7 * SS, hy - 7 * SS, hx + 7 * SS, hy + 7 * SS), fill=(*col, int(255 * fade)))
    if u >= 1:
        k = ease((t - t0 - dur) / .35); rr = 1.2 + 2.2 * k
        q2 = [cam.P(px, pz)[:2] for px, pz in arc(q[0], q[1], rr, 0, 360, 36)]
        d.line(q2, fill=(*col, int(235 * fade * (1 - .4 * k))), width=int(4 * SS), joint="curve")

# ------------------------------------------------------------------ efectos nuevos (v3.8, semana 23–29 nov)
def outnumber(b, t, t0, t1, nL, nR, colL, colR, labL, labR, out_at=None, y=600):
    """contador de superioridad: dos filas de muñecos con los colores de cada club; en la fila del que se queda
    con uno menos, un muñeco se apaga con una cruz roja (en out_at) y el marcador grande pasa a 'nL v nR'."""
    if not (t0 <= t < t1): return
    d = ImageDraw.Draw(b, "RGBA"); k = ease((t - t0) / .3) * (1 - ease((t - t1 + .3) / .3))
    if k <= .02: return
    out_at = t0 + .6 if out_at is None else out_at; gone = ease((t - out_at) / .35)
    x0, x1 = 90 * SS, W2 - 160 * SS; h = 250
    d.rounded_rectangle((x0, (y - 40) * SS, x1, (y + h) * SS), radius=26 * SS, fill=(14, 18, 22, int(225 * k)))
    nr_show = nR if gone < .5 else nR
    big = f"{nL} v {nR if gone >= .5 else nR + 1}"
    d.text((x0 + 40 * SS, (y + 4) * SS), "SUPERIORIDAD", font=font(28, "Bold"), fill=(*YEL, int(255 * k)), anchor="lm")
    kb = back((t - out_at) / .35) if gone > 0 else 1.0
    d.text((x1 - 40 * SS, (y + 4) * SS), big, font=font(56 * (.8 + .2 * min(1.2, kb)), "Black"), fill=(*WHT, int(255 * k)), anchor="rm")
    for row, (n, col, lab, drop) in enumerate(((nL, colL, labL, False), (nR + 1, colR, labR, True))):
        yy = (y + 90 + row * 92) * SS
        d.text((x0 + 40 * SS, yy), lab, font=font(34, "Black"), fill=(*WHT, int(255 * k)), anchor="lm")
        sx = x0 + 250 * SS; step = (x1 - 40 * SS - sx) / 11
        for i in range(n):
            u = ease((t - t0 - .05 * i) / .25) * k; cx = sx + step * (i + .5)
            dead = drop and i == n - 1
            a = u * (1 - .78 * gone) if dead else u
            r = 17 * SS
            d.rounded_rectangle((cx - r * .8, yy - r * .1, cx + r * .8, yy + r * 1.5), radius=r * .7, fill=(*[int(c * .78) for c in col], int(255 * a)))
            d.ellipse((cx - r * .75, yy - r * 1.6, cx + r * .75, yy - r * .1), fill=(*col, int(255 * a)))
            if dead and gone > .02:
                s_ = r * 1.3 * gone; RC = (240, 50, 56, int(255 * k))
                d.line((cx - s_, yy - s_ * .5, cx + s_, yy + s_ * 1.1), fill=RC, width=int(6 * SS))
                d.line((cx - s_, yy + s_ * 1.1, cx + s_, yy - s_ * .5), fill=RC, width=int(6 * SS))

def drillboard(b, t, t0, t1, kicker, title, rows, colA, colD, chip="Propuesta de entrenador", y=520):
    """'Antes de los 90': pizarra de la tarea de entrenamiento vista desde arriba. Mini campo con tres pasillos,
    ataque (colA) contra defensa (colD) y porteros; el balón viaja de pasillo en pasillo con el pase dibujándose,
    la defensa bascula y al final hay remate. Debajo, las reglas (rows, con *clave* en amarillo) caen una a una."""
    if not (t0 <= t < t1): return
    d = ImageDraw.Draw(b, "RGBA"); k = ease((t - t0) / .35) * (1 - ease((t - t1 + .3) / .3)); u = t - t0
    d.rectangle((0, 0, W2, H2), fill=(*BG, int(232 * k)))
    d.text((90 * SS, (y - 260) * SS), kicker, font=font(30, "Bold"), fill=(*YEL, int(255 * k)), anchor="lm")
    d.text((90 * SS, (y - 205) * SS), title, font=font(58, "Black"), fill=(*WHT, int(255 * k)), anchor="lm")
    f = font(24, "Bold"); cw = d.textlength(chip, font=f)
    d.rounded_rectangle((90 * SS, (y - 160) * SS, 90 * SS + cw + 40 * SS, (y - 122) * SS), radius=19 * SS, fill=(*YEL, int(235 * k)))
    d.text((110 * SS, (y - 141) * SS), chip, font=f, fill=(*NAVY, int(255 * k)), anchor="lm")
    # mini campo: 40x30 (largo en horizontal), de x=110 a x=910, y de y-90 a y+410
    X0, X1, Y0, Y1 = 110 * SS, 910 * SS, (y - 90) * SS, (y + 410) * SS
    kp = ease((u - .1) / .4) * k
    d.rounded_rectangle((X0, Y0, X1, Y1), radius=14 * SS, fill=(26, 40, 34, int(250 * kp)), outline=(*WHT, int(200 * kp)), width=int(3 * SS))
    for j in (1, 2):                                                  # pasillos (discontinuo, horizontales)
        yy = Y0 + (Y1 - Y0) * j / 3
        for xx in range(int(X0), int(X1), int(36 * SS)):
            d.line((xx, yy, min(X1, xx + 18 * SS), yy), fill=(*YEL, int(150 * kp)), width=int(3 * SS))
    gh = (Y1 - Y0) * .26
    for gx in (X0, X1):
        d.rectangle((gx - 10 * SS, (Y0 + Y1) / 2 - gh / 2, gx + 10 * SS, (Y0 + Y1) / 2 + gh / 2), fill=(*WHT, int(230 * kp)))
    def P(px, py): return X0 + (X1 - X0) * px, Y0 + (Y1 - Y0) * py
    ph = min(1.0, max(0.0, (u - .5) / 2.6))                           # 0..1: el balón cambia de pasillo y remata
    A = [(.30, .16), (.52, .14), (.28, .50), (.55, .52), (.32, .84), (.74, .82)]
    D = [(.66, .28), (.66, .56), (.80, .40), (.56, .34), (.58, .70)]
    sw = ease(min(1, ph * 1.4))                                       # la defensa bascula hacia abajo
    D = [(x, y_ + .14 * sw) for x, y_ in D]; A[5] = (.74 + .08 * ease(max(0, ph - .55) / .45), .82)
    seq = [A[1], A[3], A[2], A[4], A[5]]; nseg = len(seq) - 1
    s_ = min(nseg - 1e-6, ph * nseg); i = int(s_); fr = s_ - i
    for (x, y_), col in (((.04, .5), colA), ((.96, .5), colD)):     # porteros: cada uno en su portería
        cx, cy = P(x, y_); d.ellipse((cx - 16 * SS, cy - 16 * SS, cx + 16 * SS, cy + 16 * SS), fill=(*col, int(255 * kp)), outline=(*WHT, int(255 * kp)), width=int(3 * SS))
    for a_, b_ in zip(seq[:i + 1], seq[1:i + 2]):                     # pases ya dados
        e = 1.0 if (a_, b_) != (seq[i], seq[i + 1]) else fr
        pa, pb = P(*a_), P(*b_); pm = (pa[0] + (pb[0] - pa[0]) * e, pa[1] + (pb[1] - pa[1]) * e)
        d.line((pa, pm), fill=(*YEL, int(230 * kp)), width=int(5 * SS))
    for x, y_ in D:
        cx, cy = P(x, y_); d.ellipse((cx - 20 * SS, cy - 20 * SS, cx + 20 * SS, cy + 20 * SS), fill=(*colD, int(255 * kp)), outline=(*NAVY, int(255 * kp)), width=int(3 * SS))
    for x, y_ in A:
        cx, cy = P(x, y_); d.ellipse((cx - 20 * SS, cy - 20 * SS, cx + 20 * SS, cy + 20 * SS), fill=(*colA, int(255 * kp)), outline=(*NAVY, int(255 * kp)), width=int(3 * SS))
    if ph < 1:
        pa, pb = P(*seq[i]), P(*seq[i + 1]); bx, by = pa[0] + (pb[0] - pa[0]) * fr, pa[1] + (pb[1] - pa[1]) * fr
    else:
        sh = ease(min(1, (u - 3.1) / .35)); pa, pb = P(*seq[-1]), P(.995, .5); bx, by = pa[0] + (pb[0] - pa[0]) * sh, pa[1] + (pb[1] - pa[1]) * sh
    d.ellipse((bx - 11 * SS, by - 11 * SS, bx + 11 * SS, by + 11 * SS), fill=(*WHT, int(255 * kp)), outline=(*NAVY, int(255 * kp)), width=int(2 * SS))
    fr_ = font(40, "Black")
    for j, txt in enumerate(rows):
        a = ease((u - .6 - j * .55) / .35) * k
        if a <= .02: continue
        yy = (y + 480 + j * 66) * SS; x = 110 * SS
        d.ellipse((x, yy - 9 * SS, x + 18 * SS, yy + 9 * SS), fill=(*YEL, int(255 * a)))
        x += 40 * SS; on = False
        for w in txt.split():
            st = w.startswith("*"); en = w.rstrip(".,:;").endswith("*"); on = on or st
            pw = w.replace("*", "") + " "
            d.text((x, yy), pw, font=fr_, fill=(*(YEL if on else WHT), int(255 * a)), anchor="lm"); x += d.textlength(pw, font=fr_)
            if en: on = False

# ------------------------------------------------------------------ modo PIZARRA (v3.9, 27-11-2026: "más lento, más limpio, se tiene que leer")
GREY = (96, 104, 114)
def caption(b, t, caps, y=1360, hold=1.6, size=62):
    """subtítulo tranquilo: la frase entera a la vez (no palabra a palabra), una sola línea sobre una píldora oscura,
    *clave* en amarillo. caps = [(t0, t1, 'texto con *clave*')]. Si t1 es None, se queda 'hold' s."""
    cur = None
    for c in caps:
        t1 = c[1] if c[1] is not None else c[0] + hold
        if c[0] <= t < t1: cur = (c[0], t1, c[2])
    if not cur: return
    d = ImageDraw.Draw(b, "RGBA"); k = ease((t - cur[0]) / .18) * (1 - ease((t - cur[1] + .15) / .15))
    if k <= .02: return
    f = font(size, "Black"); words = cur[2].split(); on = False; parts = []
    for w in words:
        st = w.startswith("*"); on = on or st; en = w.rstrip(".,:;!?¿¡…").endswith("*") or (st and w.count("*") == 2)
        parts.append((w.replace("*", ""), on)); on = on and not en
    sp = d.textlength(" ", font=f); tw = sum(d.textlength(p, font=f) for p, _ in parts) + sp * (len(parts) - 1)
    scale = min(1.0, 900 * SS / max(1, tw)); f = font(size * scale, "Black")
    tw = sum(d.textlength(p, font=f) for p, _ in parts) + d.textlength(" ", font=f) * (len(parts) - 1); sp = d.textlength(" ", font=f)
    yy = y * SS - (1 - k) * 14 * SS; padx, h = 34 * SS, 58 * SS * scale + 22 * SS
    d.rounded_rectangle((W2 / 2 - tw / 2 - padx, yy - h, W2 / 2 + tw / 2 + padx, yy + h), radius=h, fill=(8, 10, 12, int(205 * k)))
    x = W2 / 2 - tw / 2
    for p, key in parts:
        d.text((x, yy), p, font=f, fill=(*(YEL if key else WHT), int(255 * k)), anchor="lm"); x += d.textlength(p, font=f) + sp

def question_top(b, t, t0, l1, l2, kicker=None, top=250):
    """la pregunta del vídeo, fija arriba todo el rato (lo que en el feed decide si te quedas)."""
    if t < t0: return
    d = ImageDraw.Draw(b, "RGBA"); k = ease((t - t0) / .4)
    if kicker: d.text((W2 / 2, (top - 10) * SS), kicker, font=font(28, "Bold"), fill=(*YEL, int(230 * k)), anchor="mm")
    for j, (txt, col) in enumerate(((l1, WHT), (l2, YEL))):
        f = font(58, "Black"); yy = (top + 50 + 66 * j) * SS
        d.text((W2 / 2 + 3 * SS, yy + 4 * SS), txt, font=f, fill=(0, 0, 0, int(170 * k)), anchor="mm")
        d.text((W2 / 2, yy), txt, font=f, fill=(*col, int(255 * k)), anchor="mm")

# ------------------------------------------------------------------ mejora visual (v3.10, semana 23–29 nov)
def gap(b, cam, x, z0, z1, col=(255, 204, 0), a=1.0, label=None, grow=1.0, label_z=None):
    """distancia entre líneas: una cota vertical (línea con topes en z0 y z1) a la altura x, que se estira con 'grow'
    (0..1) y una etiqueta corta al lado (HUECO, JUNTOS); con label_z, la etiqueta va a esa altura, pegada a la cota
    (para no taparse con jugadores). Para que se vea de un vistazo si un bloque está largo o corto,
    sin flechas ni zonas extra encima de los jugadores."""
    if a <= .02: return
    zz = z0 + (z1 - z0) * max(0.0, min(1.0, grow))
    d = ImageDraw.Draw(b, "RGBA"); p, q = cam.P(x, z0)[:2], cam.P(x, zz)[:2]
    d.line((p, q), fill=(0, 0, 0, int(120 * a)), width=int(11 * SS))
    d.line((p, q), fill=(*col, int(250 * a)), width=int(6 * SS))
    for (px, py), ok in ((p, True), (q, grow >= .98)):
        if ok: d.line((px - 22 * SS, py, px + 22 * SS, py), fill=(*col, int(250 * a)), width=int(6 * SS))
    if label and grow >= .6:
        k = a * ease((grow - .6) / .4); mx, my = (p[0] + q[0]) / 2, (p[1] + q[1]) / 2
        f = font(36, "Black"); tw = d.textlength(label, font=f); x0 = mx + 26 * SS
        if label_z is not None: mx, my = cam.P(x, label_z)[:2]; x0 = max(40 * SS, mx - 18 * SS)
        if x0 + tw + 40 * SS > W2 - 150 * SS: x0 = mx - 26 * SS - tw - 36 * SS      # nunca en la columna de iconos
        d.rounded_rectangle((x0, my - 28 * SS, x0 + tw + 36 * SS, my + 28 * SS), radius=12 * SS, fill=(*col, int(245 * k)))
        d.text((x0 + 18 * SS, my), label, font=f, fill=(*NAVY, int(255 * k)), anchor="lm")

def drillboard_press(b, t, t0, t1, kicker, title, rows, colA, colD, chip="Propuesta de entrenador", y=520):
    """'Antes de los 90' para tareas de PRESIÓN: mini campo en tres FRANJAS (a lo largo). El equipo que presiona (colA)
    empieza estirado por las tres franjas, se junta en las dos de arriba (se ilumina la zona válida), roba y remata.
    Debajo, las reglas caen una a una (como drillboard)."""
    if not (t0 <= t < t1): return
    d = ImageDraw.Draw(b, "RGBA"); k = ease((t - t0) / .35) * (1 - ease((t - t1 + .3) / .3)); u = t - t0
    d.rectangle((0, 0, W2, H2), fill=(*BG, int(232 * k)))
    d.text((90 * SS, (y - 260) * SS), kicker, font=font(30, "Bold"), fill=(*YEL, int(255 * k)), anchor="lm")
    d.text((90 * SS, (y - 205) * SS), title, font=font(58, "Black"), fill=(*WHT, int(255 * k)), anchor="lm")
    f = font(24, "Bold"); cw = d.textlength(chip, font=f)
    d.rounded_rectangle((90 * SS, (y - 160) * SS, 90 * SS + cw + 40 * SS, (y - 122) * SS), radius=19 * SS, fill=(*YEL, int(235 * k)))
    d.text((110 * SS, (y - 141) * SS), chip, font=f, fill=(*NAVY, int(255 * k)), anchor="lm")
    X0, X1, Y0, Y1 = 110 * SS, 910 * SS, (y - 90) * SS, (y + 410) * SS
    def P(px, py): return X0 + (X1 - X0) * px, Y0 + (Y1 - Y0) * py
    kp = ease((u - .1) / .4) * k
    d.rounded_rectangle((X0, Y0, X1, Y1), radius=14 * SS, fill=(26, 40, 34, int(250 * kp)), outline=(*WHT, int(200 * kp)), width=int(3 * SS))
    ph = min(1.0, max(0.0, (u - .6) / 2.4))                            # 0..1: se junta, roba y remata
    jn = ease(min(1, ph / .45))                                       # se junta
    if jn > .05:                                                      # zona válida: las dos franjas de arriba
        lay = Image.new("RGBA", b.size, (0, 0, 0, 0))
        ImageDraw.Draw(lay).rectangle((P(1 / 3, 0)[0], Y0 + 3 * SS, X1 - 3 * SS, Y1 - 3 * SS), fill=(*YEL, int(46 * kp * jn)))
        ImageDraw.Draw(lay).rectangle((P(2 / 3, 0)[0], Y0 + 3 * SS, X1 - 3 * SS, Y1 - 3 * SS), fill=(*YEL, int(40 * kp * jn)))
        b.alpha_composite(lay); d = ImageDraw.Draw(b, "RGBA")
        d.text((P(5 / 6, 0)[0], Y0 + 34 * SS), "ROBO = x2", font=font(30, "Black"), fill=(*YEL, int(255 * kp * jn)), anchor="mm")
    for j in (1, 2):                                                  # franjas (discontinuo, verticales)
        xx = X0 + (X1 - X0) * j / 3
        for yy in range(int(Y0), int(Y1), int(36 * SS)):
            d.line((xx, yy, xx, min(Y1, yy + 18 * SS)), fill=(*YEL, int(150 * kp)), width=int(3 * SS))
    gh = (Y1 - Y0) * .26
    for gx in (X0, X1):
        d.rectangle((gx - 10 * SS, (Y0 + Y1) / 2 - gh / 2, gx + 10 * SS, (Y0 + Y1) / 2 + gh / 2), fill=(*WHT, int(230 * kp)))
    A0 = [(.16, .30), (.16, .70), (.42, .22), (.42, .78), (.62, .40), (.66, .62)]      # estirado
    A1 = [(.44, .30), (.44, .70), (.60, .22), (.62, .76), (.80, .42), (.82, .60)]      # junto, arriba
    A = [lerp2(p, q, jn) for p, q in zip(A0, A1)]
    D = [(.90, .34), (.90, .66), (.76, .18), (.74, .82), (.66, .50), (.56, .30)]
    rob = ease(min(1, max(0, ph - .45) / .2)); shot = ease(min(1, max(0, ph - .7) / .3))
    bx, by = P(*lerp2((.90, .66), (.82, .60), rob)); 
    if shot > 0: bx, by = P(*lerp2((.82, .60), (.995, .5), shot))
    for (x, y_), col in (((.04, .5), colA), ((.96, .5), colD)):
        cx, cy = P(x, y_); d.ellipse((cx - 16 * SS, cy - 16 * SS, cx + 16 * SS, cy + 16 * SS), fill=(*col, int(255 * kp)), outline=(*WHT, int(255 * kp)), width=int(3 * SS))
    for x, y_ in D:
        cx, cy = P(x, y_); d.ellipse((cx - 20 * SS, cy - 20 * SS, cx + 20 * SS, cy + 20 * SS), fill=(*colD, int(255 * kp)), outline=(*NAVY, int(255 * kp)), width=int(3 * SS))
    for x, y_ in A:
        cx, cy = P(x, y_); d.ellipse((cx - 20 * SS, cy - 20 * SS, cx + 20 * SS, cy + 20 * SS), fill=(*colA, int(255 * kp)), outline=(*NAVY, int(255 * kp)), width=int(3 * SS))
    d.ellipse((bx - 11 * SS, by - 11 * SS, bx + 11 * SS, by + 11 * SS), fill=(*WHT, int(255 * kp)), outline=(*NAVY, int(255 * kp)), width=int(2 * SS))
    if .45 < ph < .75:
        cx, cy = P(.84, .62); r = (16 + 40 * (ph - .45) / .3) * SS
        d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=(*YEL, int(230 * kp * (1 - (ph - .45) / .3))), width=int(4 * SS))
    fr_ = font(40, "Black")
    for j, txt in enumerate(rows):
        a = ease((u - .6 - j * .55) / .35) * k
        if a <= .02: continue
        yy = (y + 480 + j * 66) * SS; x = 110 * SS
        d.ellipse((x, yy - 9 * SS, x + 18 * SS, yy + 9 * SS), fill=(*YEL, int(255 * a)))
        x += 40 * SS; on = False
        for w in txt.split():
            st = w.startswith("*"); en = w.rstrip(".,:;").endswith("*"); on = on or st
            pw = w.replace("*", "") + " "
            d.text((x, yy), pw, font=fr_, fill=(*(YEL if on else WHT), int(255 * a)), anchor="lm"); x += d.textlength(pw, font=fr_)
            if en: on = False
