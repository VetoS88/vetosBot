# -*- coding: utf8 -*-

from django.conf.urls import url

from .views import CommandReceiveView
from .test_answer import CommandTestView

urlpatterns = [
    url(r'^bot/(?P<bot_token>.+)/$', CommandReceiveView.as_view(), name='command'),
    url(r'^test/(?P<bot_token>.+)/$', CommandTestView.as_view(), name='command'),
]
