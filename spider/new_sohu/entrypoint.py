#! /usr/bin/env python
# coding: utf-8
"""
********************************************
*运行此文件，可直接调用scrapy中名字为mysohuedu的爬虫*
********************************************
"""
from scrapy.cmdline import execute
import os

# 跳转到爬虫项目目录
os.chdir('/home/spider_scrap/new_sohu')
try:
    execute(['scrapy', 'crawl', 'mysohuedu', '--logfile=sohu.log'])
    # execute(['scrapy', 'crawl', 'mysina', '-L', 'WARNING'])
finally:
    print "<------------Scrap Finish------------>"
