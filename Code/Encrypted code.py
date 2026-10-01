from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import base64
import os

# Generate a key from a password
def generate_key(password: str, salt: bytes):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = kdf.derive(password.encode())
    return key

# Encrypt message
def encrypt_message(message: str, password: str):
    salt = os.urandom(16)
    key = generate_key(password, salt)
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    ct = encryptor.update(message.encode()) + encryptor.finalize()
    # Store salt, iv and ciphertext together
    encrypted_data = base64.urlsafe_b64encode(salt + iv + ct).decode()
    return encrypted_data

# Decrypt message
def decrypt_message(encrypted_data: str, password: str):
    data = base64.urlsafe_b64decode(encrypted_data)
    salt = data[:16]
    iv = data[16:32]
    ct = data[32:]
    key = generate_key(password, salt)
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    decrypted_text = decryptor.update(ct) + decryptor.finalize()
    return decrypted_text.decode()

if __name__ == "__main__":
    print("=== Simple Encryption System ===")
    mode = input("Type 'encrypt' or 'decrypt': ").strip().lower()
    password = input("Enter your password (used for key derivation): ")

    if mode == 'encrypt':
        message = input("Enter your message to encrypt: ")
        encrypted = encrypt_message(message, password)
        print("Encrypted message:")
        print(encrypted)
    elif mode == 'decrypt':
        encrypted_message = input("Paste the encrypted message to decrypt: ")
        try:
            decrypted = decrypt_message(encrypted_message, password)
            print("Decrypted message:")
            print(decrypted)
        except Exception as e:
            print("Failed to decrypt. Check your password and message.")
    else:
        print("Invalid mode selected, please choose 'encrypt' or 'decrypt'.")
