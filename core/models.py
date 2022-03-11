from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.db.models import F, Q
from django.db.models.functions import Lower
from django.utils import timezone
from django.utils.translation import gettext, gettext_lazy
from iarp_django_utils.models import BaseSetting
from loguru import logger
from positions.fields import PositionField

from .model_helpers import _BaseModel, _BaseModelWithCommonIDs, _BasePermissions


class _UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

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


class User(_BaseModel, AbstractUser):
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    username_validator = UnicodeUsernameValidator()
    objects = _UserManager()

    username = models.CharField(
        gettext_lazy("username"),
        max_length=500,
        unique=True,
        help_text=gettext_lazy(
            "Required. 500 characters or fewer. Letters, digits and @/./+/-/_ only."
        ),
        validators=[username_validator],
        error_messages={
            "unique": gettext_lazy("A user with that username already exists."),
        },
    )

    email = models.EmailField(
        gettext_lazy("email address"),
        unique=True,
        max_length=500,
        help_text=gettext_lazy(
            "Required. 500 characters or fewer. Letters, digits and @/./+/-/_ only."
        ),
        validators=[username_validator],
        error_messages={
            "unique": gettext_lazy("A user with that email address already exists."),
        },
    )

    def __str__(self):
        return self.get_username()


class Season(_BaseModelWithCommonIDs):
    class Meta:
        ordering = ["start"]
        constraints = [
            models.CheckConstraint(
                check=Q(end__gt=F("start")),
                name="check_season_end_is_after_start_date",
            ),
            models.UniqueConstraint(Lower("name"), name="season_name_unique"),
        ]

    name = models.CharField(max_length=50)

    start = models.DateField(null=True)
    end = models.DateField(null=True)

    mbs_id = models.PositiveIntegerField(default=0)
    gsi_id = models.PositiveIntegerField(default=0)

    def get_next_season(self, season=None):
        if not season:
            season = self
        return (
            Season.objects.filter(start__gt=season.end)
            .exclude(pk=season.pk)
            .order_by("start")
            .first()
        )

    def get_previous_season(self, season=None):
        if not season:
            season = self
        return (
            Season.objects.filter(start__lt=season.end)
            .exclude(pk=season.pk)
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
            logger.critical(gettext("No season is set as current!"))
            raise

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
                    gettext(
                        "Season start and end dates cannot be between another seasons dates."
                    )
                )

        return super().save(*args, **kwargs)


class League(_BaseModelWithCommonIDs):
    class Meta:
        ordering = ["season", "weight"]
        constraints = [
            models.UniqueConstraint(
                Lower("name"),
                "season",
                name="season_league_name_unique",
            ),
        ]

    season = models.ForeignKey(Season, on_delete=models.CASCADE, related_name="leagues")
    name = models.CharField(max_length=255)

    weight = PositionField(collection="season")


class Division(_BaseModelWithCommonIDs):
    class Meta:
        ordering = ["league", "weight"]
        constraints = [
            models.UniqueConstraint(
                Lower("name"),
                "season",
                "league",
                name="division_season_league_name_unique",
            ),
        ]

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

    player_rating_factor = models.PositiveIntegerField(default=100)

    assign_first_slot_as_goalie = models.BooleanField(default=True)


class SubDivision(_BaseModelWithCommonIDs):
    class Meta:
        ordering = ["weight"]
        constraints = [
            models.UniqueConstraint(
                Lower("name"),
                "season",
                "league",
                "division",
                name="subdivision_season_league_division_name_unique",
            ),
        ]

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
    body_checking = models.BooleanField(default=False)

    player_rating_factor = models.PositiveIntegerField(default=100)
    default_number_of_teams = models.PositiveIntegerField(default=4)
    inactive = models.BooleanField(default=False)


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
        "team.Team", on_delete=models.CASCADE, related_name="+", null=True, blank=True
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


class Setting(BaseSetting):
    pass
