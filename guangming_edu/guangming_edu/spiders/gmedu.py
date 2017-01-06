#! /usr/bin/env python
# coding: utf-8
import scrapy
import datetime
from bs4 import BeautifulSoup
from scrapy.http import Request
from guangming_edu.items import GuangmingEduItem
from hdfs import *
from guangming_edu.mysqlpipelines.sql import Sql
# 设置默认编码
import sys

reload(sys)
sys.setdefaultencoding('utf-8')


class GmeduSpider(scrapy.Spider):
    name = 'gmedu'
    allowed_domains = ['edu.gmw.cn']
    # start_urls = ['http://edu.gmw.cn/node_9669.htm']

    def start_requests(self):
        start_url = 'http://edu.gmw.cn/node_9669.htm'
        for i in range(1):
            n = i + 2
            url = 'http://edu.gmw.cn/node_9669_' + str(n) + '.htm'
            yield Request(url, self.parse)
        yield Request(start_url, self.parse)

    def parse(self, response):
        # print response.text
        uls = BeautifulSoup(response.text, 'lxml').find(class_='channelLeftPart').find_all('li')
        for span in uls:
            base_url = 'http://edu.gmw.cn/'
            href = span.find('a')['href']
            if 'http://' in href:
                link = href
            else:
                link = base_url + href
            """判断网页是否已经爬取过"""
            news_id = link.split('/')[-1].split('.')[0]
            ret = Sql.select_name(news_id)
            link_hdfs = InsecureClient("http://192.168.10.117:50070", user='hadoop')  # Base HDFS web client
            dir_ls = link_hdfs.list('/testdir')
            today = datetime.date.today()
            today_dir = '/testdir' + '/' + str(today)
            if str(today) not in dir_ls:
                link_hdfs.makedirs(today_dir)
            txt_name = news_id + '.txt'
            yesterday = today - datetime.timedelta(days=1)
            yesterday_dir = '/testdir' + '/' + str(yesterday)
            if str(yesterday) not in dir_ls:
                if ret[0] == 1 and txt_name in link_hdfs.list(today_dir):
                    print "<+_+>-----页面已经爬取，结果存在HDFS与Mysql中-----<+_+>"
                    pass
                else:
                    yield Request(link, callback=self.get_content)
            else:
                if ret[0] == 1 and txt_name in link_hdfs.list(yesterday_dir):
                    print "<+_+>-----页面已经爬取，结果存在HDFS与Mysql中-----<+_+>"
                    pass
                elif ret[0] == 1 and txt_name in link_hdfs.list(today_dir):
                    print "<+_+>-----页面已经爬取，结果存在HDFS与Mysql中-----<+_+>"
                else:
                    yield Request(link, callback=self.get_content)
            # yield Request(link, callback=self.getcontent)

    def get_content(self, response):
        # print response.text
        item = GuangmingEduItem()

        info_id = response.url.strip().split('/')[-1].split('.')[0]
        if info_id:
            item['info_id'] = info_id

        self.get_title(response, item)
        self.get_link(response, item)
        self.get_online_time(response, item)
        self.get_news_from(response, item)
        self.get_source(response, item)
        self.get_tag(response, item)
        self.get_news_description(response, item)
        self.get_author(response, item)
        self.get_section(response, item)
        # self.get_comment(response, item)
        self.get_text(response, item)

        return item

    def get_title(self, response, item):
        title = response.xpath("//*[@id='articleTitle']/text()").extract()
        if title:
            item['title'] = title[0].strip()

    def get_link(self, response, item):
        link = response.url
        if link:
            item['link'] = link

    def get_online_time(self, response, item):
        time = response.xpath("//*[@id='pubTime']/text()").extract()
        online_time = time[0].replace('-', '').replace(':', '').replace(' ', '')
        if online_time:
            item['online_time'] = online_time

    def get_news_from(self, response, item):
        news_from = response.xpath("//*[@id='source']/a/text()").extract()
        try:
            if news_from:
                item['news_from'] = news_from[0]
        except IndexError:
            nsf = response.xpath("//*[@id='source']/text()").extract()
            news_from = nsf[0].split('：')[-1].strip()
            if news_from:
                item['news_from'] = news_from

    def get_source(self, response, item):
        sce = response.xpath("//*[@id='source']/a/@href").extract()
        try:
            source = sce[0]
            if source == '../../':
                item['source'] = 'http://edu.gmw.cn/'
            else:
                item['source'] = source
            # print item['source']
        except IndexError:
            item['source'] = None

    def get_tag(self, response, item):
        ta = response.xpath("//meta[@name='keywords']/@content").extract()
        if ta:
            item['tag'] = ta[0]

    def get_news_description(self, response, item):
        desc = response.xpath("//meta[@name='description']/@content").extract()
        if desc:
            item['news_description'] = desc[0]

    def get_author(self, response, item):
        ath = response.xpath("//meta[@name='author']/@content").extract()
        if ath:
            item['author'] = ath[0]

    def get_section(self, response, item):
        sct = response.xpath("//*[@id='contentBreadcrumbs2']/a/text()").extract()
        section = '-'.join(sct)
        if section:
            item['section'] = section

    # def get_comment(self, response, item):
    #     cm = response.xpath("//meta[@name='contentid']/@content").extract()
    #     cm_id = cm[0]
    #     cm_url = 'http://changyan.sohu.com/api/2/topic/comments?callback=&client_id=cyr45LmB4&topic_id=' + cm_id
        # print cm_url

    def get_text(self, response, item):
        soup = BeautifulSoup(response.text, 'lxml')
        text = soup.find(id='contentMain').get_text()
        text = text.split('\n')
        body = []
        for b in text:
            bd = b.strip().replace('\n', '')
            body.append(bd)
            while '' in body:
                body.remove('')
        if body:
            item['news_body'] = body
