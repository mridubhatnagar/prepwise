# Feb 4, 2026

1. Setup AWS Account
2. MFA setup for root and non root user
3. Budget limits and alerts enabled.

## 📅 Feb 6, 2026 — AWS Learning Log

### ✅ Completed
- **AWS Introduction** (Adrian Cantrill)
- **Scenario Section**

### 🧠 Key Takeaways
- AWS should be understood **from problems → architecture → services**, not service-first.
- Scenarios help frame *why* cloud services exist before learning *how* they work.
- Thinking in terms of availability, scalability, and failure from Day 1 sets the right mental model.

## 📅 Feb 9, 2026 — AWS Learning Log

### ✅ Completed
1. Watched the **next section** from Adrian Cantrill’s AWS course.
2. Watched videos on:
   - Creating **Root user**
   - Creating **IAM user**
   - Understanding the **difference between Root and IAM accounts**
3. Learned about **MFA (Multi-Factor Authentication)**:
   - What MFA is and why it is important
   - Difference between **Authentication** and **Authorization**
   - Setting up MFA for both Root and IAM accounts
4. Covered **IAM basics**:
   - IAM **Users**
   - IAM **Groups**
   - IAM **Roles**
   - Differences and use cases for each

---

### 🧠 Key Takeaways
- **Root account** has full control and should be locked down with MFA and rarely used.
- **IAM users** are meant for daily usage with scoped permissions.
- **Authentication** = who you are (identity verification).
- **Authorization** = what you are allowed to do (permissions).
- MFA adds an additional security layer beyond username/password.
- IAM entities serve different purposes:
  - **User** → individual identity
  - **Group** → collection of users with shared permissions
  - **Role** → permissions assumed temporarily by services or users

---

## 📅 Feb 10, 2026 — AWS Learning Log

### ✅ Completed
1. Enabled **AWS CLI** for the IAM user account.
2. Watched the **first video from AWS Fundamentals**:
   - Public services vs Private services.

---

### 🧠 Key Takeaways
- AWS CLI access allows interacting with AWS programmatically, not just via the console.
- **Public services**:
  - Exposed to or accessible via the public internet.
  - Example patterns: internet-facing endpoints, public APIs.
- **Private services**:
  - Not directly accessible from the public internet.
  - Typically accessed within a VPC or through controlled networking paths.
- Understanding whether a service is public or private is foundational for:
  - Security design
  - Network architecture
  - Access control decisions

---

## Feb 12, 2026

- Watched video on Regions, Edge Locations and Availability Zones in AWS

## 📅 Feb 10, 2026 — AWS Learning Log (Continued)

### ✅ Completed
1. Watched video on **Basics of VPC** (Adrian Cantrill).
2. Rewatched video on:
   - AWS Regions
   - Availability Zones
   - Edge Locations

---

### 🧠 Key Takeaways

#### 🌍 AWS Global Infrastructure (Reinforcement)
- **Region** = Geographic area containing multiple Availability Zones.
- **Availability Zone (AZ)** = Isolated data center(s) within a region.
- **Edge Locations** = Used for content delivery (CloudFront), DNS (Route 53), and latency optimization.
- High availability is achieved by distributing workloads across multiple AZs.

Rewatching helped clarify:
- Regions are isolated from each other.
- AZs provide fault isolation within a region.
- Edge locations improve performance but do not host general compute workloads.

---

#### 🌐 Basics of VPC
- **VPC (Virtual Private Cloud)** = A logically isolated network within AWS.
- You control:
  - IP address range (CIDR block)
  - Subnets
  - Routing
  - Security rules
- VPC acts like your **private data center network** inside AWS.

Conceptual understanding:
- Public vs Private services connect directly to VPC design.
- VPC is foundational for EC2, RDS, ALB, etc.
- Networking knowledge will become critical soon (subnets, routing tables, IGW).

---

### 🎯 Notes
- VPC feels like the backbone of AWS networking.
- Rewatching infrastructure videos improved mental clarity on how traffic flows globally.
- Understanding VPC early will make later EC2 and Load Balancer labs easier.
