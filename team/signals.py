from django.db.models.signals import pre_save
from django.dispatch import receiver

from .models import Staff


@receiver(pre_save, sender=Staff)
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
            instance.season = instance.subdivision.season
            instance.league = instance.subdivision.league
            instance.division = instance.subdivision.division

    elif instance.division_id:
        if not all([instance.season_id, instance.league_id]):
            instance.season = instance.division.season
            instance.league = instance.division.league

    elif instance.league_id:
        if not instance.season_id:
            instance.season = instance.league.season
