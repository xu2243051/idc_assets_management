#coding:utf-8
from django.db import models
from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib.auth.models import User, Group #group 代表代理
from django.core.exceptions import ValidationError

from .custon_manager import  GroupManager

class ExtraMethodMixin(object):
    """
    verbose_name
    """

    def get_field_value(self, field):
        """返回显示的值，而不是单纯的数据库中的值"""
        try:
            return self._get_FIELD_display(field)
        except :
            return field._get_val_from_obj(self)

    def get_fields(self):
        '''返回字段名及其对应值的列表'''
        field_list = []
        for field in self.__class__._meta.fields:
            if field.verbose_name:
                field_list.append((field.verbose_name, self.get_field_value(field)))
            else:
                field_list.append((field.name, self.get_field_value(field)))
        return field_list


    def get_absolute_url(self):
        """
        返回object详细内容的链接
        """
        url_name = '%s_%s' %(self.__class__.__name__.lower(), 'detail')
        return reverse_lazy(url_name, kwargs={'pk':self.pk})

    def get_detail_url(self):
        """
        返回object详细内容的链接
        """
        url_name = '%s_%s' %(self.__class__.__name__.lower(), 'detail')
        return reverse_lazy(url_name, kwargs={'pk':self.pk})

    def get_update_url(self):
        """
        返回object的更新链接
        """
        url_name = '%s_%s' %(self.__class__.__name__.lower(), 'update')
        return reverse_lazy(url_name, kwargs={'pk':self.pk})

    def get_delete_url(self):
        """
        返回object的删除链接
        """
        url_name = '%s_%s' %(self.__class__.__name__.lower(), 'delete')
        return reverse_lazy(url_name, kwargs={'pk':self.pk})

    def get_list_url(self):
        """
        返回objects的列表链接
        """
        url_name = '%s_%s' %(self.__class__.__name__.lower(), 'list')
        return reverse_lazy(url_name)

    def get_upload_url(self):
        """
        返回objects的列表链接
        """
        url_name = '%s_%s' %(self.__class__.__name__.lower(), 'upload')
        return reverse_lazy(url_name)

    def get_class_name(self):
        """
        return the name of self
        """
        return self.__class__.__name__

    def get_moudle_name(self):
        return self.__module__.split('.')

    def get_app_label(self):
        """
        这个方法只有当他是一个Model的其中一个父类才生效
        """
        return self._meta.app_lable

    def get_verbose_name(self):
        """
        返回类的显示名称
        """
        if self._meta.verbose_name:
            return self._meta.verbose_name
        else:
            return self.get_class_name()



# Create your models here.
class ComputerRoom(ExtraMethodMixin, models.Model):
    room_name = models.CharField('机房名', max_length=150, unique=True)
    room_agent = models.CharField('机房代理商', max_length=150)
    isp = models.CharField('ISP', max_length=150)
    room_broadband = models.CharField('带宽', max_length=150)
    region = models.CharField('所属区域', max_length=150)
    qq_group = models.CharField('QQ群', max_length=300, blank=True,
                                help_text="多个QQ群，逗号分隔")
    contact = models.CharField('负责人', max_length=150, blank=True)
    phone = models.CharField('电话', max_length=300, blank=True,
                            help_text="多个电话，逗号分隔")
    address = models.CharField('机房地址', max_length=300, blank=True)
    create_date = models.DateTimeField('创建时间', auto_now_add=True)
    update_date = models.DateTimeField('修改时间', auto_now_add=True, auto_now=True)

    objects = models.Manager()
    group = GroupManager()

    class Meta:
        verbose_name = "机房"
        verbose_name_plural = "机房"

    def __unicode__(self):
        return self.room_name

    def clean_fields(self, *args, **kwargs):
        """
        如果qq_group和phone不是逗号分隔的数字串，引发ValidationError
        """
        import re
        p = re.compile(r'(\d+,?)+$')
        if not p.match(self.qq_group):
            raise ValidationError({'qq_group':['无效的数据']})
        if not p.match(self.phone):
            raise ValidationError({'phone':['无效的数据']})
        super(ComputerRoom, self).clean_fields(*args, **kwargs)

default_error_messages = {
    'required': u'这个字段是必填的',
    'invalid': u'请输入一个有效的数据',
            }

class ComputerRack(ExtraMethodMixin, models.Model):
    rack_num = models.CharField('机柜号', max_length=150)
    computerroom = models.ForeignKey(ComputerRoom, verbose_name="所属机房")
    person_in_charge = models.CharField('负责人', max_length=150)
    project_team = models.CharField('项目组', max_length=150)
    rack_switch_port = models.CharField('交换机端口', max_length=150,
                                       help_text="机柜交换机端口-上联端口 <br \> eg. <strong>24-3</strong>")
    rack_capacity = models.IntegerField('机柜设备容量')
    num_of_computer_in_rack = models.IntegerField('机柜上机器数量')
    rack_available_capacity = models.IntegerField('机柜剩余容量', editable=False)
    open_date = models.DateField('开通日期', auto_now_add=True, editable=True)
    comment = models.TextField('备注', max_length=150, blank=True)
    create_date = models.DateTimeField('创建时间', auto_now_add=True)
    update_date = models.DateTimeField('修改时间', auto_now_add=True, auto_now=True)

    objects = models.Manager()
    group = GroupManager()

    class Meta:
        verbose_name = "机柜"
        verbose_name_plural = "机柜"
        unique_together = ['rack_num', 'computerroom']


    def __unicode__(self):
        return '%s:%s' % (self.computerroom, self.rack_num)
    __unicode__.short_description = '机柜标识'

    def save(self, *args, **kwargs):
        result = self.rack_capacity - self.num_of_computer_in_rack
        self.rack_available_capacity  = result if result > 0 else 0
        return super(ComputerRack, self).save(*args, **kwargs)

    def clean_fields(self, *args, **kwargs):
        """
        """
        import re
        #验证rack_switch_port数据，必须是 数字-数字 的格式
        if not re.match(r'\d+ *- *\d+', self.rack_switch_port):
            raise ValidationError({'rack_switch_port':['无效的数据']})

    def return_rack_available_capacity(self):
        return self.rack_available_capacity * self.rack_num
    return_rack_available_capacity.short_description = '这是函数生成的值'

class Computer(ExtraMethodMixin, models.Model):
    computerroom = models.ForeignKey(ComputerRoom, verbose_name="机房")
    computerrack = models.ForeignKey(ComputerRack, verbose_name="机柜")
    ip = models.GenericIPAddressField('默认IP',protocol='both', unpack_ipv4=True)
    extra_ip = models.CharField('额外IP', max_length=300, default='0.0.0.0',
                               help_text="多个IP，逗号分隔")
    computer_type = models.CharField('设备型号', max_length=300)
    computer_code = models.CharField('设备编码', max_length=300)
    asset_code = models.CharField('资产编码', max_length=300)
    game = models.CharField('游戏', max_length=300)
    person_manage = models.CharField('机器管理员', max_length=300)
    online_date = model.DateTime('上架日期', auto_now_add=True)
    switch_port = model.Charfield('上联交换机端口', max_length=300)
    #状态可能要用choice
    status = models.CharField('状态', max_length=300)



    create_date = models.DateTimeField('创建时间', auto_now_add=True)
    update_date = models.DateTimeField('修改时间', auto_now_add=True, auto_now=True)

    objects = models.Manager()
    group = GroupManager()
