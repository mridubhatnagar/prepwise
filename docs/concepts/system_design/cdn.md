# Content Delivery Network (CDN)

## What is a CDN

CDN stands for **Content Delivery Network**.

In many applications, the **origin server** (where the application is hosted) and the **users** accessing the application may be located in different geographic regions. If every request has to travel all the way to the origin server, it increases **latency** and slows down the user experience.

A CDN solves this problem by deploying **servers across multiple geographic regions**. These servers store cached copies of content and serve users from the **closest available location**.

---

## How CDN Works

Instead of every request going directly to the origin server, the request is routed to the **nearest CDN server (edge server)**.

Basic flow:

```
Client → CDN Edge Server → Origin Server
          ↑
       Cached content
```

### Cache Hit

If the requested content already exists in the CDN cache:

```
Client → CDN Edge Server → Response
```

The response is served directly from the CDN, resulting in **very low latency**.

### Cache Miss

If the content is not present in the CDN cache:

```
Client → CDN Edge Server → Origin Server → Response
                          ↓
                       Store in CDN cache
```

The CDN fetches the content from the origin server, returns it to the client, and stores it for future requests.

---

## What Content is Typically Served from CDN

CDNs are primarily used to serve **static content**, such as:

- Images
- JavaScript files
- CSS files
- Fonts
- Videos
- Static HTML pages (e.g., login or landing pages)

Since these resources change infrequently, they are ideal for caching at CDN edge locations.

---

## Benefits of CDN

1. **Reduced Latency**

Content is served from a **server closer to the user**, reducing network travel time.

2. **Reduced Load on Origin Server**

Many requests are handled by CDN servers instead of the main server.

3. **Improved Scalability**

CDNs help handle **large traffic spikes** without overwhelming the origin server.

4. **Better Global Performance**

Users across different regions experience similar performance levels.

---

## Limitations and Providers

**Limitations**

- Not ideal for **highly dynamic content** that changes frequently.
- Cache invalidation must be managed when content updates.
- CDN is typically used as a **cache layer**, not as the primary data source.

**Popular CDN Providers**

- Cloudflare
- AWS CloudFront
- Akamai
- Fastly
- Google Cloud CDN
