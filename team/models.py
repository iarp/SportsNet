from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext, gettext_lazy
from positions.fields import PositionField

from core.model_helpers import _BaseModel, _BaseModelWithCommonIDs, _BasePermissions
from core.models import Division, League, Season, SubDivision
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
        # return self.hockey_canada_id and self.status.lower() in [
        #     "approved",
        #     "resubmitted",
        # ]


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


class _StaffObjectsManagerWithDetails(models.Manager):
    def head_coach(self, *args, **kwargs):
        if isinstance(self.instance, Team):
            return self.filter(*args, type__name="Coach", **kwargs).first()
        raise TypeError(gettext_lazy("head_coach is available on the Team instance."))

    def own(self, *args, **kwargs):
        extras = {}
        if isinstance(self.instance, Season):
            extras = {
                "league_id__isnull": True,
                "division_id__isnull": True,
                "subdivision_id__isnull": True,
                "team_id__isnull": True,
            }
        elif isinstance(self.instance, League):
            extras = {
                "division_id__isnull": True,
                "subdivision_id__isnull": True,
                "team_id__isnull": True,
            }
        elif isinstance(self.instance, Division):
            extras = {
                "subdivision_id__isnull": True,
                "team_id__isnull": True,
            }
        elif isinstance(self.instance, SubDivision):
            extras = {
                "team_id__isnull": True,
            }
        return self.filter(*args, **extras, **kwargs)

    def vps(self):
        if isinstance(self.instance, Season):
            return self.filter(
                division_id__isnull=True,
                subdivision_id__isnull=True,
                team_id__isnull=True,
            ).exclude(league_id__isnull=True)
        raise TypeError(gettext("vps is available on the Season instance."))

    def senior_convenors(self):
        if isinstance(self.instance, Season):
            return self.filter(
                subdivision_id__isnull=True,
                team_id__isnull=True,
            ).exclude(Q(league_id__isnull=True) | Q(division_id__isnull=True))
        elif isinstance(self.instance, League):
            return self.filter(
                subdivision_id__isnull=True,
                team_id__isnull=True,
            ).exclude(Q(league_id__isnull=True) | Q(division_id__isnull=True))
        raise TypeError(
            gettext("senior_convenors is available on the Season or League instance.")
        )

    def convenors(self):
        if isinstance(self.instance, Season):
            return self.filter(team_id__isnull=True).exclude(
                Q(league_id__isnull=True)
                | Q(division_id__isnull=True)
                | Q(subdivision_id__isnull=True)
            )
        elif isinstance(self.instance, League):
            return self.filter(team_id__isnull=True).exclude(
                Q(division_id__isnull=True) | Q(subdivision_id__isnull=True)
            )
        elif isinstance(self.instance, Division):
            return self.filter(team_id__isnull=True).exclude(
                subdivision_id__isnull=True,
            )
        raise TypeError(
            gettext(
                "convenors is available on the Season, League, or Division instance."
            )
        )

    def coaches(self):
        return self.filter(type__name="Coach")
        # if isinstance(self.instance, Season):
        #     return qs.exclude(
        #         Q(league_id__isnull=True)
        #         | Q(division_id__isnull=True)
        #         | Q(subdivision_id__isnull=True)
        #         | Q(team_id__isnull=True)
        #     )
        # elif isinstance(self.instance, League):
        #     return qs.exclude(
        #         Q(division_id__isnull=True)
        #         | Q(subdivision_id__isnull=True)
        #         | Q(team_id__isnull=True)
        #     )
        # elif isinstance(self.instance, Division):
        #     return qs.exclude(Q(subdivision_id__isnull=True) | Q(team_id__isnull=True))
        # elif isinstance(self.instance, SubDivision):
        #     return qs.exclude(team_id__isnull=True)
        # raise TypeError(
        #     gettext("coaches is available on the Season, League, Division, or SubDivision instance.")
        # )

    def managers(self):
        if isinstance(self.instance, Team):
            return self.filter(type__name="Manager")
        raise TypeError(gettext("managers is available on the Team instance."))


class _StaffManagerCustomQuerySet(models.QuerySet):
    def emails(self):
        return self.filter(user__email__contains="@").values_list(
            "user__email", flat=True
        )


class Staff(_BaseModel):
    class Meta:
        verbose_name = gettext_lazy("Team Staff")
        verbose_name_plural = gettext_lazy("Team Staff")

    objects = _StaffObjectsManagerWithDetails.from_queryset(
        _StaffManagerCustomQuerySet
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
        verbose_name = gettext_lazy("Team Status")
        verbose_name_plural = gettext_lazy("Team Statuses")

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
            )
        ]

    status = models.ForeignKey(
        TeamStatus, on_delete=models.CASCADE, related_name="reasons"
    )

    name = models.CharField(max_length=255)
    weight = PositionField()

    default = models.BooleanField(default=None, null=True, blank=True)


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
