# Data Modelling Concepts

## What are Entities

Entities represent independent objects in the domain.

Usually nouns in the problem statement.

Examples:
- user
- product
- order
- review
- payment_method

Rules:
- Entity should represent a real-world object.
- Entity should have attributes.
- Entity should have a primary key.

Example:

user
----
user_id (PK)
username
email
password

---

## What are Relationships

Relationships describe how entities interact.

Example relationships:
- user places order
- user writes review
- order contains product
- user maintains payment_method

Relationships later become:
- foreign keys
- junction tables

---

## What is Cardinality

Cardinality describes how many instances of one entity
can be associated with a single instance of another entity.

Mental model:
Fix ONE instance of entity A.
Check how many instances of entity B can relate to it.

Example:

user ↔ order

Questions:
- For ONE user → how many orders? → many
- For ONE order → how many users? → one

Result:

user 1 ---- * order

Types:
1:1   → one-to-one
1:N   → one-to-many
M:N   → many-to-many

---

## What are Foreign Keys

A foreign key links one table to another.

Rule:
Foreign key goes on the "many" side of a 1:N relationship.

Example:

user 1 ---- * order

order table contains:

order
-----
order_id
user_id (FK → user.user_id)

Examples:

user → order
order.user_id

user → address
address.user_id

product → review
review.product_id

---

## Many-to-Many Relationships

Relational databases cannot directly represent M:N relationships.

Solution:
Introduce a junction table.

Pattern:

A *----* B

becomes

A 1----* AB *----1 B

Example:

order ↔ product

Solution:

order_item
-----------
order_id (FK)
product_id (FK)
quantity
price

This table represents the relationship between order and product.

---

## What is Normalization

Normalization organizes data to reduce redundancy.

Important normal forms:

1NF
- Each column contains atomic values.
- No lists or arrays in columns.

Bad example:
order
product_ids = [1,2,3]

2NF
- Non-key attributes depend on the full primary key.

3NF
- No transitive dependency.
- Non-key attributes should depend only on the primary key.

Goal:
Avoid data duplication and maintain consistency.

---

## Self Referencing Relationships

A self-referencing relationship occurs when an entity has a relationship with itself.

Instead of linking two different entities, the relationship connects rows of the same table.

This is common in many real-world systems.

### Pattern

Entity interacts with another entity of the same type.

Example:

User follows another User

User ── Follow ── User

### Implementation

Use a junction table with two foreign keys pointing to the same table.

Example:

User
----
user_id (PK)
username
email

Follow
------
follower_id   (FK → User.user_id)
following_id  (FK → User.user_id)

PRIMARY KEY (follower_id, following_id)

### Example Data

Users

user_id | name
1       | Alice
2       | Bob
3       | Charlie

Follow

follower_id | following_id
1           | 2
3           | 2

Meaning:

Alice follows Bob
Charlie follows Bob

### Common Self-Referencing Patterns

**Social Networks** — User follows User

**Comments** — Comment replies to another Comment

Comment
-------
comment_id
parent_comment_id → Comment.comment_id

**Categories** — Category hierarchy

Category
--------
category_id
parent_category_id → Category.category_id

**Product Recommendations** — Product related to another Product

RelatedProduct
--------------
product_id
related_product_id

### When to Detect This Pattern

Look for words like: follow, friend, reply, parent, related

These often indicate a self-referencing relationship.

### Rule

If an entity interacts with another instance of the same entity, create a table that references the same entity twice.
