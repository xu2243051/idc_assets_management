# Create your views here.
#coding:utf-8
import json
import csv
from os.path import basename, abspath, curdir
#获得app 目录名字
#app_name = basename(abspath(curdir))

from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib.auth import authenticate, logout, login
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import View, DetailView, CreateView, \
                UpdateView, DeleteView, ListView
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormMixin

from .forms import UserLoginForm, AjaxCommandForm, UploadForm
from .forms import ComputerRoomSearchForm, ComputerRoomSelectForm
from .models import ComputerRoom
from .mixins import ListDislayMixin, Processmixin, ProcessAjaxPostmixin, BtnGroupMixin
from .mixins import SearchMixin, DownLoadMixin, UpLoadMixin, FieldNameSelectMixin

class LoginView(FormMixin, Processmixin, TemplateView):
    form_class = UserLoginForm
    template_name = 'server/login.html'

    def form_valid(self, form):
        user = form.cleaned_data['user']
        passwd = form.cleaned_data['passwd']
        user = authenticate(username=user, password=passwd)

        if user is not None:
            # the password verified for the user 
             if user.is_active:
                 login(self.request, user)
                 return HttpResponseRedirect(reverse('home'))

        #如果账号无效，或者账号不存在，密码错误，都提示一样的错误
        form.errors.update({'user':[u'账号或者密码不正确']})
        return self.form_invalid(form=form)

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('home'))

class ComputerRoomCreateView(CreateView):
    model = ComputerRoom
    template_name = "manager/base_form.html"
    #form_class = ComputerRoomForm

class ComputerRoomUploadView(UpLoadMixin, CreateView):
    model = ComputerRoom
    upload_form_class = UploadForm
    template_name = "manager/base_upload.html"
    #CreateView很多地方用到self.object
    object = None
    #form_class = ComputerRoomForm

class ComputerRoomDetailView(DetailView):
    model = ComputerRoom
    template_name = "manager/base_detail.html"

class ComputerRoomUpdateView(UpdateView):
    model = ComputerRoom
    template_name = "manager/base_form.html"
    #form_class = ComputerRoomForm

class ComputerRoomDeleteView(DeleteView):
    model = ComputerRoom
    template_name = "manager/base_confirm_delete.html"
    success_url = reverse_lazy('computerroom_list')

class ComputerRoomListView(BtnGroupMixin, FieldNameSelectMixin, DownLoadMixin, \
                           SearchMixin, ProcessAjaxPostmixin, ListDislayMixin, FormMixin, ListView):
    # 开关btn-groups
    btn_groups = None
    model = ComputerRoom
    template_name = "manager/base_list.html"
    #post 使用的form
    form_class = AjaxCommandForm
    list_display = ['room_name', 'room_agent']
    link = ['room_name']

    # search 
    search_form_class = ComputerRoomSearchForm
    # che
    fieldname_multiple_select_form_class = ComputerRoomSelectForm


### ComputerRack的View
from .forms import ComputerRackSearchForm, ComputerRackSelectForm
from .models import ComputerRack
class ComputerRackCreateView(CreateView):
    model = ComputerRack
    template_name = "manager/base_form.html"
    #form_class = ComputerRackForm

class ComputerRackUploadView(UpLoadMixin, CreateView):
    model = ComputerRack
    upload_form_class = UploadForm
    template_name = "manager/base_upload.html"
    #CreateView很多地方用到self.object
    object = None
    #form_class = ComputerRackForm

class ComputerRackDetailView(DetailView):
    model = ComputerRack
    template_name = "manager/base_detail.html"

class ComputerRackUpdateView(UpdateView):
    model = ComputerRack
    template_name = "manager/base_form.html"
    #form_class = ComputerRackForm

class ComputerRackDeleteView(DeleteView):
    model = ComputerRack
    template_name = "manager/base_confirm_delete.html"
    success_url = reverse_lazy('computerrack_list')

class ComputerRackListView(BtnGroupMixin, FieldNameSelectMixin, DownLoadMixin,
                            SearchMixin, ProcessAjaxPostmixin, ListDislayMixin, FormMixin, ListView): 
    # 开关btn-groups
    btn_groups = None
    model = ComputerRack
    template_name = "manager/base_list.html"
    #post 使用的form
    form_class = AjaxCommandForm
    list_display = ['rack_num', 'computerroom', '__unicode__','return_rack_available_capacity']
    link = ['rack_num']

    # search 
    search_form_class = ComputerRackSearchForm
    # che
    fieldname_multiple_select_form_class = ComputerRackSelectForm
