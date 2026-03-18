# Load Balancer

## What is a Load Balancer?

A **Load Balancer** distributes incoming client requests across multiple servers.

When an application receives a large number of requests, a single server may not be able to handle all the traffic efficiently. To solve this, systems scale **horizontally** by adding more servers.

A load balancer sits in front of these servers and distributes incoming requests among them.

Basic architecture:

```
Client
   ↓
Load Balancer
   ↓
Server 1
Server 2
Server 3
```

The client sends requests to the load balancer, and the load balancer forwards them to one of the available servers.

A **Load Balancer is essentially a specialized Reverse Proxy** that distributes incoming requests across multiple backend servers.

---

## Why Load Balancers are Needed?

1. **Handle High Traffic**

Instead of sending all traffic to one server, requests are distributed across multiple servers.

2. **Prevent Server Overload**

If one server receives too many requests, it can slow down or crash. Load balancers distribute traffic evenly.

3. **Reduce Latency**

Balanced traffic prevents servers from becoming overloaded, which keeps response times lower.

4. **Improve Throughput**

Multiple servers can process requests simultaneously, increasing the total number of requests the system can handle.

---

## Load Balancing Algorithms

### Round Robin

Requests are distributed sequentially across servers.

Example:

```
Request 1 → Server 1
Request 2 → Server 2
Request 3 → Server 3
Request 4 → Server 1
```

### Limitation

This method assumes all servers have the same capacity. If servers have different processing power, traffic distribution may not be optimal.

---

### Weighted Round Robin

Each server is assigned a **weight based on its capacity**.

Servers with higher capacity receive more requests.

Example:

```
Server A (weight 3)
Server B (weight 1)

Requests:
A → A → A → B → repeat
```

This allows more powerful servers to handle more traffic.

---

### Least Connections

The load balancer sends the request to the server with the **fewest active connections**.

Example:

```
Server 1 → 10 active connections
Server 2 → 3 active connections
Server 3 → 6 active connections
```

The next request will go to **Server 2**.

This method works well when request processing times vary.

---

## Health Checks

Load balancers periodically check whether backend servers are healthy.

If a server fails or becomes unresponsive, the load balancer stops sending traffic to that server.

Example:

```
Client
   ↓
Load Balancer
   ↓
Server 1 ✓
Server 2 ✗ (unhealthy)
Server 3 ✓
```

Traffic will only be routed to **Server 1 and Server 3**.

---

## Load Balancer Failure

Since the load balancer is a critical component, it can become a **single point of failure**.

To prevent this, systems often deploy **multiple load balancers** with redundancy.

Example:

```
Clients
   ↓
DNS
   ↓
Load Balancer 1
Load Balancer 2
   ↓
Application Servers
```

If one load balancer fails, traffic can be routed to another.

