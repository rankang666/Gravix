#!/usr/bin/env python
# encoding: utf-8
"""
Skills Module - Gravix Extension System

This module provides a configurable, extensible skills system similar to
Claude's function calling mechanism. Skills can be defined via JSON
configuration files and executed through the SkillExecutor.
"""

from app.skills.base import BaseSkill, SkillResult
from app.skills.registry import SkillRegistry
from app.skills.executor import SkillExecutor

__all__ = ['BaseSkill', 'SkillResult', 'SkillRegistry', 'SkillExecutor']
