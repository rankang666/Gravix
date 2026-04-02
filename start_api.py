#!/usr/bin/env python
# encoding: utf-8
"""
@Time: 2026/4/1
@Project: Gravix
@File: start_api.py
@Author: Claude
@Software: PyCharm
@Desc: Start REST API Server
"""

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app.api.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
