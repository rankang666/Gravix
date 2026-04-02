---
name: evaluating-expressions
description: Evaluate mathematical expressions safely with support for basic arithmetic operations. Use when performing calculations or testing mathematical logic.
---

# Evaluating Expressions

Safe mathematical expression evaluator supporting arithmetic operations.

## Quick Start

```python
result = await executor.execute('calculate', {'expression': '2 + 2 * 3'})
# Returns: {'result': 8.0}
```

## Supported Operations

- `+` Addition
- `-` Subtraction
- `*` Multiplication
- `/` Division
- `()` Parentheses for grouping

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| expression | string | ✅ | Mathematical expression to evaluate |

## Security Limits

Allowed characters:
- Digits: `0-9`
- Operators: `+ - * /`
- Parentheses: `( )`
- Decimal points: `.`

**Blocked for security:**
- Variables and function calls
- Python built-ins
- Complex expressions

## Examples

```
"2 + 2"           → 4.0
"10 * (5 + 3)"    → 80.0
"3.14 * 2"        → 6.28
"100 / 4"         → 25.0
```
