# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-09-08 00:15
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("events", "0011_exhibition_required_referee_or_timekeeper"),
    ]

    operations = [
        migrations.AlterField(
            model_name="exhibition",
            name="arena",
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
