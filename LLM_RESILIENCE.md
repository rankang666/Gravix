# LLM 稳定性优化指南

本文档说明 Gravix 如何确保 LLM 服务的高可用性和稳定性。

## 🎯 优化特性

### 1. 自动重试机制
- **指数退避重试** - 失败后自动重试，延迟逐渐增加
- **可配置重试次数** - 默认最多重试3次
- **智能重试** - 只对可重试的错误进行重试

### 2. 多提供商自动切换
- **Fallback API Keys** - 主API失败时自动切换到备用API
- **跨提供商切换** - Claude失败时自动切换到OpenAI
- **无感知切换** - 用户无需手动干预

### 3. 请求限流
- **自动限流** - 防止请求过于频繁触发限流
- **可配置速率** - 默认每秒最多2个请求
- **队列管理** - 自动排队处理请求

### 4. 优雅降级
- **友好错误提示** - LLM不可用时提供清晰的说明
- **功能保留** - LLM故障时仍可使用Skills和MCP
- **快速恢复** - 服务恢复后自动响应

## 🚀 快速配置

### 方案1：添加备用 API Key（推荐）

在 `.env` 文件中添加备用API：

```bash
# 主API
ANTHROPIC_API_KEY=sk-ant-api03-primary-key

# 备用API（可选）
ANTHROPIC_API_KEY_FALLBACK=sk-ant-api03-backup-key
```

### 方案2：使用多个提供商

配置多个提供商作为备用：

```bash
# Claude作为主提供商
ANTHROPIC_API_KEY=sk-ant-api03-xxxxx

# OpenAI作为备用
OPENAI_API_KEY=sk-xxxxx
```

系统会自动使用：
1. 优先使用Claude
2. Claude失败时切换到OpenAI
3. 自动重试和恢复

### 方案3：调整重试和限流参数

在 `.env` 文件中添加：

```bash
# 最大重试次数（默认3）
LLM_MAX_RETRIES=3

# 重试延迟秒数（默认1.0）
LLM_RETRY_DELAY=1.0

# 请求限流秒数（默认0.5）
LLM_RATE_LIMIT=0.5
```

## 📊 工作原理

### 正常流程

```
用户请求
    ↓
获取限流令牌
    ↓
尝试主API
    ↓
成功 → 返回结果
```

### 故障切换流程

```
用户请求
    ↓
获取限流令牌
    ↓
尝试主API (Claude)
    ↓
失败 (403/Timeout/5xx)
    ↓
等待1秒（指数退避）
    ↓
重试主API
    ↓
仍然失败
    ↓
切换到备用API (OpenAI)
    ↓
成功 → 返回结果
```

### 完全失败流程

```
用户请求
    ↓
尝试所有API
    ↓
全部失败
    ↓
返回友好错误提示
    ↓
用户仍可使用Skills/MCP
```

## 🔧 高级配置

### 自定义Resilient Provider

```python
from app.llm.resilient import create_resilient_provider

config = {
    'providers': [
        {
            'type': 'claude',
            'api_key': 'sk-ant-xxx',
            'model': 'claude-3-5-sonnet-20241022'
        },
        {
            'type': 'openai',
            'api_key': 'sk-xxx',
            'model': 'gpt-4o'
        }
    ],
    'max_retries': 5,
    'retry_delay': 2.0,
    'rate_limit': 0.3
}

provider = create_resilient_provider(config)
```

### 禁用Resilient模式

如果只想使用单一API：

```python
service = LLMService(
    provider='claude',
    resilient=False  # 禁用自动切换
)
```

## 📈 监控和日志

### 重试日志

```
2026-04-04 20:00:00 | INFO | Attempting ClaudeProvider...
2026-04-04 20:00:01 | WARNING | ❌ ClaudeProvider failed: 403
2026-04-04 20:00:01 | INFO | Retry 1/3 for ClaudeProvider after 1.0s
2026-04-04 20:00:03 | WARNING | ❌ ClaudeProvider failed: 403
2026-04-04 20:00:03 | INFO | Provider ClaudeProvider exhausted, trying next...
2026-04-04 20:00:03 | INFO | Attempting OpenAIProvider...
2026-04-04 20:00:04 | INFO | ✅ OpenAIProvider succeeded
```

### 限流日志

```
2026-04-04 20:00:00 | DEBUG | Rate limit: waiting 0.3s
2026-04-04 20:00:01 | INFO | Attempting ClaudeProvider...
```

## 💡 最佳实践

### 1. 使用官方API
- ✅ Anthropic官方API最稳定
- ✅ OpenAI官方API作为备用
- ❌ 避免使用不稳定的代理服务

### 2. 合理设置限流
- 默认0.5秒适合大多数场景
- 如果频繁出现429，增加到1.0秒
- 如果API配额充足，可降低到0.3秒

### 3. 配置多个备用
- 至少配置2个不同提供商
- 确保备用API有效可用
- 定期检查API配额

### 4. 监控日志
- 定期查看错误日志
- 关注重试和切换频率
- 及时更新失效的API

## 🛠️ 故障排查

### 问题：频繁切换到备用API

**可能原因：**
- 主API配额用完
- 主API被限流
- 主API密钥失效

**解决方案：**
1. 检查主API配额
2. 调整限流参数
3. 更新API密钥

### 问题：所有API都失败

**可能原因：**
- 网络问题
- API服务故障
- 配置错误

**解决方案：**
1. 检查网络连接
2. 验证API密钥
3. 查看错误日志

### 问题：响应很慢

**可能原因：**
- 重试次数过多
- 限流设置过严
- 网络延迟

**解决方案：**
1. 减少重试次数
2. 调整限流参数
3. 使用更快的API

## 📚 相关文档

- [LLM_SETUP_GUIDE.md](LLM_SETUP_GUIDE.md) - LLM配置指南
- [README.md](README.md) - 项目总览
- [CHANGELOG.md](CHANGELOG.md) - 版本历史

## 🆘 获取帮助

如果遇到问题：
1. 查看日志文件：`logs/app.log`
2. 检查API配置：`.env` 文件
3. 测试API连接：`python tests/test_llm_chat.py`
4. 查看错误详情
