import sys, os
sys.path.insert(0, "/home/claude/antesdelos90-studio/engine")
from PIL import Image, ImageDraw
from flat import W2, H2, BG, YEL, WHT, ease, lerp2, finish, font
import cine as C
MAD=(255,204,0); PSV=(214,40,57)
def track(keys,t):
    if t<=keys[0][0]: return keys[0][1]
    for (t0,a),(t1,b) in zip(keys,keys[1:]):
        if t0<=t<=t1: return lerp2(a,b,ease((t-t0)/max(1e-6,t1-t0)))
    return keys[-1][1]
def label(b,t,txt,sub=None):
    d=ImageDraw.Draw(b,"RGBA"); k=ease(t/.3)
    f=font(62,"Black"); tw=d.textlength(txt,font=f)
    d.rounded_rectangle((W2/2-tw/2-40,250*2-70,W2/2+tw/2+40,250*2+70),radius=70,fill=(*YEL,int(255*k)))
    d.text((W2/2,250*2),txt,font=f,fill=(10,14,20,int(255*k)),anchor="mm")
    if sub: d.text((W2/2,360*2),sub,font=font(44,"Bold"),fill=(*WHT,int(255*k)),anchor="mm",stroke_width=6,stroke_fill=(0,0,0))
# Madrid ataca hacia z=105. PSV bloque bajo.
PSVP=[(0,100),(-20,86),(-7,90),(7,90),(20,86),(-14,76),(0,78),(14,76),(-24,66),(24,66),(0,64)]
def scene_cambio(t):
    # 0-3: 1ª parte (Tchouaméni+Bernardo de pivotes, Güler a la derecha), 3-6.5: 2ª (Güler baja al lado de Bernardo, Bellingham entre líneas)
    e=ease((t-3.2)/1.2)
    M={"Courtois":(0,8),"Valverde":(24,46),"cen1":(-9,36),"cen2":(9,36),"Cucurella":(-24,46),
       "Bernardo":(lerp2((-7,52),(-7,54),e)),"Güler":lerp2((22,70),(7,56),e),"Diomandé":(-22,70),"Mbappé":(4,82),"Vinícius":(-14,80)}
    piv=("Tchouaméni",(7,52)) if t<3.2 else ("Bellingham",(2,72))
    M[piv[0]]=piv[1]
    cam=C.camkeys([(0,dict(el=55,d=175,tx=0,tz=62,az=0,cy=900)),(3.0,dict(el=55,d=175,tx=0,tz=62,az=0,cy=900)),(4.4,dict(el=40,d=120,tx=0,tz=64,az=10,cy=900)),(7,dict(el=40,d=120,tx=0,tz=64,az=6,cy=900))],t)
    b=Image.new("RGBA",(W2,H2),(*BG,255)); C.pitch(b,cam)
    if t>4.4: C.zone(b,cam,[(-14,66),(14,66),(14,76),(-14,76)],YEL,ease((t-4.4)/.4),40)
    ppl=[(n,p,MAD,False) for n,p in M.items()]+[(None,p,PSV,True) for p in PSVP]
    for n,(x,z),col,dk in sorted(ppl,key=lambda q:-cam.P(*q[1])[2]):
        show = n in ("Tchouaméni","Bernardo","Güler") if t<3.2 else n in ("Bernardo","Güler","Bellingham")
        hi = (t%1.0) if (t>=3.2 and n in ("Güler","Bellingham")) else 0
        if t>=3.2 and n in ("Güler","Bellingham"): C.glow_ring(b,cam,x,z,2.6,YEL)
        C.player(b,cam,x,z,col,None,n if show else None,1,0,dk,1.0 if show else 0,below=True)
    b.alpha_composite(C.vignette())
    if t<3.2: label(b,t,"1ª PARTE","Doble pivote: Tchouaméni y Bernardo")
    else: label(b,t-3.2,"2ª PARTE","Güler baja · Bellingham entre líneas")
    return finish(b.convert("RGB"))
def scene_gol(t):
    # Vini centra (-26,88) -> Diomandé (-6,95) cede a Güler (6,86) tacón -> Valverde (12,80) dispara -> gol
    VI=(-27,90); DI=[(0,(-10,90)),(1.0,(-6,95))]; GU=(5,86); VA=[(0,(18,72)),(2.6,(13,80))]
    BALL=[(0,VI),(1.0,(-6,95)),(1.5,(-6,95)),(2.1,GU),(2.4,GU),(2.8,(12,81)),(3.0,(12,81)),(3.55,(3.0,105.6))]
    def bp(t):
        for (t0,a),(t1,c) in zip(BALL,BALL[1:]):
            if t0<=t<=t1: return lerp2(a,c,ease((t-t0)/max(1e-6,t1-t0)))
        return BALL[-1][1]
    slow = 2.8 + (t-2.8)*.45 if t>2.8 else t   # cámara lenta en el disparo
    s=slow
    cam=C.camkeys([(0,dict(el=34,d=95,tx=-6,tz=82,az=-12,cy=1150)),(2.4,dict(el=30,d=80,tx=4,tz=86,az=6,cy=1150)),(4.5,dict(el=24,d=66,tx=6,tz=92,az=14,cy=1150))],s)
    b=Image.new("RGBA",(W2,H2),(*BG,255)); C.pitch(b,cam)
    M={"Vinícius":VI,"Diomandé":track(DI,s),"Güler":GU,"Valverde":track(VA,s),"Mbappé":(0,96),"Bellingham":(-4,78)}
    P=[(0,103.5),(-8,97),(-1,94),(6,96),(12,92),(-14,88),(2,88),(16,84),(-18,82)]
    ppl=[(n,p,MAD,False) for n,p in M.items()]+[(None,p,PSV,True) for p in P]
    for n,(x,z),col,dk in sorted(ppl,key=lambda q:-cam.P(*q[1])[2]):
        show=n in ("Vinícius","Diomandé","Güler","Valverde")
        C.player(b,cam,x,z,col,None,n if show else None,1,0,dk,1.0 if show else 0,below=True)
    pts=[bp(s-.05*k) for k in range(6,-1,-1)]
    if abs(pts[0][0]-pts[-1][0])+abs(pts[0][1]-pts[-1][1])>2: C.ball_trail(b,cam,[(x,z,.4) for x,z in pts])
    bx,bz=bp(s); C.ballp(b,cam,bx,bz,.35)
    b.alpha_composite(C.vignette())
    label(b,t,"1-1 · VALVERDE 50'","Vini → Diomandé → tacón de Güler → gol")
    C.flash(b,s,3.6,"GOL")
    C.white_flash(b,s,3.55)
    return finish(b.convert("RGB"))
