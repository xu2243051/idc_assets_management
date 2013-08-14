#!/usr/bin/env python
#coding:utf-8
#下面3行是因为出现了UnicodeDecodeError
import json
import sys
reload(sys)
sys.setdefaultencoding('utf-8') 

from django.db import models
from django.core.exceptions import ValidationError
from django.http import HttpResponse, HttpResponseRedirect
from django.template import Context, Template, loader

from .exceptions import BtnFuncNotDefine, BtnValueError

class ListDislayMixin(object):
    """
    参考tutorial  2 
    def was_published_recently(self):
        return self.pub_date >= timezone.now() - datetime.timedelta(days=1)
    was_published_recently.admin_order_field = 'pub_date'
    was_published_recently.boolean = True
    was_published_recently.short_description = 'Published recently?'
    """

    list_display = None
    link = None

    def get_link(self):
        """
        自定哪些字段将会是链接
        link 的类型是字符串、列表或者元组
        """
        if self.link:
            return self.link
        else:
            return None 

    def get_list_display(self, download_all=False):
        """
        download_all在DownLoadMixin中保留，来控制显示是否下载全部字段的数据，包括函数
        """

        if  download_all:
            """
            这个判断，是给下载当前数据用的，包括函数在内，返回所有字段
            """
            fields = self.model._meta.fields
            field_names = [field.name for field in fields]
            field_names.remove('id')
            all_list = field_names + self.list_display
            return  list(set(all_list))


        if self.list_display:
            return self.list_display
        else:
            raise

    def get_attr_info(self, obj, attr):
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


    def get_thead(self):
        """
        生成table的thead部分
        list_display 是field或者method的列表
        """
        list_display = self.get_list_display()
        verbose_names = []
        start = """<th>
                    <label class="checkbox">
                        <input type="checkbox" value="all">全选
                    </label>
                    </th>"""
        end = "<th>info</th>" 
        normal_td = '<th>%s</th>'
        tr = "<tr>%s</tr>"

        obj = self.object_list[0]

        for attr in list_display:
                verbose_names.append(self.get_attr_info(obj, attr).get('verbose_name'))

        for verbose_name in verbose_names:
            start = start + normal_td % verbose_name

        return tr %  (start + end)

    def get_tbody(self):
        """
        生成table的tbody部分
        """
        list_display = self.get_list_display()
        td_start = """
        <td>
        <label class="checkbox">
            <input type="checkbox"  value="%(pk)s" name="server"> %(counter)s
        </label>
        </td>
        """
        td_end = """
        <td class="info" id="%(pk)s"></td>
        """
        td_normal = '<td>%s</td>'
        td_link = '''<td><a href="%s">%s</a></td>''' #如果是链接，就用这个
        tr = "<tr>%s</tr>"
        rows = ''

        link = self.get_link()  #指定哪些字段是链接
        counter = 1
        for obj in self.object_list:
            # tds 是 td_start +  list_display生成的多个td + td_end
            tds = td_start
            for attr in list_display:
                # 在这里检查一个字段是否是链接
                if attr in link:
                    tds  += td_link % (obj.get_absolute_url() ,self.get_attr_info(obj, attr).get('value'))
                else:
                    tds  += td_normal % self.get_attr_info(obj, attr).get('value')

            # 一个object一行
            row = tr % (tds + td_end) % {'pk':obj.pk, 'counter':counter}
            # 增加一个回车，只是让页面源代码容易查看一点，对结果无影响 
            rows  = rows +   row + '\n'

            counter += 1 # the counter of current object
        return rows

    def as_table(self):
        """
        我这里的table，第一列是checkbox，最后一列是显示信息的, 中间才是list_display的内容
        """
        errors = {'no_record':""}
        table = """
                <table class="table table-striped table-hover table-condensed table-bordered">
                    <thead>
                        %(thead)s
                    </thead>
                    <tbody>
                        %(tbody)s
                    </tbody>
                </table>
                """
        thead = ''
        tbody = ''
        if self.object_list:
            thead = self.get_thead()
            tbody = self.get_tbody()
        else:
            pass


        return table  % {'thead':thead, 'tbody':tbody}


