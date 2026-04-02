#!/usr/bin/env python
# encoding: utf-8
"""
@Time: 2026/4/1
@Project: Gravix
@File: skills_bridge.py
@Author: Claude
@Software: PyCharm
@Desc: Bridge between chat and Skills system
"""

from app.skills.executor import SkillExecutor
from app.utils.logger import logger


class SkillsBridge:
    """
    Bridge between chat interface and Skills system

    Allows the chat server to execute skills in response to user messages.

    Example:
        ```python
        executor = SkillExecutor(registry)
        bridge = SkillsBridge(executor)

        result = await bridge.execute('echo', {'message': 'Hello'})
        ```
    """

    def __init__(self, executor: SkillExecutor):
        """
        Initialize skills bridge

        Args:
            executor: SkillExecutor instance
        """
        self.executor = executor

    async def execute(
        self,
        skill_id: str,
        parameters: dict,
        context: dict = None
    ):
        """
        Execute a skill

        Args:
            skill_id: Skill identifier
            parameters: Skill parameters
            context: Optional execution context

        Returns:
            SkillResult object
        """
        logger.info(f"Executing skill via bridge: {skill_id}")
        return await self.executor.execute(
            skill_id=skill_id,
            parameters=parameters,
            context=context or {}
        )

    async def list_skills(self) -> list:
        """
        List available skills

        Returns:
            List of skill information dictionaries
        """
        return self.executor.registry.list_skills()

    async def get_skill_info(self, skill_id: str) -> dict:
        """
        Get information about a specific skill

        Args:
            skill_id: Skill identifier

        Returns:
            Skill information or None if not found
        """
        skill = self.executor.registry.get_skill(skill_id)
        if skill:
            return skill.get_info()
        return None
