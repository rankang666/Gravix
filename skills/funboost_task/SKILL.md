---
name: submitting-funboost-tasks
description: Submit tasks to Funboost message queues for asynchronous background execution. Use when delegating work to distributed job processors or implementing background task patterns.
---

# Submitting Funboost Tasks

Interface to the Funboost distributed task queue system for background job processing.

## Quick Start

```python
result = await executor.execute(
    'funboost_task',
    {
        'queue_name': 'hello_queue',
        'task_params': {'name': 'Gravix'}
    }
)
```

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| queue_name | string | ✅ | Target Funboost queue name |
| task_params | object | ❌ | Parameters to pass to the task |
| wait_for_result | boolean | ❌ | Block until task completes (default: false) |

## Returns

```json
{
  "success": true,
  "data": {
    "queue_name": "hello_queue",
    "task_submitted": true,
    "message": "Task submitted to hello_queue"
  }
}
```

## Available Queues

- `hello_queue` - Example greeting task

## Implementation

**Submission**: `app/publisher/submit.py`
**Processing**: `app/consumers/hello.py`
