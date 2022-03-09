# Generated by Django 4.0.3 on 2022-03-09 02:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("team", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="stafftype",
            name="web_access",
            field=models.BooleanField(
                default=False,
                help_text="Can a member at this level login to the website?",
            ),
        ),
    ]
