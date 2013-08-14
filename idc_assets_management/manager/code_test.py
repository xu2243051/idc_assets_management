#!/usr/bin/env python
#coding:utf-8
import os
import sys
reload(sys)
sys.setdefaultencoding('utf8')

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "idc_assets_management.settings.local")
sys.path.append('/opt/py_env/xiaojun/idc_assets_management/idc_assets_management')

def add_initial_to_choices(choices):
    """
    增加一个初始的选项，改选项为空值
    """
    choices_li = list(choices)
    choices_li.insert(0, ('--------', ''))
    return choices_li

if __name__ == '__main__':
    from django.db import connection
    from manager.models import ComputerRoom

    a = ((1,1),(2,2))
    print add_initial_to_choices(a)


