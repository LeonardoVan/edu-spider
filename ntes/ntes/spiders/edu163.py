#! /usr/bin/env python
# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.selector import Selector
from scrapy.http import Request
import urllib2
from datetime import *
from ntes.items import NtesItem
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
import json
from ntes.mysqlpipelines.sql import Sql
import sys
reload(sys)
sys.setdefaultencoding('utf8')


class Spider(CrawlSpider):
    name = "ntes"
    allowed_domains = ["edu.163.com"]
    start_urls = ['http://edu.163.com/']
    date_now = date.today().strftime('%y-%m%d').split('-')
    allow = r"/%y/%m/\d+/*".replace('%y', date_now[0]).replace('%m', date_now[1])
    rules = (
        Rule(
            LinkExtractor(allow=allow),
            callback="parse_news",
            follow=True
            # follow=ture定义了是否再爬到的结果上继续往后爬
        ),
    )

    def parse_news(self, response):
        item = NtesItem()
        if 'thecover.cn' or 'thepaper.cn' in response.url:
            pass
        else:
            item['info_id'] = response.url.strip().split('/')[-1].split('.')[0]
            self.get_title(response, item)
            self.get_keywords(response, item)
            self.get_description(response, item)
            self.get_author(response, item)
            self.get_time(response, item)
            self.get_url(response, item)
            self.get_news_from(response, item)
            self.get_from_url(response, item)
            self.get_section(response, item)
            self.get_comment_count(response, item)
            self.get_text(response, item)
            return item

    def get_title(self, response, item):
        title = response.xpath("/html/head/title/text()").extract()
        if title:
            item['title'] = title[0][:-5]

    def get_keywords(self, response, item):
        # title = response.xpath("/html/head/title/text()").extract()
        keywords = response.xpath("//meta[@name='keywords']/@content").extract()
        if keywords:
            item['tag'] = keywords[0]

    def get_description(self, response, item):
        description = response.xpath("//meta[@name='description']/@content").extract()
        if description:
            item['news_description'] = description[0]

    def get_author(self, response, item):
        author = response.xpath("//meta[@name='author']/@content").extract()
        if author:
            item['author'] = author[0]

    def get_time(self, response, item):
        online_times = response.xpath("//div[@class='post_time_source']/text()").extract()
        if online_times:
            online_time = online_times[0].strip()[0:-4]
            online_time = online_time.replace('-', '').replace(' ', '').replace(':', '')
            online_time = int(online_time)
            item['online_time'] = online_time

    def get_news_from(self, response, item):
        # news_from = response.xpath("//div[@class='ep-time-soure cDGray']/a/text()").extract()
        news_from = response.xpath("//div[@class='post_time_source']/a/text()").extract()
        if news_from:
            item['news_from'] = news_from[0]

    def get_section(self, response, item):
        section = response.xpath("//div[@class='post_crumb']/a/text()").extract()
        if section:
            item['section'] = section[1]

    def get_comment_count(self, response, item):
        comment_url = 'http://comment.news.163.com/api/v1/products/a2869674571f77b5a0867c3d71db5856/threads/' + item['info_id']
        try:
            page = urllib2.urlopen(comment_url).read()
            comment_dict = json.loads(page)
            comment_count = comment_dict['cmtVote']
            item['comment_count'] = comment_count
        except:
            item['comment_count'] = None

    def get_from_url(self, response, item):
        # from_url = response.xpath("//div[@class='ep-time-soure cDGray']/a/@href").extract()
        from_url = response.xpath("//div[@class='post_time_source']/a/@href").extract()
        # print from_url
        try:
            if 'http' in from_url[0]:
                item['source'] = from_url[0]
            else:
                item['source'] = None
        except:
             item['source'] = None

    def get_text(self, response, item):
        news_body = response.xpath("//div[@id='endText']/p/text()").extract()
        if news_body:
            item['news_body'] = news_body

    def get_url(self, response, item):
        news_url = response.url
        if news_url:
            item['link'] = news_url
