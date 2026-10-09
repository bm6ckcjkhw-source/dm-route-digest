"""Seals the planner snapshot for every registered phone.

usage: python3 tools/export_private.py <db dir>
<db dir> holds the planner collections as ArtifactData saved them: <db>/<collection>/<doc id>.json.
Writes private/<key id>.json (sealed, safe to publish) and removes files of keys that are gone.
The plaintext never leaves the run: <db dir> must stay out of git (see .gitignore).
"""
import datetime, glob, hashlib, json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from seal import key_id, load_public, seal

COLLECTIONS = ["stays", "todos", "checks", "markets", "weather"]

db = sys.argv[1]


def canon(doc):
    return json.dumps(doc, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def load(col):
    out = []
    for f in sorted(glob.glob(os.path.join(db, col, "*.json"))):
        doc = json.load(open(f, encoding="utf-8"))
        doc.pop("id", None)
        # h: a fingerprint of the planner document — the app applies a document only when it changed
        out.append({"id": os.path.splitext(os.path.basename(f))[0], "h": hashlib.sha256(canon(doc).encode()).hexdigest()[:16], "doc": doc})
    return out


snap = {"v": 1, "generated": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}
for c in COLLECTIONS:
    snap[c] = load(c)

# a partial read must never look like "everything was deleted"
assert len(snap["stays"]) == 7, ("stays", len(snap["stays"]))
assert len(snap["todos"]) >= 30, ("todos", len(snap["todos"]))

plain = canon(snap).encode()
os.makedirs("private", exist_ok=True)
keep = set()
for kf in sorted(glob.glob("keys/*.pub")):
    pub = load_public(open(kf).read())
    box = seal(pub, plain)
    box["created"] = snap["generated"]
    name = os.path.join("private", key_id(pub) + ".json")
    with open(name, "w") as f:
        json.dump(box, f)
    keep.add(name)
for f in glob.glob("private/*.json"):
    if f not in keep:
        os.remove(f)
print("sealed for", len(keep), "phone(s):", ", ".join(sorted(os.path.basename(k)[:-5] for k in keep)) or "none yet",
      "| stays", len(snap["stays"]), "todos", len(snap["todos"]), "checks", len(snap["checks"]),
      "markets", len(snap["markets"]), "weather", len(snap["weather"]))
