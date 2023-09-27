#!/usr/bin/env python3

import binascii
import hashlib
import hmac
from math import (
    ceil,
    log2,
)
import struct
from py_ecc.optimized_bls12_381 import FQ, FQ2, curve_order, G1, G2, multiply
from py_ecc.bls.hash import hkdf_expand, hkdf_extract, i2osp, os2ip
from py_ecc.bls.point_compression import compress_G1, compress_G2

privdev = 0x80000000


def KeyGen(IKM: bytes, key_info: bytes = b'') -> int:
    salt = b'BLS-SIG-KEYGEN-SALT-'
    SK = 0
    while SK == 0:
        salt = hashlib.sha256(salt).digest()
        prk = hkdf_extract(salt, IKM + b'\x00')
        l = ceil((1.5 * ceil(log2(curve_order))) / 8)  # noqa: E741
        okm = hkdf_expand(prk, key_info + i2osp(l, 2), l)
        SK = os2ip(okm) % curve_order
    return SK


def int_to_string(x, pad):
    result = [b'\x00'] * pad
    while x > 0:
        pad -= 1
        ordinal = x & 0xFF
        result[pad] = (bytes([ordinal]))
        x >>= 8
    return b''.join(result)


def string_to_int(s):
    result = 0
    for c in s:
        if not isinstance(c, int):
            c = c[0]
        result = (result << 8) + c
    return result


def seed2hdnode(seed, modifier):
    k = seed
    h = hmac.new(modifier, seed, hashlib.sha512).digest()
    Il, chaincode = h[:32], h[32:]
    secret = KeyGen(IKM=Il)

    return (secret.to_bytes(32, 'big'), chaincode)


def publickey(private_key, on_g1) -> int:
    if on_g1:
        Q = multiply(G1, string_to_int(private_key))
        c = compress_G1(Q)
        return c.to_bytes(48, "big")
    else:
        Q = multiply(G2, string_to_int(private_key))
        c = compress_G2(Q)
        return c[0].to_bytes(48, "big") + c[1].to_bytes(48, "big")


def derive(parent_key, parent_chaincode, i, on_g1):
    assert len(parent_key) == 32
    assert len(parent_chaincode) == 32
    k = parent_chaincode
    if ((i & privdev) != 0):
        if on_g1:
            key = b'\x01' + parent_key
        else:
            key = b'\x00' + parent_key
    else:
        key = publickey(parent_key, on_g1)
    d = key + struct.pack('>L', i)
    while True:
        h = hmac.new(k, d, hashlib.sha512).digest()
        key, chaincode = h[:32], h[32:]

        # print('I: ' + binascii.hexlify(h).decode())
        a = string_to_int(key)
        key = (a + string_to_int(parent_key)) % curve_order
        if (a < curve_order and key != 0):
            key = int_to_string(key, 32)
            break
        d = b'\x01' + h[32:] + struct.pack('>L', i)
        # print('a failed: ' + binascii.hexlify(h[:32]).decode())
        # print('RETRY: ' + binascii.hexlify(d).decode())

    return (key, chaincode)


def show_testvector(name, seedhex, derivationpath, on_g1):
    seedmodifier = b"BLS12381 seed"
    master_seed = binascii.unhexlify(seedhex)
    k, c = seed2hdnode(master_seed, seedmodifier)
    p = publickey(k, on_g1)
    path = 'm'
    print("### "+name+" on", "G1" if on_g1 else "G2")
    print('')
    print("Seed (hex): " + seedhex)
    print('')
    print('* Chain ' + path)
    print('  * chain code: ' + binascii.hexlify(c).decode())
    print('  * private: ' + binascii.hexlify(k).decode())
    print('  * public: ' + binascii.hexlify(p).decode())
    depth = 0
    for i in derivationpath:
        depth = depth + 1
        path = path + "/" + str(i & (privdev-1))
        if ((i & privdev) != 0):
            path = path + "H"
        k, c = derive(k, c, i, on_g1)
        p = publickey(k, on_g1)
        print('* Chain ' + path)
        print('  * chain code: ' + binascii.hexlify(c).decode())
        print('  * private: ' + binascii.hexlify(k).decode())
        print('  * public: ' + binascii.hexlify(p).decode())
    print()


show_testvector("Test vector",
                '000102030405060708090a0b0c0d0e0f',
                [privdev + 0, 1, privdev + 2, 2, 1000000000], True)

show_testvector("Test vector",
                '000102030405060708090a0b0c0d0e0f',
                [privdev + 0, 1, privdev + 2, 2, 1000000000], False)
