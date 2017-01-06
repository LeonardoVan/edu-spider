#! usr/bin/env python
# coding: utf-8


from .sql import Sql
from twisted.internet.threads import deferToThread
from new_sohu.items import NewSohuItem


class MysqlPipeline(object):

    def process_item(self, item, spider):
        if isinstance(item, NewSohuItem):
            news_id = item['info_id']
            ret = Sql.select_name(news_id)
            if ret[0] == 1:
                print "<+_+>-----已经存在MySql中-----<+_+>"
                return item
            else:
                info_id = item['info_id']
                source = item['source']
                title = item['title']
                online_time = item['online_time']
                section = item['section']
                tag = item['tag']
                author = item['author']
                link = item['link']
                Sql.insert_t_informations(info_id, source, title, online_time, section, tag, author, link)
                print "<<<<<<<<<<开始存在Mysql>>>>>>>>>>"
                return item

