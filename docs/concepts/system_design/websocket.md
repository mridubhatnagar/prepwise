# WebSocket

## What is WebSocket?

WebSocket is a protocol that enables **persistent, two-way (full-duplex) communication between a client and a server** over a single connection.

Unlike traditional HTTP where the client must repeatedly send requests to receive updates, WebSocket allows **both the client and server to send messages to each other at any time** once the connection is established.

This makes WebSockets suitable for **real-time communication**.

---

## Why WebSockets Are Needed?

In traditional HTTP communication:

Client → Request → Server  
Server → Response → Client  

If the client needs updates continuously, it must keep sending requests (polling), which increases **latency and server load**.

WebSockets solve this by maintaining a **persistent connection**, allowing real-time data transfer.

---

## Basic Flow

1. Client sends an **HTTP request to upgrade the connection** to WebSocket.
2. Server accepts the upgrade request.
3. A **persistent connection** is established between client and server.
4. Both client and server can **send messages independently** at any time.

---

## Key Characteristics and Use Cases

### Key Characteristics

- Persistent connection
- Full-duplex communication
- Low latency
- Reduces repeated HTTP requests
- Built on top of **TCP**

### Use Cases

- Live chat applications
- Real-time notifications
- Collaborative editing tools
- Live dashboards
- Multiplayer games
- Stock price updates