from django.contrib.auth.models import BaseUserManager
from django.utils.translation import gettext


class _UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    @staticmethod
    def normalize_email(email):
        return email.lower()

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError(gettext("email is required for User objects"))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields["is_staff"] = True
        extra_fields["is_superuser"] = True
        return self._create_user(email, password, **extra_fields)
