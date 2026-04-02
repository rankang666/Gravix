#!/usr/bin/env python
# encoding: utf-8
"""
@Time: 2026/4/1
@Project: Gravix
@File: test_skills.py
@Author: Claude
@Software: PyCharm
@Desc: Test script for Skills system
"""

import asyncio
from app.skills.registry import SkillRegistry
from app.skills.executor import SkillExecutor
from app.utils.logger import logger


async def test_skills():
    """Test the Skills system"""

    logger.info("=" * 60)
    logger.info("Testing Gravix Skills System")
    logger.info("=" * 60)

    # Initialize registry and executor
    registry = SkillRegistry()
    executor = SkillExecutor(registry)

    # Test 1: List all skills
    logger.info("\n[Test 1] Listing all available skills...")
    skills = registry.list_skills()
    logger.info(f"Found {len(skills)} skills:")
    for skill in skills:
        status = "enabled" if skill['enabled'] else "disabled"
        logger.info(f"  - {skill['skill_id']} ({skill['name']}) [{status}]")

    # Test 2: Test echo skill
    logger.info("\n[Test 2] Testing 'echo' skill...")
    result = await executor.execute(
        skill_id='echo',
        parameters={'message': 'Hello, Gravix Skills!'}
    )
    logger.info(f"Result: {result.to_dict()}")

    # Test 3: Test calculate skill
    logger.info("\n[Test 3] Testing 'calculate' skill...")
    result = await executor.execute(
        skill_id='calculate',
        parameters={'expression': '2 + 2 * 3'}
    )
    logger.info(f"Result: {result.to_dict()}")

    # Test 4: Test system_info skill (CPU)
    logger.info("\n[Test 4] Testing 'system_info' skill (CPU)...")
    result = await executor.execute(
        skill_id='system_info',
        parameters={'info_type': 'cpu'}
    )
    if result.success:
        logger.info(f"CPU Usage: {result.data['cpu']['percent']}%")
        logger.info(f"CPU Cores: {result.data['cpu']['count_logical']}")
    else:
        logger.error(f"Error: {result.error}")

    # Test 5: Test system_info skill (Memory)
    logger.info("\n[Test 5] Testing 'system_info' skill (Memory)...")
    result = await executor.execute(
        skill_id='system_info',
        parameters={'info_type': 'memory'}
    )
    if result.success:
        logger.info(f"Memory Usage: {result.data['memory']['percent']}%")
        logger.info(f"Memory Available: {result.data['memory']['available']} GB")
    else:
        logger.error(f"Error: {result.error}")

    # Test 6: Test funboost task skill
    logger.info("\n[Test 6] Testing 'funboost_task' skill...")
    result = await executor.execute(
        skill_id='funboost_task',
        parameters={
            'queue_name': 'hello_queue',
            'task_params': {'name': 'Skills Test'}
        }
    )
    logger.info(f"Result: {result.to_dict()}")

    # Test 7: Test batch execution
    logger.info("\n[Test 7] Testing batch execution...")
    batch_results = await executor.execute_batch([
        {'skill_id': 'echo', 'parameters': {'message': 'Batch 1'}},
        {'skill_id': 'echo', 'parameters': {'message': 'Batch 2'}},
        {'skill_id': 'calculate', 'parameters': {'expression': '10 * 5'}}
    ])
    logger.info(f"Batch execution completed: {len(batch_results)} results")
    for i, result in enumerate(batch_results):
        logger.info(f"  Result {i+1}: success={result.success}")

    # Test 8: Test error handling (invalid skill)
    logger.info("\n[Test 8] Testing error handling (invalid skill)...")
    result = await executor.execute(
        skill_id='nonexistent_skill',
        parameters={}
    )
    logger.info(f"Expected error: {result.error}")

    # Test 9: Show execution stats
    logger.info("\n[Test 9] Execution statistics...")
    stats = executor.get_stats()
    for skill_id, stat in stats.items():
        logger.info(f"  {skill_id}:")
        logger.info(f"    Total: {stat['total_executions']}")
        logger.info(f"    Success: {stat['successful_executions']}")
        logger.info(f"    Failed: {stat['failed_executions']}")
        if stat['avg_execution_time'] > 0:
            logger.info(f"    Avg Time: {stat['avg_execution_time']:.2f}s")

    logger.info("\n" + "=" * 60)
    logger.info("Skills System Test Complete!")
    logger.info("=" * 60)


if __name__ == '__main__':
    asyncio.run(test_skills())
