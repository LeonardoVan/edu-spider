#! /usr/bin/env python
# coding: utf-8
import scrapy
import urllib2
import datetime
from bs4 import BeautifulSoup
from scrapy.http import Request
from nanfang.items import NanfangItem
from nanfang.mysqlpipelines.sql import Sql
from hdfs import *
# 设置默认编码
import sys

reload(sys)
sys.setdefaultencoding('utf-8')


class NfeduSpider(scrapy.Spider):
    name = 'nanfangedu'
    allowed_domains = ['edu.oeeee.com']

    def start_requests(self):
        base_url = 'http://edu.oeeee.com/'
        header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'
        }
        base_request = urllib2.Request(base_url, headers=header)
        base_html = urllib2.urlopen(base_request)
        base_soup = BeautifulSoup(base_html, 'lxml')
        lis = base_soup.find(class_='nav-channel clearfix').find('ul').find_all('li')
        for li in lis:
            if li.find('a') is None:
                pass
            else:
                href = li.find('a')['href']
                if 'http' not in href:
                    url = 'http://edu.oeeee.com' + href
                else:
                    pass
                yield Request(url, callback=self.parse)

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        sec = soup.find(class_='location').get_text()
        sect = sec.split('>')
        section = '-'.join(sect).replace(u'\xa0', u'')
        uls = soup.find(class_='list-box').find('ul').find_all('li')
        # loc = soup.find(class_='brnone').find('a').get_text()
        # print loc
        for ul in uls:
            href = ul.find('h3').find('a')['href']
            title = ul.find('h3').find('a').get_text()
            """判断网页是否已经爬取过"""
            news_id = href.split('/')[-1].split('.')[0]
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
                    yield Request(href, callback=self.get_content, meta={'title': title,
                                                                         'section': section
                                                                         })
            else:
                if ret[0] == 1 and txt_name in link_hdfs.list(yesterday_dir):
                    print "<+_+>-----页面已经爬取，结果存在HDFS与Mysql中-----<+_+>"
                    pass
                elif ret[0] == 1 and txt_name in link_hdfs.list(today_dir):
                    print "<+_+>-----页面已经爬取，结果存在HDFS与Mysql中-----<+_+>"
                else:
                    yield Request(href, callback=self.get_content, meta={'title': title,
                                                                         'section': section
                                                                         })

    def get_content(self, response):
        head_title = response.xpath("//head/title/text()").extract()
        if '对不起，你所访问的页面已不存在' in head_title[0]:
            print '!>_<对不起，你所访问的页面已不存在>_<!'
            pass
        else:
            item = NanfangItem()
            info_id = response.url.split('/')[-1].split('.')[0]
            item['info_id'] = info_id

            link = response.url
            item['link'] = link

            item['source'] = None

            title = response.meta['title']
            item['title'] = title

            section = response.meta['section']
            item['section'] = section

            self.get_online_time(response, item)
            self.get_news_from(response, item)
            self.get_description(response, item)
            self.get_tag(response, item)
            self.read_count(response, item)
            self.get_text(response, item)

            return item

    @staticmethod
    def get_online_time(response, item):
        try:
            time = response.xpath("//span[@class='time']/text()").extract()[0]
        except IndexError:
            time_1 = response.xpath("//span[@id='pubtime_baidu']/text()").extract()
            time_2 = response.xpath("//div[@class='article']/div/div/div/text()").extract()
            if not time_1:
                time = time_2[0]
            else:
                time = time_1[0]
        online_time = time.strip().replace('-', '').replace(':', '').replace(' ', '')
        # print online_time
        item['online_time'] = online_time

    @staticmethod
    def get_news_from(response, item):
        try:
            sce = response.xpath("//span[@class='source']/text()").extract()[0]
            news_from = sce.split(':')[-1]
        except IndexError:
            sce_1 = response.xpath("//*[@id='source_baidu']/text()").extract()
            sce_2 = response.xpath("//div[@class='clearfix tag']/div[@class='fl']/text()").extract()
            if not sce_1:
                news_from = sce_2[0].split("：")[1].split('作')[0].strip()
            else:
                news_from = sce_1[0].split("：")[-1]
        item['news_from'] = news_from
        item['author'] = news_from

    @staticmethod
    def get_description(response, item):
        description = response.xpath("//meta[@name='description']/@content").extract()
        if description:
            item['description'] = description[0]

    @staticmethod
    def get_tag(response, item):
        keywords = response.xpath("//meta[@name='keywords']/@content").extract()
        if '' == keywords[0]:
            item['tag'] = None
        else:
            item['tag'] = keywords[0]

    @staticmethod
    def read_count(response, item):
        i_d = response.url.split('/')[-1].split('.')[0]
        rd_url = 'http://edu.oeeee.com/api/readnum.php?s=/readnum/readnum/id/' + i_d + '/type/article/show/1'
        header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'
        }
        rd_req = urllib2.Request(rd_url, headers=header)
        read_count = urllib2.urlopen(rd_req).read()
        if read_count:
            item['read_count'] = read_count

    @staticmethod
    def get_text(response, item):
        soup = BeautifulSoup(response.text, 'lxml')
        text = soup.find(class_='content').find_all('p')
        body = []
        if text:
            for te in text:
                bd = te.get_text().split('\n')
                body.append(bd[0].replace(u'\xa0', u''))
        while '' in body:
            body.remove('')
        item['news_body'] = body
        # print len(body)
