#!/usr/bin/env python
# encoding: utf-8
"""
@Time: 2026/4/2
@Project: Gravix
@File: demo_dataworks_mcp.py
@Author: Jerry
@Software: PyCharm
@Desc: DataWorks MCP Demo - 演示如何使用DataWorks工具
"""

import asyncio
import sys
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from app.mcp.manager import MCPManager
from app.utils.logger import logger


async def demo_dataworks_tools():
    """演示DataWorks MCP工具的使用"""

    logger.info("=" * 80)
    logger.info("DataWorks MCP 工具演示")
    logger.info("=" * 80)

    # 初始化MCP Manager
    manager = MCPManager()

    try:
        # 连接到MCP服务器
        logger.info("\n📡 正在连接到DataWorks MCP...")
        await manager.initialize()

        servers = manager.get_connected_servers()
        if not servers:
            logger.error("❌ 没有连接到任何MCP服务器")
            return

        logger.info(f"✅ 已连接到 {len(servers)} 个MCP服务器: {', '.join(servers)}")

        # 演示1: 列出所有可用工具
        logger.info("\n" + "=" * 80)
        logger.info("📋 演示1: 列出DataWorks可用工具")
        logger.info("=" * 80)

        all_tools = await manager.list_all_tools()

        for server_name, tools in all_tools.items():
            logger.info(f"\n🔧 {server_name} - 共 {len(tools)} 个工具:")
            logger.info("\n工具分类:")

            # 按功能分类
            categories = {
                '项目': ['ListProjects', 'GetProject', 'ListProjectMembers'],
                '数据库': ['ListDatabases', 'GetDatabase', 'ListSchemas'],
                '表': ['ListTables', 'GetTable', 'ListColumns', 'GetColumn'],
                '任务': ['ListTasks', 'GetTask', 'ListTaskInstances', 'GetTaskInstance'],
                '工作流': ['ListWorkflows', 'GetWorkflow', 'CreateWorkflowDefinition'],
            }

            for category, keywords in categories.items():
                matching = [t for t in tools if any(k in t.get('name', '') for k in keywords)]
                if matching:
                    logger.info(f"\n  {category}相关 ({len(matching)}个):")
                    for tool in matching[:3]:
                        logger.info(f"    - {tool.get('name')}: {tool.get('description', 'N/A')[:50]}")

        # 演示2: 调用ListProjects工具
        logger.info("\n" + "=" * 80)
        logger.info("🏢 演示2: 调用ListProjects工具 - 获取项目列表")
        logger.info("=" * 80)

        try:
            result = await manager.call_tool("dataworks", "ListProjects", {})

            if result and 'content' in result:
                content = result['content'][0].get('text', 'No data')
                logger.info(f"\n📊 项目列表结果:")
                logger.info(f"{content[:500]}...")  # 只显示前500字符
        except Exception as e:
            logger.warning(f"⚠️  调用ListProjects失败: {e}")
            logger.info("💡 提示: 需要配置DataWorks认证信息才能调用API")

        # 演示3: 显示工具参数schema
        logger.info("\n" + "=" * 80)
        logger.info("📝 演示3: 查看ListTables工具的参数要求")
        logger.info("=" * 80)

        try:
            tools = await manager.list_tools("dataworks")
            list_tables_tool = next((t for t in tools if t.get('name') == 'ListTables'), None)

            if list_tables_tool:
                logger.info(f"\n工具名称: {list_tables_tool.get('name')}")
                logger.info(f"描述: {list_tables_tool.get('description')}")
                logger.info(f"参数结构:")
                logger.info(f"{json.dumps(list_tables_tool.get('inputSchema', {}), indent=2, ensure_ascii=False)}")
        except Exception as e:
            logger.error(f"❌ 获取工具信息失败: {e}")

        # 演示4: 展示如何构建调用
        logger.info("\n" + "=" * 80)
        logger.info("💡 演示4: 如何调用DataWorks工具的示例代码")
        logger.info("=" * 80)

        example_code = '''
# Python代码示例
from app.mcp.manager import MCPManager

manager = MCPManager()
await manager.initialize()

# 示例1: 列出所有项目
projects = await manager.call_tool("dataworks", "ListProjects", {})

# 示例2: 列出指定项目的表
tables = await manager.call_tool("dataworks", "ListTables", {
    "projectName": "your_project_name"
})

# 示例3: 获取表详情
table_info = await manager.call_tool("dataworks", "GetTable", {
    "projectName": "your_project_name",
    "tableName": "your_table_name"
})

# 示例4: 列出任务实例
tasks = await manager.call_tool("dataworks", "ListTaskInstances", {
    "projectName": "your_project_name"
})
        '''

        logger.info(f"\n{example_code}")

        logger.info("\n" + "=" * 80)
        logger.info("✅ 演示完成!")
        logger.info("=" * 80)

        logger.info("\n📚 相关文档:")
        logger.info("  - DATAWORKS_MCP_INTEGRATION.md - DataWorks MCP集成文档")
        logger.info("  - GRAVIX_GUIDE.md - Gravix使用指南")
        logger.info("  - test_mcp.py - MCP测试脚本")

        logger.info("\n🔗 DataWorks API文档:")
        logger.info("  https://help.aliyun.com/document_detail/175300.html")

    except Exception as e:
        logger.error(f"❌ 演示过程中出错: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # 清理
        await manager.shutdown()
        logger.info("\n👋 MCP连接已关闭")


if __name__ == '__main__':
    try:
        asyncio.run(demo_dataworks_tools())
    except KeyboardInterrupt:
        logger.info("\n演示已中断")
