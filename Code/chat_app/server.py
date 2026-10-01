import socket
import threading

HOST = "0.0.0.0"
PORT = 55555

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

clients = []
names = []

def broadcast(message):
    for client in clients:
        try:
            client.send(message)
        except:
            pass

def handle_client(client):
    while True:
        try:
            message = client.recv(1024)
            broadcast(message)
        except:
            index = clients.index(client)
            clients.remove(client)
            client.close()
            name = names[index]
            names.remove(name)
            broadcast(f"{name} left the chat.\n".encode())
            break

def receive_connections():
    while True:
        client, address = server.accept()
        print(f"Connected with {address}")

        client.send("NAME".encode())
        name = client.recv(1024).decode()

        names.append(name)
        clients.append(client)

        print(f"Name: {name}")
        broadcast(f"{name} joined the chat!\n".encode())
        client.send("Connected to the server!\n".encode())

        thread = threading.Thread(target=handle_client, args=(client,))
        thread.start()

print("Server is running...")
receive_connections()
