# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-11-22 21:47
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("events", "0020_rink_weight"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="rink",
            options={"ordering": ["weight", "name"]},
        ),
    ]