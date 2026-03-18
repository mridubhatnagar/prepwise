# Eventual Consistency

## What is Eventual Consistency and Why it Exists

### What is Eventual Consistency?

Eventual consistency is a consistency model used in distributed systems.

It guarantees that **if no new updates occur, all replicas will eventually converge to the same value**.

### Why Eventual Consistency Exists?

In distributed systems, network delays and partitions may cause replicas to temporarily have **different versions of data**.

To maintain high availability, systems may allow reads and writes even when replicas are out of sync.

---

## Example and Key Idea

### Example

Suppose data is replicated across multiple nodes.

1. A client writes data to one node.
2. Other replicas may not immediately receive the update.
3. For a short period, replicas may contain **different values**.
4. Eventually the update propagates to all replicas.

After replication completes, all nodes contain the **same data** again.

### Key Idea

Eventual consistency allows **temporary data inconsistency** in order to achieve:

- High availability
- Better performance in distributed systems