import socket
import threading

HOST = '0.0.0.0'  # Listen on all network interfaces
PORT = 12345

# User database (username: password)
USERS = {
    "Felipe": "Lambritsa1156"
}

ADMINS = {"Felipe"}  # Admin users

clients = {}  # conn -> username


def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")
    try:
        data = conn.recv(1024).decode()
        if not data:
            conn.close()
            return

        print(f"[LOGIN ATTEMPT] From {addr}: {data}")
        try:
            username, password = data.split("|")
        except Exception:
            conn.sendall("ERROR|Invalid login format".encode())
            conn.close()
            return

        if USERS.get(username) == password:
            clients[conn] = username
            role = "ADMIN" if username in ADMINS else "USER"
            conn.sendall(f"OK|{role}".encode())
            print(f"[LOGIN SUCCESS] {username} logged in as {role}")

            while True:
                msg = conn.recv(1024)
                if not msg:
                    break
                msg = msg.decode()
                print(f"[{username}] {msg}")

                # Echo back for now; later handle commands, chat, block updates etc.
                conn.sendall(f"SERVER ECHO: {msg}".encode())

        else:
            conn.sendall("ERROR|Invalid username or password".encode())
            conn.close()

    except Exception as e:
        print(f"[EXCEPTION] {e}")
    finally:
        if conn in clients:
            print(f"[DISCONNECT] {clients[conn]} disconnected")
            del clients[conn]
        conn.close()


def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print(f"[STARTED] Server listening on {HOST}:{PORT}")

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
        thread.start()


if __name__ == "__main__":
    start_server()
