import socket
import threading

name = input("Enter your name: ")
HOST = input("Enter server IP: ")
PORT = 55555

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

def receive():
    while True:
        try:
            message = client.recv(1024).decode()
            if message == "NAME":
                client.send(name.encode())
            else:
                print(message)
        except:
            print("Disconnected from server.")
            client.close()
            break

def write():
    while True:
        message = f"{name}: {input()}"
        try:
            client.send(message.encode())
        except:
            break

receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()