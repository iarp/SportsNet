from django.db.models.signals import pre_save
from django.dispatch import receiver

from .models import Staff, Team, TeamStatusLog


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


@receiver(pre_save, sender=Team)
def log_teamstatus_changes(instance: Team, **kwargs):
    if not instance.pk or kwargs.get("raw"):
        return

    original_instance = Team.objects.get(pk=instance.pk)

    if instance.status_id != original_instance.status_id:
        TeamStatusLog.objects.create(
            team=instance,
            old_status=original_instance.status,
            old_status_reason=original_instance.status_reason,
            new_status=instance.status,
            new_status_reason=instance.status_reason,
        )
