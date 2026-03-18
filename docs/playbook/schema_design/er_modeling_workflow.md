# ER Modeling Workflow

A simple step-by-step workflow to convert a problem statement into a database schema.

---

## Understanding the Domain

### 1. Identify Entities

List the core objects in the system.

Ask:
- What things exist independently?
- What objects do we store data about?

Example:
User, Post, Comment, Photo

### 2. Add Attributes

List attributes for each entity.

Guidelines:
- Keep attributes atomic
- Avoid lists
- Avoid derived values

Example:

User
- user_id
- email
- username

Post
- post_id
- content
- created_at

### 3. Identify Relationships

Define how entities interact.

Examples:

- User creates Post
- User writes Comment
- Post has Comment
- User likes Post
- User follows User

---

## Defining Structure

### 4. Decide Cardinality

Determine relationship type.

Possible types:

1:1
1:N
N:N

Example:

User → Post = 1:N
Post → Comment = 1:N
User → Post (Like) = N:N
User → User (Follow) = N:N

### 5. Resolve Many-to-Many

Convert every **N:N relationship** into a **junction table**.

Example:

User likes Post

Like
- user_id
- post_id

### 6. Place Foreign Keys

Rules:

1. 1:N → foreign key goes on the **N side**.
Example:

Post
- post_id
- user_id (FK)

2. 1:1 → foreign key can go on **either side**

Typically place it on the **dependent entity**.

Example:

Profile
- profile_id
- user_id (FK)

Self-referencing example:

Follow
- follower_id
- following_id

---

## Finalising the Schema

### 7. Convert to Tables

Define:

- Primary keys
- Foreign keys
- Attributes

### 8. Validate

Run `schema_design_checklist.md` to check:

- missing foreign keys
- unresolved many-to-many relationships
- normalization issues