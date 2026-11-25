import os, re, torch, numpy as np, soundfile as sf
os.environ["COQUI_TOS_AGREED"]="1"
from TTS.api import TTS
tts=TTS("tts_models/multilingual/multi-dataset/xtts_v2").to("cpu")
refs=["tmp_tts/ref1.wav","tmp_tts/ref2.wav","tmp_tts/ref3.wav"]
out=[]; sr=24000; marks=[]; t=0.0
import json
for pi,para in enumerate(open("tmp_tts/guion.txt").read().strip().split("\n")):
    for s in re.split(r"(?<=[.?!…])\s+", para.strip()):
        if not s: continue
        w=np.array(tts.tts(text=s, speaker_wav=refs, language="es", temperature=0.6, repetition_penalty=5.0, speed=1.12))
        # recorta silencios del principio y final de cada frase
        nz=np.where(np.abs(w)>0.02)[0]
        if len(nz): w=w[max(0,nz[0]-600):nz[-1]+1800]
        marks.append({"p":pi,"s":s,"t0":round(t,3),"t1":round(t+len(w)/sr,3)}); out.append(w); t+=len(w)/sr
        out.append(np.zeros(int(sr*0.08))); t+=0.08
    out.append(np.zeros(int(sr*0.14))); t+=0.14
print("MARKS"+json.dumps(marks,ensure_ascii=False))
os.makedirs("out",exist_ok=True); sf.write("out/voz_clonada.wav",np.concatenate(out),sr); print("OK")
