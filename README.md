![Uploading Screenshot 2026-06-23 232127.png…]()
<img width="1920" height="1020" alt="Screenshot 2026-06-23 231938" src="https://github.com/user-attachments/assets/acdb8ce3-2563-4d8a-b662-8ca3585df37b" />
<img width="1920" height="1020" alt="Screenshot 2026-06-23 231922" src="https://github.com/user-attachments/assets/baa225f4-d9e1-489d-95da-4a656f397669" />
# Multi-threaded Chat Server with Chat Rooms (Python)

A TCP chat server supporting multiple chat rooms, where clients can create or switch between rooms in real time. Built to demonstrate concurrency, multi-threading, and synchronization over shared state.

## How it works

- **Sockets** handle network communication between server and clients (TCP).
- **Multi-threading**: every connected client gets its own dedicated thread (`handle_client`), so the server handles many clients concurrently.
- **Synchronization over complex shared state**: instead of one shared list, the server now keeps a shared dictionary `rooms = {room_name: [client, ...]}`. Every join, leave, or broadcast operation is wrapped in `rooms_lock` so that:
  - No two threads can corrupt the dictionary by modifying it at the same instant.
  - When a client switches rooms, the leave-old-room + join-new-room sequence is treated as one atomic operation, so no other thread ever sees a client "halfway" between rooms.

## Commands

| Command | What it does |
|---|---|
| (just type a message) | Sends to everyone in your current room |
| `/join <room>` | Leaves your current room, joins (or creates) another |
| `/rooms` | Lists all currently active rooms and their member counts |
| `/quit` | Disconnects |

## How to run it

1. Start the server:
   ```
   python3 server.py
   ```
2. Start 2+ clients in separate terminals:
   ```
   python3 client.py
   ```
3. Everyone starts in `#general`. Try:
   ```
   /join study-group
   /rooms
   ```
   in different terminals to see clients move between rooms and the room list update.

## What this demonstrates (for resume/interview purposes)

- Concurrency: many clients served simultaneously via threads.
- Synchronization: a shared dictionary of lists protected by a lock, with atomic multi-step operations (moving between rooms).
- Basic protocol design: a simple text-command protocol (`/join`, `/rooms`) layered on top of raw sockets.

## Suggested resume bullet

> **Multi-threaded Chat Server with Chat Rooms** | Python, Sockets, Threading
> - Built a concurrent TCP server supporting multiple chat rooms, using a dedicated thread per client connection and `threading.Lock` to synchronize access to a shared room-membership dictionary.
> - Designed atomic room-switching logic to prevent race conditions when clients move between rooms while messages are being broadcast concurrently.

## Possible further extensions

- Add a `Semaphore` to cap max clients per room.
- Persist chat history per room to a file/database.
- Add private messaging (`/whisper user message`) within a room.
