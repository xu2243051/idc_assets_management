from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView

from .views import ComputerRoomCreateView, ComputerRoomDetailView, \
        ComputerRoomUpdateView, ComputerRoomDeleteView, ComputerRoomListView, ComputerRoomUploadView

urlpatterns = patterns('',
    url(r'^$', TemplateView.as_view(template_name='base.html')),
    url(r'^computerroom/$', ComputerRoomListView.as_view(), name='computerroom_list'),
    url(r'^computerroom/upload/$', ComputerRoomUploadView.as_view(), name='computerroom_upload'),
    url(r'^computerroom/create/$', ComputerRoomCreateView.as_view(), name='computerroom_create'),
    url(r'^computerroom/detail/(?P<pk>\d+)/$', ComputerRoomDetailView.as_view(), name='computerroom_detail'),
    url(r'^computerroom/update/(?P<pk>\d+)/$', ComputerRoomUpdateView.as_view(), name='computerroom_update'),
    url(r'^computerroom/delete/(?P<pk>\d+)/$', ComputerRoomDeleteView.as_view(), name='computerroom_delete'),
)


from .views import ComputerRackCreateView, ComputerRackDetailView, ComputerRackUpdateView, \
        ComputerRackDeleteView, ComputerRackListView, ComputerRackUploadView
urlpatterns += patterns('',
    url(r'^computerrack/$', ComputerRackListView.as_view(), name='computerrack_list'),
    url(r'^computerrack/upload/$', ComputerRackUploadView.as_view(), name='computerrack_upload'),
    url(r'^computerrack/create/$', ComputerRackCreateView.as_view(), name='computerrack_create'),
    url(r'^computerrack/detail/(?P<pk>\d+)/$', ComputerRackDetailView.as_view(), name='computerrack_detail'),
    url(r'^computerrack/update/(?P<pk>\d+)/$', ComputerRackUpdateView.as_view(), name='computerrack_update'),
    url(r'^computerrack/delete/(?P<pk>\d+)/$', ComputerRackDeleteView.as_view(), name='computerrack_delete'),
)
