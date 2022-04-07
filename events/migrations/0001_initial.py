# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-06-28 18:28
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Association",
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
                ("name", models.CharField(max_length=255, verbose_name="Association")),
                ("full_name", models.CharField(max_length=255)),
                ("location", models.CharField(blank=True, max_length=255)),
                ("website", models.CharField(blank=True, max_length=500)),
                (
                    "tournament_listing_url",
                    models.CharField(blank=True, max_length=500),
                ),
                ("weight", models.IntegerField(default=100)),
                ("created", models.DateTimeField(auto_now_add=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Exhibition",
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
                ("season_id", models.IntegerField(default=0)),
                ("name", models.CharField(blank=True, max_length=255)),
                ("other_team", models.CharField(max_length=255)),
                (
                    "destination",
                    models.CharField(help_text="City, Province", max_length=255),
                ),
                ("arena", models.CharField(blank=True, max_length=255)),
                ("start_date", models.DateField()),
                ("end_date", models.DateField(blank=True, null=True)),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("last_updated", models.DateTimeField(auto_now=True)),
                ("source", models.CharField(blank=True, max_length=255)),
                ("notes", models.TextField(blank=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Tournament",
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
                ("season_id", models.IntegerField(default=0)),
                (
                    "association_other",
                    models.CharField(
                        blank=True,
                        help_text="Only supply if the association is not listed above.",
                        max_length=255,
                    ),
                ),
                ("sanction_number", models.CharField(blank=True, max_length=255)),
                ("name", models.CharField(max_length=255)),
                (
                    "location",
                    models.CharField(help_text="City, Province", max_length=255),
                ),
                (
                    "start_date",
                    models.DateField(
                        help_text="Please supply the start date of the tournament itself, not just the date you play if the two dates differ."
                    ),
                ),
                ("end_date", models.DateField(blank=True, null=True)),
                (
                    "divisions",
                    models.CharField(
                        blank=True,
                        help_text="Divisions tournament is for",
                        max_length=4000,
                    ),
                ),
                ("source", models.CharField(default="email", max_length=255)),
                ("verified", models.BooleanField(default=False)),
                ("verified_date", models.DateField(blank=True, null=True)),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("last_updated", models.DateTimeField(auto_now=True)),
                (
                    "website",
                    models.CharField(
                        blank=True,
                        help_text="URL to webpage about tournament",
                        max_length=4000,
                    ),
                ),
                ("notes", models.TextField(blank=True)),
                (
                    "association",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="events.Association",
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "permissions": (("tournament_verify", "Can verify legitimacy."),),
            },
        ),
    ]
