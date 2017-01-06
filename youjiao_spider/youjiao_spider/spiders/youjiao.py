# -*- coding: utf-8 -*-
import re
import urllib2
import cookielib
import datetime
from bs4 import BeautifulSoup
from scrapy.spiders import Spider
from scrapy import Request
from scrapy_splash import SplashRequest
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor
from youjiao_spider.items import YoujiaoItem
from hdfs import *
from youjiao_spider.mysqlpipelines.sql import Sql

import sys

reload(sys)
sys.setdefaultencoding('utf-8')

req_header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 '
                  'Safari/537.11',
    'Accept': 'text/html;q=0.9,*/*;q=0.8',
    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
    'Accept-Encoding': 'gzip',
    'Connection': 'close',
    'Referer': None  # 注意如果依然不能抓取的话，这里可以设置抓取网站的host
}

req_timeout = 60


def convert_to_dict(obj):
    """把对象(支持单个对象、list、set)转换成字典"""
    is_list = obj.__class__ == [].__class__
    is_set = obj.__class__ == set().__class__

    if is_list or is_set:
        obj_arr = []
        for o in obj:
            # 把Object对象转换成Dict对象
            dict = {}
            dict.update(o.__dict__)
            obj_arr.append(dict)
        return obj_arr
    else:
        dict = {}
        dict.update(obj.__dict__)
        return dict


