#! /usr/bin/env python
# coding: utf-8

from scrapy.cmdline import execute
import os

# 跳转到爬虫项目目录
os.chdir('/home/spider_scrap/nanfang')

try:
    #execute(['scrapy', 'crawl', 'nanfangedu'])
    execute(['scrapy', 'crawl', 'nanfangedu', '--logfile=nanfangedu.log'])
finally:
    print "<------------Mission Complete------------>"
