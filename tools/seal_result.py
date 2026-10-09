"""Validates a receipt (or answer) JSON written by the routine and seals it for every registered phone.

usage: python3 tools/seal_result.py r <id> <json file>    # receipt, format: tools/receipt-format.md
       python3 tools/seal_result.py q <id> <json file>    # answer to a question: {"id": …, "answer": "…"}
Writes private/<r|q>/<id>.json (sealed, unreadable without the phone's key), deletes the plaintext file,
and keeps at most 150 sealed files per kind (ids start with a timestamp, so the oldest sort first).
"""
import glob, json, os, re, sys
sys.path.insert(0, os.path.dirname(__file__))
from seal import key_id, load_public, seal

KIND, RID, SRC = sys.argv[1], sys.argv[2], sys.argv[3]
assert KIND in ("r", "q"), "kind must be r or q"
assert re.fullmatch(r"[0-9]{14}-[a-z0-9]{4,12}", RID), "id must look like 20261101124712-ab12"

MERCHANT = {"restoranas", "kavine", "baras", "kepykla", "parduotuve", "degaline", "parkingas", "kelio_mokestis",
            "muziejus", "vaistine", "suvenyrai", "sendaikciai", "nakvyne", "kita"}
CATEGORIES = {"gerimai.kava", "gerimai.karsti", "gerimai.gaivieji", "gerimai.alus", "gerimai.vynas", "gerimai.stiprus",
              "kepiniai", "desertai", "pusryciai", "uzkandziai", "patiekalai", "suriai", "greitas", "produktai",
              "aptarnavimas", "kuras.degalai", "kuras.kita", "keliai.mokestis", "keliai.parkingas", "bilietai.lankytinos",
              "bilietai.degustacijos", "bilietai.termos", "pirkiniai.lauktuves", "pirkiniai.sendaikciai", "pirkiniai.vynas",
              "pirkiniai.higiena", "pirkiniai.kita", "nakvyne.mokestis", "nakvyne.kita", "kita"}
PRODUCTS = {"kava.espresso", "kava.pienu", "kava.juoda", "arbata", "sokoladas", "vanduo", "gaivieji", "sultys", "alus",
            "sidras", "vynas.taure", "vynas.butelis", "sampanas.taure", "sampanas.butelis", "kruasanas", "sokoladine",
            "duona", "pyragaitis", "ledai", "krepas", "sumustinis", "mesainis", "pica", "salotos", "sriuba", "pagrindinis",
            "desertas", "meniu", "pusryciai", "degalai", "parkingas", "muziejus", "kita"}

CARD = [re.compile(p, re.I) for p in (
    r"\d[\d ]{11,}\d",                                   # long digit runs (card / IBAN-like numbers)
    r"(?:[*Xx•#]{2,}[\s-]?){1,4}\d{2,4}",                # **** 1234, XXXXXXXXXXXX1234
    r"\b(?:auth|auto|aut|autor|code aut|autoryzacja|autoryz|genehmigung|kartennr|karten-nr|nr karty|n° carte|carte n)\w*[\s.:#|°-]*\w*\d{4,}\w*",
)]


def clean(s):
    if not isinstance(s, str):
        return s
    for rx in CARD:
        s = rx.sub("•••", s)
    return s.strip()


def walk(x):
    if isinstance(x, dict):
        return {k: walk(v) for k, v in x.items()}
    if isinstance(x, list):
        return [walk(v) for v in x]
    return clean(x)


def num(v):
    if v is None or isinstance(v, (int, float)):
        return v
    return float(str(v).replace(",", ".").replace(" ", ""))


doc = walk(json.load(open(SRC, encoding="utf-8")))
if KIND == "r":
    doc["id"] = RID
    if doc.get("isReceipt", True):
        for k in ("merchant", "merchantType", "currency", "items", "total", "lines"):
            assert k in doc, "missing " + k
        if doc["merchantType"] not in MERCHANT:
            doc["merchantType"] = "kita"
        doc["total"] = num(doc["total"])
        for k in ("subtotal", "tax", "tip"):
            if k in doc:
                doc[k] = num(doc[k])
        for i, it in enumerate(doc["items"], 1):
            it.setdefault("id", "i%d" % i)
            it["qty"] = num(it.get("qty") or 1)
            it["total"] = num(it["total"])
            for k in ("unitPrice", "size"):
                if it.get(k) is not None:
                    it[k] = num(it[k])
            if it.get("category") not in CATEGORIES:
                it["category"] = "kita"
            if it.get("product") not in PRODUCTS:
                it["product"] = "kita"
        doc.setdefault("notes", [])
else:
    assert isinstance(doc.get("answer"), str) and doc["answer"].strip(), "answer missing"
    doc["id"] = RID

plain = json.dumps(doc, ensure_ascii=False, separators=(",", ":")).encode()
keys = sorted(glob.glob("keys/*.pub"))
assert keys, "no registered phone key"
out = os.path.join("private", KIND)
os.makedirs(out, exist_ok=True)
for kf in keys:
    pub = load_public(open(kf).read())
    box = seal(pub, plain)
    box["kind"], box["rid"] = KIND, RID
    with open(os.path.join(out, "%s.%s.json" % (RID, key_id(pub))), "w") as f:
        json.dump(box, f)
os.remove(SRC)
files = sorted(glob.glob(os.path.join(out, "*.json")))
for old in files[:-150 * len(keys)]:
    os.remove(old)
print("sealed", KIND, RID, "for", len(keys), "phone(s)")