'''
幼升小-幼升小资讯	http://www.youjiao.com/ysx/ysx/
     -幼升小政策  http://www.youjiao.com/ysx/zhengce/
     -招生简章	http://www.youjiao.com/ysx/zsjz/
     -择校攻略	http://www.youjiao.com/ysx/zexiao/
     -入学指南	http://www.youjiao.com/ysx/zhinan/
     -学区房		http://www.youjiao.com/ysx/xuequfang/
     -幼升小真题	http://www.youjiao.com/ysx/rxcs/
     -幼升小试题  http://www.youjiao.com/ysx/shiti/
     -现场报名	http://www.youjiao.com/ysx/xianchang/
     -幼小衔接	http://www.youjiao.com/ysx/yxxj/
     -幼升小经验  http://www.youjiao.com/ysx/jingyan/
     -名校动态	http://www.youjiao.com/ysx/mxdt/
     -教育新闻	http://www.youjiao.com/ysx/zdxx/
重点小学-

幼教-少儿教育-成长日记	http://www.youjiao.com/sejy/czrj/
幼教 > 少儿教育 > 常见问题	http://www.youjiao.com/sejy/wenti/
幼教 > 少儿教育 > 家庭教育	http://www.youjiao.com/sejy/jtjy/
幼教 > 少儿教育 > 潜能开发	http://www.youjiao.com/sejy/qnkf/
幼教 > 少儿教育 > 艺术培养	http://www.youjiao.com/sejy/yspy/
幼教 > 少儿教育 > 儿童心理	http://www.youjiao.com/sejy/etxl/
幼教 > 少儿教育 > 听说读写	http://www.youjiao.com/sejy/tsdx/
幼教 > 少儿教育 > 英语学习	http://www.youjiao.com/sejy/yyxx/
幼教 > 少儿教育 > 拼音学习	http://www.youjiao.com/sejy/pyxx/
幼教 > 少儿教育 > 教育专家	http://www.youjiao.com/sejy/jyzj/
幼教 > 少儿教育 > 国外教育	http://www.youjiao.com/sejy/gwjy/
幼教 > 少儿教育 > 教育心得	http://www.youjiao.com/sejy/jyxd/
幼教 > 少儿教育 > 入园必读	http://www.youjiao.com/sejy/ryzd/
幼教 > 少儿教育 > 早期教育 > 宝宝取名	http://www.youjiao.com/sejy/zaojiao/quming/
幼教 > 少儿教育 > 早期教育 > 育儿测评	http://www.youjiao.com/sejy/zaojiao/ceping/
幼教 > 少儿教育 > 早期教育 > 语言行为	http://www.youjiao.com/sejy/zaojiao/yyxw/
幼教 > 少儿教育 > 早期教育 > 成长指标	http://www.youjiao.com/sejy/zaojiao/czzb/
幼教 > 少儿教育 > 早期教育 > 早期教育	http://www.youjiao.com/sejy/zaojiao/zqjy/
幼教 > 少儿教育 > 早期教育 > 性格培养	http://www.youjiao.com/sejy/zaojiao/xgpy/
幼教 > 少儿教育 > 早期教育 > 亲子交流	http://www.youjiao.com/sejy/zaojiao/qinzijiaoliu/
幼教 > 少儿教育 > 早期教育 > 早教游戏	http://www.youjiao.com/sejy/zaojiao/zjyx/
幼教 > 少儿教育 > 早期教育 > 儿童玩具	http://www.youjiao.com/sejy/zaojiao/wanju/
幼教 > 少儿教育 > 早期教育 > 智力开发	http://www.youjiao.com/sejy/zaojiao/zlkf/
幼教 > 少儿教育 > 胎教 > 胎教方法	http://www.youjiao.com/sejy/taijiao/tjff/
幼教 > 少儿教育 > 胎教 > 胎教心得	http://www.youjiao.com/sejy/taijiao/tjxd/
幼教 > 少儿教育 > 胎教 > 语言胎教	http://www.youjiao.com/sejy/taijiao/yuyan/
幼教 > 少儿教育 > 胎教 > 运动胎教	http://www.youjiao.com/sejy/taijiao/ydtj/
幼教 > 少儿教育 > 胎教 > 抚摸胎教	http://www.youjiao.com/sejy/taijiao/fmtj/
幼教 > 少儿教育 > 胎教 > 音乐胎教	http://www.youjiao.com/sejy/taijiao/yinyue/
幼教 > 少儿教育 > 胎教 > 胎教故事	http://www.youjiao.com/sejy/taijiao/tjgs/
幼教 > 少儿教育 > 胎教 > 胎教音乐	http://www.youjiao.com/sejy/taijiao/tjyy/
幼教 > 少儿教育 > 胎教 > 名人胎教	http://www.youjiao.com/sejy/taijiao/mrtj/
幼教 > 少儿教育 > 胎教 > 营养胎教	http://www.youjiao.com/sejy/taijiao/yytj/
幼教 > 儿童乐园 > 智力游戏	http://www.youjiao.com/etly/zlyx/
幼教 > 儿童乐园 > 儿童歌曲	http://www.youjiao.com/etly/etgq/
幼教 > 儿童乐园 > 少儿动画	http://www.youjiao.com/etly/etgs/
幼教 > 儿童乐园 > 少儿英语	http://www.youjiao.com/etly/seyy/
幼教 > 儿童乐园 > 听故事学英语	http://www.youjiao.com/etly/gushi/
幼教 > 儿童乐园 > 轻松学英语	http://www.youjiao.com/etly/lianxi/
幼教 > 儿童乐园 > 儿歌	http://www.youjiao.com/etly/erge/
幼教 > 儿童乐园 > 玩游戏学英语	http://www.youjiao.com/etly/youxi/
幼教 > 儿童乐园 > 儿童读物	http://www.youjiao.com/etly/etdw/
幼教 > 儿童乐园 > 动漫世界	http://www.youjiao.com/etly/mhsj/
幼教 > 儿童乐园 > 睡前故事	http://www.youjiao.com/etly/sqgs/
幼教 > 儿童乐园 > 童话故事	http://www.youjiao.com/etly/qzgs/
幼教 > 儿童乐园 > 科普知识 > 高新科技	http://www.youjiao.com/etly/kpzs/gxkj/
幼教 > 儿童乐园 > 科普知识 > 中外历史	http://www.youjiao.com/etly/kpzs/zwls/
幼教 > 儿童乐园 > 科普知识 > 天文地理	http://www.youjiao.com/etly/kpzs/twdl/
幼教 > 儿童乐园 > 科普知识 > 科普常识	http://www.youjiao.com/etly/kpzs/kpcs/
幼教 > 儿童乐园 > 科普知识 > 生命科学	http://www.youjiao.com/etly/kpzs/smkx/
幼教 > 儿童乐园 > 科普知识 > 人体科学	http://www.youjiao.com/etly/kpzs/rtkx/
幼教 > 儿童乐园 > 科普知识 > 基础科学	http://www.youjiao.com/etly/kpzs/jckx/
幼教 > 儿童乐园 > 科普知识 > 音乐艺术	http://www.youjiao.com/etly/kpzs/yyys/
幼教 > 儿童乐园 > 科普知识 > 环境科学	http://www.youjiao.com/etly/kpzs/hjkx/
幼教 > 儿童乐园 > 科普知识 > 军事科学	http://www.youjiao.com/etly/kpzs/jskx/
幼教 > 儿童乐园 > 科普知识 > 日常生活	http://www.youjiao.com/etly/kpzs/rcsh/
幼教 > 儿童乐园 > 科普知识 > 美术趣闻	http://www.youjiao.com/etly/kpzs/msqw/
幼教 > 儿童乐园 > 儿童读物	http://www.youjiao.com/etly/etdw/
幼教 > 儿童乐园 > 儿童玩具	http://www.youjiao.com/etly/etwj/
幼教 > 健康宝贝 > 护理保健	http://www.youjiao.com/jkbb/huli/
幼教 > 健康宝贝 > 预防急救	http://www.youjiao.com/jkbb/yfjj/
幼教 > 健康宝贝 > 免疫接种	http://www.youjiao.com/jkbb/mianyi/
幼教 > 健康宝贝 > 常见疾病	http://www.youjiao.com/jkbb/jibing/
幼教 > 健康宝贝 > 专家答疑	http://www.youjiao.com/jkbb/zjdy/
幼教 > 健康宝贝 > 健康饮食	http://www.youjiao.com/jkbb/jkys/
幼教 > 健康宝贝 > 婴儿喂养	http://www.youjiao.com/jkbb/yewy/
幼教 > 健康宝贝 > 添加辅食	http://www.youjiao.com/jkbb/fushi/
幼教 > 健康宝贝 > 妈咪营养	http://www.youjiao.com/jkbb/mmyy/
幼教 > 健康宝贝 > 儿童营养	http://www.youjiao.com/jkbb/etyy/
幼教 > 健康宝贝 > 宝宝用品	http://www.youjiao.com/jkbb/bbyp/

幼教 > 美食厨房 > 孕期食谱	http://www.youjiao.com/shipu/yqsp/
幼教 > 美食厨房 > 婴儿辅食	http://www.youjiao.com/shipu/fushi/
幼教 > 美食厨房 > 儿童食谱	http://www.youjiao.com/shipu/etsp/
幼教 > 美食厨房 > 家庭食谱	http://www.youjiao.com/shipu/jtsp/
幼教 > 美食厨房 > 产后食谱	http://www.youjiao.com/shipu/chsp/
幼教 > 美食厨房 > 烹饪技巧	http://www.youjiao.com/shipu/pengren/
幼教 > 美食厨房 > 美食DIY	http://www.youjiao.com/shipu/meishi/
幼教 > 时尚妈咪 > 美食文化	http://www.youjiao.com/ssmm/mswh/
幼教 > 美食厨房 > 美容食谱	http://www.youjiao.com/shipu/meirong/
幼教 > 美食厨房 > 减肥食谱	http://www.youjiao.com/shipu/jianfei/

幼教 > 孕育指南 > 准备怀孕 > 怀孕知识	http://www.youjiao.com/yyzn/zhunbeihuaiyun/huaiyunzhishi/
幼教 > 孕育指南 > 准备怀孕 > 孕前准备	http://www.youjiao.com/yyzn/zhunbeihuaiyun/yunqianzhunbei/
幼教 > 孕育指南 > 准备怀孕 > 怀孕禁忌	http://www.youjiao.com/yyzn/zhunbeihuaiyun/huaiyunjinji/
幼教 > 孕育指南 > 准备怀孕 > 遗传优生	http://www.youjiao.com/yyzn/zhunbeihuaiyun/yichuanyousheng/
幼教 > 孕育指南 > 准备怀孕 > 避孕流产	http://www.youjiao.com/yyzn/zhunbeihuaiyun/biyunliuchan/
幼教 > 孕育指南 > 准备怀孕 > 不孕不育	http://www.youjiao.com/yyzn/zhunbeihuaiyun/buyunbuyu/
幼教 > 孕育指南 > 准备怀孕 > 生男生女	http://www.youjiao.com/yyzn/zhunbeihuaiyun/shengnanshengnv/
幼教 > 孕育指南 > 实用工具	http://www.youjiao.com/yyzn/gongju/

幼教 > 时尚妈咪 > 星妈达人	http://www.youjiao.com/ssmm/xmdr/
幼教 > 时尚妈咪 > 家庭理财	http://www.youjiao.com/ssmm/jtlc/
幼教 > 时尚妈咪 > 服饰装扮	http://www.youjiao.com/ssmm/fscl/
幼教 > 时尚妈咪 > 美食文化	http://www.youjiao.com/ssmm/mswh/
幼教 > 时尚妈咪 > 婆媳关系	http://www.youjiao.com/ssmm/pxgx/
幼教 > 时尚妈咪 > 美容护肤	http://www.youjiao.com/ssmm/meirong/
幼教 > 时尚妈咪 > 纤体瘦身	http://www.youjiao.com/ssmm/sushen/
幼教 > 时尚妈咪 > 时尚潮流	http://www.youjiao.com/ssmm/yuedu/
幼教 > 时尚妈咪 > 职场妈妈	http://www.youjiao.com/ssmm/zhichang/
幼教 > 时尚妈咪 > 爸爸手记	http://www.youjiao.com/ssmm/bbsj/
幼教 > 时尚妈咪 > 旅游度假	http://www.youjiao.com/ssmm/lydj/
幼教 > 时尚妈咪 > 都市家居	http://www.youjiao.com/ssmm/jiaju/
幼教 > 时尚妈咪 > 夫妻关系	http://www.youjiao.com/ssmm/fqgx/
幼教 > 时尚妈咪 > 妈咪心理	http://www.youjiao.com/ssmm/mmxl/

幼教 > 专题 > 精彩专题	http://www.youjiao.com/zt/jczt/index.shtml

幼教 > 广州 > 2016广州幼升小	http://www.youjiao.com/gz/2016ysx/
幼教 > 广州 > 广州重点小学	http://www.youjiao.com/gz/zdxx/
'''


