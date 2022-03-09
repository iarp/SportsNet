# Generated by Django 4.0.3 on 2022-03-09 21:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("team", "0003_rename_new_status_id_teamstatuslog_new_status_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="teamstatus",
            old_name="ClrChgdStfPlyrSts",
            new_name="clear_changed_staff_players_flag",
        ),
        migrations.AddField(
            model_name="team",
            name="players_has_changed_flag",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="team",
            name="staff_has_changed_flag",
            field=models.BooleanField(default=False),
        ),
    ]
