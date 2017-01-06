#! /usr/bin/env python
# coding: utf-8

from scrapy.cmdline import execute
import os

# 跳转到爬虫项目目录
os.chdir('/home/spider_scrap/guangming_edu')

try:
    #execute(['scrapy', 'crawl', 'gmedu'])
    execute(['scrapy', 'crawl', 'gmedu', '--logfile=gmedu.log'])
finally:
    print "<------------Mission Complete------------>"