class Processmixin(object):
    """
    A mixin that renders a form on GET and processes it on POST.
    """
    def get(self, request, *args, **kwargs):
        """
        Handles GET requests and instantiates a blank version of the form.
        """
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        kwargs.update({'form':form})
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests, instantiating a form instance with the passed
        POST variables and then checked for validity.
        """
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    # PUT is a valid HTTP verb for creating (with a known URL) or editing an
    # object, note that browsers only support POST for now.
    def put(self, *args, **kwargs):
        return self.post(*args, **kwargs)

class BtnGroupMixin(object):
    """
    生成btn-group，并且定义对应的函数
    """
    btn_errors = {'func_not_define':'function %s has not define',
                  'invalid':'invalid value: %s'}
    # verbose_name value class
    # class 决定了html的jquery  click的处理
    btn_group = {'name':'时间处理',
                 'buttons':[
                     {'name':'显示机器时间', 'value':'show_time' },
                     {'name':'修改时间', 'value':'update time', 'class':'inputdate_command'},
                 ],
                 'default_class':'server_command',
                }
    btn_group2 = {'name':'关服',
                 'buttons':[
                     {'name':'3分钟关服', 'value':'3 minutes shutdown', 'class':'command'},
                     {'name':'reload', 'value':'reload'},
                 ],
                 'default_class':'ommand',
                }


    btn_groups = []
    #可以自定btn_group， 然后添加到btn_groups中
    btn_groups.append(btn_group)
    btn_groups.append(btn_group2)

    def check_btn_group(self):
        for btn_group in self.btn_groups:
            for btn in btn_group.get('buttons'):
                self.get_func(btn.get('value'))

        return 'success'

    def get_func(self, btn_value):
        """
        根据button的value获得对应的函数
        """
        function_name = self.get_function_name(btn_value)
        try:
            handler =  getattr(self, function_name)
        except:
            raise BtnFuncNotDefine(self.btn_errors['func_not_define'] % function_name)

        return handler

    def get_function_name(self, btn_value):
        """
        根据button的value获得对应的函数名
        """
        # 要定义的函数的前缀
        prefix = 'process_'

        import re
        p = re.compile(r'\W+')

        # 把所有非下划线、字母、数字的字符转换为下划线
        # 中文都会被转换，多个连续的会被转换为一个
        # asa  , a --> asa_a
        new_btnvalue = p.sub( '_', btn_value).strip('_').lower()
        if re.match(r'^[a-z0-9]+(_[a-z0-9]+)*$', new_btnvalue):
            function_name = prefix + new_btnvalue
        else:
            raise BtnValueError(self.btn_errors['invalid'] % (btn_value))
        return function_name

    def render_btngroups(self):
        """
        要求本view有model属性
        """
        app_label = self.model.__module__.split('.')[0]
        template_name = "%s/btn_group.html" % app_label
        html = ""
        t = loader.get_template(template_name)
        for btn_group in self.btn_groups:
            html +=t.render(Context(btn_group))

        return html


    def process_show_time(self, form):
        """
        更新客户端
        返回值: status, success 代表成功，其它代表失败,不存在也代表失败
        """
        cd = form.cleaned_data
        pk = cd['pk']
        server = self.model.objects.get(pk=pk)
        import myssh
        myconnect = myssh.my_pyssh(server.ip1) 
        stdin, stdout, stderr = myconnect.exec_com('''date "+%Y-%m-%d %H:%M:%S"''')
        
        return {'result': stdout.read().strip(), 'status':'success', 'error':stderr.read(), 'pk':pk}

    def form_valid(self, form):
        """
        处理post, 覆盖了其它mixins的form_valid， 在继承的时候必须在最左边
        这里的post都是link的点击
        获取value，这个决定了是当前mixin的哪个函数
        """
        command = form.cleaned_data['command']

        handler = self.get_func(command)
        result = handler(form)
        return self.render_to_ajax_response(result)




class ProcessAjaxPostmixin(object):
    """
    这个mixin是用来处理listview中ajax提交的POST
    """

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests, instantiating a form instance with the passed
        POST variables and then checked for validity.
        """
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        command = form.cleaned_data['command']
        context = {}
        context.update(command=command)

        return self.render_to_ajax_response(context)

    def render_to_ajax_response(self, context, **response_kwargs):
        """
        Return a HttpResponse, 
        translate context to json
        """
        response_kwargs['content_type']='application/json'
        return HttpResponse(self.convert_context_to_json(context), **response_kwargs)

    def convert_context_to_json(self, context):
        """Convert the context dictionary into a JSON object"""
        # Note: This is *EXTREMELY* naive; in reality, you'll need
        # to do much more complex handling to ensure that arbitrary
        # objects -- such as Django model instances or querysets
        # - can be serialized as JSON.
        return json.dumps(context)


