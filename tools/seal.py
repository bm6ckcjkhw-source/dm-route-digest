"""Sealed boxes for the app's private planner file — Python standard library only.

Scheme (v1), mirrored in the app (PlannerSync.swift, CryptoKit):
  X25519 with a fresh ephemeral key  ->  shared secret
  HKDF-SHA256(ikm=shared, salt=epk || recipient, info="dm-planner-sync-v1", 64 bytes) -> enc key | mac key
  keystream block i = HMAC-SHA256(enc key, nonce || i as 4-byte big endian)   (i = 0, 1, …)
  ct  = plaintext XOR keystream
  tag = HMAC-SHA256(mac key, epk || nonce || ct)
Only the phone holding the private key can open it; the repository only ever sees public keys.
"""
import base64, hashlib, hmac, json, os

P = 2 ** 255 - 19
A24 = 121665
INFO = b"dm-planner-sync-v1"


def _scalar(k):
    k = bytearray(k)
    k[0] &= 248
    k[31] &= 127
    k[31] |= 64
    return int.from_bytes(k, "little")


def x25519(k, u):
    """RFC 7748 scalar multiplication (constant control flow is not needed here: the key is ephemeral)."""
    k = _scalar(k)
    ub = bytearray(u)
    ub[31] &= 127
    x1 = int.from_bytes(ub, "little") % P
    x2, z2, x3, z3, swap = 1, 0, x1, 1, 0
    for t in reversed(range(255)):
        kt = (k >> t) & 1
        swap ^= kt
        if swap:
            x2, x3, z2, z3 = x3, x2, z3, z2
        swap = kt
        a = (x2 + z2) % P
        aa = a * a % P
        b = (x2 - z2) % P
        bb = b * b % P
        e = (aa - bb) % P
        c = (x3 + z3) % P
        d = (x3 - z3) % P
        da = d * a % P
        cb = c * b % P
        x3 = (da + cb) ** 2 % P
        z3 = x1 * (da - cb) ** 2 % P
        x2 = aa * bb % P
        z2 = e * (aa + A24 * e) % P
    if swap:
        x2, z2 = x3, z3
    return (x2 * pow(z2, P - 2, P) % P).to_bytes(32, "little")


BASE = (9).to_bytes(32, "little")


def public_key(private):
    return x25519(private, BASE)


def _hkdf(ikm, salt, info, n):
    prk = hmac.new(salt, ikm, hashlib.sha256).digest()
    out, t, i = b"", b"", 1
    while len(out) < n:
        t = hmac.new(prk, t + info + bytes([i]), hashlib.sha256).digest()
        out += t
        i += 1
    return out[:n]


def _stream(key, nonce, data):
    out = bytearray()
    for i in range(0, len(data), 32):
        block = hmac.new(key, nonce + (i // 32).to_bytes(4, "big"), hashlib.sha256).digest()
        chunk = data[i:i + 32]
        out += bytes(a ^ b for a, b in zip(chunk, block))
    return bytes(out)


def key_id(pub):
    return hashlib.sha256(pub).hexdigest()[:16]


def load_public(text):
    pub = base64.b64decode(text.strip(), validate=True)
    if len(pub) != 32 or pub == bytes(32):
        raise ValueError("not an X25519 public key")
    return pub


def seal(recipient, plaintext):
    eph = os.urandom(32)
    epk = public_key(eph)
    shared = x25519(eph, recipient)
    if shared == bytes(32):
        raise ValueError("weak recipient key")
    keys = _hkdf(shared, epk + recipient, INFO, 64)
    nonce = os.urandom(16)
    ct = _stream(keys[:32], nonce, plaintext)
    tag = hmac.new(keys[32:], epk + nonce + ct, hashlib.sha256).digest()
    b64 = lambda b: base64.b64encode(b).decode()
    return {"v": 1, "kid": key_id(recipient), "epk": b64(epk), "nonce": b64(nonce), "ct": b64(ct), "tag": b64(tag)}


def open_box(private, box):
    """Used only by the self-test; the app opens boxes itself."""
    d = lambda k: base64.b64decode(box[k])
    epk, nonce, ct, tag = d("epk"), d("nonce"), d("ct"), d("tag")
    me = public_key(private)
    keys = _hkdf(x25519(private, epk), epk + me, INFO, 64)
    if not hmac.compare_digest(tag, hmac.new(keys[32:], epk + nonce + ct, hashlib.sha256).digest()):
        raise ValueError("bad tag")
    return _stream(keys[:32], nonce, ct)


if __name__ == "__main__":
    # self-test: RFC 7748 vector + round trip
    k = bytes.fromhex("a546e36bf0527c9d3b16154b82465edd62144c0ac1fc5a18506a2244ba449ac4")
    u = bytes.fromhex("e6db6867583030db3594c1a424b15f7c726624ec26b3353b10a903a6d0ab1c4c")
    assert x25519(k, u).hex() == "c3da55379de9c6908e94ea4df28d084f32eccf03491c71f754b4075577a28552"
    a = os.urandom(32)
    box = seal(public_key(a), "Labas, ąčęėįšųūž".encode())
    assert open_box(a, json.loads(json.dumps(box))).decode() == "Labas, ąčęėįšųūž"
    print("seal self-test ok")
