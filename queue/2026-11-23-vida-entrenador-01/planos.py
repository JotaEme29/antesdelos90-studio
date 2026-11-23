"""Planos generados por código para 'La vida del entrenador' (ep. 1): escenas animadas e ilustradas
que sustituyen a los clips que no hay (mesa, conos, calle de noche, móvil, grada, banquillo).
Cada función: f(b, lt, dur) pinta sobre el lienzo RGBA b (W2 x H2) el instante lt (s) de un plano de 'dur' s."""
import math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from flat import W2, H2, SS, BG, YEL, WHT, NAVY, font, ease
import cine as C

def grad(b, top, bot):
    a = np.linspace(0, 1, H2)[:, None, None]; t = np.array(top, np.float32); u = np.array(bot, np.float32)
    g = (t + (u - t) * a).astype(np.uint8); b.paste(Image.fromarray(np.repeat(g, W2, axis=1), "RGB").convert("RGBA"))

def glow(b, x, y, r, col, a=1.0):
    l = Image.new("RGBA", b.size, (0, 0, 0, 0)); ImageDraw.Draw(l).ellipse((x - r, y - r, x + r, y + r), fill=(*col, int(150 * a)))
    b.alpha_composite(l.filter(ImageFilter.GaussianBlur(r * .45)))

def person(d, x, y, s, col=(16, 19, 24), pose="walk", ph=0.0, hood=False, bag=False, rim=None):
    """silueta de espaldas; (x, y) = pies; s = altura en px (ya escalada)."""
    hw = s * .13; head = s * .075; sh_y = y - s * .80; hip_y = y - s * .45
    if pose == "sit":
        hip_y = y - s * .30; sh_y = y - s * .62
        d.rounded_rectangle((x - hw, sh_y, x + hw, hip_y + s * .05), radius=hw * .5, fill=col)
        d.rounded_rectangle((x - hw * .95, hip_y - s * .02, x + hw * .95, hip_y + s * .08), radius=s * .03, fill=col)
        hy = sh_y - head * .6 + s * .03                      # cabeza baja
    else:
        sw = math.sin(ph) * s * .07
        for sg in (-1, 1):
            d.line((x + sg * hw * .45, hip_y, x + sg * hw * .45 + sg * sw, y), fill=col, width=int(s * .085))
        d.rounded_rectangle((x - hw, sh_y, x + hw, hip_y + s * .04), radius=hw * .5, fill=col)
        if pose == "shout":
            up = .5 + .5 * math.sin(ph * 2)
            for sg in (-1, 1):
                ex, ey = x + sg * hw * 2.1, sh_y - s * (.10 + .22 * up)
                d.line((x + sg * hw * .8, sh_y + s * .05, ex, ey), fill=col, width=int(s * .06))
        else:
            for sg in (-1, 1):
                d.line((x + sg * hw * 1.0, sh_y + s * .04, x + sg * hw * 1.15 - sg * sw * .5, hip_y + s * .02), fill=col, width=int(s * .055))
        hy = sh_y - head * .9
    d.ellipse((x - head, hy - head, x + head, hy + head), fill=col)
    if hood: d.pieslice((x - head * 1.45, hy - head * 1.3, x + head * 1.45, hy + head * 1.7), 180, 360, fill=col)
    if bag: d.rounded_rectangle((x - hw * .85, sh_y + s * .03, x + hw * .85, sh_y + s * .30), radius=s * .04, fill=(34, 38, 46))
    if rim:
        d.arc((x - head, hy - head, x + head, hy + head), 200, 340, fill=rim, width=max(2, int(s * .012)))

