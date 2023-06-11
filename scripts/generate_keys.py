#!/usr/bin/env python3

from paseto.v4 import Ed25519PrivateKey


def generate_private_key_hex() -> str:
    priv = Ed25519PrivateKey.generate()
    priv_bytes = priv.private_bytes_raw()
    return priv_bytes.hex()


if __name__ == '__main__':
    print(generate_private_key_hex())
