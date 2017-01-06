#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
********************************************
*运行此文件，可直接调用scrapy中名字为mysina的爬虫*
********************************************
"""
from scrapy.cmdline import execute
import os

# 跳转到爬虫项目目录
os.chdir('/home/spider_scrap/ntes')

try:
    execute(['scrapy', 'crawl', 'ntes', '--logfile=ntes.log'])
    #execute(['scrapy', 'crawl', 'ntes'])
finally:
    print "<<<<<<<<<<Mission Complete>>>>>>>>>>"
