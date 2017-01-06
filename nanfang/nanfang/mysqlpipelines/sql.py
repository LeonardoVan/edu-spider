#! usr/bin/env python
# -*- coding: utf-8 -*-
import mysql.connector
from nanfang import settings


MYSQL_HOSTS = settings.MYSQL_HOSTS
MYSQL_USER = settings.MYSQL_USER
MYSQL_PASSWORD = settings.MYSQL_PASSWORD
MYSQL_PORT = settings.MYSQL_PORT
MYSQL_DB = settings.MYSQL_DB

cnx = mysql.connector.connect(user=MYSQL_USER, password=MYSQL_PASSWORD, host=MYSQL_HOSTS, database=MYSQL_DB)
cur = cnx.cursor(buffered=True)


class Sql:
    @classmethod
    def insert_t_informations(cls, info_id, source, tag, title, section, online_time, author, link):
        sql = 'INSERT INTO t_informations (`info_id`, `source`, `tag`, `title`, `section`, `online_time`,' \
              ' `author`, `link`) ' \
              'VALUE (%(info_id)s, %(source)s, %(tag)s, %(title)s, %(section_)s, %(online_time)s, %(author)s, %(link)s)'
        value = {
            'info_id': info_id,
            'source': source,
            'tag': tag,
            'title': title,
            'section_': section,
            'online_time': online_time,
            'author': author,
            'link': link
        }
        cur.execute(sql, value)
        cnx.commit()

    @classmethod
    def select_name(cls, news_id):
        sql = "SELECT EXISTS(SELECT 1 FROM t_informations WHERE info_id=%(info_id)s)"
        value = {
            'info_id': news_id
        }
        cur.execute(sql, value)
        return cur.fetchall()[0]
