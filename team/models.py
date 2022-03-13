from django.conf import settings
from django.db import models
from django.db.models.functions import Lower
from django.utils.translation import gettext_lazy
from positions.fields import PositionField

from core.model_helpers import _BaseModel, _BaseModelWithCommonIDs, _BasePermissions
from core.perms import add_override_permission, has_perm

from . import managers


class Team(_BaseModelWithCommonIDs):
    season = models.ForeignKey(
        "core.Season", on_delete=models.PROTECT, related_name="teams"
    )
    league = models.ForeignKey(
        "core.League", on_delete=models.PROTECT, related_name="teams"
    )
    division = models.ForeignKey(
        "core.Division", on_delete=models.PROTECT, related_name="teams"
    )
    subdivision = models.ForeignKey(
        "core.SubDivision", on_delete=models.PROTECT, related_name="teams"
    )
    name = models.CharField(max_length=255)
    number = models.PositiveIntegerField(default=0)

    status = models.ForeignKey("team.TeamStatus", on_delete=models.PROTECT)
    status_reason = models.ForeignKey(
        "team.TeamStatusReason", on_delete=models.SET_NULL, null=True, blank=True
    )

    old_teamseason_id = models.PositiveIntegerField(null=True, blank=True)

    # NOTE: These were on the original table, unknown
    # RegStatus = models.BooleanField(default=False)
    # ApprovalRequired = models.BooleanField(default=False)  # all records are false in current table
    # Comments = models.TextField(blank=True)

    players_has_changed_flag = models.BooleanField(default=False)
    staff_has_changed_flag = models.BooleanField(default=False)

    jersey_home = models.CharField(max_length=255, blank=True)
    jersey_away = models.CharField(max_length=255, blank=True)
    submitted = models.BooleanField(default=False)
    submitted_date = models.DateTimeField(null=True, blank=True)
    approved = models.BooleanField(default=False)

    active = models.BooleanField(default=True)

    draft_start_position = models.PositiveIntegerField(default=1)

    weight = PositionField(collection=["season"])

    def get_full_team_name(self, separator=" / "):
        return separator.join(
            [
                str(self.league),
                str(self.division),
                str(self.subdivision),
                str(self.name),
            ]
        )

    def can_edit(self, target_user):
        return has_perm(target_user, self, "team_can_edit")

    def can_vote(self, target_user):
        return has_perm(target_user, self, "team_can_vote")

    @property
    def is_approved(self):
        return self.hockey_canada_id and self.status.considered_approved

    def save(self, *args, **kwargs):

        # Reset status_reason on status change.
        if self.pk:
            original_instance = Team.objects.get(pk=self.pk)

            if self.status_id != original_instance.status_id:

                if any([self.staff_has_changed_flag, self.players_has_changed_flag]):

                    if self.status.clear_changed_staff_players_flag:
                        self.players_has_changed_flag = False
                        self.staff_has_changed_flag = False

                # status has changed, now we need to ensure the
                # status_reason is a reason of the newly assigned status.
                if not self.status.reasons.filter(pk=self.status_reason.pk).exists():
                    self.status_reason = None

            if (self.status_id != original_instance.status_id) or (
                self.status_reason_id != original_instance.status_reason_id
            ):
                TeamStatusLog.objects.create(
                    team=self,
                    old_status=original_instance.status,
                    old_status_reason=original_instance.status_reason,
                    new_status=self.status,
                    new_status_reason=self.status_reason,
                )

        # On new objects or those without a status_reason,
        # assign the default reason for the specific status.
        if not self.status_reason_id or (not self.status_reason_id and not self.pk):
            try:
                self.status_reason = self.status.reasons.get(default=True)
            except TeamStatusReason.DoesNotExist:
                self.status_reason = None

        return super().save(*args, **kwargs)


class TeamStatus(_BaseModel):
    class Meta:
        ordering = ["weight"]
        verbose_name = gettext_lazy("Team Status")
        verbose_name_plural = gettext_lazy("Team Statuses")

        constraints = [
            models.constraints.UniqueConstraint(
                Lower("name"), name="teamstatus_name_uniqueness"
            )
        ]

    name = models.CharField(max_length=255)
    weight = PositionField(default=0)

    include_in_roster_export = models.BooleanField(default=True)

    # NOTE: Used in Team.is_approved mainly for roster downloader
    considered_approved = models.BooleanField(
        default=False,
        help_text=gettext_lazy(
            "If a team is assigned this status, are they "
            "technically considered approved in hockey canada?"
        ),
    )

    # NOTE: Was in the table, all entries False. Unknown usage.
    clear_changed_staff_players_flag = models.BooleanField(default=False)


