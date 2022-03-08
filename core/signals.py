from django.contrib.auth import get_user_model
from django.db.models.signals import pre_save
from django.dispatch import receiver

from .models import TeamStaff


@receiver(pre_save, sender=get_user_model())
def core_user_set_username_to_email(instance, **kwargs):
    instance.username = instance.email


@receiver(pre_save, sender=TeamStaff)
def ensure_teamstaff_entry_has_proper_ids(instance, **kwargs):

    if instance.team_id:
        if not all(
            [
                instance.season_id,
                instance.league_id,
                instance.division_id,
                instance.subdivision_id,
            ]
        ):
            instance.season = instance.team.season
            instance.league = instance.team.league
            instance.division = instance.team.division
            instance.subdivision = instance.team.subdivision

    elif instance.subdivision_id:
        if not all([instance.season_id, instance.league_id, instance.division_id]):
            instance.season = instance.subdivision.division.league.season
            instance.league = instance.subdivision.division.league
            instance.division = instance.subdivision.division

    elif instance.division_id:
        if not all([instance.season_id, instance.league_id]):
            instance.season = instance.division.league.season
            instance.league = instance.division.league

    elif instance.league_id:
        if not instance.season_id:
            instance.season = instance.league.season
