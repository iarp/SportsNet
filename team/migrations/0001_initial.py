# Generated by Django 4.0.3 on 2022-03-09 01:32

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import positions.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("core", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="StaffStatus",
            fields=[
                (
                    "id",
                    models.BigAutoField(
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
                ("inserted", models.DateTimeField(auto_now_add=True)),
                ("updated", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=255)),
                ("weight", positions.fields.PositionField(default=-1)),
                ("include_in_roster_export", models.BooleanField(default=True)),
            ],
            options={
                "verbose_name": "Team Staff Status",
                "verbose_name_plural": "Team Staff Statuses",
                "ordering": ["weight"],
            },
        ),
        migrations.CreateModel(
            name="StaffStatusReason",
            fields=[
                (
                    "id",
                    models.BigAutoField(
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
                ("inserted", models.DateTimeField(auto_now_add=True)),
                ("updated", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=255)),
                ("weight", positions.fields.PositionField(default=0)),
            ],
            options={
                "verbose_name": "Team Staff Status Reason",
                "verbose_name_plural": "Team Staff Status Reasons",
                "ordering": ["weight"],
            },
        ),
        migrations.CreateModel(
            name="StaffType",
            fields=[
                (
                    "id",
                    models.BigAutoField(
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
                ("inserted", models.DateTimeField(auto_now_add=True)),
                ("updated", models.DateTimeField(auto_now=True)),
                ("team_can_edit", models.BooleanField(default=True)),
                ("team_can_vote", models.BooleanField(default=False)),
                ("name", models.CharField(max_length=255)),
                ("weight", positions.fields.PositionField(default=-1)),
                ("required", models.BooleanField(default=False)),
            ],
            options={
                "verbose_name": "Team Staff Type",
                "verbose_name_plural": "Team Staff Types",
                "ordering": ["weight"],
            },
        ),
        migrations.CreateModel(
            name="Team",
            fields=[
                (
                    "id",
                    models.BigAutoField(
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
                ("inserted", models.DateTimeField(auto_now_add=True)),
                ("updated", models.DateTimeField(auto_now=True)),
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
                ("number", models.PositiveIntegerField(default=0)),
                ("jersey_home", models.CharField(blank=True, max_length=255)),
                ("jersey_away", models.CharField(blank=True, max_length=255)),
                ("submitted", models.BooleanField(default=False)),
                ("submitted_date", models.DateTimeField(blank=True, null=True)),
                ("approved", models.BooleanField(default=False)),
                ("active", models.BooleanField(default=True)),
                ("draft_start_position", models.PositiveIntegerField(default=1)),
                ("weight", positions.fields.PositionField(default=-1)),
                (
                    "division",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="teams",
                        to="core.division",
                    ),
                ),
                (
                    "league",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="teams",
                        to="core.league",
                    ),
                ),
                (
                    "season",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="teams",
                        to="core.season",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="TeamStatus",
            fields=[
                (
                    "id",
                    models.BigAutoField(
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
                ("inserted", models.DateTimeField(auto_now_add=True)),
                ("updated", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=255)),
                ("weight", positions.fields.PositionField(default=0)),
                ("include_in_roster_export", models.BooleanField(default=True)),
                ("ClrChgdStfPlyrSts", models.BooleanField(default=False)),
            ],
            options={
                "verbose_name": "Team Status",
                "verbose_name_plural": "Team Statuses",
                "ordering": ["weight"],
            },
        ),
        migrations.CreateModel(
            name="TeamStatusReason",
            fields=[
                (
                    "id",
                    models.BigAutoField(
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
                ("inserted", models.DateTimeField(auto_now_add=True)),
                ("updated", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=255)),
                ("weight", positions.fields.PositionField(default=0)),
                (
                    "status",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="reasons",
                        to="team.teamstatus",
                    ),
                ),
            ],
            options={
                "verbose_name": "Team Status Reason",
                "verbose_name_plural": "Team Status Reasons",
                "ordering": ["weight"],
            },
        ),
        migrations.CreateModel(
            name="TeamStatusLog",
            fields=[
                (
                    "id",
                    models.BigAutoField(
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
                ("inserted", models.DateTimeField(auto_now_add=True)),
                ("updated", models.DateTimeField(auto_now=True)),
                (
                    "new_status_id",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="team.teamstatus",
                    ),
                ),
                (
                    "new_status_reason_id",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="team.teamstatusreason",
                    ),
                ),
                (
                    "old_status_id",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="team.teamstatus",
                    ),
                ),
                (
                    "old_status_reason_id",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="team.teamstatusreason",
                    ),
                ),
                (
                    "team",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="team.team"
                    ),
                ),
            ],
            options={
                "verbose_name": "Team Status Log",
                "verbose_name_plural": "Team Status Logs",
                "ordering": ["inserted"],
            },
        ),
        migrations.CreateModel(
            name="TeamNote",
            fields=[
                (
                    "id",
                    models.BigAutoField(
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
                ("inserted", models.DateTimeField(auto_now_add=True)),
                ("updated", models.DateTimeField(auto_now=True)),
                (
                    "type",
                    models.CharField(
                        choices=[("ROSTER", "Roster"), ("PLAYER", "Player")],
                        default="ROSTER",
                        max_length=255,
                    ),
                ),
                ("note", models.TextField()),
                (
                    "team",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="notes",
                        to="team.team",
                    ),
                ),
            ],
            options={
                "verbose_name": "Team Note",
                "verbose_name_plural": "Team Notes",
                "ordering": ["inserted"],
            },
        ),
        migrations.AddField(
            model_name="team",
            name="status",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT, to="team.teamstatus"
            ),
        ),
        migrations.AddField(
            model_name="team",
            name="status_reason",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT, to="team.teamstatusreason"
            ),
        ),
        migrations.AddField(
            model_name="team",
            name="subdivision",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="teams",
                to="core.subdivision",
            ),
        ),
        migrations.CreateModel(
            name="Staff",
            fields=[
                (
                    "id",
                    models.BigAutoField(
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
                ("inserted", models.DateTimeField(auto_now_add=True)),
                ("updated", models.DateTimeField(auto_now=True)),
                ("importer", models.BooleanField(default=False)),
                ("affiliate", models.BooleanField(default=False)),
                ("tryout", models.BooleanField(default=False)),
                ("registration_date", models.DateTimeField(blank=True, null=True)),
                ("release_date", models.DateTimeField(blank=True, null=True)),
                (
                    "division",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="staff",
                        to="core.division",
                    ),
                ),
                (
                    "league",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="staff",
                        to="core.league",
                    ),
                ),
                (
                    "season",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="staff",
                        to="core.season",
                    ),
                ),
                (
                    "status",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="team.staffstatus",
                    ),
                ),
                (
                    "subdivision",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="staff",
                        to="core.subdivision",
                    ),
                ),
                (
                    "team",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="staff",
                        to="team.team",
                    ),
                ),
                (
                    "type",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT, to="team.stafftype"
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                        related_name="staff_assignments",
                    ),
                ),
            ],
            options={
                "verbose_name": "Team Staff",
                "verbose_name_plural": "Team Staff",
            },
        ),
    ]
