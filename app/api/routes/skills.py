#!/usr/bin/env python
# encoding: utf-8
"""
@Time: 2026/4/1
@Project: Gravix
@File: skills.py
@Author: Claude
@Software: PyCharm
@Desc: Skills API Routes
"""

from fastapi import APIRouter, HTTPException
from typing import List
from app.schemas.skill import SkillInfo, SkillExecutionRequest, SkillExecutionResponse
from app.skills.registry import SkillRegistry
from app.skills.executor import SkillExecutor
from app.utils.logger import logger

router = APIRouter()

# Global instances (initialized on module import)
registry = SkillRegistry()
executor = SkillExecutor(registry)

logger.info(f"Loaded {len(registry)} skills on API startup")


@router.get("/", response_model=List[SkillInfo])
async def list_skills(include_disabled: bool = False):
    """
    List all available skills

    Args:
        include_disabled: Whether to include disabled skills

    Returns:
        List of skill information
    """
    try:
        skills = registry.list_skills(include_disabled=include_disabled)
        return skills
    except Exception as e:
        logger.error(f"Error listing skills: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{skill_id}", response_model=SkillInfo)
async def get_skill(skill_id: str):
    """
    Get information about a specific skill

    Args:
        skill_id: Skill identifier

    Returns:
        Skill information
    """
    skill = registry.get_skill(skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail=f"Skill not found: {skill_id}")
    return skill.get_info()


@router.post("/execute", response_model=SkillExecutionResponse)
async def execute_skill(request: SkillExecutionRequest):
    """
    Execute a skill

    Args:
        request: Skill execution request

    Returns:
        Skill execution result
    """
    try:
        result = await executor.execute(
            skill_id=request.skill_id,
            parameters=request.parameters,
            context=request.context
        )

        return SkillExecutionResponse(
            success=result.success,
            data=result.data,
            error=result.error
        )
    except Exception as e:
        logger.error(f"Error executing skill {request.skill_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{skill_id}/enable", response_model=dict)
async def enable_skill(skill_id: str):
    """
    Enable a skill

    Args:
        skill_id: Skill identifier

    Returns:
        Success message
    """
    success = registry.enable_skill(skill_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Skill not found: {skill_id}")
    return {"message": f"Skill '{skill_id}' enabled"}


@router.get("/{skill_id}/disable", response_model=dict)
async def disable_skill(skill_id: str):
    """
    Disable a skill

    Args:
        skill_id: Skill identifier

    Returns:
        Success message
    """
    success = registry.disable_skill(skill_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Skill not found: {skill_id}")
    return {"message": f"Skill '{skill_id}' disabled"}


@router.post("/reload", response_model=dict)
async def reload_skills():
    """
    Reload all skill configurations

    Returns:
        Success message with number of skills loaded
    """
    try:
        registry.reload_skills()
        count = registry.get_skill_count()
        return {"message": f"Reloaded {count} skills"}
    except Exception as e:
        logger.error(f"Error reloading skills: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/execution")
async def get_execution_stats(skill_id: str = None):
    """
    Get execution statistics

    Args:
        skill_id: Optional skill ID to get stats for specific skill

    Returns:
        Execution statistics
    """
    try:
        stats = executor.get_stats(skill_id)
        return stats
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))
