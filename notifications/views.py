# -*- coding: utf-8 -*-
''' Django Notifications example views '''
from packaging.version import Version

from django import get_version
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.utils.decorators import method_decorator
from django.utils.encoding import iri_to_uri
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.cache import never_cache
from django.views.generic import ListView
from swapper import load_model

from notifications import settings as notification_settings
from notifications.helpers import get_notification_list
from notifications.utils import slug2id
from notifications.serializers import NotificationSerializer

from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework import filters as rest_filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError

from django_filters import rest_framework as filters

from notifications.app_settings import api_settings as settings


Notification = load_model('notifications', 'Notification')

if Version(get_version()) >= Version('1.7.0'):
    from django.http import JsonResponse  # noqa
else:
    # Django 1.6 doesn't have a proper JsonResponse
    import json

    from django.http import HttpResponse  # noqa

    def date_handler(obj):
        return obj.isoformat() if hasattr(obj, 'isoformat') else obj

    def JsonResponse(data):  # noqa
        return HttpResponse(
            json.dumps(data, default=date_handler),
            content_type="application/json")


class NotificationViewList(ListView):
    template_name = 'notifications/list.html'
    context_object_name = 'notifications'
    paginate_by = notification_settings.get_config()['PAGINATE_BY']

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(NotificationViewList, self).dispatch(
            request, *args, **kwargs)


class AllNotificationsList(NotificationViewList):
    """
    Index page for authenticated user
    """

    def get_queryset(self):
        if notification_settings.get_config()['SOFT_DELETE']:
            qset = self.request.user.notifications.active()
        else:
            qset = self.request.user.notifications.all()
        return qset


class UnreadNotificationsList(NotificationViewList):

    def get_queryset(self):
        return self.request.user.notifications.unread()


@login_required
def mark_all_as_read(request):
    request.user.notifications.mark_all_as_read()

    _next = request.GET.get('next')

    if _next and url_has_allowed_host_and_scheme(_next, settings.ALLOWED_HOSTS):
        return redirect(iri_to_uri(_next))
    return redirect('notifications:unread')


@login_required
def mark_as_read(request, slug=None):
    notification_id = slug2id(slug)

    notification = get_object_or_404(
        Notification, recipient=request.user, id=notification_id)
    notification.mark_as_read()

    _next = request.GET.get('next')

    if _next and url_has_allowed_host_and_scheme(_next, settings.ALLOWED_HOSTS):
        return redirect(iri_to_uri(_next))

    return redirect('notifications:unread')


@login_required
def mark_as_unread(request, slug=None):
    notification_id = slug2id(slug)

    notification = get_object_or_404(
        Notification, recipient=request.user, id=notification_id)
    notification.mark_as_unread()

    _next = request.GET.get('next')

    if _next and url_has_allowed_host_and_scheme(_next, settings.ALLOWED_HOSTS):
        return redirect(iri_to_uri(_next))

    return redirect('notifications:unread')


@login_required
def delete(request, slug=None):
    notification_id = slug2id(slug)

    notification = get_object_or_404(
        Notification, recipient=request.user, id=notification_id)

    if notification_settings.get_config()['SOFT_DELETE']:
        notification.deleted = True
        notification.save()
    else:
        notification.delete()

    _next = request.GET.get('next')

    if _next and url_has_allowed_host_and_scheme(_next, settings.ALLOWED_HOSTS):
        return redirect(iri_to_uri(_next))

    return redirect('notifications:all')


@never_cache
def live_unread_notification_count(request):
    try:
        user_is_authenticated = request.user.is_authenticated()
    except TypeError:  # Django >= 1.11
        user_is_authenticated = request.user.is_authenticated

    if not user_is_authenticated:
        data = {
            'unread_count': 0
        }
    else:
        data = {
            'unread_count': request.user.notifications.unread().count(),
        }
    return JsonResponse(data)


@never_cache
def live_unread_notification_list(request):
    ''' Return a json with a unread notification list '''
    try:
        user_is_authenticated = request.user.is_authenticated()
    except TypeError:  # Django >= 1.11
        user_is_authenticated = request.user.is_authenticated

    if not user_is_authenticated:
        data = {
            'unread_count': 0,
            'unread_list': []
        }
        return JsonResponse(data)

    unread_list = get_notification_list(request, 'unread')

    data = {
        'unread_count': request.user.notifications.unread().count(),
        'unread_list': unread_list
    }
    return JsonResponse(data)


@never_cache
def live_all_notification_list(request):
    ''' Return a json with a unread notification list '''
    try:
        user_is_authenticated = request.user.is_authenticated()
    except TypeError:  # Django >= 1.11
        user_is_authenticated = request.user.is_authenticated

    if not user_is_authenticated:
        data = {
            'all_count': 0,
            'all_list': []
        }
        return JsonResponse(data)

    all_list = get_notification_list(request)

    data = {
        'all_count': request.user.notifications.count(),
        'all_list': all_list
    }
    return JsonResponse(data)


def live_all_notification_count(request):
    try:
        user_is_authenticated = request.user.is_authenticated()
    except TypeError:  # Django >= 1.11
        user_is_authenticated = request.user.is_authenticated

    if not user_is_authenticated:
        data = {
            'all_count': 0
        }
    else:
        data = {
            'all_count': request.user.notifications.count(),
        }
    return JsonResponse(data)


class NotificationsViewSet(GenericViewSet, ListModelMixin, RetrieveModelMixin):
    permission_classes = [IsAuthenticated]

    filter_backends = (
        filters.DjangoFilterBackend,
        rest_filters.SearchFilter,
        rest_filters.OrderingFilter,
    )

    filterset_fields = ("unread",)
    
    search_fields = ("description", "verb")

    page_size_query_param = "page_size"

    ordering_fields = ("update_at", "created_at")

    serializer_class = NotificationSerializer


    def get_queryset(self):
        return self.request.user.notifications.all()

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.unread = False
        instance.save()
        return super().retrieve(request, *args, **kwargs)

    @action(detail=False, methods=["post"], url_path="read-all")
    def mark_all_as_read(self, request):
        for notification in self.get_queryset():
            notification.unread = False
            notification.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

if settings.get_user_setting('USE_EXPO_NOTIFICATIONS'):
    from notifications.models import ExpoToken
    class ManageDeviceExpo(GenericViewSet):
        permission_classes = [IsAuthenticated]

        @action(detail=False, url_path="register-device", methods=["POST"])
        def register_device(self, request, *args, **kwargs):
            user = request.user

            token = request.data.get("token")
            if not token:
                raise ValidationError("'token' is required")

            ExpoToken.objects.update_or_create(user=user, token=token)

            # Remove oldest token if user exceeds token limit
            token_count = ExpoToken.objects.filter(user=user).count()
            if token_count > 10:
                oldest_token = ExpoToken.objects.filter(user=user).order_by("created_at").first()
                oldest_token.delete()

            return Response(status=status.HTTP_201_CREATED)


        @action(detail=False, url_path="unregister-device", methods=["POST"])
        def unregister_device(self, request, *args, **kwargs):
            user = request.user

            token = request.data.get("token")
            if not token:
                raise ValidationError("token is required")

            ExpoToken.objects.filter(user=user, token=token).delete()

            return Response(status=status.HTTP_204_NO_CONTENT)