''' Django notification urls file '''
# -*- coding: utf-8 -*-
from packaging.version import Version

from django import get_version
from notifications.views import NotificationsViewSet
from notifications.app_settings import api_settings as settings


from . import views

if Version(get_version()) >= Version('2.0'):
    from django.urls import re_path as pattern
else:
    from django.conf.urls import url as pattern


urlpatterns = [
    pattern(r'^$', views.AllNotificationsList.as_view(), name='all'),
    pattern(r'^unread/$', views.UnreadNotificationsList.as_view(), name='unread'),
    pattern(r'^mark-all-as-read/$', views.mark_all_as_read, name='mark_all_as_read'),
    pattern(r'^mark-as-read/(?P<slug>\d+)/$', views.mark_as_read, name='mark_as_read'),
    pattern(r'^mark-as-unread/(?P<slug>\d+)/$', views.mark_as_unread, name='mark_as_unread'),
    pattern(r'^delete/(?P<slug>\d+)/$', views.delete, name='delete'),
    pattern(r'^api/unread_count/$', views.live_unread_notification_count, name='live_unread_notification_count'),
    pattern(r'^api/all_count/$', views.live_all_notification_count, name='live_all_notification_count'),
    pattern(r'^api/unread_list/$', views.live_unread_notification_list, name='live_unread_notification_list'),
    pattern(r'^api/all_list/', views.live_all_notification_list, name='live_all_notification_list'),
]
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r"notifications", NotificationsViewSet, basename="notifications")

if settings.get_user_setting("USE_EXPO_NOTIFICATIONS"):
    from notifications.views import ManageDeviceExpo
    router.register(r"expo-devices", ManageDeviceExpo, basename="expo")


app_name = 'notifications'
