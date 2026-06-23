"""
Multi-threaded Chat Server with Chat Rooms
-------------------------------------------
New concept added: instead of one shared list of clients, we now have
MULTIPLE shared lists -- one per "room" -- all stored inside a single
shared dictionary (`rooms`). This is a step up in complexity because:

- Every read/write to `rooms` (joining, leaving, broadcasting) must be
  protected by `rooms_lock`, since many client threads touch this
  dictionary at the same time.
- A client can MOVE between rooms while the server is running, so we
  must safely remove them from their old room and add them to a new
  one -- this is a critical section that needs the lock held for the
  whole operation, not just part of it (otherwise another thread could
  see an inconsistent state mid-move).

Commands supported by clients:
  /join <room>   -> leave current room, join (or create) another
  /rooms         -> list all currently active rooms
  /quit          -> disconnect
"""

import socket
import threading

HOST = "127.0.0.1"
PORT = 5050

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen()

# Shared state: { room_name: [ {"socket": ..., "username": ...}, ... ] }
rooms = {}
rooms_lock = threading.Lock()


def broadcast_to_room(room, message, sender_socket=None):
    """Send a message to everyone in `room` except the sender."""
    with rooms_lock:
        members = rooms.get(room, [])
        for member in members:
            if member["socket"] != sender_socket:
                try:
                    member["socket"].send(message)
                except Exception:
                    pass


def join_room(client_socket, username, room):
    """
    Adds a client to `room`. Creates the room if it doesn't exist yet.
    This whole operation happens under one lock acquisition so no other
    thread can see a half-finished state.
    """
    with rooms_lock:
        if room not in rooms:
            rooms[room] = []
        rooms[room].append({"socket": client_socket, "username": username})


def leave_room(client_socket, room):
    """Removes a client from `room`. Cleans up empty rooms."""
    with rooms_lock:
        if room in rooms:
            rooms[room] = [m for m in rooms[room] if m["socket"] != client_socket]
            if not rooms[room]:
                del rooms[room]   # no point keeping an empty room around


def list_rooms():
    with rooms_lock:
        if not rooms:
            return "No active rooms."
        return "Active rooms: " + ", ".join(
            f"{name} ({len(members)})" for name, members in rooms.items()
        )


def handle_client(client_socket, username):
    current_room = "general"
    join_room(client_socket, username, current_room)
    broadcast_to_room(current_room, f"{username} has joined #{current_room}".encode(), client_socket)

    while True:
        try:
            data = client_socket.recv(1024)
            if not data:
                break
            message = data.decode()

            if message.startswith("/join "):
                new_room = message.split(" ", 1)[1].strip()
                leave_room(client_socket, current_room)
                broadcast_to_room(current_room, f"{username} left #{current_room}".encode())
                current_room = new_room
                join_room(client_socket, username, current_room)
                broadcast_to_room(current_room, f"{username} has joined #{current_room}".encode(), client_socket)
                client_socket.send(f"You joined #{current_room}".encode())

            elif message.strip() == "/rooms":
                client_socket.send(list_rooms().encode())

            else:
                broadcast_to_room(current_room, f"[#{current_room}] {username}: {message}".encode(), client_socket)

        except ConnectionResetError:
            break

    leave_room(client_socket, current_room)
    broadcast_to_room(current_room, f"{username} has left #{current_room}".encode())
    client_socket.close()


def accept_connections():
    print(f"Server listening on {HOST}:{PORT}")
    while True:
        client_socket, addr = server_socket.accept()
        client_socket.send("USERNAME?".encode())
        username = client_socket.recv(1024).decode()
        print(f"{username} connected from {addr}")

        thread = threading.Thread(target=handle_client, args=(client_socket, username), daemon=True)
        thread.start()


if __name__ == "__main__":
    accept_connections()
