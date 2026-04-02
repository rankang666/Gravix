#!/usr/bin/env python
# encoding: utf-8
"""
@Time: 2026/4/1
@Project: Gravix
@File: echo.py
@Author: Claude
@Software: PyCharm
@Desc: Echo Skill - Simple echo for testing
"""

from app.skills.base import BaseSkill, SkillResult


class EchoSkill(BaseSkill):
    """Simple skill that echoes back the input message"""

    async def execute(self, message: str, **kwargs) -> SkillResult:
        """
        Echo the input message

        Args:
            message: The message to echo back

        Returns:
            SkillResult with the echoed message
        """
        return SkillResult(
            success=True,
            data={
                'echo': message,
                'timestamp': self._get_timestamp()
            },
            metadata={
                'skill': 'echo',
                'message_length': len(message)
            }
        )

    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.utcnow().isoformat()
