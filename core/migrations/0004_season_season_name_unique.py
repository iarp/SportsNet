# Generated by Django 4.0.3 on 2022-03-10 17:19

from django.db import migrations, models
import django.db.models.functions.text


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0003_division_inserted_by_division_updated_by_and_more"),
    ]

    operations = [
        migrations.AddConstraint(
            model_name="season",
            constraint=models.UniqueConstraint(
                django.db.models.functions.text.Lower("name"), name="season_name_unique"
            ),
        ),
    ]