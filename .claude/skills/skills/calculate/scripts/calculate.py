#!/usr/bin/env python
# encoding: utf-8
"""
@Time: 2026/4/1
@Project: Gravix
@File: calculate.py
@Author: Claude
@Software: PyCharm
@Desc: Calculator Skill Implementation
"""

import re
from app.skills.base import BaseSkill, SkillResult


class CalculateSkill(BaseSkill):
    """执行数学计算"""

    skill_id = "calculate"
    name = "Calculator"
    version = "1.0.0"
    description = "Perform basic mathematical calculations"
    category = "utility"
    timeout = 10

    parameters_schema = {
        "type": "object",
        "properties": {
            "expression": {
                "type": "string",
                "description": "Mathematical expression to evaluate (e.g., '2 + 2')"
            }
        },
        "required": ["expression"]
    }

    async def execute(self, expression: str, **kwargs) -> SkillResult:
        """
        计算数学表达式

        Args:
            expression: 数学表达式（例如："2 + 2"）

        Returns:
            SkillResult with calculation result
        """
        try:
            # 验证表达式安全性
            if not self._is_safe_expression(expression):
                return SkillResult(
                    success=False,
                    data=None,
                    error="Expression contains unsafe characters"
                )

            # 计算表达式
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
        检查表达式是否只包含安全字符

        Args:
            expr: 要检查的表达式

        Returns:
            True if safe
        """
        # 只允许数字、运算符、括号和空格
        pattern = r'^[\d+\-*/().\s]+$'
        return bool(re.match(pattern, expr))
