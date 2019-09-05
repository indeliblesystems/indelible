import nacl.secret
import nacl.hash
import nacl.pwhash
from base64 import standard_b64encode

encrypt_nonce_len = 24
derive_key_salt_len = 16
key_len = 32

def derive_key(master_key, context):
    return nacl.pwhash.argon2id.kdf(
        key_len,
        standard_b64encode(master_key),
        nonce(context + master_key, derive_key_salt_len),
        1,
        8192
    )

def nonce(message, nonce_len = derive_key_salt_len):
    return nacl.hash.blake2b(message, nonce_len, encoder=nacl.encoding.RawEncoder)

def decrypt(key, message):
    if len(message) < encrypt_nonce_len:
        raise Exception("invalid message, too short")
    return nacl.secret.SecretBox(key).decrypt(message)

def encrypt(key, message):
    n = nonce(message + key, encrypt_nonce_len)
    return nacl.secret.SecretBox(key).encrypt(message, n)
