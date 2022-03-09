from django.contrib.auth import get_user_model
from django.db.models.signals import pre_save
from django.dispatch import receiver


@receiver(pre_save, sender=get_user_model())
def core_user_set_username_to_email(instance, **kwargs):
    instance.username = instance.email
