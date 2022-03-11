from django.contrib.auth.backends import ModelBackend


class LoginRequiresStaffTypeWebAccessTrueBackend(ModelBackend):
    def authenticate(self, *args, **kwargs):
        user = super().authenticate(*args, **kwargs)

        if not user:
            return

        if user.is_staff or user.is_superuser:
            return user

        if user.staff_assignments.filter(type__web_access=True).exists():
            return user
