# Caching

## Caching Basics

When a client sends a request to a server, the server usually needs to fetch data from a database or disk. Accessing disk or databases involves **network and I/O operations**, which can be relatively slow.

To reduce latency and improve read performance, frequently accessed data can be stored in a **fast in-memory datastore** called a **cache**.

Instead of querying the database every time, the server can check the cache first. If the required data is present, it can return the response much faster.

### Cache Hit

The requested data is already present in the cache.

Flow:

Client → Server → Cache → Response

Since the server retrieves data from memory instead of disk, the response time is significantly faster.

### Cache Miss

The requested data is not found in the cache.

Flow:

Client → Server → Cache (miss) → Database → Response
                                  ↓
                               Store in cache

After fetching the data from the database, the server usually stores it in the cache so future requests can be served faster.

---

## Caching Strategies

### 1. Write-Around Cache (Lazy Loading)

In this strategy, data is written directly to the **database**, not the cache.

The cache only gets populated **when a read request occurs**.

Flow:
1. Client requests data
2. Cache miss occurs
3. Server fetches data from database
4. Response is returned to client
5. Data is stored in cache for future requests

**Characteristics**

- First request is always a cache miss
- Good when many writes occur but only some data is read frequently

---

### 2. Write-Through Cache

In this strategy, **every write goes to both cache and database simultaneously**.

Flow:

Client write → Cache → Database

**Characteristics**

- Cache and database remain consistent
- Faster reads because data is always available in cache
- Writes are slower since both cache and DB must be updated

---

### 3. Write-Back Cache (Write-Behind)

In this strategy, writes are made **only to the cache first**.

The cache periodically writes the data back to the database.

Flow:

Client write → Cache → (Later) Database

**Characteristics**

- Very fast writes
- Risk of **data loss** if the cache crashes before syncing to the database

---

## Cache Eviction (Invalidation)

Since cache memory is limited, older entries must be removed when space is needed.

### FIFO — First In First Out

The oldest entry in the cache is removed first.

**Limitation**

Frequently accessed data may still be evicted.

---

### LRU — Least Recently Used

The entry that **has not been accessed for the longest time** is removed.

**Advantages**

Works well when recently accessed data is likely to be requested again.

---

### LFU — Least Frequently Used

The entry with the **lowest access frequency** is evicted.

**Characteristics**

- Keeps frequently used data longer
- Requires tracking access counts

---

## Where Caching is Used

### Frontend

Browsers cache static assets such as:

- Images
- CSS
- JavaScript
- Fonts

This reduces repeated network requests.

---

### Backend

Servers use caching to reduce database load.

Example architecture:

Client → API Server → Cache (Redis / Memcached)  
                         ↓  
                      Database

**Benefits**

- Faster response time
- Reduced database load
- Better scalability

---

## Important Limitation

Cache is **not persistent storage**.

If the cache crashes or is cleared, the data stored in it will be lost. Therefore, the **database remains the source of truth**.