class YoujiaoSpider(Spider):
    # name='ry'
    name = 'youjiao'
    download_delay = 5
    allowed_domains = ['youjiao.com']
    # start_urls = ['http://www.youjiao.com/sejy/qnkf/']
  #  start_urls = ['http://www.youjiao.com/etly/kpzs/gxkj/']
    
    start_urls = ['http://www.youjiao.com/ysx/ysx/', 'http://www.youjiao.com/ysx/zhengce/',
                  'http://www.youjiao.com/ysx/zsjz/', 'http://www.youjiao.com/ysx/zexiao/',
                  'http://www.youjiao.com/ysx/zhinan/', 'http://www.youjiao.com/ysx/xuequfang/',
                  'http://www.youjiao.com/ysx/rxcs/', 'http://www.youjiao.com/ysx/shiti/',
                  'http://www.youjiao.com/ysx/xianchang/', 'http://www.youjiao.com/ysx/yxxj/',
                  'http://www.youjiao.com/ysx/jingyan/', 'http://www.youjiao.com/ysx/mxdt/',
                  'http://www.youjiao.com/ysx/zdxx/', 'http://www.youjiao.com/sejy/czrj/',
                  'http://www.youjiao.com/sejy/wenti/', 'http://www.youjiao.com/sejy/jtjy/',
                  'http://www.youjiao.com/sejy/qnkf/', 'http://www.youjiao.com/sejy/yspy/',
                  'http://www.youjiao.com/sejy/etxl/', 'http://www.youjiao.com/sejy/tsdx/',
                  'http://www.youjiao.com/sejy/yyxx/', 'http://www.youjiao.com/sejy/pyxx/',
                  'http://www.youjiao.com/sejy/jyzj/', 'http://www.youjiao.com/sejy/gwjy/',
                  'http://www.youjiao.com/sejy/jyxd/', 'http://www.youjiao.com/sejy/ryzd/',
                  'http://www.youjiao.com/sejy/zaojiao/quming/', 'http://www.youjiao.com/sejy/zaojiao/ceping/',
                  'http://www.youjiao.com/sejy/zaojiao/yyxw/', 'http://www.youjiao.com/sejy/zaojiao/czzb/',
                  'http://www.youjiao.com/sejy/zaojiao/zqjy/', 'http://www.youjiao.com/sejy/zaojiao/xgpy/',
                  'http://www.youjiao.com/sejy/zaojiao/qinzijiaoliu/', 'http://www.youjiao.com/sejy/zaojiao/zjyx/',
                  'http://www.youjiao.com/sejy/zaojiao/wanju/', 'http://www.youjiao.com/sejy/zaojiao/zlkf/',
                  'http://www.youjiao.com/sejy/taijiao/tjff/', 'http://www.youjiao.com/sejy/taijiao/tjxd/',
                  'http://www.youjiao.com/sejy/taijiao/yuyan/', 'http://www.youjiao.com/sejy/taijiao/ydtj/',
                  'http://www.youjiao.com/sejy/taijiao/fmtj/', 'http://www.youjiao.com/sejy/taijiao/yinyue/',
                  'http://www.youjiao.com/sejy/taijiao/tjgs/', 'http://www.youjiao.com/sejy/taijiao/tjyy/',
                  'http://www.youjiao.com/sejy/taijiao/mrtj/', 'http://www.youjiao.com/sejy/taijiao/yytj/',
                  'http://www.youjiao.com/etly/zlyx/', 'http://www.youjiao.com/etly/etgq/',
                  'http://www.youjiao.com/etly/etgs/', 'http://www.youjiao.com/etly/seyy/',
                  'http://www.youjiao.com/etly/gushi/', 'http://www.youjiao.com/etly/lianxi/',
                  'http://www.youjiao.com/etly/erge/', 'http://www.youjiao.com/etly/youxi/',
                  'http://www.youjiao.com/etly/etdw/', 'http://www.youjiao.com/etly/mhsj/',
                  'http://www.youjiao.com/etly/sqgs/', 'http://www.youjiao.com/etly/qzgs/',
                  'http://www.youjiao.com/etly/kpzs/gxkj/', 'http://www.youjiao.com/etly/kpzs/zwls/',
                  'http://www.youjiao.com/etly/kpzs/twdl/', 'http://www.youjiao.com/etly/kpzs/kpcs/',
                  'http://www.youjiao.com/etly/kpzs/smkx/', 'http://www.youjiao.com/etly/kpzs/rtkx/',
                  'http://www.youjiao.com/etly/kpzs/jckx/', 'http://www.youjiao.com/etly/kpzs/yyys/',
                  'http://www.youjiao.com/etly/kpzs/hjkx/', 'http://www.youjiao.com/etly/kpzs/jskx/',
                  'http://www.youjiao.com/etly/kpzs/rcsh/', 'http://www.youjiao.com/etly/kpzs/msqw/',
                  'http://www.youjiao.com/etly/etdw/', 'http://www.youjiao.com/etly/etwj/',
                  'http://www.youjiao.com/jkbb/huli/', 'http://www.youjiao.com/jkbb/yfjj/',
                  'http://www.youjiao.com/jkbb/mianyi/', 'http://www.youjiao.com/jkbb/jibing/',
                  'http://www.youjiao.com/jkbb/zjdy/', 'http://www.youjiao.com/jkbb/jkys/',
                  'http://www.youjiao.com/jkbb/yewy/', 'http://www.youjiao.com/jkbb/fushi/',
                  'http://www.youjiao.com/jkbb/mmyy/', 'http://www.youjiao.com/jkbb/etyy/',
                  'http://www.youjiao.com/jkbb/bbyp/', 'http://www.youjiao.com/shipu/yqsp/',
                  'http://www.youjiao.com/shipu/fushi/', 'http://www.youjiao.com/shipu/etsp/',
                  'http://www.youjiao.com/shipu/jtsp/', 'http://www.youjiao.com/shipu/chsp/',
                  'http://www.youjiao.com/shipu/pengren/', 'http://www.youjiao.com/shipu/meishi/',
                  'http://www.youjiao.com/ssmm/mswh/', 'http://www.youjiao.com/shipu/meirong/',
                  'http://www.youjiao.com/shipu/jianfei/', 'http://www.youjiao.com/yyzn/zhunbeihuaiyun/huaiyunzhishi/',
                  'http://www.youjiao.com/yyzn/zhunbeihuaiyun/yunqianzhunbei/',
                  'http://www.youjiao.com/yyzn/zhunbeihuaiyun/huaiyunjinji/',
                  'http://www.youjiao.com/yyzn/zhunbeihuaiyun/yichuanyousheng/',
                  'http://www.youjiao.com/yyzn/zhunbeihuaiyun/biyunliuchan/',
                  'http://www.youjiao.com/yyzn/zhunbeihuaiyun/buyunbuyu/',
                  'http://www.youjiao.com/yyzn/zhunbeihuaiyun/shengnanshengnv/', 'http://www.youjiao.com/yyzn/gongju/',
                  'http://www.youjiao.com/ssmm/xmdr/', 'http://www.youjiao.com/ssmm/jtlc/',
                  'http://www.youjiao.com/ssmm/fscl/', 'http://www.youjiao.com/ssmm/mswh/',
                  'http://www.youjiao.com/ssmm/pxgx/', 'http://www.youjiao.com/ssmm/meirong/',
                  'http://www.youjiao.com/ssmm/sushen/', 'http://www.youjiao.com/ssmm/yuedu/',
                  'http://www.youjiao.com/ssmm/zhichang/', 'http://www.youjiao.com/ssmm/bbsj/',
                  'http://www.youjiao.com/ssmm/lydj/', 'http://www.youjiao.com/ssmm/jiaju/',
                  'http://www.youjiao.com/ssmm/fqgx/', 'http://www.youjiao.com/ssmm/mmxl/']
                  

    # url_pattern=[r'.*rank=sale&type=hot.*']
    url_pattern = [r'id=.*']
    url_extractor = LxmlLinkExtractor(allow=url_pattern)
    item_dict = {}

    cj = cookielib.LWPCookieJar()
    cookie_support = urllib2.HTTPCookieProcessor(cj)
    opener = urllib2.build_opener(cookie_support, urllib2.HTTPHandler)
    urllib2.install_opener(opener)

    def start_requests(self):
        for url in self.start_urls:
            """爬取网站分页"""
            # for i in range(2, 3):
            #     next_url = url + 'index_' + str(i) + '.shtml'
            #     yield SplashRequest(next_url, callback=self.parse, args={
            #         'wait': 0.5, 'html': 1,
            #     })
            yield SplashRequest(url, callback=self.parse, args={
                'wait': 0.5, 'html': 1,
            })

    def parse(self, response):
        # print response.url
        lis = response.xpath("//*[@id='content']/li/div/a/@href").extract()
        # print lis
        for li in lis:
            news_href = li
            """判断网页是否已经被爬取过"""
            news_id = news_href.split('/')[-1].split('.')[0]
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
                    print "<+_+>-----已经存在HDFS与Mysql中-----<+_+>"
                    pass
                else:
                    yield Request(news_href, callback=self.get_content)
            else:
                if ret[0] == 1 and txt_name in link_hdfs.list(yesterday_dir):
                    print "<+_+>-----已经存在HDFS与Mysql中-----<+_+>"
                    pass
                elif ret[0] == 1 and txt_name in link_hdfs.list(today_dir):
                    print "<+_+>-----已经存在HDFS与Mysql中-----<+_+>"
                else:
                    yield Request(news_href, callback=self.get_content)

    def get_content(self, response):
        item = YoujiaoItem()
        """提取info_id"""
        info_id = response.url.split('/')[-1].split('.')[0]
        item['info_id'] = info_id

        """提取新闻标题"""
        title = response.xpath("//div[@class='wrapper']/div/div[@class='wrapper']/div[@class='container']"
                               "/div[@class='content']/h1/text()").extract()
        item['title'] = title[0]

        """提取新闻地址"""
        url = response.url
        item['link'] = url
        # url_id = url.split('/')[-1].split('.')[0]
        # print url_id

        """提取新闻发布时间"""
        o_time = response.xpath("//p[@class='data']/text()").extract()[-1]
        # print time
        online_time = o_time.replace('(', '').replace(')', '').replace(' ', '').replace(':', '').replace('-', '')
        item['online_time'] = online_time

        """提取新闻来源"""
        news_from = response.xpath("//p[@class='data']/em/text()").extract()
        try:
            item['news_from'] = news_from[0]
        except IndexError:
            item['news_from'] = news_from

        """提取新闻来源地址"""
        item['source'] = None

        """提取新闻关键字"""
        tags = response.xpath("//*[@id='xg_tag']/span/a/text()").extract()
        tag = ','.join(tags)
        item['tag'] = tag

        """提取新闻描述"""
        desc = response.xpath("//meta[@name='description']/@content").extract()
        item['news_description'] = desc[0]

        """提取新闻作者"""
        try:
            author = response.xpath("//p[@class='data']/text()").extract()[1].replace(' ', '')
            author = author.split('：')[-1]
            item['author'] = author
        except:
            author = None
            item['author'] = author

        """提取版块"""
        section = response.xpath("//div[@class='logoArea']/span/a/text()").extract()
        section = '-'.join(section)
        item['section'] = section

        """提取评论数"""
        try:
            cmt_url = response.xpath("//*[@id='bbs']/iframe[@id='rating']/@src").extract()[0]
            cmt_req = urllib2.Request(cmt_url)
            cmt_html = urllib2.urlopen(cmt_req).read()
            # print cmt_html
            cmt_re = re.findall(r'<span class="talk">(.*?)</span>', cmt_html)
            item['comment_count'] = cmt_re[0]
        except:
            item['comment_count'] = None

        """提取内容"""
        soup = BeautifulSoup(response.text, 'lxml')
        [script.extract() for script in soup.find_all('script')]  # 去除script标签
        [style.extract() for style in soup.find_all('style')]  # 去除style标签
        text_soup = soup.find(class_='content_txt').get_text()
        if '上一页' in text_soup:
            text = text_soup.split('上一页')[0]
        else:
            text = text_soup.split('幼教网微信')[0]
        text = text.split('\n')
        # text = response.xpath("//div[@class='content_txt']/p/text()").extract()
        body = []
        for t_body in text:
            bdy = t_body.replace('\r', '').replace('\n', '').replace('\t', '').replace(u'\xa0', '')
            body.append(bdy)
        """提取网页内容分页"""
        try:
            next_urls = response.xpath("//div[@class='pages']/a/@href").extract()[:-1]
            header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                    'Chrome/55.0.2883.87 Safari/537.36'}
            for i in range(len(next_urls)):
                if item['info_id'] in next_urls[i]:
                    next_url = next_urls[i]
                    next_url_req = urllib2.Request(next_url, headers=header)
                    next_url_html = urllib2.urlopen(next_url_req).read()
                    soup_body = BeautifulSoup(next_url_html, 'html.parser').find(class_='content_txt').get_text()
                    n_body = soup_body.split('上一页')[0]
                    n_body = n_body.split('\n')
                    for bdy in n_body:
                        n_by = bdy.replace('\n', '').replace('\r', '').replace('\t', '').replace(u'\xa0', '')
                        # print n_by
                        body.append(n_by)
        except Exception, e:
            print Exception, "没有下一页内容", e
            pass
        while '' in body:
            body.remove('')
        item['news_body'] = body

        return item
