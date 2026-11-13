#!/usr/bin/env python3
"""Renderiza y sube a YouTube, programados, los vídeos con status 'approved'.
Cada vídeo sube como privado con publishAt: YouTube lo hace público solo a esa hora."""
import os, subprocess, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import datetime as dt
from common import items, save_meta, ROOT, BUILD, now, parse
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

def render(slug, d, voice=False):
    os.makedirs(BUILD, exist_ok=True); out = os.path.join(BUILD, f"{slug}.mp4")
    if voice: subprocess.run([sys.executable, os.path.join(ROOT, "engine", "voice.py"), d], check=True)
    if not os.path.isfile(out):
        subprocess.run([sys.executable, os.path.join(ROOT, "engine", "render_spec.py"), os.path.join(d, "spec.json"), out], check=True)
    return out

def has_voice(d):
    sys.path.insert(0, os.path.join(ROOT, "engine")); from voice import find_voice; return find_voice(d) is not None

def next_slot(taken):
    """Siguiente hueco libre a las 19:30 (Madrid), desde mañana."""
    from zoneinfo import ZoneInfo
    tz = ZoneInfo("Europe/Madrid"); day = now().astimezone(tz).date() + dt.timedelta(days=1)
    while True:
        cand = dt.datetime.combine(day, dt.time(19, 30), tz)
        if all(abs((cand - t).total_seconds()) > 3 * 3600 for t in taken): return cand.isoformat()
        day += dt.timedelta(days=1)

def upload(yt, path, m):
    body = {"snippet": {"title": m["title"], "description": m.get("description", ""), "tags": m.get("tags", []),
                        "categoryId": m.get("category", "17"), "defaultLanguage": "es", "defaultAudioLanguage": "es"},
            "status": {"privacyStatus": "private", "publishAt": m["publish_at"], "selfDeclaredMadeForKids": False,
                       "embeddable": True, "license": "youtube"}}
    req = yt.videos().insert(part="snippet,status", body=body, notifySubscribers=True,
                             media_body=MediaFileUpload(path, mimetype="video/mp4", chunksize=8 * 1024 * 1024, resumable=True))
    resp = None
    while resp is None:
        st, resp = req.next_chunk()
        if st: print(f"  subiendo… {int(st.progress() * 100)} %", flush=True)
    return resp["id"]

WINDOW_H = 30   # solo se sube lo que se publica en las próximas 30 h: hasta entonces se puede frenar

def main():
    if os.path.exists(os.path.join(ROOT, "PAUSA")): print("Archivo PAUSA presente: no se publica nada."); return
    limit = now() + dt.timedelta(hours=WINDOW_H)
    allm = list(items())
    taken = [parse(m["publish_at"]) for _, _, m in allm if m.get("publish_at") and m.get("status") in ("approved", "scheduled", "published")]
    for slug, d, m in allm:                         # vídeos con voz: en cuanto llega la grabación, se programan
        if m.get("status") == "awaiting_voice" and has_voice(d):
            if not m.get("publish_at") or parse(m["publish_at"]) < now() + dt.timedelta(hours=3):
                m["publish_at"] = next_slot(taken); taken.append(parse(m["publish_at"]))
            m["status"] = "approved"; save_meta(d, m); print(f"voz recibida: {slug} → {m['publish_at']}")
    todo = [(s, d, m) for s, d, m in items() if m.get("status") == "approved" and not m.get("video_id") and parse(m["publish_at"]) <= limit]
    if not todo: print("Nada pendiente."); return
    from yt import youtube
    yt = youtube(); fails = 0
    want = os.environ.get("YT_CHANNEL_HANDLE", "@antesdelos90").lower()
    ch = yt.channels().list(part="snippet", mine=True).execute().get("items", [])
    got = [(c["snippet"].get("customUrl", "") or "").lower() for c in ch]
    if want not in got:
        names = ", ".join(f"{c['snippet'].get('title')} ({c['snippet'].get('customUrl')})" for c in ch) or "ninguno"
        print(f"PARADO: la autorización es del canal {names}, no de {want}. No se sube nada. Repite get_token.py eligiendo {want}.")
        sys.exit(1)
    for slug, d, m in todo:
        print("→", slug)
        try:
            path = os.path.join(d, "video.mp4") if m.get("format") in ("long", "file") else render(slug, d, voice=bool(m.get("voice")))
            vid = upload(yt, path, m)
            thumb = os.path.join(d, "thumbnail.jpg")
            if m.get("format") == "long" and os.path.isfile(thumb):
                yt.thumbnails().set(videoId=vid, media_body=MediaFileUpload(thumb, mimetype="image/jpeg")).execute()
            m.update(video_id=vid, status="scheduled", uploaded_at=now().isoformat(timespec="seconds"), error=None)
            print(f"  OK https://youtu.be/{vid} · se publica {m['publish_at']}")
        except (HttpError, subprocess.CalledProcessError, OSError) as e:
            m.update(status="failed", error=str(e)[:500]); fails += 1; print("  ERROR", e)
        save_meta(d, m)
    sys.exit(1 if fails else 0)

if __name__ == "__main__": main()
