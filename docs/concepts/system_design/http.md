# HTTP (HyperText Transfer Protocol)

## HTTP Overview

### What is HTTP?

HTTP is an **application layer protocol** used for communication between a client and a server on the web.

It follows a **request–response model**, where a client sends a request and the server returns a response.

HTTP is built on top of **TCP**, which ensures reliable delivery of data between systems.

### Basic Flow

1. A **TCP connection is established** between the client and server using a **3-way handshake**.
2. The client sends an **HTTP request** to the server.
3. The server processes the request.
4. The server sends an **HTTP response** back to the client.

Flow:

Client → HTTP Request → Server
Server → HTTP Response → Client

### TCP Handshake (Before HTTP Communication)

Before HTTP communication begins, TCP establishes a connection using a **3-way handshake**.

1. Client → **SYN**
2. Server → **SYN-ACK**
3. Client → **ACK**

Once the connection is established, **HTTP messages can be exchanged**.

### Key Characteristics

- Application layer protocol
- Built on top of **TCP**
- Uses **request–response communication**
- **Stateless protocol** (each request is independent)

---

## HTTP vs HTTPS

| Feature | HTTP | HTTPS |
|------|------|------|
| Security | Not encrypted | Encrypted |
| Protocol | HTTP over TCP | HTTP over TLS/SSL |
| Use Case | Non-secure communication | Secure communication |