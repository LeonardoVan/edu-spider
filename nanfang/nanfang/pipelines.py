# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import datetime
import os
import json
from hdfs import *


class SavetoHdfs(object):
    @staticmethod
    def process_item(item, spider):
        if spider.name != "nanfangedu":
            return item
        link_hdfs = InsecureClient("http://192.168.10.117:50070", user='hadoop')  # Base HDFS web client
        today = datetime.date.today()
        today_dir = '/testdir' + '/' + str(today)
        dir_ls = link_hdfs.list('/testdir')
        if str(today) not in dir_ls:
            link_hdfs.makedirs(today_dir)
        txt_name = str(item['info_id']) + '.txt'
        txt_path = today_dir + '/' + txt_name
        records = dict(item)
        # 转成json的格式，编码转成utf-8
        uncode = json.dumps(records, ensure_ascii=False, indent=2).encode('utf-8') + '\n'
        yesterday = today - datetime.timedelta(days=1)
        yesterday_dir = '/testdir' + '/' + str(yesterday)
        if str(yesterday) not in dir_ls:
            if txt_name in link_hdfs.list(today_dir):
                print "<+_+>-----已经存在HDFS中-----<+_+>"
                return item
            else:
                link_hdfs.write(txt_path, data=uncode)
                print ">>>>>>>>>>>>>>Saved to HDFS>>>>>>>>>>>>>>>>>>>"
                return item
        else:
            if txt_name in link_hdfs.list(yesterday_dir):
                print "<+_+>-|-|-|-|-已经存在HDFS中-|-|-|-|-<+_+>"
                return item
            elif txt_name in link_hdfs.list(today_dir):
                print "<+_+>-|-|-|-|-已经存在HDFS中-|-|-|-|-<+_+>"
                return item
            else:
                link_hdfs.write(txt_path, data=uncode)
                print ">>>>>>>>>>>>>>Saved to HDFS>>>>>>>>>>>>>>>>>>>"
                # with link_hdfs.write(txt_path, encoding='utf-8') as writer:
                # json.dump(records, writer)
                return item


class NanfangPipeline(object):
    @staticmethod
    def process_item(item, spider):
        print "<<<--<<-<噜啦啦噜啦啦噜啦噜啦嘞>->>-->>>"
        if spider.name != "nanfangedu":
            return item
        if item.get('info_id', None) is None:
            return item
        now = datetime.datetime.now()
        id_ = item['info_id']
        # print os.path.abspath('.')
        path = os.path.abspath('.') + '\\theResultofGM\\'
        file_ = path + now.strftime('%y%m%d') + '.' + id_ + '.txt'
        fo = open(file_, 'a+')
        fo.write(json.dumps(dict(item), ensure_ascii=False, indent=2).encode('utf-8') + "\n")
        fo.close()
        print ">>>>>>>>>>>>>>Saved to txt>>>>>>>>>>>>>>>>>>>"
        return item