class TeamStatusReason(_BaseModel):
    class Meta:
        ordering = ["weight", "name"]
        verbose_name = gettext_lazy("Team Status Reason")
        verbose_name_plural = gettext_lazy("Team Status Reasons")

        constraints = [
            models.constraints.UniqueConstraint(
                "status", "default", name="teamstatusreason_status_default_uniqueness"
            ),
            models.constraints.UniqueConstraint(
                Lower("name"), "status", name="teamstatusreason_name_status_uniqueness"
            ),
        ]

    status = models.ForeignKey(
        TeamStatus, on_delete=models.CASCADE, related_name="reasons"
    )

    name = models.CharField(max_length=255)
    weight = PositionField()

    default = models.BooleanField(default=None, null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.default is False:
            self.default = None
        return super().save(*args, **kwargs)


class TeamStatusLog(_BaseModel):
    class Meta:
        ordering = ["inserted"]
        verbose_name = gettext_lazy("Team Status Log")
        verbose_name_plural = gettext_lazy("Team Status Logs")

    team = models.ForeignKey("team.Team", on_delete=models.CASCADE)

    old_status = models.ForeignKey(
        TeamStatus, on_delete=models.SET_NULL, null=True, blank=True, related_name="+"
    )
    old_status_reason = models.ForeignKey(
        TeamStatusReason,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )

    new_status = models.ForeignKey(
        TeamStatus, on_delete=models.SET_NULL, null=True, blank=True, related_name="+"
    )
    new_status_reason = models.ForeignKey(
        TeamStatusReason,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )


class TeamNote(_BaseModel):
    class Meta:
        ordering = ["inserted"]
        verbose_name = gettext_lazy("Team Note")
        verbose_name_plural = gettext_lazy("Team Notes")

    team = models.ForeignKey(
        "team.Team", on_delete=models.CASCADE, related_name="notes"
    )

    class NoteTypes(models.TextChoices):
        ROSTER = "ROSTER", gettext_lazy("Roster")
        PLAYER = "PLAYER", gettext_lazy("Player")

    type = models.CharField(
        max_length=255, default=NoteTypes.ROSTER, choices=NoteTypes.choices
    )

    note = models.TextField()


class StaffType(_BasePermissions):
    class Meta:
        ordering = ["weight"]
        verbose_name = gettext_lazy("Staff Type")
        verbose_name_plural = gettext_lazy("Staff Types")

    name = models.CharField(max_length=255)
    weight = PositionField()

    required = models.BooleanField(default=False)

    web_access = models.BooleanField(
        default=False,
        help_text=gettext_lazy(
            "Can a Staff record assigned with this StaffType be allowed to login?"
        ),
    )

    change_causes_staff_flag_on_team_to_enable = models.BooleanField(
        default=True,
        verbose_name=gettext_lazy(
            "Change causes team.staff_has_changed_flag set to True"
        ),
        help_text=gettext_lazy(
            "Does changing a Staff record assigned with this "
            "StaffType cause the team.staff_has_changed_flag to be True?"
        ),
    )


class StaffStatus(_BaseModel):
    class Meta:
        ordering = ["weight"]
        verbose_name = gettext_lazy("Staff Status")
        verbose_name_plural = gettext_lazy("Staff Statuses")

    name = models.CharField(max_length=255)
    weight = PositionField()
    include_in_roster_export = models.BooleanField(default=True)


class StaffStatusReason(_BaseModel):
    class Meta:
        ordering = ["weight"]
        verbose_name = gettext_lazy("Team Staff Status Reason")
        verbose_name_plural = gettext_lazy("Team Staff Status Reasons")

    name = models.CharField(max_length=255)
    weight = PositionField(default=0)


class Staff(_BaseModel):
    class Meta:
        verbose_name = gettext_lazy("Team Staff")
        verbose_name_plural = gettext_lazy("Team Staff")

    objects = managers._StaffObjectsManagerWithDetails.from_queryset(
        managers._StaffManagerCustomQuerySet
    )()

    season = models.ForeignKey(
        "core.Season", on_delete=models.CASCADE, related_name="staff"
    )
    league = models.ForeignKey(
        "core.League",
        on_delete=models.CASCADE,
        related_name="staff",
        null=True,
        blank=True,
    )
    division = models.ForeignKey(
        "core.Division",
        on_delete=models.CASCADE,
        related_name="staff",
        null=True,
        blank=True,
    )
    subdivision = models.ForeignKey(
        "core.SubDivision",
        on_delete=models.CASCADE,
        related_name="staff",
        null=True,
        blank=True,
    )
    team = models.ForeignKey(
        "team.Team",
        on_delete=models.CASCADE,
        related_name="staff",
        null=True,
        blank=True,
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="staff_assignments",
    )

    member = models.ForeignKey("core.Member", on_delete=models.PROTECT)

    type = models.ForeignKey(StaffType, on_delete=models.PROTECT)
    status = models.ForeignKey(StaffStatus, on_delete=models.PROTECT)

    importer = models.BooleanField(default=False)
    affiliate = models.BooleanField(default=False)
    tryout = models.BooleanField(default=False)

    registration_date = models.DateTimeField(null=True, blank=True)
    release_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.user)

    def permissions_add_override(self, obj, permission_name, value, assigned_by=None):
        return add_override_permission(
            self, obj, permission_name, value, assigned_by=assigned_by
        )

    def save(self, *args, **kwargs):

        if not self.pk:
            if self.team_id:
                self.season = self.team.season
                self.league = self.team.league
                self.division = self.team.division
                self.subdivision = self.team.subdivision

            elif self.subdivision_id:
                self.season = self.subdivision.season
                self.league = self.subdivision.league
                self.division = self.subdivision.division

            elif self.division_id:
                self.season = self.division.season
                self.league = self.division.league

            elif self.league_id:
                self.season = self.league.season

        # TODO: Add same same to Player model whenever that is in place.
        if self.team_id and self.type.change_causes_staff_flag_on_team_to_enable:
            self.team.staff_has_changed_flag = True
            self.team.save()

        return super().save(*args, **kwargs)
