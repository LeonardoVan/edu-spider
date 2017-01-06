#! /usr/bin/env python
# coding: utf-8
import scrapy
import re
import json
import urllib2
import time
from new_sohu.items import NewSohuItem
from scrapy.http import Request
from bs4 import BeautifulSoup
from selenium import webdriver


class NewSohuspider(scrapy.Spider):

    name = 'mysohuedu'
    allowed_domains = ['sohu.com']
    # base_url_head = 'http://mt.sohu.com/learning/index_'
    # base_url_tail = '.shtml'
    # base_urls = ['http://mt.sohu.com/learning/index.shtml']

    def start_requests(self):
        base_url = 'http://mt.sohu.com/learning/index.shtml'
        for i in range(6):
            driver = webdriver.PhantomJS(
                executable_path='/phantomjs/bin/phantomjs',
                desired_capabilities={
                    'javascriptEnabled': True,
                    'platform': 'windows',
                    'browserName': 'Mozilla',
                    'version': '5.0',
                    'phantomjs.page.setting.userAgent': "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36",
                },
                service_args=['--load-images=no']  # 不加载图片
            )
            driver.get(base_url)
            time.sleep(5)
            driver.find_element_by_link_text(u"下一页").click()  # 加载下一页
            # body = driver.page_source  # 获取内容
            url = driver.current_url
            driver.close()
            next_url = url
            # print body
            i += 1
            yield Request(next_url, self.parse)
        yield Request(base_url, self.parse)

    def parse(self, response):
        # print response.text
        spans = BeautifulSoup(response.text, 'lxml').find(class_='list-box').find_all(class_="content-title")
        # print spans
        for span in spans:
            href = span.find('a')['href']
            # print href
            title = span.find('a').get_text()
            # print title
            yield Request(href, callback=self.get_content, meta={'title': title,
                                                                 'href': href})

    def get_content(self, response):
        item = NewSohuItem()

        """>>>>>提取info_id<<<<<"""
        item['info_id'] = response.url.strip().split('/')[-1].split('.')[0]
        # print info_id

        """>>>>>提取新闻标题<<<<<"""
        item['title'] = response.meta['title']
        # print title

        """>>>>>提取新闻链接<<<<<"""
        item['link'] = response.url.strip()
        # print link

        """>>>>>提取新闻发布时间<<<<<"""
        online_time = response.xpath("//*[@id='pubtime_baidu']/text()").extract()
        online_time = online_time[0].replace(' ', '').replace('-', '').replace(':', '')
        item['online_time'] = int(online_time)
        # print int(online_time), type(int(online_time))

        """>>>>>提取新闻版块<<<<<"""
        section = response.xpath("//*[@id='channel-dir']/div[@class='left']/span/a/text()").extract()
        # print section[0]
        item['section'] = section[0]

        """>>>>>提取新闻概述<<<<<"""
        description = response.xpath("//meta[@name='description']/@content").extract()
        item['description'] = description[0]

        """>>>>>提取新闻作者<<<<<"""
        author = response.xpath("//div[@class='user-txt']/h4/span/a/text()").extract()
        try:
            item['author'] = author[0]
        except IndexError:
            item['author'] = None

        """>>>>>提取新闻来源地址<<<<<"""
        source = response.xpath("//div[@class='user-txt']/h4/span[@class='user-name']/a/@href").extract()
        try:
            item['source'] = source[0]
        except IndexError:
            item['source'] = None

        """>>>>>提取新闻标签(关键字)<<<<<"""
        tag_list = response.xpath("//span[@class='tag']/a/text()").extract()
        if len(tag_list) > 0:
            tag = ','.join(tag_list)
        else:
            tag = None
        # print tag_list, len(tag_list)
        item['tag'] = tag

        """-----提取新闻阅读数（点击量）、评论数-----"""
        get_ids = response.xpath("/html/head/script[4]/text()").extract()
        ids = get_ids[0].split('var ')
        entityId = ids[1].strip().replace(' ', '').replace(';', '').replace('entityId=', '')
        mpId = ids[2].strip().replace(';', '').replace('mpId=', '')
        header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
        }
        """>>>>>提取阅读数（点击量）<<<<<"""
        read_url = 'http://mp.sohu.com/openapi/profile/getRichInfo?cb=?&mpId=' + mpId + '&newsId=' + entityId
        # print read_url
        rj_request = urllib2.Request(read_url, headers=header)
        rj_get = urllib2.urlopen(rj_request).read().replace('?(', '').replace(')', '')
        try:
            rj_count = json.loads(rj_get)[u'data'][u'newspv']
            item['read_count'] = rj_count
        except:
            item['read_count'] = None

        """>>>>>提取评论数<<<<<"""
        cmt_url = 'http://changyan.sohu.com/node/html?t=1457788383080&callback=fn&client_id=cyqemw6s1&topicurl=' \
                  + item['link'] + '&topicsid=' + entityId
        # print cmt_url
        cj_request = urllib2.Request(cmt_url, headers=header)
        cj_get = urllib2.urlopen(cj_request).read().replace('fn(', '').replace(');', '')
        cj_count = json.loads(cj_get)[u'listData'][u'cmt_sum']
        item['comment_count'] = cj_count

        """>>>>>提取新闻内容<<<<<"""
        # body = response.xpath("//div[@class='content-wrapper']/div[@class='text clear']/p/text()").extract()
        # item['news_body'] = body
        soup = BeautifulSoup(response.text, 'lxml')
        [script.extract() for script in soup.find_all('script')]  # 去除script标签
        [style.extract() for style in soup.find_all('style')]  # 去除style标签
        news_body = soup.find(itemprop='articleBody').get_text()
        news_body = news_body.split('\n')
        body = []
        for ct in news_body:
            by = ct.replace('\n', '')
            body.append(by)
            while '' in body:
                body.remove('')
        item['news_body'] = body

        return item
