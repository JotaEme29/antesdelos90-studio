#!/usr/bin/env python3
"""Vigila los vídeos subidos: procesado, rechazos y publicación. Sale con error si algo va mal
(GitHub te avisa por email cuando falla un workflow)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import items, save_meta, now, parse
def main():
    tracked = [(s, d, m) for s, d, m in items() if m.get("video_id") and m.get("status") in ("scheduled", "published")]
    if not tracked: print("Sin vídeos subidos todavía."); return
    from yt import youtube
    yt = youtube(); ids = [m["video_id"] for _, _, m in tracked]; info = {}
    for k in range(0, len(ids), 50):
        r = yt.videos().list(part="status,processingDetails,snippet", id=",".join(ids[k:k + 50])).execute()
        info.update({v["id"]: v for v in r.get("items", [])})
    problems = 0
    for slug, d, m in tracked:
        v = info.get(m["video_id"])
        if not v: print("FALLO", slug, "· el vídeo ya no existe en el canal"); m.update(status="failed", error="no encontrado"); problems += 1; save_meta(d, m); continue
        st = v["status"]; up = st.get("uploadStatus"); priv = st.get("privacyStatus")
        if up in ("failed", "rejected", "deleted"):
            reason = st.get("failureReason") or st.get("rejectionReason"); print("FALLO", slug, "·", up, reason)
            m.update(status="failed", error=f"{up}: {reason}"); problems += 1
        elif priv == "public":
            if m["status"] != "published": m.update(status="published", published_at=now().isoformat(timespec="seconds"))
            print("OK   ", slug, "· público")
        elif parse(m["publish_at"]) < now() and priv != "public":
            print("AVISO", slug, "· la hora de publicación ya pasó y sigue", priv); problems += 1
        else: print("OK   ", slug, "·", up, "· programado", m["publish_at"])
        save_meta(d, m)
    sys.exit(1 if problems else 0)
if __name__ == "__main__": main()