# ------------------------------------------------------------------ 03 · la mesa de noche: planificar la sesión
def mesa(b, lt, dur):
    grad(b, (38, 26, 18), (18, 12, 9)); d = ImageDraw.Draw(b, "RGBA")
    rnd = random.Random(3)
    for i in range(70):                                  # vetas de la madera
        y = rnd.uniform(0, H2); d.line((0, y, W2, y + rnd.uniform(-40, 40) * SS), fill=(70, 48, 30, rnd.randint(18, 40)), width=int(rnd.uniform(1, 4) * SS))
    glow(b, W2 * .78, H2 * .2, 900 * SS, (255, 196, 110), .55 + .05 * math.sin(lt * 3))
    pg = Image.new("RGBA", (int(820 * SS), int(1100 * SS)), (0, 0, 0, 0)); p = ImageDraw.Draw(pg)
    p.rounded_rectangle((0, 0, pg.width - 1, pg.height - 1), radius=14 * SS, fill=(244, 238, 222, 255))
    for k in range(22): p.line((40 * SS, (150 + k * 46) * SS, pg.width - 40 * SS, (150 + k * 46) * SS), fill=(190, 205, 225, 150), width=int(2 * SS))
    p.line((110 * SS, 0, 110 * SS, pg.height), fill=(230, 130, 130, 160), width=int(3 * SS))
    ink = (30, 46, 92, 255)
    p.text((140 * SS, 90 * SS), "SESIÓN · MARTES", font=font(46, "Black"), fill=ink, anchor="lm")
    px0, py0, pw, ph_ = 150 * SS, 190 * SS, 560 * SS, 330 * SS     # mini campo con la tarea
    p.rounded_rectangle((px0, py0, px0 + pw, py0 + ph_), radius=8 * SS, outline=ink, width=int(4 * SS))
    p.line((px0 + pw / 2, py0, px0 + pw / 2, py0 + ph_), fill=ink, width=int(3 * SS))
    for (u, v, c) in ((.2, .3, ink), (.2, .7, ink), (.4, .5, ink), (.62, .35, (200, 40, 40, 255)), (.62, .65, (200, 40, 40, 255))):
        cx, cy = px0 + pw * u, py0 + ph_ * v; p.ellipse((cx - 16 * SS, cy - 16 * SS, cx + 16 * SS, cy + 16 * SS), outline=c, width=int(5 * SS))
    e = ease((lt - .4) / 1.6)                            # la flecha se dibuja mientras miras
    if e > 0:
        a0, a1 = (px0 + pw * .4, py0 + ph_ * .5), (px0 + pw * .85, py0 + ph_ * .45)
        m = (a0[0] + (a1[0] - a0[0]) * e, a0[1] + (a1[1] - a0[1]) * e - math.sin(e * math.pi) * 40 * SS)
        p.line((a0, m), fill=ink, width=int(5 * SS))
    rows = ["1. Rondo 4 contra 2 · 12'", "2. Posesión 6 contra 3 · 15'", "3. Partido condicionado · 20'", "Convocatoria → viernes"]
    for k, r in enumerate(rows):
        a = ease((lt - .6 - k * .5) / .4)
        if a > 0: p.text((140 * SS, (600 + k * 92) * SS), r, font=font(40, "SemiBold"), fill=(*ink[:3], int(255 * a)), anchor="lm")
    z = .86 + .05 * ease(lt / max(1, dur)); pg2 = pg.rotate(-4, expand=True, resample=Image.BICUBIC)
    pg2 = pg2.resize((int(pg2.width * z), int(pg2.height * z)), Image.BICUBIC)
    sh = Image.new("RGBA", b.size, (0, 0, 0, 0)); x0, y0 = int(W2 / 2 - pg2.width / 2), int(H2 * .465 - pg2.height / 2)
    ImageDraw.Draw(sh).rectangle((x0 + 30 * SS, y0 + 40 * SS, x0 + pg2.width + 30 * SS, y0 + pg2.height + 40 * SS), fill=(0, 0, 0, 140))
    b.alpha_composite(sh.filter(ImageFilter.GaussianBlur(30 * SS))); b.alpha_composite(pg2, (x0, y0))
    d = ImageDraw.Draw(b, "RGBA"); bx, by = x0 + pg2.width * .78, y0 + pg2.height * .62   # bolígrafo
    d.line((bx, by, bx + 260 * SS, by + 330 * SS), fill=(20, 22, 30, 255), width=int(22 * SS))
    d.line((bx, by, bx + 40 * SS, by + 50 * SS), fill=(200, 200, 205, 255), width=int(14 * SS))

