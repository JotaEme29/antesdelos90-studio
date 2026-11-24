import sys,json
from faster_whisper import WhisperModel
m=WhisperModel("small",device="cpu",compute_type="int8")
seg,_=m.transcribe(sys.argv[1],language="es",word_timestamps=True,condition_on_previous_text=False)
out=[[round(w.start,2),round(w.end,2),w.word.strip()] for s in seg for w in s.words]
print("JSON"+json.dumps(out,ensure_ascii=False))
