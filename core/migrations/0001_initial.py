# Generated by Django 4.0.3 on 2022-03-13 16:02

from django.conf import settings
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import phonenumber_field.modelfields
import positions.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="User",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("password", models.CharField(max_length=128, verbose_name="password")),
                (
                    "last_login",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="last login"
                    ),
                ),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text="Designates that this user has all permissions without explicitly assigning them.",
                        verbose_name="superuser status",
                    ),
                ),
                (
                    "first_name",
                    models.CharField(
                        blank=True, max_length=150, verbose_name="first name"
                    ),
                ),
                (
                    "last_name",
                    models.CharField(
                        blank=True, max_length=150, verbose_name="last name"
                    ),
                ),
                (
                    "is_staff",
                    models.BooleanField(
                        default=False,
                        help_text="Designates whether the user can log into this admin site.",
                        verbose_name="staff status",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="Designates whether this user should be treated as active. Unselect this instead of deleting accounts.",
                        verbose_name="active",
                    ),
                ),
                (
                    "date_joined",
                    models.DateTimeField(
                        default=django.utils.timezone.now, verbose_name="date joined"
                    ),
                ),
                (
                    "old_sk_id",
                    models.PositiveIntegerField(
                        blank=True,
                        help_text="The old primary id for the entry",
                        null=True,
                        unique=True,
                    ),
                ),
                ("inserted", models.DateTimeField(default=django.utils.timezone.now)),
                ("updated", models.DateTimeField(default=django.utils.timezone.now)),
                (
                    "username",
                    models.CharField(
                        error_messages={
                            "unique": "A user with that username already exists."
                        },
                        help_text="Required. 500 characters or fewer. Letters, digits and @/./+/-/_ only.",
                        max_length=500,
                        unique=True,
                        validators=[
                            django.contrib.auth.validators.UnicodeUsernameValidator()
                        ],
                        verbose_name="username",
                    ),
                ),
                (
                    "email",
                    models.EmailField(
                        error_messages={
                            "unique": "A user with that email address already exists."
                        },
                        help_text="Required. 500 characters or fewer. Letters, digits and @/./+/-/_ only.",
                        max_length=500,
                        unique=True,
                        validators=[
                            django.contrib.auth.validators.UnicodeUsernameValidator()
                        ],
                        verbose_name="email address",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Division",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "old_sk_id",
                    models.PositiveIntegerField(
                        blank=True,
                        help_text="The old primary id for the entry",
                        null=True,
                        unique=True,
                    ),
                ),
                ("inserted", models.DateTimeField(default=django.utils.timezone.now)),
                ("updated", models.DateTimeField(default=django.utils.timezone.now)),
                (
                    "hockey_canada_id",
                    models.PositiveBigIntegerField(
                        blank=True, help_text="HcID Value", null=True, unique=True
                    ),
                ),
                (
                    "hockey_canada_system_id",
                    models.CharField(
                        blank=True,
                        help_text="*_id value for api, not meant to be editable or seen by users. Backend only.",
                        max_length=255,
                        null=True,
                        unique=True,
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                ("age_from", models.PositiveIntegerField(default=0)),
                ("age_to", models.PositiveIntegerField(default=0)),
                ("weight", positions.fields.PositionField(default=-1)),
                ("player_rating_factor", models.PositiveIntegerField(default=100)),
                ("assign_first_slot_as_goalie", models.BooleanField(default=True)),
            ],
            options={
                "ordering": ["league", "weight"],
            },
        ),
        migrations.CreateModel(
            name="Gender",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "old_sk_id",
                    models.PositiveIntegerField(
                        blank=True,
                        help_text="The old primary id for the entry",
                        null=True,
                        unique=True,
                    ),
                ),
                ("inserted", models.DateTimeField(default=django.utils.timezone.now)),
                ("updated", models.DateTimeField(default=django.utils.timezone.now)),
                ("name", models.CharField(max_length=255)),
            ],
            options={
                "verbose_name": "Gender",
                "verbose_name_plural": "Genders",
            },
        ),
        migrations.CreateModel(
            name="League",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "old_sk_id",
                    models.PositiveIntegerField(
                        blank=True,
                        help_text="The old primary id for the entry",
                        null=True,
                        unique=True,
                    ),
                ),
                ("inserted", models.DateTimeField(default=django.utils.timezone.now)),
                ("updated", models.DateTimeField(default=django.utils.timezone.now)),
                (
                    "hockey_canada_id",
                    models.PositiveBigIntegerField(
                        blank=True, help_text="HcID Value", null=True, unique=True
                    ),
                ),
                (
                    "hockey_canada_system_id",
                    models.CharField(
                        blank=True,
                        help_text="*_id value for api, not meant to be editable or seen by users. Backend only.",
                        max_length=255,
                        null=True,
                        unique=True,
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                ("weight", positions.fields.PositionField(default=-1)),
            ],
            options={
                "ordering": ["season", "weight"],
            },
        ),
        migrations.CreateModel(
            name="Member",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "old_sk_id",
                    models.PositiveIntegerField(
                        blank=True,
                        help_text="The old primary id for the entry",
                        null=True,
                        unique=True,
                    ),
                ),
                ("inserted", models.DateTimeField(default=django.utils.timezone.now)),
                ("updated", models.DateTimeField(default=django.utils.timezone.now)),
                (
                    "hockey_canada_id",
                    models.PositiveBigIntegerField(
                        blank=True, help_text="HcID Value", null=True, unique=True
                    ),
                ),
                (
                    "hockey_canada_system_id",
                    models.CharField(
                        blank=True,
                        help_text="*_id value for api, not meant to be editable or seen by users. Backend only.",
                        max_length=255,
                        null=True,
                        unique=True,
                    ),
                ),
                ("first_name", models.CharField(max_length=255)),
                ("last_name", models.CharField(max_length=255)),
                ("date_of_birth", models.DateField(null=True)),
                ("comments", models.TextField(blank=True)),
                ("address1", models.CharField(blank=True, max_length=255)),
                ("address2", models.CharField(blank=True, max_length=255)),
                ("city", models.CharField(blank=True, max_length=255)),
                ("province", models.CharField(blank=True, max_length=255)),
                ("postal_code", models.CharField(blank=True, max_length=10)),
                (
                    "phone_home",
                    phonenumber_field.modelfields.PhoneNumberField(
                        blank=True, max_length=128, region=None
                    ),
                ),
                (
                    "phone_work",
                    phonenumber_field.modelfields.PhoneNumberField(
                        blank=True, max_length=128, region=None
                    ),
                ),
                (
                    "phone_cell",
                    phonenumber_field.modelfields.PhoneNumberField(
                        blank=True, max_length=128, region=None
                    ),
                ),
                (
                    "phone_fax",
                    phonenumber_field.modelfields.PhoneNumberField(
                        blank=True, max_length=128, region=None
                    ),
                ),
                ("email", models.EmailField(blank=True, max_length=254)),
                ("sportsmanager_id", models.IntegerField(blank=True, null=True)),
            ],
            options={
                "verbose_name": "Member",
                "verbose_name_plural": "Members",
            },
        ),
        migrations.CreateModel(
            name="MemberStatus",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "old_sk_id",
                    models.PositiveIntegerField(
                        blank=True,
                        help_text="The old primary id for the entry",
                        null=True,
                        unique=True,
                    ),
                ),
                ("inserted", models.DateTimeField(default=django.utils.timezone.now)),
                ("updated", models.DateTimeField(default=django.utils.timezone.now)),
                ("name", models.CharField(max_length=255)),
                ("weight", positions.fields.PositionField(default=-1)),
                (
                    "default",
                    models.BooleanField(
                        blank=True, default=None, null=True, unique=True
                    ),
                ),
            ],
            options={
                "verbose_name": "Member Status",
                "verbose_name_plural": "Member Statuses",
                "ordering": ["weight"],
            },
        ),
        migrations.CreateModel(
            name="Season",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "old_sk_id",
                    models.PositiveIntegerField(
                        blank=True,
                        help_text="The old primary id for the entry",
                        null=True,
                        unique=True,
                    ),
                ),
                ("inserted", models.DateTimeField(default=django.utils.timezone.now)),
                ("updated", models.DateTimeField(default=django.utils.timezone.now)),
                (
                    "hockey_canada_id",
                    models.PositiveBigIntegerField(
                        blank=True, help_text="HcID Value", null=True, unique=True
                    ),
                ),
                (
                    "hockey_canada_system_id",
                    models.CharField(
                        blank=True,
                        help_text="*_id value for api, not meant to be editable or seen by users. Backend only.",
                        max_length=255,
                        null=True,
                        unique=True,
                    ),
                ),
                ("name", models.CharField(max_length=50)),
                ("start", models.DateField(null=True)),
                ("end", models.DateField(null=True)),
                ("mbs_id", models.PositiveIntegerField(default=0)),
                ("gsi_id", models.PositiveIntegerField(default=0)),
                (
                    "inserted_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="%(class)s_inserted",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "updated_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="%(class)s_updated",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["start"],
            },
        ),
        migrations.CreateModel(
            name="SubDivision",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "old_sk_id",
                    models.PositiveIntegerField(
                        blank=True,
                        help_text="The old primary id for the entry",
                        null=True,
                        unique=True,
                    ),
                ),
                ("inserted", models.DateTimeField(default=django.utils.timezone.now)),
                ("updated", models.DateTimeField(default=django.utils.timezone.now)),
                (
                    "hockey_canada_id",
                    models.PositiveBigIntegerField(
                        blank=True, help_text="HcID Value", null=True, unique=True
                    ),
                ),
                (
                    "hockey_canada_system_id",
                    models.CharField(
                        blank=True,
                        help_text="*_id value for api, not meant to be editable or seen by users. Backend only.",
                        max_length=255,
                        null=True,
                        unique=True,
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                ("weight", positions.fields.PositionField(default=-1)),
                ("body_checking", models.BooleanField(default=False)),
                ("player_rating_factor", models.PositiveIntegerField(default=100)),
                ("default_number_of_teams", models.PositiveIntegerField(default=4)),
                ("inactive", models.BooleanField(default=False)),
                (
                    "division",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="subdivisions",
                        to="core.division",
                    ),
                ),
                (
                    "inserted_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="%(class)s_inserted",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "league",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="subdivisions",
                        to="core.league",
                    ),
                ),
                (
                    "season",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="subdivisions",
                        to="core.season",
                    ),
                ),
                (
                    "updated_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="%(class)s_updated",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["weight"],
            },
        ),
        migrations.CreateModel(
            name="Setting",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "app",
                    models.CharField(
                        help_text="Typically the app it belongs to i.e. games",
                        max_length=255,
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        help_text="Name that corresponds to the value stored i.e. username",
                        max_length=255,
                    ),
                ),
                (
                    "hostname",
                    models.CharField(
                        blank=True,
                        default="",
                        help_text="Name of the computer this setting is specific to.",
                        max_length=255,
                    ),
                ),
                ("value", models.TextField(blank=True)),
                ("inserted", models.DateTimeField(auto_now_add=True)),
                ("updated", models.DateTimeField(auto_now=True)),
            ],
            options={
                "ordering": ["app", "name", "hostname"],
                "abstract": False,
                "unique_together": {("app", "name", "hostname")},
            },
        ),
        migrations.CreateModel(
            name="PermissionOverrides",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "old_sk_id",
                    models.PositiveIntegerField(
                        blank=True,
                        help_text="The old primary id for the entry",
                        null=True,
                        unique=True,
                    ),
                ),
                ("inserted", models.DateTimeField(default=django.utils.timezone.now)),
                ("updated", models.DateTimeField(default=django.utils.timezone.now)),
                ("team_can_edit", models.BooleanField(default=True)),
                ("team_can_vote", models.BooleanField(default=False)),
                ("assigned_on", models.DateTimeField(blank=True, null=True)),
                (
                    "assigned_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "division",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="+",
                        to="core.division",
                    ),
                ),
                (
                    "inserted_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="%(class)s_inserted",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "league",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="+",
                        to="core.league",
                    ),
                ),
                (
                    "season",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="+",
                        to="core.season",
                    ),
                ),
                (
                    "subdivision",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="+",
                        to="core.subdivision",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