class SearchMixin(object):
    """
    根据get的过滤条件过滤objects
    """
    def get_searchform_class(self):
        """
        返回searchform
        """
        if self.search_form_class:
            return self.search_form_class
        else:
            raise Exception('search_form_class没定义')

    def get_searchform(self, searchform_class):
        """
        生成search_form
        """
        return searchform_class(data=self.request.GET)
         

    def get_context_data(self, **kwargs):
        """
        添加一个searchform
        """
        searchform_class = self.get_searchform_class()
        search_form = self.get_searchform(searchform_class)
        kwargs.update(searchform=search_form)
        return super(SearchMixin, self).get_context_data(**kwargs)

    def  get_queryset(self):
        """
        根据get的条件过滤queryset
        """
        #下面4个保留字段不可以为searchform中的字段
        reserve_key = ['download', 'search', 'field_names', 'download_filename']

        queryset = super(SearchMixin, self).get_queryset()
        searchform_class = self.get_searchform_class()
        search_form = self.get_searchform(searchform_class)
        if search_form.is_valid():
            cleaned_data = search_form.cleaned_data
            for key in cleaned_data:
                if key in reserve_key:
                    pass
                elif cleaned_data[key]:
                    queryset = queryset.filter(**{key:cleaned_data[key]})

        return queryset

class DownLoadMixin(object):
    """
    根据download来决定是否导出文件，或者正常显示
    需要和ListDislayMixin一起使用
    """
    def get(self, request, *args, **kwargs):
        download = self.request.GET.get('download', None)
        if download:

            download_filename  = self.request.GET.get('download_filename', None)
            download_filename  = download_filename +'.csv'  if download_filename else 'download.csv'

            if len(download.split('_')) != 2:
                raise '%s is not a valid value of download' % download

            # download格式为 '%(queryset)s_%(fields)s'  
            # queryset和fields  都为all 或者current
            object_list = self.get_queryset() if download.split('_')[0] != 'all' else self.model.objects.all() 

            #是否下载所有字段
            download_all = False if download.split('_')[1] != 'all' else True
            list_display = self.get_list_display(download_all) 

            return self.render_to_csv(object_list, download_filename, list_display)

        else:
            return super(DownLoadMixin, self).get(request, *args, **kwargs)



    def render_to_csv(self, object_list, filename, list_display):
        response = HttpResponse(content_type='text/csv, charset=utf-8')
        response.write('\xEF\xBB\xBF')
        response['Content-Disposition'] = 'attachment; filename="%s"' % filename

        import csv
        writer = csv.writer(response)    
        if object_list:   
            obj = object_list[0]  
            verbose_names = []
            #导出字段信息 
            for attr in list_display:
                verbose_names.append(self.get_attr_info(obj, attr).get('verbose_name'))
            writer.writerow(verbose_names)

            #导出字段的值 
            for obj in object_list:
                value_list = []
                for attr in list_display:
                     value_list.append(self.get_attr_info(obj, attr).get('value'))
                writer.writerow(value_list)

        return response

