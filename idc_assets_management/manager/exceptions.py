#!/usr/bin/env python
#coding:utf-8
class BtnFuncNotDefine(Exception):
    "Django is somehow improperly configured"
    pass

class BtnValueError(Exception):
    "This means the btn value is not a valid value"
    pass
