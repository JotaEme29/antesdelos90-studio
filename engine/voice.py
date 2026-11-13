#!/usr/bin/env python3
"""Prepara la voz grabada por Miguel: limpia silencios, normaliza y transcribe con marcas por palabra.

  python engine/voice.py queue/<slug>        → build/<slug>/voice.wav + build/<slug>/words.json

words.json = [{"w": "palabra", "s": inicio, "e": fin}, ...] en segundos sobre voice.wav.
Transcripción: faster-whisper (modelo 'small', español). Si no está disponible y existe
un words.json escrito a mano en la carpeta del vídeo, se usa ese.
"""
import glob, json, os, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def find_voice(d):
    for ext in ("m4a", "mp3", "wav", "aac", "ogg", "opus", "mp4", "mov", "webm"):
        f = glob.glob(os.path.join(d, f"voz*.{ext}")) + glob.glob(os.path.join(d, f"voz*.{ext.upper()}"))
        if f: return sorted(f)[0]
    return None

def prepare(d, out_dir):
    src = find_voice(d)
    if not src: raise SystemExit(f"No hay archivo voz.* en {d}")
    os.makedirs(out_dir, exist_ok=True); wav = os.path.join(out_dir, "voice.wav")
    # quita silencio inicial y final, filtra graves/ruido suave y normaliza a -16 LUFS
    af = ("highpass=f=80,afftdn=nf=-25,"
          "silenceremove=start_periods=1:start_threshold=-42dB:start_silence=0.15,"
          "areverse,silenceremove=start_periods=1:start_threshold=-42dB:start_silence=0.25,areverse,"
          "loudnorm=I=-16:TP=-1.5:LRA=11")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-vn", "-ac", "1", "-ar", "48000", "-af", af, wav], check=True)
    words = os.path.join(out_dir, "words.json"); manual = os.path.join(d, "words.json")
    try:
        from faster_whisper import WhisperModel
        model = WhisperModel(os.environ.get("WHISPER_MODEL", "small"), device="cpu", compute_type="int8")
        segs, _ = model.transcribe(wav, language="es", word_timestamps=True, vad_filter=True, beam_size=5)
        W = [{"w": w.word.strip(), "s": round(w.start, 3), "e": round(w.end, 3)} for s in segs for w in (s.words or []) if w.word.strip()]
    except Exception as e:
        if not os.path.isfile(manual): raise SystemExit(f"No se pudo transcribir ({e}) y no hay words.json manual")
        W = json.load(open(manual)); print("usando words.json manual")
    json.dump(W, open(words, "w"), ensure_ascii=False, indent=1)
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", wav], capture_output=True, text=True).stdout)
    print(f"voz: {os.path.basename(src)} → {dur:.1f} s, {len(W)} palabras")
    return wav, words, dur

if __name__ == "__main__":
    d = sys.argv[1].rstrip("/"); slug = os.path.basename(d)
    prepare(d, os.path.join(ROOT, "build", slug))
