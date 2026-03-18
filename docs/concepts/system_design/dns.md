# DNS (Domain Name System)

## What is DNS and Why is it Needed

### What is DNS?

DNS stands for **Domain Name System**.

It translates **human-readable domain names** into **IP addresses** that computers use to communicate.

Example:

```
google.com → 142.250.183.206
```

Humans use domain names, but servers communicate using IP addresses.

DNS acts like the **phonebook of the internet**.

### Why DNS is Needed?

It is easier for users to remember:

```
google.com
amazon.com
github.com
```

instead of IP addresses like:

```
142.250.183.206
54.239.28.85
140.82.114.3
```

DNS maps domain names to their corresponding IP addresses.

---

## Explain DNS Lookup Process?

When a user enters a website URL in the browser, the browser performs a DNS lookup to find the server's IP address.

### Step 1: Browser Cache

The browser first checks if the domain name exists in its **local DNS cache**.

```
Browser Cache → IP found → Request sent to server
```

If not found, the lookup continues.

---

### Step 2: OS Cache

The operating system checks its **DNS cache**.

If the IP address is found, it is returned to the browser.

---

### Step 3: Router / ISP Resolver

If the OS cache does not contain the result, the request goes to the **DNS resolver**, usually provided by the ISP.

---

## Recursive DNS Lookup

If the resolver does not have the answer cached, it performs a recursive lookup.

### Root DNS Server

The resolver asks the **Root DNS Server** where to find information for the domain.

```
www.google.com → Root Server
```

The root server points to the appropriate **TLD server**.

---

### TLD Server

The **Top Level Domain (TLD) server** manages domain extensions like:

```
.com
.org
.in
.net
```

Example:

```
google.com → .com TLD server
```

The TLD server directs the resolver to the **Authoritative DNS Server**.

---

### Authoritative DNS Server

The authoritative server contains the **actual mapping of domain name to IP address**.

Example response:

```
google.com → 142.250.183.206
```

The resolver returns this IP address to the browser.

---

## Final Request Flow

```
User enters URL
      ↓
Browser Cache
      ↓
OS Cache
      ↓
DNS Resolver (ISP)
      ↓
Root Server
      ↓
TLD Server
      ↓
Authoritative DNS Server
      ↓
IP Address returned
```

The browser can now connect to the web server using the IP address.

---

## DNS Caching

DNS results are cached at multiple levels to reduce lookup time.

Caching layers include:

- Browser cache
- OS cache
- ISP DNS resolver

This significantly improves performance and reduces DNS traffic.

---

## Key Insight

DNS is a **distributed and hierarchical system** that allows the internet to scale to billions of domain name lookups.