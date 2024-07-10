from ecdsa import SigningKey, SECP256k1

def generate_key_pair():
    private_key = SigningKey.generate(curve=SECP256k1)
    public_key = private_key.get_verifying_key()
    return private_key, public_key

# Generate key pairs for miners
miners_keys = {
    'miner1': generate_key_pair(),
    'miner2': generate_key_pair(),
    'miner3': generate_key_pair()
}
