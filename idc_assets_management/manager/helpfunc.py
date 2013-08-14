#!/usr/bin/env python
#coding:utf-8
def get_attr_info(obj, attr):
    """
    对list_filter的element进行处理，如果是field，返回name，value，verbose_name
        如果是函数，返回回func name， func value， func的short_description
    """
    try:
        field = obj._meta.get_field(attr)
        verbose_name = field.verbose_name if field.verbose_name else field.name
        name = field.name

        try:
            # 如果是有choices, 下面将获得choice的显示部分
            value = obj._get_FIELD_display(field)
        except :
            # 外键获取得到的是PK值
            value = field._get_val_from_obj(obj)

        #如果是外键，获得对应外键的的object
        if isinstance(field, models.ForeignKey):
            pk = value
            parent_model = field.related.parent_model
            value = parent_model.objects.get(pk=pk)

    except:
        try:
            fun = getattr(obj, attr)
            if getattr(fun, '__func__', None):  #判断是否函数， 
                name = attr
                verbose_name = fun.short_description if fun.short_description else attr
                value = fun()
        except:
            raise ValidationError,  'attr 必须是一个字符串，并且是类的field或者function'

    return {'name':name, 'value':value, 'verbose_name':verbose_name}
