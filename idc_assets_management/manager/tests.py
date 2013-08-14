#coding:utf-8
import os
import sys
reload(sys)
sys.setdefaultencoding('utf8')

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "idc_assets_management.settings.local")
sys.path.append('/opt/py_env/xiaojun/idc_assets_management/idc_assets_management')
"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase

from .models import *

class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)

class ComputerRoomTestCreate(TestCase):
    def setUp(self):
        ComputerRoom.objects.create(room_name='银沙', room_agent='北京看丹桥',
                                   isp='电信', room_broadband='1000M', region='北京',
                                   qq_group='324098', contact='许冥', phone='1239334370',
                                   address = '北京五道口')

    def test_computerroom_get_name(self):
        yinsha =  ComputerRoom.objects.get(room_name="银沙")
        self.assertEqual(yinsha.__unicode__, u'银沙')


def my_func(a_list, idx):
    """
    >>> a = ['larry', 'curly', 'moe']
    >>> my_func(a, 0)
    'larry'
    >>> my_func(a, 1)
    'curly'
    >>> my_func(a, 2)
    'moe'
    """
    return a_list[idx]

if __name__ == '__main__':
    import doctest
    doctest.testmod()
