---
name: echoing-messages
description: Echo back messages with timestamps for testing the skills system or verifying message delivery.
---

# Echoing Messages

Returns the input message with a server timestamp for testing and verification.

## Quick Start

```python
result = await executor.execute('echo', {'message': 'Hello!'})
# Returns: {'echo': 'Hello!', 'timestamp': '2026-04-02T12:00:00'}
```

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| message | string | ✅ | Message to echo back |

## Returns

Echoed message with ISO 8601 timestamp:

```json
{
  "success": true,
  "data": {
    "echo": "Hello!",
    "timestamp": "2026-04-02T12:00:00.000000"
  }
}
```
