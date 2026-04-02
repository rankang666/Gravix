#!/usr/bin/env python
# encoding: utf-8
"""
@Time: 2026/4/1
@Project: Gravix
@File: system_info.py
@Author: Claude
@Software: PyCharm
@Desc: System Information Skill Implementation
"""

import platform
import psutil
from app.skills.base import BaseSkill, SkillResult


class SystemInfoSkill(BaseSkill):
    """获取系统信息"""

    skill_id = "system_info"
    name = "System Information"
    version = "1.0.0"
    description = "Get system information such as CPU, memory, and disk usage"
    category = "system"
    timeout = 30

    parameters_schema = {
        "type": "object",
        "properties": {
            "info_type": {
                "type": "string",
                "enum": ["cpu", "memory", "disk", "all"],
                "description": "Type of system information to retrieve"
            }
        },
        "required": ["info_type"]
    }

    async def execute(self, info_type: str = 'all', **kwargs) -> SkillResult:
        """
        获取系统信息

        Args:
            info_type: 信息类型（cpu, memory, disk, all）

        Returns:
            SkillResult with system information
        """
        try:
            result = {}

            if info_type in ['cpu', 'all']:
                result['cpu'] = self._get_cpu_info()

            if info_type in ['memory', 'all']:
                result['memory'] = self._get_memory_info()

            if info_type in ['disk', 'all']:
                result['disk'] = self._get_disk_info()

            # 添加系统信息
            result['system'] = self._get_system_info()

            return SkillResult(
                success=True,
                data=result,
                metadata={'info_type': info_type}
            )

        except Exception as e:
            return SkillResult(
                success=False,
                data=None,
                error=f"Failed to get system info: {str(e)}"
            )

    def _get_cpu_info(self) -> dict:
        """获取CPU信息"""
        cpu_freq = psutil.cpu_freq()
        return {
            'percent': psutil.cpu_percent(interval=1),
            'count_physical': psutil.cpu_count(logical=False),
            'count_logical': psutil.cpu_count(logical=True),
            'freq_max': cpu_freq.max if cpu_freq else None
        }

    def _get_memory_info(self) -> dict:
        """获取内存信息"""
        mem = psutil.virtual_memory()
        return {
            'total': self._bytes_to_gb(mem.total),
            'available': self._bytes_to_gb(mem.available),
            'percent': mem.percent,
            'used': self._bytes_to_gb(mem.used)
        }

    def _get_disk_info(self) -> dict:
        """获取磁盘信息"""
        disk = psutil.disk_usage('/')
        return {
            'total': self._bytes_to_gb(disk.total),
            'used': self._bytes_to_gb(disk.used),
            'free': self._bytes_to_gb(disk.free),
            'percent': disk.percent
        }

    def _get_system_info(self) -> dict:
        """获取系统信息"""
        return {
            'platform': platform.system(),
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine(),
            'processor': platform.processor()
        }

    def _bytes_to_gb(self, bytes_value: int) -> float:
        """字节转换为GB"""
        return round(bytes_value / (1024 ** 3), 2)
