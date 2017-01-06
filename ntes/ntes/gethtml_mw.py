# -*- coding: utf-8 -*-
"""
*********************************************************************************
* 自定义download中间件，用于解析网页中的js                                           *
* 运用selenium + phantomjs解析js,selenium是一个自动化模块,phantomjs是一个无界面浏览器  *
* 需要在setting.py中激活DOWNLOADER_MIDDLEWARES                                    *
*********************************************************************************
"""
from selenium import webdriver
from scrapy.http import HtmlResponse
import time
from ntes.mysqlpipelines.sql import Sql


class JavaScriptMiddleware(object):
    def process_request(self, request, spider):
        if spider.name == "ntes":
            news_id = request.url.strip().split('/')[-1].split('.')[0]
            ret = Sql.select_name(news_id)
            if ret[0] == 1:
                print "%s 已经存在了" % news_id
                pass
            else:
                print "---+==========>>>PhantomJs is starting---+==========>>>"
                # 调用selenium的webdriver运行PhantomJs对网页中的js进行渲染
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
                driver.get(request.url)
                time.sleep(10)
                body = driver.page_source
                url = driver.current_url
                driver.close()
                return HtmlResponse(url, body=body, encoding='utf-8', request=request)  # 返回response
        else:
            return
    