# ------------------------------------------------------------------ 04 · conos y balones antes de la sesión (cámara a ras de césped)
CONES = [(-12 + 2.6 * i, 41 + (i % 2) * 2.2) for i in range(9)] + [(-9, 48), (-3, 48), (3, 48), (9, 48), (-9, 36), (9, 36)]
BALLS = [(-15, 38), (-14.2, 38.8), (-15.6, 39.4), (-14.6, 37.2), (6, 45), (1, 50)]
def cone(b, cam, x, z, a=1.0):
    d = ImageDraw.Draw(b, "RGBA"); bx, by, sc = cam.P(x, z); tx, ty, _ = cam.P(x, z, .5); r = .34 * sc * SS
    d.ellipse((bx - r * 1.5, by - r * .5, bx + r * 1.5, by + r * .5), fill=(0, 0, 0, int(110 * a)))
    d.polygon([(bx - r, by), (bx + r, by), (tx, ty)], fill=(255, 122, 30, int(255 * a)))
    d.line((bx - r * .55, by - (by - ty) * .45, bx + r * .55, by - (by - ty) * .45), fill=(255, 255, 255, int(200 * a)), width=max(1, int(r * .25)))
def conos(b, lt, dur):
    u = ease(lt / max(1, dur)); cam = C.Cam(el=13 + 3 * u, d=17 - 3 * u, tx=-5 + 6 * u, tz=43, az=-32 + 22 * u, cy=1120)
    grad(b, (96, 104, 140), (40, 44, 56)); glow(b, W2 * .25, H2 * .30, 900 * SS, (255, 170, 90), .9)
    C.pitch(b, cam)
    items = [("c", x, z) for x, z in CONES] + [("b", x, z) for x, z in BALLS]
    for k, x, z in sorted(items, key=lambda it: -cam.P(it[1], it[2])[2]):
        cone(b, cam, x, z) if k == "c" else C.ballp(b, cam, x, z, .22)

# ------------------------------------------------------------------ 06 · el chaval que vuelve a casa (calle de noche, de espaldas)
def calle(b, lt, dur):
    grad(b, (12, 18, 34), (8, 9, 12)); d = ImageDraw.Draw(b, "RGBA"); vx, vy = W2 / 2, H2 * .40
    d.polygon([(0, H2), (W2, H2), (vx + 40 * SS, vy), (vx - 40 * SS, vy)], fill=(24, 26, 31, 255))       # acera
    for k in range(12):                                                    # baldosas
        f = (k + (lt * .35) % 1) / 12; y = vy + (H2 - vy) * f ** 2
        d.line((vx - (W2 / 2 + 300 * SS) * f ** 2, y, vx + (W2 / 2 + 300 * SS) * f ** 2, y), fill=(36, 38, 44, 255), width=int(3 * SS))
    for k in range(5):                                                     # farolas que se alejan
        f = 1 / (1.3 + k * .9); x = vx - 520 * SS * f; top = vy - 1300 * SS * f * .55; base = vy + (H2 - vy) * f ** 1.2 * .9
        d.line((x, base, x, top), fill=(46, 48, 54, 255), width=max(2, int(16 * SS * f)))
        glow(b, x + 30 * SS * f, top, 260 * SS * f + 30 * SS, (255, 160, 70), .8)
        d = ImageDraw.Draw(b, "RGBA")
        l = Image.new("RGBA", b.size, (0, 0, 0, 0)); ImageDraw.Draw(l).polygon([(x, top), (x - 200 * SS * f, base), (x + 260 * SS * f, base)], fill=(255, 170, 80, 26))
        b.alpha_composite(l.filter(ImageFilter.GaussianBlur(20 * SS))); d = ImageDraw.Draw(b, "RGBA")
    s = (900 - 260 * ease(lt / max(1, dur))) * SS; px, py = W2 * .54, H2 * .80 - 120 * SS * ease(lt / max(1, dur))
    l = Image.new("RGBA", b.size, (0, 0, 0, 0)); ImageDraw.Draw(l).ellipse((px - s * .22, py - s * .03, px + s * .5, py + s * .05), fill=(0, 0, 0, 150))
    b.alpha_composite(l.filter(ImageFilter.GaussianBlur(12 * SS))); d = ImageDraw.Draw(b, "RGBA")
    person(d, px, py, s, col=(20, 22, 28), pose="walk", ph=lt * 5.5, bag=True)

