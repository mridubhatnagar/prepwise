# System Design Terminologies

## Key Terminologies

### Stateless
- Server does not store client session information.
- Each request is independent of previous requests.

### Stateful
- Server keeps track of client session information across multiple requests.
- Requests may depend on previous interactions.

### Idempotency
- An operation is **idempotent** if performing it multiple times has the same effect as performing it once.
- Example: `PUT /user/123` with the same data always results in the same state.