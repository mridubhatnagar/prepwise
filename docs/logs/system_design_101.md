## 📅 Feb 13, 2026 — System Design Learning Log

### ✅ Completed
1. Watched lecture on **Computer Architecture Basics**:
   - CPU
   - Cache
   - RAM
   - Disk
   - Memory interaction flow
2. Watched lecture on **Basic Application Architecture**:
   - Request flow
   - Observability components (logs, metrics, alerts)
3. Understood core terminology:
   - Latency
   - Throughput
   - Tradeoffs in system design
   - fault tolerance
   - Reliability
   - Redundancy

---

### 🧠 Key Takeaways

#### 🖥️ Computer Architecture (Performance Foundations)

- CPU executes instructions, but performance bottlenecks usually come from memory and I/O.
- Memory hierarchy:
  - Cache → Fastest, smallest
  - RAM → Fast, volatile
  - Disk (SSD/HDD) → Persistent, much slower
  - Network → Highest latency in distributed systems

**Core Insight:**
System slowness is typically caused by memory access and network hops, not raw computation.

Implication:
- Caching reduces disk and DB calls.
- Minimizing network calls improves performance.
- Data locality matters.

---

#### 🏗️ Basic Application Architecture

**Request Flow:**

User  
→ Load Balancer  
→ Application Server  
→ Database  

**Observability Flow:**

Application  
→ Logs  
→ Metrics  
→ Monitoring System  
→ Alerts  
→ Developer  

**Observations:**
- Request handling and observability are separate concerns.
- Production systems require monitoring and alerting, not just functional correctness.
- Feedback loop (alerts → developer → fix) is essential for reliability.

---

#### ⚖️ Latency vs Throughput

- **Latency** = Time taken to complete a single request.
- **Throughput** = Number of requests processed per unit time.

**Tradeoff:**
Optimizing throughput (e.g., batching) can increase per-request latency.

Scaling decisions must balance both metrics.

---

### 🎯 Notes

- Computer architecture forms the foundation for understanding caching and distributed systems.
- Application architecture extends beyond server + DB; observability is critical.
- System design requires evaluating tradeoffs, not finding perfect solutions.
- Next areas to deepen:
  - Role of load balancers beyond traffic distribution.
  - Cost vs performance tradeoffs in scaling.
  - Failure scenarios in monitoring systems.

## 📅 Mar 3, 2026 — System Design Learning Log

### Topic: API Paradigm & API Design

**Key Points**
- APIs define the interface between client and server; they encapsulate server logic while exposing necessary operations.
- RESTful principles:
  - Resources via URIs
  - HTTP methods: GET, POST, PUT, DELETE
  - Single-responsibility endpoints
  - Versioning for backward compatibility
- Tradeoffs:
  - Granular endpoints → easier maintenance, more network calls → higher latency
  - Fewer endpoints → lower latency, harder to evolve
- Clear contracts (inputs, outputs, error handling) are critical for reliability and scalability.

**Insight**
Understanding API design is foundational before scaling, caching, or introducing rate limiting; it shapes system architecture and tradeoff reasoning.

## 📅 Mar 4, 2026 — System Design Learning Log

### ✅ Completed
1. Studied about **Caching** and **CDN**.

### Key Takeaways
- **Caching** is a technique used to reduce latency. It makes reads faster. 
- There are 3 types of caching:
    - Write around caching
    - Write through caching
    - Write back caching
- There are 3 cache invalidation techniques:
    - FIFO
    - LRU
    - LFU
- CDN is content delivery network. This also helps in reducing latency. 


## March 5, 2026 - System Design Learning Log

### Completed
1. Consolidated learning by adding it to the knowledgebase.
2. Watched video on Proxies & Load Balancers

### 🧠 Key Takeaways

#### ⏱️ Latency
- **Latency** is the time taken for a single request to complete.
- Example: Time taken from sending a request to receiving the response.
- Measured in **milliseconds (ms)**.
- Lower latency means **faster response time for users**.

#### 🚀 Throughput
- **Throughput** refers to the number of requests a system can handle within a given time period.
- Example: A server handling **1000 requests per second**.
- Higher throughput means the system can **serve more users simultaneously**.

#### ⚖️ Trade-off
- System design often involves balancing **latency and throughput**.
- Goal is usually:
  - **Lower latency**
  - **Higher throughput**

### 🎯 Notes
- Latency measures **speed of a single request**.
- Throughput measures **capacity of the system**.
- Both are fundamental metrics when evaluating system performance.