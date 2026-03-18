# Proxy

## What is a Proxy

A **proxy server** is an intermediary server that sits between a **client** and a **destination server**.

Instead of communicating directly with the destination server, the client sends requests to the proxy, which then forwards the request to the destination server and returns the response back to the client.

Basic flow:

```
Client → Proxy → Server
```

Proxies are used for:
- Security
- Traffic control
- Caching
- Anonymity
- Monitoring network usage

---

## Types of Proxies

### Forward Proxy

A **Forward Proxy** sits between the **client and the internet**.

The client sends requests to the proxy, and the proxy forwards them to the destination server.

```
Client → Forward Proxy → Internet Server
```

```
Employee Laptop
      │
      │ (internal company network)
      ▼
Forward Proxy
      │
      │ (internet)
      ▼
Website Server
```

The **proxy represents the client** to the destination server. The destination server does **not know the actual client IP** — it only sees the proxy.

Use cases: corporate networks blocking certain websites, anonymous browsing, monitoring user internet activity.

Example flow:

1. Client sends request to proxy
2. Proxy forwards request to destination server
3. Server sends response to proxy
4. Proxy returns response to client

### Reverse Proxy

A **Reverse Proxy** sits between the **client and backend servers**.

Clients send requests to the reverse proxy, which forwards the request to one of the backend servers.

```
Client → Reverse Proxy → Backend Server
```

The **proxy represents the server** to the client. Clients interact only with the proxy and do not know about the actual backend servers.

Use cases: load balancing, security (hiding internal infrastructure), SSL termination, caching, CDN.

Example flow:

1. Client sends request to reverse proxy
2. Reverse proxy forwards request to backend server
3. Backend server sends response to proxy
4. Proxy returns response to client


## Forward Proxy vs Reverse Proxy

| Feature | Forward Proxy | Reverse Proxy |
|-------|-------|-------|
| Position | Sits between **client and internet** | Sits between **client and backend servers** |
| Represents | Represents the **client** to the server | Represents the **server** to the client |
| Client Awareness | Client **knows it is using a proxy** | Client **does not know about backend servers** |
| Server Awareness | Server sees **proxy instead of real client** | Client sees **proxy instead of real servers** |
| Main Purpose | Control and monitor **client access to internet** | Manage and distribute **traffic to backend servers** |
| Common Use Cases | Network filtering, anonymity, monitoring | Load balancing, caching, security, CDN |

---

