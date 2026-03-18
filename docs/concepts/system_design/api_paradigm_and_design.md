# API Paradigm and API Design

## API Paradigm (Concept)

API Paradigm defines **how APIs are structured and interact**.  
It is more conceptual and focuses on the **communication style and philosophy**.

### Common Paradigms

1. **RESTful APIs**
   - Resource-based
   - Stateless communication
   - Uses HTTP verbs (GET, POST, PUT, DELETE)

2. **RPC (Remote Procedure Call)**
   - Method-based
   - Invokes functions on remote servers
   - Can be over HTTP or other protocols

**Key Idea:** Paradigm is about **how systems communicate**, not the implementation.

---

## API Design (NeetCode)

API Design focuses on **practical implementation details** of APIs — how requests and responses are structured, and which technology to use.

### Examples

1. **REST**
   - Resource-oriented
   - Stateless
   - Multiple endpoints (e.g., `/users`, `/posts`)
   - Simple, widely adopted

2. **GraphQL**
   - Single endpoint
   - Clients request **exactly the data they need**
   - Avoids over-fetching / under-fetching
   - Flexible query structure

3. **gRPC**
   - High performance, binary protocol
   - Uses **Protocol Buffers (protobuf)**
   - Supports streaming (bidirectional)
   - Common in **microservices communication**

---

## Basic Flow (REST Example)

1. Client sends HTTP GET request to `/users/123`
2. Server processes the request
3. Server returns JSON with user data

**GraphQL Flow**

1. Client sends query specifying exactly which fields of `User` it wants
2. Server resolves query
3. Server returns only requested fields

**gRPC Flow**

1. Client calls remote procedure `GetUser(123)`
2. Server executes the function
3. Server streams back response (could be multiple messages)

---

## Key Takeaways

- **API Paradigm** = Conceptual “style” of communication (REST vs RPC)  
- **API Design** = Practical “how to implement” APIs using REST, GraphQL, gRPC  
- Understanding both is critical for **system design interviews** and building **scalable APIs**

---

