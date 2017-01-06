# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class NanfangItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    # 新闻ID
    info_id = scrapy.Field()
    # 新闻标题
    title = scrapy.Field()
    # 新闻发布时间
    online_time = scrapy.Field()
    # 新闻地址
    link = scrapy.Field()
    # 新闻来源
    news_from = scrapy.Field()
    # 新闻来源地址
    source = scrapy.Field()
    # 新闻版块
    section = scrapy.Field()
    # 网页概述
    description = scrapy.Field()
    # 新闻归属地
    region = scrapy.Field()
    # 新闻作者
    author = scrapy.Field()
    # 新闻标签（关键字）
    tag = scrapy.Field()
    # 新闻内容
    news_body = scrapy.Field()
    # 阅读人数
    read_count = scrapy.Field()
