# TCP vs UDP

## TCP (Transmission Control Protocol)

TCP is a **transport layer protocol** used for reliable communication between a client and a server.

Before data transfer begins, TCP establishes a **connection** between the client and the server. The server sends **acknowledgements (ACKs)** to confirm that packets were received.

### Key Characteristics

- **Connection-oriented** protocol.
- Data is split into **small packets** before transmission.
- Each packet contains a **sequence number**.
- Sequence numbers allow the receiver to **reassemble data in the correct order**.
- If a packet is **lost**, it can be **retransmitted**.
- Ensures **reliable and ordered delivery of data**.

### Example Use Cases

- Web browsing (HTTP / HTTPS)
- File transfers
- Emails
- Database connections

---

## UDP (User Datagram Protocol)

UDP is also a **transport layer protocol**, but it is designed for **fast communication** rather than reliability.

Unlike TCP, UDP **does not establish a connection** and **does not send acknowledgements**.

### Key Characteristics

- **Connectionless** protocol.
- No handshake before sending data.
- No guarantee of **packet delivery**.
- No guarantee of **packet order**.
- Lower **latency** compared to TCP.
- Faster due to **minimal overhead**.

### Example Use Cases

- Video streaming
- Online gaming
- Voice calls (VoIP)
- DNS queries

---

## TCP vs UDP

| Feature | TCP | UDP |
|------|------|------|
| Connection | Connection-oriented | Connectionless |
| Reliability | Reliable | Not reliable |
| Packet Ordering | Guaranteed | Not guaranteed |
| Retransmission | Yes | No |
| Speed | Slower | Faster |
| Overhead | Higher | Lower |
| Use Cases | Web, email, file transfer | Streaming, gaming, DNS |