#!/usr/bin/env python
#coding:utf-8
from django.db  import models
class GroupManager(models.Manager):
    def get_query_set(self):
        return super(GroupManager, self).get_query_set()
    
    def get_group_in_tuple(self, field_name):
        """
        得到field_name对应的字段的指，不重复，并且生成元组，
        给form 中的choices使用
        """
        table_name = self.model._meta.db_table
        kwargs = {}
        kwargs.update(table_name=table_name)
        kwargs.update(field_name=field_name)

        sql = """SELECT %(field_name)s from %(table_name)s GROUP by %(field_name)s;""" % kwargs
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute(sql)

        result_list = []
        for row in cursor.fetchall():
            result_list.append((row[0], row[0]))


        return tuple(result_list)
