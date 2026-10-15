from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import secrets
from quantum_key import generate_quantum_key

def encrypt_message(message, key):
    iv = secrets.token_bytes(12)
    cipher = Cipher(algorithms.AES(key), modes.GCM(iv))
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(message.encode('utf-8')) + encryptor.finalize()
    return iv + encryptor.tag + ciphertext

def decrypt_message(encrypted_data, key):
    iv = encrypted_data[:12]
    tag = encrypted_data[12:28]
    ciphertext = encrypted_data[28:]
    cipher = Cipher(algorithms.AES(key), modes.GCM(iv, tag))
    decryptor = cipher.decryptor()
    plaintext = decryptor.update(ciphertext) + decryptor.finalize()
    return plaintext.decode('utf-8')

if __name__ == "__main__":
    key = generate_quantum_key()
    msg = "Test message"
    encrypted = encrypt_message(msg, key)
    decrypted = decrypt_message(encrypted, key)
    print(f"Original: {msg}")
    print(f"Encrypted: {encrypted.hex()}")
    print(f"Decrypted: {decrypted}")
