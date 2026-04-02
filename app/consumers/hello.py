#!/usr/bin/env python
# encoding: utf-8
'''
@Time: 2026/1/30 下午5:25
@Project: Gravix
@File: hello.py
@Author: ran
@Software: pycharm
@Desc:
'''
from funboost import boost
from app.utils.logger import logger


@boost(
    queue_name='hello_queue',
    is_show_message_get_from_broker=True
)
def hello_consumer(name: str):
    logger.info(f"Hello, {name}")
    return f"hello {name}"
