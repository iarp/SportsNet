# Generated by Django 4.0.3 on 2022-03-17 19:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("team", "0006_stafftype_team_can_access"),
    ]

    operations = [
        migrations.AddField(
            model_name="team",
            name="comments",
            field=models.TextField(blank=True),
        ),
    ]