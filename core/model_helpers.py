from django.conf import settings
from django.db import models
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

    inserted = models.DateTimeField(auto_now_add=True)
    inserted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )

    updated = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )

    def __str__(self):
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
        help_text=gettext_lazy(
            "*_id value for api, not meant to be editable or seen by users. Backend only."
        ),
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
