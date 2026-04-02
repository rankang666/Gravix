# Changelog

All notable changes to the Gravix project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-04-02

### Added

#### 核心功能
- **Skills系统** - 可配置的技能调用机制
  - 4个内置技能：calculate, echo, system_info, funboost_task
  - 自定义技能支持
  - 异步执行引擎
- **MCP协议集成** - Model Context Protocol支持
  - DataWorks MCP服务器（186个工具）
  - MCP客户端实现
  - 多服务器管理
  - stdio和SSE传输适配器
- **LLM集成** - 大语言模型对话功能
  - Claude API支持
  - OpenAI API支持
  - 工具调用自动识别
  - 流式响应支持
- **WebSocket聊天服务器** - 实时对话界面
  - 会话管理
  - 多客户端支持
  - 自动重连机制
- **Web UI** - 用户友好的聊天界面
  - 现代化设计
  - 快捷按钮
  - Markdown渲染
  - 响应式布局
- **REST API** - FastAPI构建的管理接口
  - Swagger文档
  - 健康检查端点
  - Skills执行API
  - MCP工具调用API

#### 配置和部署
- **环境变量配置** - .env文件支持
- **配置模板** - .env.example
- **Git忽略规则** - .gitignore
- **依赖管理** - requirements.txt

#### 文档
- **README.md** - 项目介绍和快速开始
- **GRAVIX_GUIDE.md** - 完整使用指南
- **LLM_SETUP_GUIDE.md** - LLM配置指南
- **DATAWORKS_MCP_INTEGRATION.md** - DataWorks集成文档
- **CREATING_SKILLS.md** - 创建自定义技能指南
- **CHANGELOG.md** - 版本更新记录

#### 测试
- **测试套件** - 14个测试脚本
  - Skills系统测试
  - MCP集成测试
  - LLM对话测试
  - WebSocket聊天测试

### Changed

#### 项目结构优化
- **目录重组** - 测试文件移至tests/
- **文件归档** - 调试脚本移至archive/
- **__init__.py** - 添加缺失的__init__.py文件

#### 代码改进
- **异步优化** - 修复协程未await警告
- **错误处理** - 改进异常处理机制
- **日志系统** - 结构化日志输出

### Fixed

#### Bug修复
- **MCP工具调用参数顺序** - 修复call_tool参数顺序错误
  - app/chat/tool_calling.py
  - app/chat/server.py
- **环境变量加载** - 确保 run_all.py 正确加载.env
- **Region映射** - 修复DataWorks Region配置问题

#### 安全性
- **敏感信息保护** - 从Git历史中移除API密钥
- **.gitignore** - 添加.env到忽略列表
- **配置模板** - 创建安全的.env.example

### Performance

#### 性能优化
- **异步处理** - 全面采用async/await
- **连接复用** - WebSocket和HTTP连接池
- **缓存机制** - MCP工具列表缓存

## [0.2.0] - 2026-03-15

### Added
- Funboost任务队列集成
- REST API基础框架
- Skills注册系统

### Changed
- 重构Skills执行器
- 优化配置加载机制

## [0.1.0] - 2026-03-01

### Added
- 初始项目结构
- 基础Skills系统
- 简单的HTTP API

---

## 版本说明

### 版本格式：MAJOR.MINOR.PATCH

- **MAJOR** - 不兼容的API变更
- **MINOR** - 向后兼容的功能新增
- **PATCH** - 向后兼容的问题修复

### 变更类型

- **Added** - 新增功能
- **Changed** - 功能变更
- **Deprecated** - 即将废弃的功能
- **Removed** - 已移除的功能
- **Fixed** - 问题修复
- **Security** - 安全性改进

---

## 未来计划

### v1.1.0 (计划中)
- [ ] Docker支持
- [ ] 性能监控
- [ ] 更多LLM提供商
- [ ] Web UI改进

### v1.2.0 (计划中)
- [ ] 插件系统
- [ ] 工作流引擎
- [ ] 更多MCP服务器
- [ ] 移动端支持

### v2.0.0 (远期)
- [ ] 多租户支持
- [ ] 分布式部署
- [ ] 企业级功能
- [ ] 云原生架构
