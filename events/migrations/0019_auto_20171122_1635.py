# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-11-22 21:35
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("events", "0018_auto_20171107_1848"),
    ]

    operations = [
        migrations.AlterField(
            model_name="rink",
            name="city",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name="rink",
            name="province",
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
