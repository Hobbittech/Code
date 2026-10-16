import os
import json
from cryptography.fernet import Fernet

# Paths for credentials and keys
CREDENTIALS_FILE = 'users_credentials.json'
KEYS_FILE = 'user_keys.json'

# Load or initialize credentials
if os.path.exists(CREDENTIALS_FILE):
    with open(CREDENTIALS_FILE, 'r') as f:
        users = json.load(f)
else:
    users = {}

# Load or initialize user keys
if os.path.exists(KEYS_FILE):
    with open(KEYS_FILE, 'r') as f:
        user_keys = json.load(f)
else:
    user_keys = {}

def save_data():
    with open(CREDENTIALS_FILE, 'w') as f:
        json.dump(users, f)
    with open(KEYS_FILE, 'w') as f:
        json.dump(user_keys, f)

def generate_key():
    return Fernet.generate_key().decode()

def encrypt_message(key, message):
    fernet = Fernet(key.encode())
    return fernet.encrypt(message.encode()).decode()

def decrypt_message(key, token):
    fernet = Fernet(key.encode())
    return fernet.decrypt(token.encode()).decode()

def register():
    username = input("Choose a username: ")
    if username in users:
        print("Username already exists.")
        return False
    password = input("Choose a password: ")
    users[username] = password
    key = generate_key()
    user_keys[username] = key
    save_data()
    print(f"User '{username}' registered successfully.")
    return username

def login():
    username = input("Username: ")
    password = input("Password: ")
    if username in users and users[username] == password:
        print(f"Welcome back, {username}!")
        return username
    else:
        print("Invalid username or password.")
        return False

def chat(username):
    print("Type 'exit' to leave the chat.")
    user_key = user_keys[username]
    while True:
        msg = input("You: ")
        if msg.lower() == 'exit':
            break
        encrypted_msg = encrypt_message(user_key, msg)
        print(f"Encrypted message: {encrypted_msg}")
        # For demo, just decrypt to show
        decrypted_msg = decrypt_message(user_key, encrypted_msg)
        print(f"Decrypted message: {decrypted_msg}")

def main():
    choice = input("Type 'login' to login or 'register' to register: ").lower()
    if choice == 'register':
        user = register()
        if user:
            chat(user)
    elif choice == 'login':
        user = login()
        if user:
            chat(user)
    else:
        print("Invalid option.")

if __name__ == "__main__":
    main()