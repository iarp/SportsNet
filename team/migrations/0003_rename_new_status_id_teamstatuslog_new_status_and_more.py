# Generated by Django 4.0.3 on 2022-03-09 17:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("team", "0002_stafftype_web_access"),
    ]

    operations = [
        migrations.RenameField(
            model_name="teamstatuslog",
            old_name="new_status_id",
            new_name="new_status",
        ),
        migrations.RenameField(
            model_name="teamstatuslog",
            old_name="new_status_reason_id",
            new_name="new_status_reason",
        ),
        migrations.RenameField(
            model_name="teamstatuslog",
            old_name="old_status_id",
            new_name="old_status",
        ),
        migrations.RenameField(
            model_name="teamstatuslog",
            old_name="old_status_reason_id",
            new_name="old_status_reason",
        ),
        migrations.AddField(
            model_name="teamstatus",
            name="considered_approved",
            field=models.BooleanField(
                default=False,
                help_text="If a team is assigned this status, are they technically considered approved in hockey canada?",
            ),
        ),
    ]