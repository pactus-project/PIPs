#!/usr/bin/env python3
"""Reference parser and test vectors for the Anchor Request URI (pactus:anchor).

Standard library only. Run it to check the vectors: it exits non-zero on any failure.
"""

import base64
import re
import sys
from urllib.parse import unquote_to_bytes

NANO_PAC = 10**9
MIN_ANCHOR_DEPOSIT = 1 * NANO_PAC  # PIP-50
MAX_NANO_PAC = 42_000_000 * NANO_PAC  # total supply, the protocol's amount bound
NETWORK_HRP = {"mainnet": "pc", "testnet": "tpc"}
ACCOUNT_TYPES = {2, 3, 4}  # BLS, Ed25519 and secp256k1 accounts; not the treasury (0) or validators (1)
AMOUNT = re.compile(r"(0|[1-9][0-9]*)(?:\.([0-9]{1,9}))?")

# ---- bech32m (BIP-350), as used by Pactus addresses ----

CHARSET = "qpzry9x8gf2tvdw0s3jn54khce6mua7l"
BECH32M_CONST = 0x2BC830A3


def _polymod(values):
    gen = [0x3B6A57B2, 0x26508E6D, 0x1EA119FA, 0x3D4233DD, 0x2A1462B3]
    chk = 1
    for v in values:
        top = chk >> 25
        chk = (chk & 0x1FFFFFF) << 5 ^ v
        for i in range(5):
            chk ^= gen[i] if (top >> i) & 1 else 0
    return chk


def _hrp_expand(hrp):
    return [ord(c) >> 5 for c in hrp] + [0] + [ord(c) & 31 for c in hrp]


def _convertbits(data, frombits, tobits, pad):
    acc, bits, out = 0, 0, []
    for value in data:
        acc = (acc << frombits) | value
        bits += frombits
        while bits >= tobits:
            bits -= tobits
            out.append((acc >> bits) & ((1 << tobits) - 1))
    if pad and bits:
        out.append((acc << (tobits - bits)) & ((1 << tobits) - 1))
    elif not pad and (bits >= frombits or (acc << (tobits - bits)) & ((1 << tobits) - 1)):
        return None
    return out


def encode_address(hrp, typ, data):
    words = [typ] + _convertbits(data, 8, 5, True)
    poly = _polymod(_hrp_expand(hrp) + words + [0] * 6) ^ BECH32M_CONST
    checksum = [(poly >> 5 * (5 - i)) & 31 for i in range(6)]
    return hrp + "1" + "".join(CHARSET[w] for w in words + checksum)


def decode_address(addr):
    """Returns (hrp, type, 20-byte data), or None if it is not a valid Pactus address."""
    if addr != addr.lower() or "1" not in addr:
        return None
    hrp, _, rest = addr.rpartition("1")
    if len(rest) < 7 or any(c not in CHARSET for c in rest):
        return None
    words = [CHARSET.index(c) for c in rest]
    if _polymod(_hrp_expand(hrp) + words) != BECH32M_CONST:
        return None
    data = _convertbits(words[1:-6], 5, 8, False)
    if data is None or len(data) != 20:
        return None
    return hrp, words[0], bytes(data)


# ---- pactus:anchor ----


class Reject(Exception):
    pass


