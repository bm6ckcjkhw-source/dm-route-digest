"""Registers the app's public key (sent in the text of a run started from the app).

usage: python3 tools/register_key.py <base64 public key>
Writes keys/<id>.pub. At most 4 keys are kept (two phones, plus reinstalls); the oldest is dropped.
A public key is not a secret — it only lets the routine seal the private file for that phone.
"""
import glob, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from seal import key_id, load_public

MAX_KEYS = 4

pub = load_public(sys.argv[1])
os.makedirs("keys", exist_ok=True)
path = os.path.join("keys", key_id(pub) + ".pub")
if os.path.exists(path):
    print("already registered", key_id(pub))
    sys.exit(0)
with open(path, "w") as f:
    f.write(sys.argv[1].strip() + "\n")
keys = sorted(glob.glob("keys/*.pub"), key=os.path.getmtime)
for old in keys[:-MAX_KEYS]:
    os.remove(old)
    print("dropped old key", os.path.basename(old))
print("registered", key_id(pub))
