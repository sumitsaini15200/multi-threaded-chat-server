"""
Chat Client (with chat room support)
-------------------------------------
Two threads as before:
- Main thread: reads what you type and sends it.
- Background thread: continuously listens for incoming messages
  (so you receive messages from your room while typing).

New commands:
  /join <room>   -> switch to a different chat room (created if new)
  /rooms         -> list all currently active rooms on the server
  /quit          -> disconnect
"""

import socket
import threading

HOST = "127.0.0.1"
PORT = 5050

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))


def receive_messages():
    while True:
        try:
            message = client_socket.recv(1024).decode()
            if message == "USERNAME?":
                client_socket.send(username.encode())
            else:
                print(message)
        except Exception:
            print("Disconnected from server.")
            client_socket.close()
            break


username = input("Enter your username: ")
print("Connected. You're in #general by default.")
print("Commands: /join <room>   /rooms   /quit\n")

receive_thread = threading.Thread(target=receive_messages, daemon=True)
receive_thread.start()

while True:
    msg = input()
    if msg.lower() == "/quit":
        client_socket.close()
        break
    client_socket.send(msg.encode())
