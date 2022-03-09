from django.conf import settings
from django.db import models
from django.utils.functional import cached_property
from positions.fields import PositionField

from core.model_helpers import _BaseModel, _BaseModelWithCommonIDs, _BasePermissions
from core.perms import add_override_permission, has_perm


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
    status_reason = models.ForeignKey("team.TeamStatusReason", on_delete=models.PROTECT)

    # NOTE: These were on the original table, unknown
    # RegStatus = models.BooleanField(default=False)
    # ApprovalRequired = models.BooleanField(default=False)  # all records are false in current table
    # ChgdPlayers = models.BooleanField(default=False)
    # ChgdStaff = models.BooleanField(default=False)
    # Comments = models.TextField(blank=True)

    jersey_home = models.CharField(max_length=255, blank=True)
    jersey_away = models.CharField(max_length=255, blank=True)
    submitted = models.BooleanField(default=False)
    submitted_date = models.DateTimeField(null=True, blank=True)
    approved = models.BooleanField(default=False)

    active = models.BooleanField(default=True)

    draft_start_position = models.PositiveIntegerField(default=1)

    weight = PositionField(collection=["season"])

    def __str__(self):
        return self.get_full_team_name()

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

    @cached_property
    def staff(self):
        return self.staff_direct.all()

    def is_approved(self):
        return self.hockey_canada_id and self.status.lower() in [
            "approved",
            "resubmitted",
        ]


class StaffType(_BasePermissions):
    class Meta:
        ordering = ["weight"]
        verbose_name = "Team Staff Type"
        verbose_name_plural = "Team Staff Types"

    name = models.CharField(max_length=255)
    weight = PositionField()

    required = models.BooleanField(default=False)

    # WebAccess bit,
    # EditEvalAsgndAllowed bit,
    # EditEvalAvailAllowed bit,
    # EditCoachEvalAllowed bit,
    # MultipleSeasonsAllowed bit,
    # AllowAssignUnAssignPlayers bit,
    # AllowAssignUnAssignStaff bit,
    # AdminPower bit,
    # TeamStaffTypeChangeUnRestricted bit,
    # TravelPermitViewAllowed bit,
    # TravelPermitUpdateAllowed bit,
    # MemberViewAllowed bit,
    # StaffTeamViewAllowed bit,
    # StaffSeasonViewAllowed bit,
    # PlayerTeamViewAllowed bit,
    # PlayerSeasonViewAllowed bit,


class StaffStatus(_BaseModel):
    class Meta:
        ordering = ["weight"]
        verbose_name = "Team Staff Status"
        verbose_name_plural = "Team Staff Statuses"

    name = models.CharField(max_length=255)
    weight = PositionField()
    include_in_roster_export = models.BooleanField(default=True)


class StaffStatusReason(_BaseModel):
    class Meta:
        ordering = ["weight"]
        verbose_name = "Team Staff Status Reason"
        verbose_name_plural = "Team Staff Status Reasons"

    name = models.CharField(max_length=255)
    weight = PositionField(default=0)


class Staff(_BaseModel):
    class Meta:
        verbose_name = "Team Staff"
        verbose_name_plural = "Team Staff"

    season = models.ForeignKey(
        "core.Season", on_delete=models.CASCADE, related_name="staff_direct"
    )
    league = models.ForeignKey(
        "core.League",
        on_delete=models.CASCADE,
        related_name="staff_direct",
        null=True,
        blank=True,
    )
    division = models.ForeignKey(
        "core.Division",
        on_delete=models.CASCADE,
        related_name="staff_direct",
        null=True,
        blank=True,
    )
    subdivision = models.ForeignKey(
        "core.SubDivision",
        on_delete=models.CASCADE,
        related_name="staff_direct",
        null=True,
        blank=True,
    )
    team = models.ForeignKey(
        "team.Team",
        on_delete=models.CASCADE,
        related_name="staff_direct",
        null=True,
        blank=True,
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    # TODO: Where is persons being stored?
    # person = models.ForeignKey()

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


class TeamStatus(_BaseModel):
    class Meta:
        ordering = ["weight"]
        verbose_name = "Team Status"
        verbose_name_plural = "Team Statuses"

    name = models.CharField(max_length=255)
    weight = PositionField(default=0)

    include_in_roster_export = models.BooleanField(default=True)

    # NOTE: Was in the table, all entries False. Unknown usage.
    ClrChgdStfPlyrSts = models.BooleanField(default=False)


class TeamStatusReason(_BaseModel):
    class Meta:
        ordering = ["weight"]
        verbose_name = "Team Status Reason"
        verbose_name_plural = "Team Status Reasons"

    name = models.CharField(max_length=255)
    status = models.ForeignKey(
        TeamStatus, on_delete=models.CASCADE, related_name="reasons"
    )
    weight = PositionField(default=0)


class TeamStatusLog(_BaseModel):
    class Meta:
        ordering = ["inserted"]
        verbose_name = "Team Status Log"
        verbose_name_plural = "Team Status Logs"

    team = models.ForeignKey("team.Team", on_delete=models.CASCADE)

    old_status_id = models.ForeignKey(
        TeamStatus, on_delete=models.DO_NOTHING, null=True, blank=True, related_name="+"
    )
    old_status_reason_id = models.ForeignKey(
        TeamStatusReason,
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        related_name="+",
    )

    new_status_id = models.ForeignKey(
        TeamStatus, on_delete=models.DO_NOTHING, null=True, blank=True, related_name="+"
    )
    new_status_reason_id = models.ForeignKey(
        TeamStatusReason,
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        related_name="+",
    )

    # NOTE: Was in the table, all entries False. Unknown usage.
    # ChgdStfPlyrSts = models.BooleanField(default=False)


class TeamNote(_BaseModel):
    class Meta:
        ordering = ["inserted"]
        verbose_name = "Team Note"
        verbose_name_plural = "Team Notes"

    team = models.ForeignKey(
        "team.Team", on_delete=models.CASCADE, related_name="notes"
    )

    class NoteTypes(models.TextChoices):
        ROSTER = "ROSTER", "Roster"
        PLAYER = "PLAYER", "Player"

    type = models.CharField(
        max_length=255, default=NoteTypes.ROSTER, choices=NoteTypes.choices
    )

    note = models.TextField()
