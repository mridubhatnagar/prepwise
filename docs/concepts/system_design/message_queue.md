# Message Queues

## What is a Message Queue

### Concept

A message queue is a system that allows applications to communicate asynchronously.

Messages are placed in a queue by a **producer** and later processed by a **consumer**.

This helps handle large volumes of events without overwhelming the application servers.

### Basic Architecture

Producer → Queue → Consumer

1. Producers send messages to the queue.
2. The queue temporarily stores the messages.
3. Consumers process the messages asynchronously.

### Why Message Queues Are Used

Message queues provide several benefits:

- handle traffic spikes
- enable asynchronous processing
- decouple services
- improve system reliability

---

## Key Concepts

### Push vs Pull Model

**Push Model** — the queue pushes messages to consumers as soon as they arrive.

**Pull Model** — consumers periodically poll the queue to fetch messages. Many modern systems use the pull model.

### Durability

Message queues often store messages on disk to ensure durability.

This prevents message loss in case of system failures.

### Acknowledgement Mechanism

After processing a message, the consumer sends an acknowledgement (ACK) to the queue.

If the acknowledgement is not received, the message may be delivered again.

This ensures reliable message processing.

---

## Publish–Subscribe (Pub/Sub)

In the publish–subscribe model, messages are sent to a **topic** instead of a single queue.

Multiple consumers can subscribe to the topic and receive the messages.

Example:

Topic: PAYMENTS

Subscribers:
- payment processing service
- analytics service
- fraud detection service

---

## Examples

Popular message queue systems include:

- Apache Kafka
- RabbitMQ
- Amazon SQS
- Google Pub/Sub

### Order Processing Example


```
User places order
        ↓
Order Service
        ↓
Message Queue
        ↓
Inventory Service
        ↓
Payment Service
        ↓
Notification Service
```