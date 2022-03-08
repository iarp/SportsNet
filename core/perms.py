from django.db.models import Q
from django.utils import timezone
from loguru import logger


def has_perm(user, obj, permission_name):
    from core.models import PermissionOverrides, TeamStaff

    # Allow us to pass User or TeamStaff object.
    if isinstance(user, TeamStaff):
        user = user.user

    if user.is_superuser:
        return True

    args = (
        (Q(league_id__isnull=True) | Q(league=obj.league)),
        (Q(division_id__isnull=True) | Q(division=obj.division)),
        (Q(subdivision_id__isnull=True) | Q(subdivision=obj.subdivision)),
        (Q(team_id__isnull=True) | Q(team=obj)),
    )
    kwargs = {
        "user": user,
        "season": obj.season,
    }

    if TeamStaff.objects.filter(
        *args, **kwargs, **{f"type__{permission_name}": True}
    ).exists():
        return True

    return PermissionOverrides.objects.filter(
        *args,
        **kwargs,
        **{f"{permission_name}": True},
    ).exists()


def add_override_permission(user, obj, permission_name, value, assigned_by=None):

    from core.models import (
        Division,
        League,
        PermissionOverrides,
        Season,
        SubDivision,
        Team,
        TeamStaff,
    )

    if not isinstance(obj, (Season, League, Division, SubDivision, Team)):
        raise ValueError(
            "Parameter obj must be of type Season, League, Division, SubDivision, or Team."
        )

    if permission_name not in PermissionOverrides.PERMISSION_TYPES:
        raise ValueError(
            "Parameter permission_name value must be an attribute of PermissionOverrides model."
        )

    if isinstance(user, TeamStaff):
        user = user.user
    if isinstance(assigned_by, TeamStaff):
        assigned_by = assigned_by.user

    data = {}

    if isinstance(obj, Season):
        data = {"season": obj}
    elif isinstance(obj, League):
        data = {"season": obj.season, "league": obj}
    elif isinstance(obj, Division):
        data = {"season": obj.league.season, "league": obj.league, "division": obj}
    elif isinstance(obj, SubDivision):
        data = {
            "season": obj.division.league.season,
            "league": obj.division.league,
            "division": obj.division,
            "subdivision": obj,
        }
    elif isinstance(obj, Team):
        data = {
            "season": obj.season,
            "league": obj.league,
            "division": obj.division,
            "subdivision": obj.subdivision,
            "team": obj,
        }

    defaults = {
        permission_name: value,
    }
    if assigned_by:
        defaults["assigned_by"] = assigned_by
        defaults["assigned_on"] = timezone.now()

    logger.debug(f"{user} now has {permission_name}=={value} assigned by {assigned_by}")

    perms, _ = PermissionOverrides.objects.update_or_create(
        **data,
        user=user,
        defaults=defaults,
    )
    return perms
