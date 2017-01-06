# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class GuangmingEduItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    # 新闻ID
    info_id = scrapy.Field()
    # 新闻标题
    title = scrapy.Field()
    # 新闻地址
    link = scrapy.Field()
    # 新闻发布时间
    online_time = scrapy.Field()
    # 新闻来源
    news_from = scrapy.Field()
    # 来源地址
    source = scrapy.Field()
    # 新闻内容
    news_body = scrapy.Field()
    # 新闻关键字
    tag = scrapy.Field()
    # 新闻描述
    news_description = scrapy.Field()
    # 作者
    author = scrapy.Field()
    # 版块
    section = scrapy.Field()
    # 评论数
    comment_count = scrapy.Field()
