# Generated by Django 4.0.3 on 2022-03-12 21:00

from django.db import migrations, models
import django.db.models.functions.text


class Migration(migrations.Migration):

    dependencies = [
        ("team", "0001_initial"),
    ]

    operations = [
        migrations.AddConstraint(
            model_name="teamstatus",
            constraint=models.UniqueConstraint(
                django.db.models.functions.text.Lower("name"),
                name="teamstatus_name_uniqueness",
            ),
        ),
    ]