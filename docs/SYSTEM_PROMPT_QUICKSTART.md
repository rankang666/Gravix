# 系统提示词快速入门

## 三种配置方式

### 1. 代码配置（最灵活）

```python
# run_all.py
custom_prompt = "你是一位数据分析师..."

chat_server = ChatServer(
    system_prompt=custom_prompt  # 传入自定义提示词
)
```

### 2. 文件配置（推荐）

创建 `system_prompt.txt` 文件，然后在代码中读取：

```python
# run_all.py
with open('system_prompt.txt', 'r', encoding='utf-8') as f:
    custom_prompt = f.read()

chat_server = ChatServer(
    system_prompt=custom_prompt
)
```

### 3. 使用默认提示词

不传 `system_prompt` 参数，系统使用内置的默认提示词。

## 快速示例

### 示例 1：简洁版

```
你是一位专业的数据分析师，擅长使用 MaxCompute/ODPS 进行数据分析。

## 工作原则
- 准确性优先
- 用户目标导向
- 安全第一
- 持续优化
```

### 示例 2：详细版

```
你是一位经验丰富的 SQL 查询优化专家。

## 你的专长
- SQL 查询性能优化
- 索引和分区策略
- 数据质量分析
- 业务洞察提炼

## 工作流程
1. 理解查询目标和业务场景
2. 分析表结构和数据分布
3. 设计优化方案
4. 对比优化效果
5. 提供最佳实践建议

## 沟通风格
- 技术精确，解释清晰
- 提供可运行的代码示例
- 说明优化理由和效果
- 标注注意事项
```

## 关键要素

好的系统提示词应包含：

1. **角色定义** - AI 是什么身份
2. **专长领域** - 擅长什么
3. **工作方式** - 如何处理问题
4. **沟通风格** - 怎么与用户交流
5. **行为规则** - 什么可以做，什么不能做
6. **安全原则** - 注意事项和边界

## 调试技巧

### 查看实际使用的提示词

```python
# 在 ChatServer 类中添加日志
logger.info(f"System prompt:\n{self.system_prompt}")
```

### 测试不同提示词效果

```python
prompts = {
    "简洁": "简洁回答问题",
    "详细": "详细解释每个概念",
    "技术": "提供技术细节和代码"
}
```

## 常见问题

**Q: 提示词多长合适？**
A: 建议 500-1500 字。太短不够明确，太长可能影响性能。

**Q: 如何提高回答质量？**
A: 提供具体示例，明确期望的响应格式，设定清晰的边界。

**Q: 可以使用中文吗？**
A: 完全可以！使用您希望 AI 回复的语言。

**Q: 如何让 AI 更专业？**
A: 明确专业领域，提供行业术语，设定专业标准。

## 下一步

1. 查看 `docs/SYSTEM_PROMPT_GUIDE.md` 了解详细指南
2. 参考 `examples/custom_prompt_example.py` 查看更多示例
3. 复制 `system_prompt.txt.example` 开始配置

## 修改建议路径

1. 复制示例文件
2. 根据业务需求修改内容
3. 在 `run_all.py` 中加载使用
4. 测试效果并迭代优化
