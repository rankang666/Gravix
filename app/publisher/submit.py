#!/usr/bin/env python
# encoding: utf-8
'''
@Time: 2026/1/30 下午5:26
@Project: Gravix
@File: submit.py
@Author: ran
@Software: pycharm
@Desc:
'''
from app.consumers.hello import hello_consumer


def submit_hello(name: str):
    """
    所有外部触发，只能走 publisher
    """
    hello_consumer.push(name)
