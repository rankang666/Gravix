#!/usr/bin/env python
# encoding: utf-8
"""
@Time: 2026/4/1
@Project: Gravix
@File: base.py
@Author: Claude
@Software: PyCharm
@Desc: Base classes for the Skills system
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class SkillResult:
    """
    Standard result object returned by all skills

    Attributes:
        success: Whether the skill execution was successful
        data: The result data returned by the skill
        error: Error message if execution failed
        metadata: Additional metadata about the execution
        execution_time: Time taken to execute the skill
    """
    success: bool
    data: Any
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    execution_time: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary"""
        return {
            'success': self.success,
            'data': self.data,
            'error': self.error,
            'metadata': self.metadata,
            'execution_time': self.execution_time
        }


class BaseSkill(ABC):
    """
    Base class for all skills

    All skills must inherit from this class and implement the execute() method.
    Skills are configured via JSON files and loaded dynamically by the SkillRegistry.

    Example:
        ```python
        class MySkill(BaseSkill):
            async def execute(self, **kwargs) -> SkillResult:
                # Your skill logic here
                return SkillResult(success=True, data="result")
        ```
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the skill with configuration

        Args:
            config: Skill configuration dictionary from JSON file
        """
        self.config = config
        self.skill_id = config.get('skill_id')
        self.name = config.get('name')
        self.description = config.get('description', '')
        self.version = config.get('version', '1.0.0')
        self.category = config.get('category', 'general')
        self.enabled = config.get('enabled', True)
        self.parameters_schema = config.get('parameters', {})
        self.timeout = config.get('timeout', 300)  # Default 5 minutes
        self.rate_limit = config.get('rate_limit', {})

    @abstractmethod
    async def execute(self, **kwargs) -> SkillResult:
        """
        Execute the skill with given parameters

        Args:
            **kwargs: Skill parameters as defined in the schema

        Returns:
            SkillResult: Result object containing success status, data, and optional error

        Raises:
            Exception: Skill-specific exceptions during execution
        """
        pass

    async def validate(self, **kwargs) -> bool:
        """
        Validate input parameters against the skill's schema

        Args:
            **kwargs: Parameters to validate

        Returns:
            bool: True if parameters are valid, False otherwise
        """
        # Basic validation - check required parameters
        if self.parameters_schema:
            required = self.parameters_schema.get('required', [])
            properties = self.parameters_schema.get('properties', {})

            for param in required:
                if param not in kwargs:
                    return False

                # Type validation
                param_schema = properties.get(param, {})
                expected_type = param_schema.get('type')
                if expected_type:
                    if not self._check_type(kwargs[param], expected_type):
                        return False

        return True

    def _check_type(self, value: Any, expected_type: str) -> bool:
        """
        Check if value matches expected type

        Args:
            value: Value to check
            expected_type: Expected type string

        Returns:
            bool: True if type matches
        """
        type_map = {
            'string': str,
            'integer': int,
            'number': (int, float),
            'boolean': bool,
            'array': list,
            'object': dict
        }

        expected_python_type = type_map.get(expected_type)
        if expected_python_type:
            return isinstance(value, expected_python_type)

        return True

    def get_info(self) -> Dict[str, Any]:
        """
        Get skill information

        Returns:
            Dict containing skill metadata
        """
        return {
            'skill_id': self.skill_id,
            'name': self.name,
            'description': self.description,
            'version': self.version,
            'category': self.category,
            'enabled': self.enabled,
            'parameters': self.parameters_schema,
            'timeout': self.timeout
        }

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(skill_id='{self.skill_id}', name='{self.name}')>"