# ------------------------------------------------------------------ 07 · el móvil que no para (notificaciones genéricas, ilegibles)
def movil(b, lt, dur):
    grad(b, (30, 22, 16), (14, 10, 8)); glow(b, W2 * .5, H2 * .62, 700 * SS, (120, 160, 255), .25 + .1 * math.sin(lt * 9))
    vib = (math.sin(lt * 70) * 6 * SS) if (lt % 1.4) < .35 else 0
    ph = Image.new("RGBA", (int(620 * SS), int(1240 * SS)), (0, 0, 0, 0)); p = ImageDraw.Draw(ph)
    p.rounded_rectangle((0, 0, ph.width - 1, ph.height - 1), radius=90 * SS, fill=(10, 10, 12, 255))
    p.rounded_rectangle((22 * SS, 22 * SS, ph.width - 22 * SS, ph.height - 22 * SS), radius=72 * SS, fill=(22, 30, 52, 255))
    p.text((ph.width / 2, 210 * SS), "22:47", font=font(120, "Bold"), fill=(235, 238, 245, 255), anchor="mm")
    n = int(lt / .55) + 1
    for k in range(min(n, 6)):
        a = ease((lt - k * .55) / .3); y = (380 + k * 150) * SS
        p.rounded_rectangle((50 * SS, y, ph.width - 50 * SS, y + 128 * SS), radius=28 * SS, fill=(235, 238, 245, int(225 * a)))
        p.ellipse((80 * SS, y + 34 * SS, 140 * SS, y + 94 * SS), fill=(150, 160, 175, int(255 * a)))
        p.rounded_rectangle((165 * SS, y + 36 * SS, 400 * SS, y + 56 * SS), radius=10 * SS, fill=(120, 128, 140, int(255 * a)))
        p.rounded_rectangle((165 * SS, y + 72 * SS, (480 - 40 * (k % 3)) * SS, y + 90 * SS), radius=9 * SS, fill=(170, 176, 186, int(255 * a)))
    ph = ph.rotate(8, expand=True, resample=Image.BICUBIC)
    sh = Image.new("RGBA", b.size, (0, 0, 0, 0)); x0, y0 = int(W2 / 2 - ph.width / 2 + vib), int(H2 * .70 - ph.height / 2)
    ImageDraw.Draw(sh).rounded_rectangle((x0 + 40 * SS, y0 + 50 * SS, x0 + ph.width, y0 + ph.height + 20 * SS), radius=90 * SS, fill=(0, 0, 0, 170))
    b.alpha_composite(sh.filter(ImageFilter.GaussianBlur(40 * SS))); b.alpha_composite(ph, (x0, y0))

# ------------------------------------------------------------------ 08 · la grada: el que entrena desde fuera
def grada(b, lt, dur):
    u = ease(lt / max(1, dur)); grad(b, (64, 84, 118), (22, 26, 32)); d = ImageDraw.Draw(b, "RGBA")
    y0 = H2 * .30; rows = 9
    for r in range(rows):                                                  # gradas en perspectiva
        y = y0 + r * 120 * SS; sc = .7 + r * .05
        d.rectangle((0, y + 70 * SS, W2, y + 120 * SS), fill=(52, 60, 72, 255))
        for k in range(-2, 20):
            x = (k * 118 + (r % 2) * 59 - 60 * u) * SS * sc + W2 * .02
            d.rounded_rectangle((x, y, x + 86 * SS * sc, y + 78 * SS), radius=12 * SS, fill=(226, 230, 236, 255) if (k + r) % 7 else (60, 110, 200, 255))
    d.rectangle((0, y0 + rows * 120 * SS, W2, H2), fill=(30, 70, 42, 255))   # valla y césped
    for k in range(0, int(W2), int(60 * SS)): d.line((k, y0 + rows * 120 * SS - 160 * SS, k, y0 + rows * 120 * SS), fill=(90, 96, 104, 200), width=int(4 * SS))
    d.line((0, y0 + rows * 120 * SS - 160 * SS, W2, y0 + rows * 120 * SS - 160 * SS), fill=(90, 96, 104, 220), width=int(6 * SS))
    person(d, W2 * .62, y0 + 7 * 120 * SS + 76 * SS, 900 * SS, col=(18, 20, 26), pose="shout", ph=lt * 3.2)
    person(d, W2 * .18, y0 + 2 * 120 * SS + 76 * SS, 300 * SS, col=(80, 86, 96), pose="stand")