class UpLoadMixin(object):
    upload_form_class = None


    def get_upload_form_class(self):
        if self.upload_form_class:
            return self.upload_form_class
        else:
            raise Exception('upload_form_class 没定义')

    def get(self, request, *args, **kwargs):
        """
        上传的时候，get的form是upload_form
        """
        form_class = self.get_upload_form_class()
        form = self.get_form(form_class)
        return self.render_to_response(self.get_context_data(form=form))

    def post(self, request, *args, **kwargs):
        form_class = self.get_upload_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        model_form_class = self.get_form_class()
        import csv
        upload_file = self.request.FILES.get('filename')
        spamreader = csv.reader(upload_file, quotechar='"', delimiter=',')

        fields = self.model._meta.fields
        field_names= [field.name for field in fields]
        #去除id，因为增加页面没有ID
        field_names.remove('id')
        for row in spamreader:
            k = len(row)
            if k == 0 :
                #跳过空行
                continue

            #这里获得的是model的form class
            data = dict(map(lambda x, y: (x,y) , field_names, row))
            form_class = self.get_form_class()
            obj = None
            if self.model.objects.filter(**{field_names[0]:row[0]}):
                # 过滤第一个字段，如果有多个数据，取第一个
                # 这里是防止反复创建已经存在的数据
                obj = self.model.objects.filter(**{field_names[0]:row[0]})[0]
            form = form_class(data=data, instance=obj)

            if form.is_valid():
                obj = form.save()
            else:
                # 如果是select框， 显示内容和value是不同的，上传数据不可能让人输入value值
                # 所以这里要进行处理，这里暂时处理 ChoiceField
                for key in form.errors: # form.errors 是<class 'django.forms.util.ErrorDict'>
                    form_field = form.fields.get(key) #获得出错的field， 这里的form_field 是对应的field class
                    try :
                        for value, verbose in form_field.choices:
                            if data.get(key) == verbose:
                                data.update({key:value})
                    except AttributeError:
                        raise Exception('没有处理好所有的转换，比如checkbox或者其它的情况还没处理,只处理了select')
                    finally:
                        #以为可能已经有一些select的数据转换了，所以需要重新初始一次form
                        form = form_class(data=data, instance=obj)
                        if form.is_valid():  
                            obj = form.save()
                        else:
                            return self.render_to_response(self.get_context_data(form=form))

        return HttpResponseRedirect(obj.get_list_url())
            

        return HttpResponse(data)
        HttpResponseRedirect(self.get_success_url())

    def get_form_kwargs(self):
        """
        Returns the keyword arguments for instantiating the form.
        """
        kwargs = {'initial': self.get_initial()}
        if self.request.method in ('POST', 'PUT'):
            kwargs.update({
                'data': self.request.POST,
                'files': self.request.FILES,
            })
        return kwargs

class FieldNameSelectMixin(object):
    """
    使得listview可以自定义显示哪些字段
    MRO必须在ListDislayMixin前面，因为重定义了ListDislayMixin的get_list_display
    FieldNameSelectMixin必须和ListDislayMixin一起继承
    """

    #下面这个参数是{{Model}}SelectForm中定义，这个Form只有这个字段
    form_field_name = 'field_names'
    fieldname_multiple_select_form_class = None


    def get_fieldname_multiple_select_form_class(self):
        """
        返回fieldname_multiple_select_form_class
        """
        if self.fieldname_multiple_select_form_class:
            return self.fieldname_multiple_select_form_class
        else:
            raise Exception('fieldname_multiple_select_form_class没定义')

    def get_fieldname_multiple_select_form(self, form_class):
        """
        生成fieldname_multiple_select_form
        """
        #data = self.request.GET.copy()
        #field_names = list(set((data.getlist(self.form_field_name, []) + self.list_display)))
        #data.update({self.form_field_name:field_names})
        return  form_class(self.request.GET)


    def get_list_display(self, download_all=False):
        """
        """

        if  download_all:
            """
            这个判断，是给下载当前数据用的，包括函数在内，返回所有字段
            """
            fields = self.model._meta.fields
            field_names = [field.name for field in fields]
            field_names.remove('id')
            all_list = field_names + self.list_display
            return  list(set(all_list))

        form_class = self.get_fieldname_multiple_select_form_class()
        form = self.get_fieldname_multiple_select_form(form_class)
        if form.is_valid():
            """
            如果有指定显示字段，则显示默认加上指定的字段
            """
            cd = form.cleaned_data
            if cd.get(self.form_field_name, None):
                #如果存在就返回字段多选的value list
                return list(set(self.list_display + cd.get(self.form_field_name)))

        if self.list_display:
            return self.list_display
        else:
            raise

    def get_context_data(self,  **kwargs):
        form_class = self.get_fieldname_multiple_select_form_class()
        form = self.get_fieldname_multiple_select_form(form_class)
        k = form.as_p()

        kwargs.update(field_name_select_form=form)
        return super(FieldNameSelectMixin, self).get_context_data(**kwargs)
