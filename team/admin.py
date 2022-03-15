from django.apps import apps
from django.contrib import admin
from django.contrib.admin.sites import AlreadyRegistered
from reversion.admin import VersionAdmin

app_models = apps.get_app_config("team").get_models()
for model in app_models:
    try:
        admin.site.register(model, VersionAdmin)
    except AlreadyRegistered:  # pragma: no cover
        pass
