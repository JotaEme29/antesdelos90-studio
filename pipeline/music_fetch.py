#!/usr/bin/env python3
"""Descarga temas de Mixkit (licencia Mixkit Stock Music Free License) a music/mixkit/ según music/fuentes.txt.
Busca en cada página las URLs de MP3 (JSON-LD 'contentUrl' o enlaces assets.mixkit.co/music/...) y el nombre del tema.
Se ejecuta en GitHub Actions (desde la sesión de Claude el proxy bloquea mixkit.co)."""
import json, os, re, sys, urllib.request, html
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "music", "mixkit"); os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (antesdelos90 music fetch)"}
def get(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60).read()
def slug(s): return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")[:60]
def tracks(page):
    h = get(page).decode("utf-8", "replace"); found = []
    for blk in re.findall(r'<script[^>]+application/ld\+json[^>]*>(.*?)</script>', h, re.S):
        try: data = json.loads(html.unescape(blk))
        except Exception: continue
        stack = [data]
        while stack:
            o = stack.pop()
            if isinstance(o, list): stack += o; continue
            if not isinstance(o, dict): continue
            u = o.get("contentUrl") or ""
            if isinstance(u, str) and u.endswith(".mp3"):
                by = o.get("byArtist") or o.get("author") or {}
                by = by.get("name") if isinstance(by, dict) else (by if isinstance(by, str) else "")
                found.append((o.get("name") or os.path.basename(u), by or "", u))
            stack += [v for v in o.values() if isinstance(v, (dict, list))]
    if not found:
        for u in dict.fromkeys(re.findall(r'https://assets\.mixkit\.co/music/[^"\'\s>]+?\.mp3', h)):
            found.append((os.path.basename(u).replace(".mp3", ""), "", u))
    return found
credits = os.path.join(OUT, "CREDITOS.md"); have = open(credits).read() if os.path.exists(credits) else "# Música de Mixkit\n\nLicencia: Mixkit Stock Music Free License (https://mixkit.co/license/#musicFree). Sin atribución obligatoria.\n\n"
n_new = 0
for line in open(os.path.join(ROOT, "music", "fuentes.txt")):
    line = line.strip()
    if not line or line.startswith("#"): continue
    page, _, k = line.partition("|"); page = page.strip(); k = int(k or 5)
    try: lst = tracks(page)
    except Exception as e: print("ERROR leyendo", page, e); continue
    print(page, "→", len(lst), "temas")
    for name, by, u in lst[:k]:
        fn = f"{slug(name)}-{slug(by) or 'mixkit'}.mp3"; dst = os.path.join(OUT, fn)
        if os.path.exists(dst): continue
        try:
            data = get(u)
            if len(data) < 100_000: print("  demasiado pequeño, ¿preview?", u); continue
            open(dst, "wb").write(data); n_new += 1
            have += f"- `{fn}` · «{name}» · {by or 'Mixkit'} · {u} · página: {page}\n"; print("  OK", fn)
        except Exception as e: print("  ERROR", u, e)
open(credits, "w").write(have)
print("nuevos:", n_new, "· total:", len([f for f in os.listdir(OUT) if f.endswith('.mp3')]))
sys.exit(0 if n_new or os.listdir(OUT) else 1)
