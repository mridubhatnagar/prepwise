# Replication vs Sharding

## Replication vs Sharding

### Key Difference

Replication creates **copies of the same data** across multiple databases.

Sharding **splits the data** across multiple databases.

### Replication

- Same data exists on multiple servers
- Improves **read scalability**
- Improves **availability and fault tolerance**
- Writes typically go to a **leader database**

### Sharding

- Data is **partitioned across multiple servers**
- Improves **write scalability**
- Improves **storage scalability**
- Each shard contains **different subset of data**

---

## Summary

| Feature | Replication | Sharding |
|-------|------|------|
| Data | Same data copied | Data split |
| Main Goal | Read scaling | Write scaling |
| Availability | High | Depends on shard health |
| Storage | Same data repeated | Data distributed |

---

## Real Systems

Large systems often use **both together**:

- Data is **sharded across servers**
- Each shard may have **replicas for fault tolerance**