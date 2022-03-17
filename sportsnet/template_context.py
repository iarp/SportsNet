from django.conf import settings
from django.urls import resolve

from core.models import Season


def add_season(request):
    try:
        season = Season.get_current()
    except Season.DoesNotExist:
        season = None
    return {"season": season}


def add_django_settings(request):
    """Access to django settings file"""
    return {"system_settings": settings}


def sys_app_name(request):
    try:
        return {"sys_app_name": resolve(request.path).app_name}
    except:  # noqa
        return {"sys_app_name": "unknown"}
