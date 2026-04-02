---
name: monitoring-system-resources
description: Retrieve CPU, memory, and disk usage information for system monitoring and health checks. Use when checking server resources or diagnosing performance issues.
---

# Monitoring System Resources

Retrieve detailed system metrics including CPU usage, memory utilization, and disk space.

## Quick Start

```python
# Get CPU usage
result = await executor.execute('system_info', {'info_type': 'cpu'})

# Get memory usage
result = await executor.execute('system_info', {'info_type': 'memory'})

# Get all metrics
result = await executor.execute('system_info', {'info_type': 'all'})
```

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| info_type | string | ✅ | Metric type: `cpu`, `memory`, `disk`, or `all` |

## Returns

System metrics in JSON format:

### CPU
```json
{
  "cpu": {
    "percent": 45.2,
    "count_physical": 4,
    "count_logical": 8,
    "freq_max": 3200
  }
}
```

### Memory
```json
{
  "memory": {
    "total": 16.0,
    "available": 4.5,
    "percent": 72.0,
    "used": 11.5
  }
}
```

### Disk
```json
{
  "disk": {
    "total": 512.0,
    "used": 256.0,
    "free": 256.0,
    "percent": 50.0
  }
}
```
