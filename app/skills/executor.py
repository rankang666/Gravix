#!/usr/bin/env python
# encoding: utf-8
"""
@Time: 2026/4/1
@Project: Gravix
@File: executor.py
@Author: Claude
@Software: PyCharm
@Desc: Skill Executor - Execute skills with proper error handling and validation
"""

import asyncio
import time
from typing import Dict, Any, List, Optional
from app.skills.registry import SkillRegistry
from app.skills.base import BaseSkill, SkillResult
from app.utils.logger import logger


class SkillExecutor:
    """
    Execute skills with proper error handling, validation, and timeout management

    The executor provides a unified interface for running skills, handling
    errors, validating parameters, and managing execution context.

    Example:
        ```python
        registry = SkillRegistry()
        executor = SkillExecutor(registry)

        result = await executor.execute(
            skill_id='system_info',
            parameters={'info_type': 'cpu'},
            context={'user_id': '123'}
        )
        ```
    """

    def __init__(self, registry: SkillRegistry):
        """
        Initialize the skill executor

        Args:
            registry: SkillRegistry instance for loading skills
        """
        self.registry = registry
        self._execution_stats: Dict[str, Dict[str, Any]] = {}

    async def execute(
        self,
        skill_id: str,
        parameters: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> SkillResult:
        """
        Execute a skill with given parameters

        Args:
            skill_id: Unique identifier for the skill
            parameters: Parameters to pass to the skill
            context: Optional execution context (user_id, request_id, etc.)

        Returns:
            SkillResult containing execution result
        """
        skill = self.registry.get_skill(skill_id)

        if not skill:
            return SkillResult(
                success=False,
                data=None,
                error=f"Skill not found: {skill_id}"
            )

        if not skill.enabled:
            return SkillResult(
                success=False,
                data=None,
                error=f"Skill is disabled: {skill_id}"
            )

        try:
            # Validate parameters
            if not await skill.validate(**parameters):
                return SkillResult(
                    success=False,
                    data=None,
                    error="Parameter validation failed"
                )

            # Execute with timeout
            start_time = time.time()
            result = await asyncio.wait_for(
                skill.execute(**parameters),
                timeout=skill.timeout
            )
            execution_time = time.time() - start_time

            # Update execution stats
            self._update_stats(skill_id, True, execution_time)

            # Add execution time to result if not already set
            if result.execution_time == 0:
                result.execution_time = execution_time

            # Add context to metadata
            if context:
                result.metadata.update({
                    'context': context,
                    'skill_id': skill_id,
                    'skill_name': skill.name
                })

            logger.info(
                f"Skill '{skill_id}' executed successfully "
                f"in {execution_time:.2f}s"
            )

            return result

        except asyncio.TimeoutError:
            self._update_stats(skill_id, False, 0)
            logger.error(f"Skill '{skill_id}' timed out after {skill.timeout}s")
            return SkillResult(
                success=False,
                data=None,
                error=f"Skill execution timed out after {skill.timeout}s"
            )

        except Exception as e:
            self._update_stats(skill_id, False, 0)
            logger.error(f"Error executing skill '{skill_id}': {e}", exc_info=True)
            return SkillResult(
                success=False,
                data=None,
                error=f"Skill execution error: {str(e)}"
            )

    async def execute_batch(
        self,
        executions: List[Dict[str, Any]]
    ) -> List[SkillResult]:
        """
        Execute multiple skills in parallel

        Args:
            executions: List of execution dictionaries, each containing:
                       - skill_id: str
                       - parameters: Dict
                       - context: Optional[Dict]

        Returns:
            List of SkillResult objects
        """
        tasks = [
            self.execute(
                exec_data['skill_id'],
                exec_data.get('parameters', {}),
                exec_data.get('context')
            )
            for exec_data in executions
        ]

        return await asyncio.gather(*tasks, return_exceptions=False)

    async def execute_with_retry(
        self,
        skill_id: str,
        parameters: Dict[str, Any],
        max_retries: int = 3,
        retry_delay: float = 1.0,
        context: Optional[Dict[str, Any]] = None
    ) -> SkillResult:
        """
        Execute a skill with automatic retry on failure

        Args:
            skill_id: Skill identifier
            parameters: Skill parameters
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds
            context: Optional execution context

        Returns:
            SkillResult from the last attempt
        """
        last_error = None

        for attempt in range(max_retries):
            result = await self.execute(skill_id, parameters, context)

            if result.success:
                if attempt > 0:
                    logger.info(
                        f"Skill '{skill_id}' succeeded on attempt {attempt + 1}"
                    )
                return result

            last_error = result.error

            if attempt < max_retries - 1:
                logger.warning(
                    f"Skill '{skill_id}' failed on attempt {attempt + 1}, "
                    f"retrying in {retry_delay}s..."
                )
                await asyncio.sleep(retry_delay)

        return SkillResult(
            success=False,
            data=None,
            error=f"Skill '{skill_id}' failed after {max_retries} attempts: {last_error}"
        )

    def _update_stats(self, skill_id: str, success: bool, execution_time: float):
        """
        Update execution statistics for a skill

        Args:
            skill_id: Skill identifier
            success: Whether execution was successful
            execution_time: Time taken to execute
        """
        if skill_id not in self._execution_stats:
            self._execution_stats[skill_id] = {
                'total_executions': 0,
                'successful_executions': 0,
                'failed_executions': 0,
                'total_execution_time': 0.0,
                'avg_execution_time': 0.0
            }

        stats = self._execution_stats[skill_id]
        stats['total_executions'] += 1

        if success:
            stats['successful_executions'] += 1
            stats['total_execution_time'] += execution_time
            stats['avg_execution_time'] = (
                stats['total_execution_time'] / stats['successful_executions']
            )
        else:
            stats['failed_executions'] += 1

    def get_stats(self, skill_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get execution statistics

        Args:
            skill_id: Specific skill ID or None for all skills

        Returns:
            Dictionary containing execution statistics
        """
        if skill_id:
            return self._execution_stats.get(skill_id, {})
        return self._execution_stats

    def clear_stats(self, skill_id: Optional[str] = None):
        """
        Clear execution statistics

        Args:
            skill_id: Specific skill ID or None for all skills
        """
        if skill_id:
            if skill_id in self._execution_stats:
                del self._execution_stats[skill_id]
        else:
            self._execution_stats.clear()
