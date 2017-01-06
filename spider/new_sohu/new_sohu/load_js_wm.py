# coding: utf-8
from selenium import webdriver
from scrapy.http import HtmlResponse
import time


class NextPageMiddleware(object):
    def process_request(self, request, spider):
        if spider.name == 'mysohuedu':
            print "--->>>...<<<---PhantomJs is starting<<<---...--->>>"
            # 调用selenium的webdriver运行PhantomJs对网页中的js进行渲染
            driver = webdriver.PhantomJS(
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
            time.sleep(5)
            driver.find_element_by_link_text(u"下一页").click()  # 加载下一页
            body = driver.page_source  # 获取内容
            url = driver.current_url
            driver.close()
            print body.encode('gbk', 'ignore')
            print url
            return HtmlResponse(url, body=body, encoding='utf-8', request=request)  # 返回response
        else:
            return

