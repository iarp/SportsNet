from django.utils.functional import cached_property


class ProjSettings(object):
    def _value(self, app, name, **kwargs):
        from core.models import Settings

        return Settings.get_value(app=app, name=name, **kwargs)

    def _values(self, app):
        from core.models import Settings

        return Settings.get_values(app=app)

    @cached_property
    def DOMAIN_BASE(self):
        return self._value("system", "domain_base")

    @cached_property
    def PAYMENT_SETTINGS(self):
        return self._values(app="Payments")

    @cached_property
    def USE_CELERY_TASKS(self):
        return self._value("system", "use_tasks", system_specific=True, default=True)


proj_settings = ProjSettings()
