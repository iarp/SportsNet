from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy


class _BaseModel(models.Model):
    class Meta:
        abstract = True

    old_sk_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        unique=True,
        help_text=gettext_lazy("The old primary id for the entry"),
    )

    inserted = models.DateTimeField(default=timezone.now)
    inserted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_inserted",
    )

    updated = models.DateTimeField(default=timezone.now)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_updated",
    )

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):

        if not getattr(settings, "INSERTED_UPDATED_SKIP_DEFAULTS", False):
            self.updated = timezone.now()

            if update_fields := kwargs.get("update_fields"):
                kwargs["update_fields"] = set(update_fields).union({"updated"})

        super().save(*args, **kwargs)


class _BaseModelWithCommonIDs(_BaseModel):
    class Meta:
        abstract = True

    hockey_canada_id = models.PositiveBigIntegerField(
        null=True, blank=True, help_text="HcID Value", unique=True
    )
    hockey_canada_system_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text=gettext_lazy(
            "*_id value for api, not meant to be editable or seen by users. Backend only."
        ),
        unique=True,
    )


class _BasePermissions(_BaseModel):
    class Meta:
        abstract = True

    # NOTE: Add permissions here

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

    team_can_edit = models.BooleanField(default=True)
    team_can_vote = models.BooleanField(default=False)
    team_can_access = models.BooleanField(default=True)
