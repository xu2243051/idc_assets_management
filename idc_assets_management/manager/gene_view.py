#!/usr/bin/env python
#coding:utf-8
import os
import sys
reload(sys)
sys.setdefaultencoding('utf8')

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "idc_assets_management.settings.local")
sys.path.append('/opt/py_env/xiaojun/idc_assets_management/idc_assets_management')

from django.template import Context, loader, Template

template = """
models.py  
from .forms import {{modelname}}SearchForm, {{modelname}}SelectForm
from .models import {{modelname}}
class {{modelname}}CreateView(CreateView):
    model = {{modelname}}
    template_name = "manager/base_form.html"
    #form_class = {{modelname}}Form

class {{modelname}}UploadView(UpLoadMixin, CreateView):
    model = {{modelname}}
    upload_form_class = UploadForm
    template_name = "manager/base_upload.html"
    #CreateView很多地方用到self.object
    object = None
    #form_class = {{modelname}}Form

class {{modelname}}DetailView(DetailView):
    model = {{modelname}}
    template_name = "manager/base_detail.html"

class {{modelname}}UpdateView(UpdateView):
    model = {{modelname}}
    template_name = "manager/base_form.html"
    #form_class = {{modelname}}Form

class {{modelname}}DeleteView(DeleteView):
    model = {{modelname}}
    template_name = "manager/base_confirm_delete.html"
    success_url = reverse_lazy('{{ modelname_lower }}_list')

class {{modelname}}ListView(BtnGroupMixin, FieldNameSelectMixin, DownLoadMixin, \
                           SearchMixin, ProcessAjaxPostmixin, ListDislayMixin, FormMixin, ListView): 
    # 开关btn-groups
    btn_groups = None
    model = {{modelname}}
    template_name = "manager/base_list.html"
    #post 使用的form
    form_class = AjaxCommandForm
    list_display = ['id']
    link = ['id']

    # search 
    search_form_class = {{modelname}}SearchForm
    # che
    fieldname_multiple_select_form_class = {{modelname}}SelectForm

-----------------
urls.py
from .views import {{ modelname }}CreateView, {{ modelname }}DetailView, {{ modelname }}UpdateView, \
        {{ modelname }}DeleteView, {{ modelname }}ListView, {{ modelname }}UploadView
urlpatterns += patterns('',
    url(r'^{{ modelname_lower }}/$', {{ modelname }}ListView.as_view(), name='{{ modelname_lower }}_list'),
    url(r'^{{ modelname_lower }}/upload/$', {{ modelname }}UploadView.as_view(), name='{{ modelname_lower }}_upload'),
    url(r'^{{ modelname_lower }}/create/$', {{ modelname }}CreateView.as_view(), name='{{ modelname_lower }}_create'),
    url(r'^{{ modelname_lower }}/detail/(?P<pk>\d+)/$', {{ modelname }}DetailView.as_view(), name='{{ modelname_lower }}_detail'),
    url(r'^{{ modelname_lower }}/update/(?P<pk>\d+)/$', {{ modelname }}UpdateView.as_view(), name='{{ modelname_lower }}_update'),
    url(r'^{{ modelname_lower }}/delete/(?P<pk>\d+)/$', {{ modelname }}DeleteView.as_view(), name='{{ modelname_lower }}_delete'),
)
-----------------------------------
forms.py

from .models import {{ modelname }}
class {{ modelname }}SearchForm(forms.Form):
    ""\"
    定义{{ modelname }}列表的过滤条件
    ""\"
    room_name = forms.ChoiceField(label="机房名", required=False,
                                  choices = add_initial_to_choices({{ modelname }}.group.get_group_in_tuple('room_name')))
    room_agent = forms.ChoiceField(label="机房代理商", required=False,
                                choices = add_initial_to_choices({{ modelname }}.group.get_group_in_tuple('room_agent')))
    #download_filename = forms.CharField(label="请输入文件名", required=False, help_text="不添为download.csv")

class {{ modelname }}SelectForm(forms.Form):
    field_names = forms.MultipleChoiceField(label='请选择显示的字段',
                                            choices=get_choices_from_model({{ modelname }}), required=False,
                                            widget=forms.CheckboxSelectMultiple(attrs={'form':'base_form'}))
                                            
"""

def repl(matchobj):
    return '_%s' % matchobj.group(0).lower()

def change_camelcase(string):
    import re 
    return re.sub(r'\B[A-Z]', repl, string).lower()

if __name__ == '__main__':
    t = Template(template)
    modelname = sys.argv[1]
    print change_camelcase(modelname)
    c = Context({'modelname':modelname, 'modelname_lower':modelname.lower()})
    print t.render(c)