# ------------------------------------------------------------------ 09 · el banquillo: el que cree que es personal
def banquillo(b, lt, dur):
    u = ease(lt / max(1, dur)); grad(b, (120, 140, 170), (60, 72, 86)); d = ImageDraw.Draw(b, "RGBA")
    hz = H2 * .36
    d.rectangle((0, hz, W2, H2), fill=(36, 92, 52, 255))                                   # césped
    for k in range(9): d.rectangle((0, hz + k * k * 22 * SS, W2, hz + k * k * 22 * SS + 11 * k * SS), fill=(40, 102, 58, 255))
    d.line((0, hz + 90 * SS, W2, hz + 70 * SS), fill=(230, 236, 230, 200), width=int(5 * SS))
    for k in range(7):                                                                     # partido al fondo
        x = W2 * (.1 + k * .13) + 40 * SS * math.sin(lt * 1.4 + k); y = hz + 40 * SS + 25 * SS * math.sin(lt + k * 2)
        person(d, x, y, 120 * SS, col=(240, 200, 40) if k % 2 else (235, 236, 240), pose="walk", ph=lt * 6 + k)
    b.alpha_composite(Image.new("RGBA", b.size, (0, 0, 0, 0)).filter(ImageFilter.GaussianBlur(1)))
    l = Image.new("RGBA", b.size, (0, 0, 0, 0)); ImageDraw.Draw(l).rectangle((0, 0, W2, hz + 200 * SS), fill=(0, 0, 0, 0))
    d = ImageDraw.Draw(b, "RGBA")
    d.polygon([(0, H2 * .08), (W2, H2 * .03), (W2, H2 * .14), (0, H2 * .18)], fill=(230, 200, 40, 200))        # techo del banquillo
    d.rectangle((0, H2 * .70, W2, H2 * .74), fill=(28, 30, 34, 255))                    # asiento
    d.rectangle((0, H2 * .74, W2, H2), fill=(18, 20, 24, 255))
    for x in (W2 * .08, W2 * .92): d.rectangle((x - 14 * SS, H2 * .14, x + 14 * SS, H2 * .72), fill=(40, 42, 48, 255))
    cx, by = W2 * (.50 - .02 * u), H2 * .725; k = 1.0 + .03 * u; col = (14, 16, 20)       # chaval sentado de espaldas, capucha y cabeza gacha
    d.polygon([(cx - 250 * SS * k, by), (cx + 250 * SS * k, by), (cx + 200 * SS * k, by - 520 * SS * k), (cx - 200 * SS * k, by - 520 * SS * k)], fill=col)
    d.ellipse((cx - 230 * SS * k, by - 600 * SS * k, cx + 230 * SS * k, by - 400 * SS * k), fill=col)          # hombros
    d.ellipse((cx - 125 * SS * k, by - 700 * SS * k, cx + 125 * SS * k, by - 470 * SS * k), fill=(24, 26, 32))  # capucha
    d.arc((cx - 125 * SS * k, by - 700 * SS * k, cx + 125 * SS * k, by - 470 * SS * k), 200, 340, fill=(90, 96, 110), width=int(6 * SS))

FN = {"mesa": mesa, "conos": conos, "calle": calle, "movil": movil, "grada": grada, "banquillo": banquillo}