def parse(uri, wallet_network):
    """Parses a pactus:anchor URI for a wallet on `wallet_network`, or raises Reject."""
    if not uri.startswith("pactus:"):
        raise Reject("not a pactus: URI")
    path, _, query = uri[len("pactus:") :].partition("?")
    if path != "anchor":
        raise Reject("path is not anchor")
    params = {}
    for part in filter(None, query.split("&")):
        name, _, value = part.partition("=")
        if name in params:
            raise Reject("parameter repeated: " + name)
        try:
            params[name] = unquote_to_bytes(value).decode("utf-8")
        except UnicodeDecodeError:
            raise Reject("not UTF-8: " + name)
    for name in params:
        if name.startswith("req-"):
            raise Reject("unknown required parameter: " + name)

    network, action = params.get("network"), params.get("action")
    if network not in NETWORK_HRP:
        raise Reject("network missing or unknown")
    if action not in ("set", "delete"):
        raise Reject("action missing or unknown")
    if network != wallet_network:
        raise Reject("network mismatch")
    if len(params.get("memo", "").encode()) > 64:
        raise Reject("memo longer than 64 bytes")
    if "sender" in params:
        decoded = decode_address(params["sender"])
        if not decoded or decoded[0] != NETWORK_HRP[network] or decoded[1] not in ACCOUNT_TYPES:
            raise Reject("sender is not an account address for the network")

    request = {"network": network, "action": action, "memo": params.get("memo", ""), "sender": params.get("sender")}
    if action == "delete":
        return request  # type, root, uri and locked are ignored, so not validated

    if "type" not in params or "root" not in params:
        raise Reject("type or root missing")
    if not re.fullmatch(r"0|[1-9][0-9]{0,2}", params["type"]) or int(params["type"]) > 255:
        raise Reject("type out of range")
    root = params["root"]
    if not re.fullmatch(r"(?:[0-9a-fA-F]{2}){32,64}", root):
        raise Reject("root is not 32 to 64 bytes of hex")
    uri_value = params.get("uri", "")
    if len(uri_value.encode()) > 128:
        raise Reject("uri longer than 128 bytes")
    locked = MIN_ANCHOR_DEPOSIT
    if "locked" in params:
        m = AMOUNT.fullmatch(params["locked"])
        if not m:
            raise Reject("locked is not a plain PAC amount")
        locked = int(m.group(1)) * NANO_PAC + int((m.group(2) or "").ljust(9, "0"))
        if locked > MAX_NANO_PAC:
            raise Reject("locked too large")
    request.update(type=int(params["type"]), root=root.lower(), uri=uri_value, locked=locked)
    return request


def deposit_to_add(locked, current_locked):
    """The transaction's Deposit for a set: what is missing to reach the target."""
    return max(0, max(locked, MIN_ANCHOR_DEPOSIT) - current_locked)


# ---- vectors ----

ROOT = "2727edf1004e656e34a07948dfccde9ae583b5f240c88f9f5dc1ae36c5ae9261"
CID = "bafk2bzaceatsp3prabhgk3ruub4urx6m32nola5v6jamrd47lxa24nwfv2jgc"
URI = "ipfs%3A%2F%2F" + CID
H = "ab" * 32
SET = "pactus:anchor?network=mainnet&action=set&type=1&root="
ZERO = bytes(20)
MAIN_BLS, MAIN_ED, MAIN_SECP = (encode_address("pc", t, ZERO) for t in (2, 3, 4))
MAIN_VALIDATOR, MAIN_TREASURY = encode_address("pc", 1, ZERO), encode_address("pc", 0, ZERO)
TEST_ED = "tpc1rw03cn7xkd7jjl5ajjkwj67wwhsf7e252fu50nz"

VALID = [
    # (uri, wallet network, expected fields)
    (f"{SET}{ROOT}&uri={URI}&memo=pactus.page", "mainnet",
     {"type": 1, "root": ROOT, "uri": "ipfs://" + CID, "locked": 1 * NANO_PAC, "memo": "pactus.page"}),
    (f"{SET}{ROOT}&uri={URI}&locked=100&memo=pactus.page", "mainnet", {"locked": 100 * NANO_PAC}),
    ("pactus:anchor?network=mainnet&action=delete&memo=pactus.page", "mainnet", {"action": "delete"}),
    ("pactus:anchor?network=mainnet&action=delete&type=x&root=zz", "mainnet", {"action": "delete"}),
    (f"{SET}{ROOT.upper()}&locked=2.5", "mainnet", {"root": ROOT, "locked": 2_500_000_000}),
    (f"{SET}{H}&locked=0.000000001", "mainnet", {"locked": 1}),
    (f"{SET}{H}", "mainnet", {"uri": ""}),
    (f"{SET}{H}&uri={'x' * 128}", "mainnet", {"uri": "x" * 128}),
    (f"{SET}{'cd' * 64}", "mainnet", {"root": "cd" * 64}),
    ("pactus:anchor?network=mainnet&action=set&type=200&root=" + H, "mainnet", {"type": 200}),
    (f"{SET}{H}&memo=a+b", "mainnet", {"memo": "a+b"}),
    (f"{SET}{H}&memo=10%20%E2%82%AC", "mainnet", {"memo": "10 €"}),
    (f"{SET}{H}&sender={MAIN_BLS}", "mainnet", {"sender": MAIN_BLS}),
    (f"{SET}{H}&sender={MAIN_ED}", "mainnet", {"sender": MAIN_ED}),
    (f"{SET}{H}&sender={MAIN_SECP}", "mainnet", {"sender": MAIN_SECP}),
    (f"pactus:anchor?network=testnet&action=delete&sender={TEST_ED}", "testnet", {"sender": TEST_ED}),
    (f"{SET}{H}&label=ignored", "mainnet", {"type": 1}),
]

