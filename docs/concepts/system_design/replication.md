# Replication

## Concept

Replication is a technique where **multiple copies of the same database are maintained on different servers**.

It is used when a **single database server cannot handle a large number of requests while maintaining low latency**.

Replication helps distribute the load across multiple database servers.

### Why Replication is Needed

- A single database server may become a **bottleneck under heavy traffic**.
- Replication helps:
  - Improve **read scalability**
  - Increase **availability**
  - Provide **fault tolerance**

### Key Point

Replication mainly helps with **read scalability**, **high availability**, and **fault tolerance**.

Replication **does not solve write scalability**. For that, **sharding** is used.

---

## Types of Replication

### Leader–Follower Replication (Master–Slave)

In this approach:

- One database acts as the **Leader**.
- Other databases act as **Followers**.

Flow:

1. Client sends **write requests to the Leader**.
2. Leader updates its data.
3. Leader **replicates the data to follower databases**.
4. Clients can **read data from followers**.

This reduces the load on the leader for read operations.

```
      Write
Client -----> Leader
                |
                | replicate
                v
          Follower DBs
           /        \
         Read      Read
```

### Limitation

Followers may be **temporarily out of sync with the leader** because replication is usually asynchronous.
This delay is called **replication lag**.

### Leader–Leader Replication (Multi-Leader)

In this approach:

- Multiple databases act as **leaders**.
- Clients can **read and write to any leader**.

Flow:

- Each leader **replicates its updates to other leaders**.

```
Client --> Leader A <----> Leader B <-- Client
            Write           Write
```

### Limitations

- **Conflict resolution** may be required if two leaders update the same data.
- Two-way replication can **increase system complexity and latency**.