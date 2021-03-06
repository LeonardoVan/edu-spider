#! usr/bin/env python
# -*- coding: utf-8 -*-


from .sql import Sql
from ntes.items import NtesItem


class MysqlPipeline(object):

    def process_item(self, item, spider):
        if isinstance(item, NtesItem):
            news_id = item['info_id']
            ret = Sql.select_name(news_id)
            if ret[0] == 1:
                print "<+_+>-----已经存在MySql中-----<+_+>"
                return item
            else:
                info_id = item['info_id']
                source = item['source']
                tag = item['tag']
                title = item['title']
                section = item['section']
                online_time = item['online_time']
                author = item['author']
                link = item['link']
                Sql.insert_t_informations(info_id, source, tag, title, section, online_time, author, link)
                print "<<<<<<<<<<开始保存在Mysql>>>>>>>>>>"
                return item

