# Generated by Django 4.0.3 on 2022-03-10 02:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("team", "0006_stafftype_change_causes_staff_flag_on_team_to_enable_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="team",
            name="status_reason",
        ),
        migrations.RemoveField(
            model_name="teamstatuslog",
            name="new_status_reason",
        ),
        migrations.RemoveField(
            model_name="teamstatuslog",
            name="old_status_reason",
        ),
        migrations.DeleteModel(
            name="TeamStatusReason",
        ),
    ]
