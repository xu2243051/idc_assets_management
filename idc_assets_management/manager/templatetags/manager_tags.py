#!/usr/bin/env python
#coding:utf-8
from django import template
from django.core.urlresolvers import reverse, reverse_lazy

register = template.Library()

@register.filter
def render_verbose_name(value):
    if value._meta.verbose_name:
        return value._meta.verbose_name
    else:
        return value.__name__

@register.filter
def render_list_link(value):
    k = value.__class__
    name =  k.__name__.lower()
    url_name = '%s_%s' %(name, 'list')
    return reverse(url_name)

@register.filter
def render_create_link(value):
    k = value.__class__
    name =  k.__name__.lower()
    url_name = '%s_%s' %(name, 'create')
    return reverse(url_name)

@register.filter
def render_upload_link(value):
    k = value.__class__
    name =  k.__name__.lower()
    url_name = '%s_%s' %(name, 'upload')
    return reverse(url_name)
