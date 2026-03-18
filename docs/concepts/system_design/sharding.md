# Sharding

## What is Sharding

### What is Sharding?

Sharding is a technique where a **database is horizontally partitioned across multiple servers**.

Instead of storing all data in a single database, the data is **split into smaller parts called shards**, and each shard is stored on a different database server.

### Why Sharding is Needed?

A single database server has limits in terms of:

- Storage capacity
- Write throughput
- CPU and memory resources

Sharding helps scale the database by **distributing data and write operations across multiple servers**.

---

## How Sharding Works?

Data is split across multiple databases based on a **shard key**.

The shard key determines **which shard stores a particular record**.

### Range-based Sharding

Data is divided based on ranges.

Example:

Shard 1 → Users A–L  
Shard 2 → Users M–Z  

### Hash-based Sharding

A hash function determines which shard stores the data.

Example:

hash(user_id) % number_of_shards

This helps distribute data more evenly.

---

## Key Concepts

### Role of Application Layer

In many systems, the **application layer determines which shard to query** based on the shard key.

The database itself may not automatically manage sharding.

### Challenges of Sharding

Sharding introduces complexity:

- Cross-shard joins become difficult
- Transactions across shards are harder
- Rebalancing shards when data grows
- Hot shard problem if one shard receives more traffic than others

### Key Idea

Sharding mainly helps with **write scalability** and **storage scalability**.

Replication and sharding are often used **together in large distributed systems**.