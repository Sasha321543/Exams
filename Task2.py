from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import os
import json

# Parameters
key_length = 32  # AES-256
iv_length = 12   # Recommended length for GCM
salt_length = 16

def generate_key(password: bytes, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=key_length,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    return kdf.derive(password)

def aes_gcm_encrypt(plaintext: bytes, key: bytes, iv: bytes):
    cipher = Cipher(
        algorithms.AES(key),
        modes.GCM(iv),
        backend=default_backend()
    )
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(plaintext) + encryptor.finalize()
    return ciphertext, encryptor.tag

# Step 1: Generate or load plaintext file
plaintext_file = "plaintext.txt"
with open(plaintext_file, "w") as f:
    f.write("This is a sample text to encrypt using AES-GCM.")

with open(plaintext_file, "rb") as f:
    plaintext = f.read()

# Step 2: Generate key and IV
password = b"strongpassword"  # Replace with secure password input
salt = os.urandom(salt_length)
key = generate_key(password, salt)
iv = os.urandom(iv_length)

# Step 3: Encrypt plaintext
ciphertext, tag = aes_gcm_encrypt(plaintext, key, iv)

# Step 4: Write ciphertext and tag to files
ciphertext_file = "ciphertext.bin"
tag_file = "tag.bin"
salt_file = "salt.bin"
iv_file = "iv.bin"

with open(ciphertext_file, "wb") as f:
    f.write(ciphertext)

with open(tag_file, "wb") as f:
    f.write(tag)

with open(salt_file, "wb") as f:
    f.write(salt)

with open(iv_file, "wb") as f:
    f.write(iv)

# Output results
print(f"Ciphertext written to {ciphertext_file}")
print(f"Authentication tag written to {tag_file}")
print(f"Salt written to {salt_file}")
print(f"IV written to {iv_file}")