#!/usr/bin/env python
# encoding: utf-8
"""
@Time: 2026/4/1
@Project: Gravix
@File: echo.py
@Author: Claude
@Software: PyCharm
@Desc: Echo Skill Implementation
"""

from app.skills.base import BaseSkill, SkillResult
from datetime import datetime


class EchoSkill(BaseSkill):
    """简单技能，回显用户输入的消息"""

    # 技能元数据
    skill_id = "echo"
    name = "Echo Skill"
    version = "1.0.0"
    description = "Echo back the input message (useful for testing)"
    category = "utility"
    timeout = 10

    # 输入参数Schema (JSON Schema格式)
    parameters_schema = {
        "type": "object",
        "properties": {
            "message": {
                "type": "string",
                "description": "The message to echo back"
            }
        },
        "required": ["message"]
    }

    async def execute(self, message: str, **kwargs) -> SkillResult:
        """
        回显输入消息

        Args:
            message: 要回显的消息

        Returns:
            SkillResult with the echoed message
        """
        return SkillResult(
            success=True,
            data={
                'echo': message,
                'timestamp': datetime.utcnow().isoformat()
            },
            metadata={
                'skill': 'echo',
                'message_length': len(message)
            }
        )
