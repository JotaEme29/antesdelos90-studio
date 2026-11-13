#!/usr/bin/env python3
"""Renderiza y sube a YouTube, programados, los vídeos con status 'approved'.
Cada vídeo sube como privado con publishAt: YouTube lo hace público solo a esa hora."""
import os, subprocess, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import items, save_meta, ROOT, BUILD, now
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

def render(slug, d):
    os.makedirs(BUILD, exist_ok=True); out = os.path.join(BUILD, f"{slug}.mp4")
    if not os.path.isfile(out):
        subprocess.run([sys.executable, os.path.join(ROOT, "engine", "render_spec.py"), os.path.join(d, "spec.json"), out], check=True)
    return out

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

def main():
    todo = [(s, d, m) for s, d, m in items() if m.get("status") == "approved" and not m.get("video_id")]
    if not todo: print("Nada pendiente."); return
    from yt import youtube
    yt = youtube(); fails = 0
    for slug, d, m in todo:
        print("→", slug)
        try:
            path = os.path.join(d, "video.mp4") if m.get("format") == "long" else render(slug, d)
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
