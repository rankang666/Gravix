#!/usr/bin/env python
# encoding: utf-8
"""
@Time: 2026/4/1
@Project: Gravix
@File: skill.py
@Author: Claude
@Software: PyCharm
@Desc: Skill-related data schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any


class SkillInfo(BaseModel):
    """Skill information model"""
    skill_id: str
    name: str
    description: str
    version: str = "1.0.0"
    category: str = "general"
    enabled: bool = True


class SkillExecutionRequest(BaseModel):
    """Skill execution request model"""
    skill_id: str = Field(..., description="Skill identifier to execute")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Skill parameters")
    context: Optional[Dict[str, Any]] = Field(None, description="Execution context")


class SkillExecutionResponse(BaseModel):
    """Skill execution response model"""
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
