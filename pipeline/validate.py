#!/usr/bin/env python3
"""Comprueba specs y metadatos antes de publicar. Sale con error si algo no cumple."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import items, parse, now, ROOT
STATES = {"draft", "approved", "scheduled", "published", "failed"}
def check(slug, d, m):
    e = []
    if m.get("status") not in STATES: e.append(f"status inválido: {m.get('status')}")
    t = m.get("title", "")
    if not t or len(t) > 100: e.append("título vacío o de más de 100 caracteres")
    if "<" in t or ">" in t: e.append("el título no puede llevar < ni >")
    if len(m.get("description", "")) > 5000: e.append("descripción de más de 5000 caracteres")
    if sum(len(x) + 1 for x in m.get("tags", [])) > 480: e.append("etiquetas: más de 480 caracteres en total")
    if m.get("status") == "approved":
        try:
            if parse(m["publish_at"]) <= now(): e.append("publish_at ya ha pasado")
        except Exception: e.append("publish_at falta o no es una fecha ISO (2026-11-15T13:30:00+01:00)")
    sp = os.path.join(d, "spec.json")
    if m.get("format", "short") == "short":
        if not os.path.isfile(sp): e.append("falta spec.json")
        else:
            s = json.load(open(sp))
            if len(s["team"]["base"]) != 11 or len(s["team"]["nums"]) != 11: e.append("team.base y team.nums deben tener 11 jugadores")
            if not os.path.isfile(os.path.join(ROOT, s["music"])): e.append(f"no existe la música {s['music']}")
            if s["end"] + s.get("endcard", {}).get("dur", 3) > 60: e.append("un Short debe durar menos de 60 s")
    elif not os.path.isfile(os.path.join(d, "video.mp4")): e.append("formato long: falta video.mp4 en la carpeta")
    return e
bad = 0
for slug, d, m in items():
    errs = check(slug, d, m)
    print(("OK   " if not errs else "FALLO"), slug, "·", m.get("status"), *(["\n      - " + x for x in errs]))
    bad += bool(errs)
sys.exit(1 if bad else 0)
