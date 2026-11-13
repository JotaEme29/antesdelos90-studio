import json, os, glob, datetime as dt
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QUEUE = os.path.join(ROOT, "queue"); BUILD = os.path.join(ROOT, "build"); DATA = os.path.join(ROOT, "data")
def items():
    for d in sorted(glob.glob(os.path.join(QUEUE, "*"))):
        m = os.path.join(d, "meta.json")
        if os.path.isfile(m): yield os.path.basename(d), d, json.load(open(m))
def save_meta(d, meta):
    with open(os.path.join(d, "meta.json"), "w") as f: json.dump(meta, f, ensure_ascii=False, indent=2); f.write("\n")
def now(): return dt.datetime.now(dt.timezone.utc)
def parse(ts): return dt.datetime.fromisoformat(ts.replace("Z", "+00:00"))
