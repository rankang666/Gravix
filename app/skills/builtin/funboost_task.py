#!/usr/bin/env python
# encoding: utf-8
"""
@Time: 2026/4/1
@Project: Gravix
@File: funboost_task.py
@Author: Claude
@Software: PyCharm
@Desc: Funboost Task Executor Skill
"""

from app.skills.base import BaseSkill, SkillResult
from app.utils.logger import logger


class FunboostTaskSkill(BaseSkill):
    """Execute funboost tasks through the queue system"""

    async def execute(
        self,
        queue_name: str,
        task_params: dict = None,
        wait_for_result: bool = False,
        **kwargs
    ) -> SkillResult:
        """
        Submit a task to a funboost queue

        Args:
            queue_name: Name of the funboost queue
            task_params: Parameters for the task
            wait_for_result: Whether to wait for completion

        Returns:
            SkillResult with task submission info
        """
        try:
            # Import here to avoid circular dependencies
            from app.publisher.submit import submit_hello

            # For now, we use the existing hello consumer as an example
            # In production, this would dynamically load consumers
            if queue_name == 'hello_queue':
                name = task_params.get('name', 'Gravix') if task_params else 'Gravix'
                submit_hello(name)

                return SkillResult(
                    success=True,
                    data={
                        'queue_name': queue_name,
                        'task_submitted': True,
                        'message': f'Task submitted to {queue_name} with name={name}'
                    },
                    metadata={
                        'queue': queue_name,
                        'wait_for_result': wait_for_result
                    }
                )
            else:
                return SkillResult(
                    success=False,
                    data=None,
                    error=f"Queue '{queue_name}' not found. Available queues: hello_queue"
                )

        except Exception as e:
            logger.error(f"Failed to submit funboost task: {e}")
            return SkillResult(
                success=False,
                data=None,
                error=f"Failed to submit task: {str(e)}"
            )