def scene_presion(t):
    # 2ª parte: línea alta (Konaté y Huijsen) y presión arriba; el PSV sale desde atrás y pierde el balón
    e=ease((t-0.8)/1.4)
    base={"Courtois":(0,8),"Valverde":(24,46),"Konaté":(9,34),"Huijsen":(-9,34),"Cucurella":(-24,46),"Bernardo":(-6,52),"Güler":(7,54),
          "Bellingham":(2,70),"Diomandé":(-20,72),"Mbappé":(2,84),"Vinícius":(-12,82)}
    up={"Courtois":(0,22),"Valverde":(26,62),"Konaté":(9,50),"Huijsen":(-9,50),"Cucurella":(-26,62),"Bernardo":(-7,68),"Güler":(8,70),
        "Bellingham":(3,82),"Diomandé":(-20,86),"Mbappé":(6,94),"Vinícius":(-14,92)}
    M={k:lerp2(base[k],up[k],e) for k in base}
    P=[(0,101),(-22,90),(-8,95),(8,95),(22,90),(-12,84),(2,84),(14,84),(-26,74),(26,74),(0,72)]
    BALL=[(0,(-8,95)),(2.6,(-8,95)),(3.2,(-12,84)),(3.6,(-12,84))]
    def bp(t):
        if t>=3.6: return M["Vinícius"] if t<4.0 else lerp2(M["Vinícius"],(-4,96),ease((t-4.0)/.6))
        for (t0,a),(t1,c) in zip(BALL,BALL[1:]):
            if t0<=t<=t1: return lerp2(a,c,ease((t-t0)/max(1e-6,t1-t0)))
        return BALL[-1][1]
    if t>2.8: M["Vinícius"]=lerp2(M["Vinícius"],(-12,85),ease((t-2.8)/.6))
    cam=C.camkeys([(0,dict(el=50,d=170,tx=0,tz=58,az=0,cy=900)),(2.4,dict(el=46,d=150,tx=0,tz=66,az=8,cy=900)),(5.5,dict(el=36,d=105,tx=-4,tz=80,az=-10,cy=950))],t)
    b=Image.new("RGBA",(W2,H2),(*BG,255)); C.pitch(b,cam)
    a=ease((t-1.0)/.4)
    zl=34+(50-34)*e
    d=ImageDraw.Draw(b,"RGBA"); q=[cam.P(x,zl)[:2] for x in (-34,34)]; d.line(q,fill=(*YEL,int(230*a)),width=8)
    for n,tgt in (("Mbappé",(-8,95)),("Bellingham",(-12,84)),("Vinícius",(-22,90))):
        if 1.6<t<3.6: C.arrow(b,cam,M[n],lerp2(M[n],tgt,.75),YEL,ease((t-1.6)/.5),1-ease((t-3.3)/.3))
    ppl=[(n,p,MAD,False) for n,p in M.items()]+[(None,p,PSV,True) for p in P]
    for n,(x,z),col,dk in sorted(ppl,key=lambda q:-cam.P(*q[1])[2]):
        show=n in ("Konaté","Huijsen") if t<2.4 else n in ("Bellingham","Mbappé","Vinícius")
        C.player(b,cam,x,z,col,None,n if show else None,1,0,dk,1.0 if show else 0,below=True)
    bx,bz=bp(t); C.ballp(b,cam,bx,bz,.3)
    b.alpha_composite(C.vignette())
    label(b,t,"2ª PARTE: PRESIÓN ALTA","Línea arriba con Konaté y Huijsen")
    if t>3.6: C.flash(b,t,3.6,"ROBO")
    return finish(b.convert("RGB"))
if __name__=="__main__":
    which=sys.argv[1]; out=sys.argv[2]
    fn={"cambio":(scene_cambio,7.0),"gol":(scene_gol,6.4),"presion":(scene_presion,6.0)}[which]
    if "--sheet" in sys.argv:
        ts=[float(x) for x in sys.argv[sys.argv.index("--sheet")+1:]]
        C.sheet(lambda t,r: fn[0](t), ts, out)
    else:
        sfx=out+".wav"; C.sfx_track(sfx,fn[1],whooshes={"cambio":[0.0,3.1],"gol":[0.0],"presion":[0.0,1.6]}[which],hits={"cambio":[],"gol":[4.3],"presion":[3.6]}[which])
        C.encode(fn[0],fn[1],out,"/home/claude/antesdelos90-studio/music/okay_for_now-televisions.mp3",sfx,gain=-14)
