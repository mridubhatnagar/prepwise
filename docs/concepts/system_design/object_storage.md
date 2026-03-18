# Object Storage

## What is Object Storage

### Concept

Object storage is a storage architecture used to store large amounts of unstructured data such as:

- images
- videos
- logs
- backups
- large datasets

Data is stored as **objects** instead of files or blocks.

Each object contains:

- the data itself
- metadata
- a unique identifier (object key)

### Structure

Object storage uses a **flat structure** rather than a hierarchical folder structure.

All objects exist in a single namespace inside a **bucket**.

```
Bucket: my-bucket
┌────────────────────────────────────────────┐
│  key: images/2024/photo.png  → data + meta │
│  key: videos/intro.mp4       → data + meta │
│  key: logs/2024-01-01.log    → data + meta │
└────────────────────────────────────────────┘
```

Although keys look like folder paths, there are no real directories — `images/2024/` is just part of the key name.

### Access Method

Object storage is accessed using **HTTP-based APIs**.

Common operations include:

- PUT → upload object
- GET → retrieve object
- DELETE → remove object

---

## Advantages and Examples

### Advantages

Object storage provides:

- massive scalability
- high durability
- easy access over the internet

It is ideal for storing large unstructured data.

### Examples

Popular object storage services include:

- Amazon S3
- Google Cloud Storage
- Azure Blob Storage

---

## User Flow

```
User uploads image
      ↓
API Server
      ↓
Object Storage (S3)
      ↓
Image URL stored in database
```