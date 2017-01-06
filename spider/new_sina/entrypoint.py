#! /usr/bin/env python
# coding: utf-8
"""
**************************************************
*运行此文件，可直接调用scrapy中名字为mysina的爬虫*
*需要跳转到scrapy项目目录下才能运行爬虫          *
**************************************************
"""
from scrapy.cmdline import execute
import os

# 跳转到爬虫项目目录
os.chdir('/home/spider_scrap/new_sina')

try:
    execute(['scrapy', 'crawl', 'mysina', '--logfile=sina.log'])
finally:
    print "<------------Scrap Finish------------>"