REJECTED = [
    # (uri, wallet network)
    ("pactus:anchor?network=testnet&action=set&type=1&root=" + H, "mainnet"),
    ("pactus:anchor?action=set&type=1&root=" + H, "mainnet"),
    ("pactus:anchor?network=betanet&action=set&type=1&root=" + H, "mainnet"),
    ("pactus:anchor?network=mainnet&action=update&type=1&root=" + H, "mainnet"),
    ("pactus:anchor?network=mainnet&action=set&root=" + H, "mainnet"),
    ("pactus:anchor?network=mainnet&action=set&type=1", "mainnet"),
    ("pactus:anchor?network=mainnet&action=set&type=256&root=" + H, "mainnet"),
    ("pactus:anchor?network=mainnet&action=set&type=01&root=" + H, "mainnet"),
    (SET + "a" * 63, "mainnet"),
    (SET + "a" * 62, "mainnet"),
    (SET + "a" * 130, "mainnet"),
    (SET + "g" * 64, "mainnet"),
    (SET + H + "&uri=" + "x" * 129, "mainnet"),
    (SET + H + "&memo=" + "m" * 65, "mainnet"),
    (SET + H + "&memo=%FF", "mainnet"),
    ("pactus:anchor?network=mainnet&action=set&type=1&type=2&root=" + H, "mainnet"),
    (SET + H + "&locked=-1", "mainnet"),
    (SET + H + "&locked=+1", "mainnet"),
    (SET + H + "&locked=1e2", "mainnet"),
    (SET + H + "&locked=007", "mainnet"),
    (SET + H + "&locked=1.", "mainnet"),
    (SET + H + "&locked=1,5", "mainnet"),
    (SET + H + "&locked=0.0000000001", "mainnet"),
    (SET + H + "&locked=42000001", "mainnet"),
    (SET + H + "&req-expiry=1", "mainnet"),
    (SET + H + "&sender=" + MAIN_VALIDATOR, "mainnet"),
    (SET + H + "&sender=" + MAIN_TREASURY, "mainnet"),
    (SET + H + "&sender=" + TEST_ED, "mainnet"),
    (SET + H + "&sender=" + MAIN_ED[:-1] + ("q" if MAIN_ED[-1] != "q" else "p"), "mainnet"),
    ("pactus:" + MAIN_ED + "?amount=1", "mainnet"),
]

DEPOSITS = [
    # (locked now, locked in the URI, Deposit), in PAC
    (0, 1, 1),
    (0, 0.5, 1),
    (0, 100, 100),
    (1, 1, 0),
    (1, 100, 99),
    (100, 1, 0),
]


def main():
    failures = 0
    raw = base64.b32decode(CID[1:].upper() + "=" * (-len(CID[1:]) % 8))
    if raw[-32:].hex() != ROOT:
        failures += 1
        print("FAIL example root is not the CID's blake2b-256 digest")
    if decode_address(TEST_ED) is None:
        failures += 1
        print("FAIL known testnet address does not decode")
    for uri, net, want in VALID:
        try:
            got = parse(uri, net)
        except Reject as e:
            failures += 1
            print(f"FAIL rejected ({e}): {uri}")
            continue
        for k, v in want.items():
            if got.get(k) != v:
                failures += 1
                print(f"FAIL {k}={got.get(k)!r}, want {v!r}: {uri}")
    for uri, net in REJECTED:
        try:
            parse(uri, net)
            failures += 1
            print(f"FAIL accepted: {uri}")
        except Reject:
            pass
    for now, target, want in DEPOSITS:
        got = deposit_to_add(int(target * NANO_PAC), int(now * NANO_PAC))
        if got != int(want * NANO_PAC):
            failures += 1
            print(f"FAIL deposit {now} -> {target}: got {got / NANO_PAC}, want {want}")
    total = 2 + len(VALID) + len(REJECTED) + len(DEPOSITS)
    print(f"{total - failures}/{total} vectors pass")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
