import os, re, torch, numpy as np, soundfile as sf
os.environ["COQUI_TOS_AGREED"]="1"
from TTS.api import TTS
tts=TTS("tts_models/multilingual/multi-dataset/xtts_v2").to("cpu")
refs=["tmp_tts/ref1.wav","tmp_tts/ref2.wav","tmp_tts/ref3.wav"]
out=[]; sr=24000
for para in open("tmp_tts/guion.txt").read().strip().split("\n"):
    for s in re.split(r"(?<=[.?!…])\s+", para.strip()):
        if not s: continue
        w=tts.tts(text=s, speaker_wav=refs, language="es", temperature=0.65, repetition_penalty=5.0, speed=1.05)
        out.append(np.array(w)); out.append(np.zeros(int(sr*0.12)))
    out.append(np.zeros(int(sr*0.25)))
os.makedirs("out",exist_ok=True); sf.write("out/voz_clonada.wav",np.concatenate(out),sr); print("OK")
