from django.contrib.auth import get_user_model
from django.db.models.signals import pre_save
from django.dispatch import receiver

from .models import Member, MemberStatus


@receiver(pre_save, sender=get_user_model())
def core_user_set_username_to_email(instance, **kwargs):
    instance.username = instance.email


@receiver(pre_save, sender=Member)
def new_member_without_status_assigned_gets_default(instance, **kwargs):
    if instance.status_id or instance.pk or kwargs.get("raw"):
        return

    try:
        instance.status = MemberStatus.objects.get(default=True)
    except MemberStatus.DoesNotExist:
        return
