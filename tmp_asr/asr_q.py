import sys
from faster_whisper import WhisperModel
m=WhisperModel("small",device="cpu",compute_type="int8")
seg,_=m.transcribe(sys.argv[1],language="es",word_timestamps=True,condition_on_previous_text=False)
for s in seg:
    for w in s.words:
        if w.start>40: print(f"W {w.start:6.2f} {w.end:6.2f} {w.word}")
