from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from .models import Staff, Team, TeamStatusLog, TeamStatusReason


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

    if (instance.status_id != original_instance.status_id) or (
        instance.status_reason_id != original_instance.status_reason_id
    ):
        TeamStatusLog.objects.create(
            team=instance,
            old_status=original_instance.status,
            old_status_reason=original_instance.status_reason,
            new_status=instance.status,
            new_status_reason=instance.status_reason,
        )


@receiver(pre_save, sender=Team)
def clear_players_or_staff_has_changed_flags_on_status_change(instance, **kwargs):
    if not instance.pk or kwargs.get("raw"):
        return
    if not any([instance.staff_has_changed_flag, instance.players_has_changed_flag]):
        return

    original_instance = Team.objects.get(pk=instance.pk)

    if instance.status_id != original_instance.status_id:

        if instance.status.clear_changed_staff_players_flag:
            instance.players_has_changed_flag = False
            instance.staff_has_changed_flag = False


@receiver(post_save, sender=Staff)
def set_staff_has_changed_flag_on_associated_team(instance: Staff, **kwargs):
    if kwargs.get("raw") or not instance.team_id:
        return

    if not instance.type.change_causes_staff_flag_on_team_to_enable:
        return

    instance.team.staff_has_changed_flag = True
    instance.team.save()


# TODO: Same signal as above for players whenever that is in place.


@receiver(pre_save, sender=Team)
def clear_or_reset_teamstatusreason_if_status_changed(instance: Team, **kwargs):
    if not instance.pk or kwargs.get("raw"):
        return

    original_instance = Team.objects.get(pk=instance.pk)

    if instance.status_id != original_instance.status_id:
        # status has changed, now we need to ensure the status_reason is a reason of the newly assigned status.

        if not instance.status.reasons.filter(pk=instance.status_reason.pk).exists():
            instance.status_reason = None


@receiver(pre_save, sender=Team)
def set_teamstatusreason_on_new_team_entries(instance: Team, **kwargs):
    if instance.pk or instance.status_reason or kwargs.get("raw"):
        return

    try:
        instance.status_reason = instance.status.reasons.get(default=True)
    except TeamStatusReason.DoesNotExist:
        instance.status_reason = None
