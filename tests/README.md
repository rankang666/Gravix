# 测试文件说明

本目录包含Gravix项目的测试脚本。

## 运行测试

```bash
# 运行单个测试
python tests/test_skills.py

# 运行所有测试
pytest tests/

# 运行特定测试
pytest tests/test_mcp.py -v
```

## 测试文件列表

- `test_skills.py` - Skills系统测试
- `test_mcp.py` - MCP集成测试
- `test_llm_chat.py` - LLM聊天测试
- `test_websocket_chat.py` - WebSocket聊天测试
- `test_mcp_tool.py` - MCP工具调用测试
- 等等...
