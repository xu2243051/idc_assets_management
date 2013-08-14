#!/usr/bin/env python
#coding:utf-8
from django import forms
from django.forms import SelectMultiple
#from django.forms.extras.widgets import SelectDateWidget

from .models import ComputerRoom
from .helpfunc import get_attr_info

def add_initial_to_choices(choices):
    """
    增加一个初始的选项，改选项为空值
    """
    choices_li = list(choices)
    choices_li.insert(0, ('', '--------'))
    return choices_li

def get_choices_from_model(model):
    """
    返回缺省model.list_display+model所有字段的value和verbose_name组成的元组列表
    """
    choices =  []
    fields = model._meta.fields
    field_names = [field.name for field in fields]
    field_names.remove('id')

    #这里确定model是否有数据，必须至少有1行数据才能生成checkbox的选择选项
    objs = model.objects.all()
    if objs:
        obj = objs[0]
    else:
        #如果model为空，生成的choices为None
        return choices

    if obj:
        for attr in field_names:
            verbose_name = get_attr_info(obj, attr).get('verbose_name')
            value = attr
            choices.append((value, verbose_name))

    return choices

class UserLoginForm(forms.Form):
    required_css_class = 'required'
    error_css_class = 'error'
    user = forms.CharField(label='用户')
    passwd = forms.CharField(label='密码', widget = forms.TextInput(attrs={'type':'password'}))

class AjaxCommandForm(forms.Form):
    """
    这个form是为了listview中的post创建的

    """
    pk = forms.CharField(label='主键值')
    command = forms.CharField(label='值')
    data = forms.CharField(label='数据', required=False)

class UploadForm(forms.Form):
    filename = forms.FileField(label="请选择上传文件", required=True)

class ComputerRoomSearchForm(forms.Form):
    """
    定义ComputerRoom列表的过滤条件
    """
    room_name = forms.ChoiceField(label="机房名", required=False, 
                                  choices = add_initial_to_choices(ComputerRoom.group.get_group_in_tuple('room_name')))
    room_agent = forms.ChoiceField(label="机房代理商", required=False,
                                choices = add_initial_to_choices(ComputerRoom.group.get_group_in_tuple('room_agent')))
    #download_filename = forms.CharField(label="请输入文件名", required=False, help_text="不添为download.csv")

class ComputerRoomSelectForm(forms.Form):
    field_names = forms.MultipleChoiceField(label='请选择显示的字段',
                                            choices=get_choices_from_model(ComputerRoom), required=False,
                                            widget=forms.CheckboxSelectMultiple(attrs={'form':'base_form'}))


from .models import ComputerRack
class ComputerRackSearchForm(forms.Form):
    """
    定义ComputerRack列表的过滤条件
    """
    computerroom = forms.ModelChoiceField(queryset=ComputerRoom.objects.all(), label="机房", required=False)
    person_in_charge  = forms.ChoiceField(label="负责人", required=False,
                                choices = add_initial_to_choices(ComputerRack.group.get_group_in_tuple('person_in_charge ')))

class ComputerRackSelectForm(forms.Form):
    field_names = forms.MultipleChoiceField(label='请选择显示的字段',
                                            choices=get_choices_from_model(ComputerRack), required=False,
                                            widget=forms.CheckboxSelectMultiple(attrs={'form':'base_form'}))
