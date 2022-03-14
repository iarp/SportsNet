# Generated by Django 4.0.3 on 2022-03-14 21:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "team",
            "0004_remove_playertype_change_causes_player_flag_on_team_to_enable_and_more",
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="team",
            name="approval_required",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="team",
            name="registration_status",
            field=models.BooleanField(default=False),
        ),
    ]