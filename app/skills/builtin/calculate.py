#!/usr/bin/env python
# encoding: utf-8
"""
@Time: 2026/4/1
@Project: Gravix
@File: calculate.py
@Author: Claude
@Software: PyCharm
@Desc: Calculator Skill
"""

import re
from app.skills.base import BaseSkill, SkillResult


class CalculateSkill(BaseSkill):
    """Perform mathematical calculations"""

    async def execute(self, expression: str, **kwargs) -> SkillResult:
        """
        Evaluate a mathematical expression

        Args:
            expression: Mathematical expression (e.g., "2 + 2")

        Returns:
            SkillResult with calculation result
        """
        try:
            # Sanitize the expression to only allow safe characters
            if not self._is_safe_expression(expression):
                return SkillResult(
                    success=False,
                    data=None,
                    error="Expression contains unsafe characters"
                )

            # Evaluate the expression
            result = eval(expression, {"__builtins__": {}}, {})

            return SkillResult(
                success=True,
                data={
                    'expression': expression,
                    'result': result,
                    'type': type(result).__name__
                },
                metadata={
                    'calculator': 'basic'
                }
            )

        except Exception as e:
            return SkillResult(
                success=False,
                data=None,
                error=f"Calculation error: {str(e)}"
            )

    def _is_safe_expression(self, expr: str) -> bool:
        """
        Check if expression contains only safe characters

        Args:
            expr: Expression to check

        Returns:
            True if safe
        """
        # Only allow digits, operators, parentheses, and whitespace
        pattern = r'^[\d+\-*/().\s]+$'
        return bool(re.match(pattern, expr))
