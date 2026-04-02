#!/usr/bin/env python
# encoding: utf-8
"""
@Time: 2026/4/1
@Project: Gravix
@File: system_info.py
@Author: Claude
@Software: PyCharm
@Desc: System Information Skill
"""

import platform
import psutil
from app.skills.base import BaseSkill, SkillResult


class SystemInfoSkill(BaseSkill):
    """Get system information"""

    async def execute(self, info_type: str = 'all', **kwargs) -> SkillResult:
        """
        Get system information

        Args:
            info_type: Type of info (cpu, memory, disk, all)

        Returns:
            SkillResult with system information
        """
        try:
            result = {}

            if info_type in ['cpu', 'all']:
                result['cpu'] = {
                    'percent': psutil.cpu_percent(interval=1),
                    'count_physical': psutil.cpu_count(logical=False),
                    'count_logical': psutil.cpu_count(logical=True),
                    'freq_max': psutil.cpu_freq().max if psutil.cpu_freq() else None
                }

            if info_type in ['memory', 'all']:
                mem = psutil.virtual_memory()
                result['memory'] = {
                    'total': self._bytes_to_gb(mem.total),
                    'available': self._bytes_to_gb(mem.available),
                    'percent': mem.percent,
                    'used': self._bytes_to_gb(mem.used)
                }

            if info_type in ['disk', 'all']:
                disk = psutil.disk_usage('/')
                result['disk'] = {
                    'total': self._bytes_to_gb(disk.total),
                    'used': self._bytes_to_gb(disk.used),
                    'free': self._bytes_to_gb(disk.free),
                    'percent': disk.percent
                }

            # Add system info
            result['system'] = {
                'platform': platform.system(),
                'release': platform.release(),
                'version': platform.version(),
                'machine': platform.machine(),
                'processor': platform.processor()
            }

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

    def _bytes_to_gb(self, bytes_value: int) -> float:
        """Convert bytes to gigabytes"""
        return round(bytes_value / (1024 ** 3), 2)
