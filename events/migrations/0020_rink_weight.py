# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-11-22 21:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("events", "0019_auto_20171122_1635"),
    ]

    operations = [
        migrations.AddField(
            model_name="rink",
            name="weight",
            field=models.PositiveIntegerField(default=100),
        ),
    ]