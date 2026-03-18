# CAP Theorem

## Concept

The CAP theorem states that a distributed system can guarantee **only two out of the following three properties** at the same time:

- Consistency (C)
- Availability (A)
- Partition Tolerance (P)

---

## Consistency

Consistency means that **all nodes return the same data at the same time**.

Every read request receives the **most recent write** or an error.

---

## Availability

Availability means that **every request receives a response**, even if the data returned may not be the most recent.

The system always responds to requests and does not reject them.

---

## Partition Tolerance

Partition tolerance means that the system **continues operating even if communication between nodes fails** due to a network partition.

Network partitions occur when nodes cannot communicate with each other because of network failures.

---

## Trade-off During Network Partition

When a network partition occurs, the system must choose between **Consistency** and **Availability**.

### CP (Consistency + Partition Tolerance)

The system maintains **consistent data across nodes**.

Some requests may be **rejected or delayed** to ensure that all nodes return the same data.

Example systems:
- HBase
- MongoDB (in certain configurations)


### AP (Availability + Partition Tolerance)

The system continues to **serve requests even if data becomes temporarily inconsistent**.

Nodes may return **stale data**, but the system remains available.

Example systems:
- Cassandra
- DynamoDB

---

## Key Idea

In distributed systems, **network partitions are unavoidable**, so systems typically choose between:

- **CP systems** → prioritize data consistency
- **AP systems** → prioritize system availability


### In a distributed system:

```
                Consistency
                     (C)
                    /   \
                   /     \
                  /       \
                 /         \
                /           \
               /             \
Partition Tolerance -------- Availability
        (P)                       (A)
```

Choose any two properties:

CP → Consistency + Partition Tolerance
AP → Availability + Partition Tolerance
CA → Consistency + Availability
      (only possible when there is no network partition)