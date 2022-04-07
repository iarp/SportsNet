import pytz
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models.functions import Lower
from django.utils import timezone
from positions.fields import PositionField

from core.model_helpers import _BaseModel

# from travelpermits.models import TravelPermit


class Association(_BaseModel):
    class Meta:
        constraints = [
            models.UniqueConstraint(
                Lower("name"),
                name="association_name_uniqueness",
            )
        ]

    name = models.CharField(max_length=255, verbose_name="Association")
    full_name = models.CharField(max_length=255)
    location = models.CharField(max_length=255, blank=True)
    website = models.CharField(max_length=500, blank=True)
    tournament_listing_url = models.CharField(max_length=500, blank=True)

    exhibition_is_in_ohf = models.BooleanField(
        default=False,
        help_text="Setting applies to Exhibitions only, is this association within the OHF?",
    )

    weight = PositionField()

    def __str__(self):
        if self.name.lower() == "other":
            return "Other (Supply Below)"
        return self.name

    def is_omha(self):
        return self.name in ["OMHA"]


class Rink(_BaseModel):
    class Meta:
        ordering = ["weight", "name"]
        constraints = [
            models.UniqueConstraint(
                Lower("name"),
                Lower("city"),
                Lower("province"),
                name="rink_name_city_province_uniqueness",
            )
        ]

    name = models.CharField(max_length=255)
    city = models.CharField(max_length=255, blank=True)
    province = models.CharField(max_length=255, blank=True)

    weight = PositionField()

    def __str__(self):
        return f"{self.name}, {self.city}, {self.province}"


class Tournament(_BaseModel):
    class Meta:
        permissions = (("tournament_verify", "Can verify legitimacy."),)

    association = models.ForeignKey(
        Association, on_delete=models.CASCADE, verbose_name="Host Association"
    )
    association_other = models.CharField(
        max_length=255, blank=True, verbose_name='Host Association "Other"'
    )

    sanction_number = models.CharField(max_length=255, blank=True)

    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    start_date = models.DateField(verbose_name="Tournament Start Date")
    end_date = models.DateField(blank=True, null=True)
    divisions = models.CharField(
        max_length=4000, blank=True, help_text="Divisions tournament is for. * Optional"
    )

    source = models.CharField(max_length=255, blank=True)
    verified = models.BooleanField(default=False)
    verified_date = models.DateField(blank=True, null=True)

    # Let's us store where they found the tournament information from if they are
    # submitting a tournament we don't already know
    website = models.CharField(max_length=4000, blank=True)

    notes = models.TextField(blank=True)

    def has_been_verified(self):
        self.verified = True
        self.verified_date = timezone.now()
        self.save()

    def __str__(self):
        return f'{self.association}: {self.start_date} to {self.end_date} - "{self.name}" at "{self.location}"'

    def is_in_omha_region(self):
        return self.association.is_omha()

    def can_edit(self):
        return not self.travelpermit_set.exclude(number=0).exists()


class Exhibition(_BaseModel):

    name = models.CharField(max_length=255, blank=True)

    other_team = models.CharField(max_length=255)
    other_team_association = models.ForeignKey(
        Association, on_delete=models.CASCADE, verbose_name="Other Team Association"
    )
    other_team_association_other = models.CharField(
        max_length=255, blank=True, verbose_name='Other Team Association "Other"'
    )

    destination = models.CharField(max_length=255)
    arena = models.CharField(max_length=255, blank=True)

    start_date = models.DateTimeField(verbose_name="Start Date and Time")
    end_datetime = models.DateTimeField(
        null=True, blank=True, verbose_name="End Date and Time"
    )

    source = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)

    REF_REQ_TWO_REFS = "2 Refs"
    REF_REQ_ONE_REF_TWO_LINESMEN = "1 Ref / 2 Linesmen"
    REF_REQ_TWO_REF_TWO_LINESMEN = "2 Refs / 2 Linesmen"

    REF_REQUIREMENTS = (
        (REF_REQ_TWO_REFS, REF_REQ_TWO_REFS),
        (REF_REQ_ONE_REF_TWO_LINESMEN, REF_REQ_ONE_REF_TWO_LINESMEN),
        (REF_REQ_TWO_REF_TWO_LINESMEN, REF_REQ_TWO_REF_TWO_LINESMEN),
    )

    required_referee_or_timekeeper = models.BooleanField(default=False)

    rink = models.ForeignKey(Rink, on_delete=models.CASCADE)
    referee_requirements = models.CharField(
        max_length=255, choices=REF_REQUIREMENTS, blank=True
    )
    timekeeper_needed = models.BooleanField(default=False, blank=True)
    timekeeper_notes = models.TextField(blank=True)

    contact_name = models.CharField(
        max_length=255,
        blank=True,
        help_text="Whose phone number are you supplying above?",
    )
    cell_phone = models.CharField(
        max_length=255,
        blank=True,
        help_text="This is the phone number you will be contacted at if there is a problem.",
    )

    referee_timekeeper_request_sent_to_office = models.BooleanField(default=False)

    def __str__(self):
        return ", ".join(
            [self.other_team, self.destination, self.start_date.strftime("%Y-%m-%d")]
        )

    def is_in_ohf_region(self):
        return self.other_team_association.exhibition_is_in_ohf

    def get_start_date_local_timezone(self):
        return self.start_date.astimezone(pytz.timezone(settings.TIME_ZONE))

    def get_arena(self):

        if self.rink and self.rink.name.startswith("Other"):
            return self.arena

        return "-".join([self.rink.name, self.destination])

    def can_edit(self):
        return not self.travelpermit_set.exclude(number=0).exists()

    def get_other_team_association(self):
        if self.other_team_association.name == "OTHER":
            return self.other_team_association_other
        return self.other_team_association
