#! /usr/bin/env python
# coding: utf-8
import re
import scrapy
from bs4 import BeautifulSoup
from scrapy.http import Request
from new_sina.items import NewSinaItem
import urllib2
import json
# 设置默认编码
import sys

reload(sys)
sys.setdefaultencoding('utf-8')


class Myspider(scrapy.Spider):
    name = 'mysina'
    allowed_domains = ['edu.sina.com.cn', 'blog.sina.com.cn']
    base_url_head = 'http://roll.edu.sina.com.cn/more/index_'
    base_url_tail = '.shtml'
    start_urls = ['http://roll.edu.sina.com.cn/more/index.shtml']

    def parse(self, response):
        # print response.text
        for i in range(1, 2):
            url = self.base_url_head + str(i) + self.base_url_tail
            # print url
            yield Request(url, callback=self.get_name)
            """yield Request,请求新的URL，后面跟的是回调函数，需要哪个函数来处理这个返回值，就调用哪个函数，
               返回值会以参数的形式传递到所调用的函数。
            """

    def get_name(self, response):
        # print response.text
        lis = BeautifulSoup(response.text, 'lxml').find(class_='list_009').find_all('li')
        # print lis
        """find_all取出来的标签存放在一个列表；不然不能继续使用find"""
        for li in lis:
            # print li
            news_href = li.find('a')['href']
            # print news_href
            news_name = li.find('a').get_text()
            # print news_name
            news_time = li.find('span').get_text()
            # print news_time
            yield Request(news_href, callback=self.get_content, meta={'name': news_name,
                                                                      'url': news_href})
            # meta字典，是Scrapy中传递额外数据的方法。因为我们需要在下一个页面中获取新闻内容

    def get_content(self, response):
        item = NewSinaItem()
        # 定义newsid
        item['info_id'] = response.url.strip().split('/')[-1].split('.')[0]

        # 提取news标题
        name = response.meta['name']
        item['title'] = name

        # 提取news链接
        url = response.meta['url']
        item['link'] = url

        # 提取news发布时间
        if 'blog.sina' in url:
            online_time = response.xpath("//*[@id='articlebody']/div[@class='articalTitle']/span[@class='time SG_txtc']/text()").extract()
            # print online_time
            online_time = online_time[0].replace('(', '').replace(')', '').replace(' ', '').replace(':', '').replace('-', '')
            item['online_time'] = online_time
        elif 'zl/' in url:
            online_time = response.xpath("//span[@id='pub_date']/text()").extract()
            # print online_time
            online_time = online_time[0].replace(' ', '').replace(':', '').replace(u'\u5e74', '')
            online_time = online_time.replace(u'\u6708', '').replace(u'\u65e5', '')
            online_time = int(online_time)
            # print online_time, type(online_time)
            item['online_time'] = online_time
        else:
            online_time = response.xpath("//div[@id='page-tools']/span/span[@class='titer']/text()").extract()
            online_time = online_time[0].replace(' ', '').replace(':', '').replace(u'\u5e74', '')
            online_time = online_time.replace(u'\u6708', '').replace(u'\u65e5', '')
            online_time = int(online_time)
            # print online_time, type(online_time)
            item['online_time'] = online_time

        # 提取版块
        if 'blog.sina' in url:
            item['section'] = '博客'
        elif 'zl/' in url:
            sections = response.xpath("//div[@class='artInfo']/div/span/a/text()").extract()
            section = sections[0]
            item['section'] = section
        else:
            sections = response.xpath("//div[@class='text notInPad']/a/text()").extract()
            section = '-'.join(sections)
            # print section
            item['section'] = section

        # 提取网页概述
        if 'blog.sina' in url:
            descriptions = response.xpath("//meta[@name='description']/@content").extract()
            item['news_description'] = descriptions[0]
        else:
            descriptions = response.xpath("//meta[@property='og:description']/@content").extract()

            item['news_description'] = descriptions[0]

        # 提取news作者
        if 'blog.sina' in url:
            authors = response.xpath("//div/span/strong[@id='ownernick']/text()").extract()
            author = authors[0]
            item['author'] = author
        else:
            authors = response.xpath("//meta[@property='article:author']/@content").extract()
            for author in authors:
                # print author
                item['author'] = author

        # 提取关键词
        if 'blog.sina' in url:
            # keyword = response.xpath("//meta[@name='keywords']/@content").extract()
            # keywords = str(keyword).split(',')[2:][0].replace(']', '')
            try:
                keywords = response.xpath("//td[@class='blog_tag']/h3/a/text()").extract()[0]
            except:
                keywords = None
        else:
            keywords = response.xpath("//meta[@name='tags']/@content").extract()[0]
        item['tag'] = keywords

        # 提取news来源地址
        if 'blog.sina' in url:
            source = response.xpath("//h1[@id='blogname']/a/@href").extract()
        elif 'zl/' in url:
            source = response.xpath("//span[@id='author_name']/a[1]/@href").extract()
        else:
            source = response.xpath("//a[@class='ent1 fred']/@href").extract()
        if len(source) >= 1:
            item['source'] = source[0]
        else:
            item['source'] = None

        # print url
        soup = BeautifulSoup(response.text, 'lxml')
        [script.extract() for script in soup.find_all('script')]  # 去除script标签
        [style.extract() for style in soup.find_all('style')]  # 去除style标签

        # 提取news内容
        if 'blog.sina' in url:
            content = soup.find(id='sina_keyword_ad_area2').get_text()
        else:
            content = soup.find(id='artibody').get_text()
        # print content
        # 去除\a0,\u2022，不去除会引起转码报错
        contents = content.replace(u'\xa0', u'').replace(u'\u2022', u'')
        contents = contents.split('\n')
        body = []
        for ct in contents:
            by = ct.replace('\n', '')
            body.append(by)
            while '' in body:
                body.remove('')
        item['news_body'] = body

        # 提取评论数
        if 'blog.sina' in url:
            comment_id = item['info_id'].split('_')[1]
            # print comment_id
            comment_url = 'http://blog.sina.com.cn/s/comment_' + comment_id + '_1.html?comment_v=articlenew'
            json_request = urllib2.Request(comment_url)
            json_get = urllib2.urlopen(json_request).read()
            json_dct = json.loads(json_get)
            item['comment_count'] = json_dct['data']['comment_total_num']
        else:
            comment_mark = response.xpath("//meta[@name='comment']/@content").extract()
            comment_mark = comment_mark[0].split(':')
            # print comment_mark
            comment_section = comment_mark[0].replace('_', '')
            comment_id = comment_mark[1]
            comment_url = 'http://comment5.news.sina.com.cn/page/info?version=1&format=js&channel=' + comment_section \
                          + '&newsid=' + comment_id + '&group=0&compress=1&ie=gbk&oe=gbk&page=1&page_size=20'
            json_request = urllib2.Request(comment_url)
            json_get = urllib2.urlopen(json_request).read().replace('var ', '').replace('data=', '')
            # 去除‘var data=’，否则转字典时报错
            # print json_get
            json_dct = json.loads(json_get)
            # print json_dct
            item['comment_count'] = json_dct['result']['count']['total']

        # 提取博客关注人数
        if 'blog.sina' in url:
            blog_count = response.xpath("//span[@id='comp_901_attention']/strong/text()").extract()
            item['blog_count'] = blog_count[0]
        elif '/zl/' in url:
            json_id = response.xpath("//meta[@name='sudameta'][2]/@content").extract()[0].split(';')[0].split(':')[1]
            json_url = 'http://hi.news.sina.com.cn/blog/totalauthor/total_zlauthor.php?interface=json&callback=show_author&t_col2=' + json_id
            json_request = urllib2.Request(json_url)
            json_get = urllib2.urlopen(json_request).read()
            # print json_get
            # 这里采用正则匹配出博客地址
            reg = re.findall('"t_col6":"(.*?)"', json_get)
            try:
                blog_url = reg[0].replace('\\', '')
                # print blog_url
                blog_request = urllib2.Request(blog_url)
                blog_html = urllib2.urlopen(blog_request).read()
                # print blog_html
                blog_soup = BeautifulSoup(blog_html, 'lxml')
                blog_count = blog_soup.find(id='comp_901_attention').get_text()
                # print blog_count, type(blog_count)
                item['blog_count'] = blog_count
            except:
                item['blog_count'] = "Can not reach to Blog."

        else:
            item['blog_count'] = "Can not reach to Blog."

        # 提取微博信息（从手机端微博爬取信息，网页端需要登陆才能爬取）
        if 'blog.sina' in url:
            weibo_id = response.xpath("//div[@class='info_btn1']/a/@href").extract()[0].split('/')[-1].split('?')[0]
            weibo_link = "http://weibo.cn/" + weibo_id
            # print weibo_link
            header = {'Connection': 'keep-alive',
                      'Host': 'weibo.cn',
                      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                    'Chrome/55.0.2883.87 Safari/537.36'}
            # 必须加上header，不然会被禁止访问
            try:
                weibo_request = urllib2.Request(weibo_link, headers=header)
                weibo_html = urllib2.urlopen(weibo_request).read()
                weibo_soup = BeautifulSoup(weibo_html, 'lxml')
                weibo_info = weibo_soup.find(class_='tip2').get_text()
                a = str(weibo_info).split(']')
                weibo_num = a[0].replace('[', ' ')
                fans_num = a[2].replace('[', ' ')
                # print weibo_num, fans_num
            except:
                weibo_num = 'Can not reach to WeiBo'
                fans_num = 'Can not reach to WeiBo'
        elif '/zl/' in url:
            json_id = response.xpath("//meta[@name='sudameta'][2]/@content").extract()[0].split(';')[0].split(':')[1]
            # print json_id
            json_url = 'http://hi.news.sina.com.cn/blog/totalauthor/total_zlauthor.php?interface=json&callback=show_author&t_col2=' + json_id
            json_request = urllib2.Request(json_url)
            json_get = urllib2.urlopen(json_request).read()
            # print json_get
            # 这里采用正则匹配出微博地址，取出微博ID，访问手机端微博
            reg = re.findall('"t_col5":"(.*?)"', json_get)
            try:
                weibo_id = reg[0].split('/')[-1]
                # print weibo_id
                weibo_link = "http://weibo.cn/" + weibo_id
                header = {'Connection': 'keep-alive',
                          'Host': 'weibo.cn',
                          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                        'Chrome/55.0.2883.87 Safari/537.36'}
                # 必须加上header，不然会被禁止访问
                weibo_request = urllib2.Request(weibo_link, headers=header)
                weibo_html = urllib2.urlopen(weibo_request).read()
                weibo_soup = BeautifulSoup(weibo_html, 'lxml')
                weibo_info = weibo_soup.find(class_='tip2').get_text()
                a = str(weibo_info).split(']')
                weibo_num = a[0].replace('[', ' ')
                fans_num = a[2].replace('[', ' ')
                # print weibo_num, fans_num

            except:
                weibo_num = 'Can not reach to WeiBo'
                fans_num = 'Can not reach to WeiBo'
        else:
            try:
                weibo_id = response.xpath("//a[@id='media_weibo']/@href").extract()[0].split('?')[0].split('/')[-1]
                # print weibo_id
                weibo_link = "http://weibo.cn/" + weibo_id
                header = {'Connection': 'keep-alive',
                          'Host': 'weibo.cn',
                          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                        'Chrome/55.0.2883.87 Safari/537.36'}
                # 必须加上header，不然会被禁止访问
                weibo_request = urllib2.Request(weibo_link, headers=header)
                weibo_html = urllib2.urlopen(weibo_request).read()
                weibo_soup = BeautifulSoup(weibo_html, 'lxml')
                weibo_info = weibo_soup.find(class_='tip2').get_text()
                a = str(weibo_info).split(']')
                weibo_num = a[0].replace('[', ' ')
                fans_num = a[2].replace('[', ' ')
                # print weibo_num, fans_num
            except:
                weibo_num = 'Can not reach to WeiBo'
                fans_num = 'Can not reach to WeiBo'
        item['weibo_num'] = weibo_num
        item['weibo_fans_num'] = fans_num

        return item
