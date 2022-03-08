from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.db.models import F, Q
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from loguru import logger
from positions.fields import PositionField

from .model_helpers import _BaseModel, _BaseModelWithCommonIDs, _BasePermissions
from .perms import add_override_permission, has_perm


class User(AbstractUser):
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    username_validator = UnicodeUsernameValidator()

    username = models.CharField(
        _("username"),
        max_length=500,
        unique=True,
        help_text=_(
            "Required. 500 characters or fewer. Letters, digits and @/./+/-/_ only."
        ),
        validators=[username_validator],
        error_messages={
            "unique": _("A user with that username already exists."),
        },
    )

    email = models.EmailField(
        _("email address"),
        unique=True,
        max_length=500,
        help_text=_(
            "Required. 500 characters or fewer. Letters, digits and @/./+/-/_ only."
        ),
        validators=[username_validator],
        error_messages={
            "unique": _("A user with that email address already exists."),
        },
    )
    inserted = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


class Season(_BaseModelWithCommonIDs):
    class Meta:
        ordering = ["start"]
        constraints = [
            models.CheckConstraint(
                check=Q(end__gt=F("start")),
                name="check_season_end_is_after_start_date",
            )
        ]

    name = models.CharField(max_length=50)

    start = models.DateField(null=True)
    end = models.DateField(null=True)

    mbs_id = models.PositiveIntegerField(default=0)
    gsi_id = models.PositiveIntegerField(default=0)

    def get_next_season(self):
        """Next season is based on the first season with a start greater than current seasons end"""
        return (
            Season.objects.filter(start__gt=self.end)
            .exclude(pk=self.pk)
            .order_by("start")
            .first()
        )

    def get_previous_season(self):
        return (
            Season.objects.filter(start__lt=self.end)
            .exclude(pk=self.pk)
            .order_by("-start")
            .first()
        )

    @classmethod
    def get_current(cls, based_on_date=None):
        if not based_on_date:
            based_on_date = timezone.now().date()
        try:
            return cls.objects.filter(
                start__lte=based_on_date, end__gte=based_on_date
            ).get()
        except cls.DoesNotExist:
            logger.critical("No season is set as current!")
            raise

    @cached_property
    def staff(self):
        return self.staff_direct.filter(
            league_id__isnull=True,
            division_id__isnull=True,
            subdivision_id__isnull=True,
            team_id__isnull=True,
        )

    def save(self, *args, **kwargs):

        qs = Season.objects.all()
        if self.pk:
            qs = qs.exclude(pk=self.pk)

        for season in qs:

            try:
                start = self.start.date()
            except (AttributeError, TypeError):
                start = self.start

            if season.start <= start <= season.end:
                raise ValueError(
                    "Season start and end dates cannot be between another seasons dates."
                )

        return super().save(*args, **kwargs)


class League(_BaseModelWithCommonIDs):
    class Meta:
        ordering = ["season", "weight"]

    season = models.ForeignKey(Season, on_delete=models.CASCADE, related_name="leagues")
    name = models.CharField(max_length=255)

    weight = PositionField(collection="season")

    @cached_property
    def staff(self):
        return self.staff_direct.filter(
            division_id__isnull=True,
            subdivision_id__isnull=True,
            team_id__isnull=True,
        )


class Division(_BaseModelWithCommonIDs):
    class Meta:
        ordering = ["league", "weight"]

    season = models.ForeignKey(
        Season, on_delete=models.CASCADE, related_name="divisions"
    )
    league = models.ForeignKey(
        League, on_delete=models.CASCADE, related_name="divisions"
    )
    name = models.CharField(max_length=255)

    age_from = models.PositiveIntegerField(default=0)
    age_to = models.PositiveIntegerField(default=0)
    weight = PositionField(collection=["season"])

    @cached_property
    def staff(self):
        return self.staff_direct.filter(
            subdivision_id__isnull=True,
            team_id__isnull=True,
        )


class SubDivision(_BaseModelWithCommonIDs):
    season = models.ForeignKey(
        Season, on_delete=models.CASCADE, related_name="subdivisions"
    )
    league = models.ForeignKey(
        League, on_delete=models.CASCADE, related_name="subdivisions"
    )
    division = models.ForeignKey(
        Division, on_delete=models.CASCADE, related_name="subdivisions"
    )
    name = models.CharField(max_length=255)

    weight = PositionField(collection="season")

    @cached_property
    def staff(self):
        return self.staff_direct.filter(
            team_id__isnull=True,
        )


class Team(_BaseModelWithCommonIDs):
    season = models.ForeignKey(Season, on_delete=models.PROTECT, related_name="teams")
    league = models.ForeignKey(League, on_delete=models.PROTECT, related_name="teams")
    division = models.ForeignKey(
        Division, on_delete=models.PROTECT, related_name="teams"
    )
    subdivision = models.ForeignKey(
        SubDivision, on_delete=models.PROTECT, related_name="teams"
    )
    name = models.CharField(max_length=255)

    weight = PositionField(collection=["season"])

    def can_edit(self, target_user):
        return has_perm(target_user, self, "team_can_edit")

    def can_vote(self, target_user):
        return has_perm(target_user, self, "team_can_vote")

    @cached_property
    def staff(self):
        return self.staff_direct.all()


class TeamStaffType(_BasePermissions):
    name = models.CharField(max_length=255)


class TeamStaff(_BaseModel):

    season = models.ForeignKey(
        Season, on_delete=models.CASCADE, related_name="staff_direct"
    )
    league = models.ForeignKey(
        League,
        on_delete=models.CASCADE,
        related_name="staff_direct",
        null=True,
        blank=True,
    )
    division = models.ForeignKey(
        Division,
        on_delete=models.CASCADE,
        related_name="staff_direct",
        null=True,
        blank=True,
    )
    subdivision = models.ForeignKey(
        SubDivision,
        on_delete=models.CASCADE,
        related_name="staff_direct",
        null=True,
        blank=True,
    )
    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name="staff_direct",
        null=True,
        blank=True,
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    type = models.ForeignKey(TeamStaffType, on_delete=models.PROTECT)

    def __str__(self):
        return str(self.user)

    def permissions_add_override(self, obj, permission_name, value, assigned_by=None):
        return add_override_permission(
            self, obj, permission_name, value, assigned_by=assigned_by
        )


class PermissionOverrides(_BasePermissions):

    season = models.ForeignKey(
        Season, on_delete=models.CASCADE, related_name="+", null=True, blank=True
    )
    league = models.ForeignKey(
        League, on_delete=models.CASCADE, related_name="+", null=True, blank=True
    )
    division = models.ForeignKey(
        Division, on_delete=models.CASCADE, related_name="+", null=True, blank=True
    )
    subdivision = models.ForeignKey(
        SubDivision,
        on_delete=models.CASCADE,
        related_name="+",
        null=True,
        blank=True,
    )
    team = models.ForeignKey(
        Team, on_delete=models.CASCADE, related_name="+", null=True, blank=True
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="overridden_permissions",
    )

    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )

    assigned_on = models.DateTimeField(null=True, blank=True)
