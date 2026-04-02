#!/usr/bin/env python
# encoding: utf-8
"""
@Time: 2026/4/1
@Project: Gravix
@File: funboost_task.py
@Author: Claude
@Software: PyCharm
@Desc: Funboost Task Executor Skill Implementation
"""

from app.skills.base import BaseSkill, SkillResult
from app.utils.logger import logger


class FunboostTaskSkill(BaseSkill):
    """通过Funboost队列系统执行任务"""

    skill_id = "funboost_task"
    name = "Funboost Task Executor"
    version = "1.0.0"
    description = "Execute funboost tasks asynchronously through the queue system"
    category = "task_execution"
    timeout = 300

    parameters_schema = {
        "type": "object",
        "properties": {
            "queue_name": {
                "type": "string",
                "description": "Name of the funboost queue to submit task to"
            },
            "task_params": {
                "type": "object",
                "description": "Parameters for the task"
            },
            "wait_for_result": {
                "type": "boolean",
                "description": "Whether to wait for task completion",
                "default": False
            }
        },
        "required": ["queue_name"]
    }

    async def execute(
        self,
        queue_name: str,
        task_params: dict = None,
        wait_for_result: bool = False,
        **kwargs
    ) -> SkillResult:
        """
        提交任务到Funboost队列

        Args:
            queue_name: Funboost队列名称
            task_params: 任务参数
            wait_for_result: 是否等待完成

        Returns:
            SkillResult with task submission info
        """
        try:
            # 导入publisher以避免循环依赖
            from app.publisher.submit import submit_hello

            # 使用现有的hello consumer作为示例
            # 生产环境中应动态加载consumers
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
