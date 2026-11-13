#!/usr/bin/env python3
"""Descarga estadísticas por vídeo y del canal → data/metrics.json y data/report.md"""
import json, os, sys, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import items, DATA, now
METRICS = "views,estimatedMinutesWatched,averageViewDuration,averageViewPercentage,likes,comments,shares,subscribersGained"
def main():
    pub = [(s, m) for s, _, m in items() if m.get("status") == "published" and m.get("video_id")]
    os.makedirs(DATA, exist_ok=True)
    if not pub: print("Aún no hay vídeos publicados."); return
    from yt import analytics, youtube
    ya, yt = analytics(), youtube()
    start = min(m.get("published_at", now().isoformat())[:10] for _, m in pub); end = now().date().isoformat()
    ids = [m["video_id"] for _, m in pub]; rows = {}
    for k in range(0, len(ids), 200):
        r = ya.reports().query(ids="channel==MINE", startDate=start, endDate=end, metrics=METRICS, dimensions="video",
                               filters="video==" + ",".join(ids[k:k + 200]), maxResults=200, sort="-views").execute()
        cols = [h["name"] for h in r["columnHeaders"]]
        for row in r.get("rows", []): rows[row[0]] = dict(zip(cols[1:], row[1:]))
    ch = yt.channels().list(part="statistics", mine=True).execute()["items"][0]["statistics"]
    out = {"updated": now().isoformat(timespec="seconds"), "channel": ch, "videos": []}
    for slug, m in pub:
        out["videos"].append({"slug": slug, "id": m["video_id"], "title": m["title"], "published_at": m.get("published_at"), **rows.get(m["video_id"], {})})
    json.dump(out, open(os.path.join(DATA, "metrics.json"), "w"), ensure_ascii=False, indent=2)
    L = [f"# Informe @antesdelos90 · {end}", "", f"Suscriptores: {ch.get('subscriberCount')} · Vistas totales: {ch.get('viewCount')} · Vídeos: {ch.get('videoCount')}", "",
         "| Vídeo | Vistas | Min vistos | Dur. media (s) | % visto | Likes | Coment. | Subs |", "|---|---|---|---|---|---|---|---|"]
    for v in sorted(out["videos"], key=lambda v: -(v.get("views") or 0)):
        L.append(f"| [{v['title']}](https://youtu.be/{v['id']}) | {v.get('views', 0)} | {v.get('estimatedMinutesWatched', 0)} | {v.get('averageViewDuration', 0)} | "
                 f"{round(v.get('averageViewPercentage', 0) or 0, 1)} | {v.get('likes', 0)} | {v.get('comments', 0)} | {v.get('subscribersGained', 0)} |")
    open(os.path.join(DATA, "report.md"), "w").write("\n".join(L) + "\n"); print("\n".join(L))
if __name__ == "__main__": main()
