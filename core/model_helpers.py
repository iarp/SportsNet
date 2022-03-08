from django.db import models


class _BaseModel(models.Model):
    class Meta:
        abstract = True

    inserted = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):  # pragma: no cover
        return self.name


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
        help_text="*_id value for api, not meant to be editable or seen by users. Backend only.",
        unique=True,
    )


class _BasePermissions(_BaseModel):
    class Meta:
        abstract = True

    # NOTE: Add permissions here??

    # Used in PermissionOverrides.add_override for deleting rows where the
    # row entries matches the defaults listed below
    PERMISSION_TYPES = [
        "team_can_edit",
        "team_can_vote",
    ]

    team_can_edit = models.BooleanField(default=True)
    team_can_vote = models.BooleanField(default=False)
