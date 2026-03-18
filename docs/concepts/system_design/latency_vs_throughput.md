# Latency vs Throughput

## Latency

**Latency** is the time taken for a single request to travel through the system and return a response.

Example:
- A user opens a website.
- The request is sent to the server.
- The server processes the request and sends back a response.

If this process takes **200 milliseconds**, the latency is **200 ms**.

In simple terms:

Latency = **Waiting time for a request to complete**

### Example Analogy

Restaurant order:

Customer places order → food arrives.

The time taken between ordering and receiving the food is similar to **latency**.

---

## Throughput

**Throughput** refers to the number of requests a system can handle within a given time period.

Example:

A server processes:

- 1000 requests per second

Throughput = **1000 requests/second**

In simple terms:

Throughput = **How much work a system can handle**

### Example Analogy

Restaurant kitchen:

If a kitchen can prepare **100 meals per hour**, then:

Throughput = **100 meals/hour**

---

## Key Difference and Tradeoffs

### Key Difference

| Metric | Meaning |
|------|------|
| Latency | Time taken to process a single request |
| Throughput | Number of requests processed in a given time |

### Tradeoffs

In system design, engineers try to:

- **Reduce latency** (make responses faster)
- **Increase throughput** (handle more users)

However, improving one can sometimes affect the other, so systems are designed by balancing these trade-offs.