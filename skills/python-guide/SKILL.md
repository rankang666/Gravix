---
name: python-guide
version: 1.0.0
description: Python 编程指南 - 常用代码片段和最佳实践
metadata:
  openclaw:
    emoji: "🐍"
    requires:
      bins: []
---

# Python 编程指南 Skill

提供常用的 Python 代码片段、最佳实践和编程模式。

## 数据结构

### 列表操作

```python
# 列表推导式
squares = [x**2 for x in range(10)]

# 过滤列表
evens = [x for x in range(20) if x % 2 == 0]

# 排序
sorted_list = sorted(my_list, key=lambda x: x.lower())
```

### 字典操作

```python
# 字典推导式
squared = {x: x**2 for x in range(6)}

# 合并字典
dict1 = {'a': 1, 'b': 2}
dict2 = {'c': 3, 'd': 4}
merged = {**dict1, **dict2}

# 获取默认值
value = my_dict.get('key', 'default_value')
```

## 函数式编程

```python
# map
result = list(map(lambda x: x**2, numbers))

# filter
evens = list(filter(lambda x: x % 2 == 0, numbers))

# reduce
from functools import reduce
total = reduce(lambda x, y: x + y, numbers)
```

## 文件操作

```python
# 上下文管理器
with open('file.txt', 'r') as f:
    content = f.read()

# 路径处理
from pathlib import Path
path = Path('dir/file.txt')
path.exists()  # 检查是否存在
path.read_text()  # 读取文件
```

## 异步编程

```python
import asyncio

async def fetch_data():
    await asyncio.sleep(1)
    return "data"

async def main():
    tasks = [fetch_data() for _ in range(5)]
    results = await asyncio.gather(*tasks)
    return results

asyncio.run(main())
```

## 错误处理

```python
try:
    result = risky_operation()
except ValueError as e:
    logger.error(f"Value error: {e}")
except Exception as e:
    logger.error(f"Unexpected error: {e}")
else:
    logger.info("Success!")
finally:
    cleanup()
```

## 装饰器

```python
def timer(func):
    import time
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        print(f"{func.__name__} took {time.time() - start:.2f}s")
        return result
    return wrapper

@timer
def slow_function():
    time.sleep(1)
```

## 类型提示

```python
from typing import List, Dict, Optional

def process_data(
    items: List[int],
    config: Dict[str, Any] = None
) -> Optional[str]:
    if not items:
        return None
    return str(len(items))
```

## 最佳实践

1. **使用上下文管理器**处理资源
2. **添加类型提示**提高代码可读性
3. **编写文档字符串**说明函数用途
4. **使用异常处理**而不是返回错误码
5. **避免全局变量**，使用函数参数
6. **遵循 PEP 8** 代码风格指南
