# Generated by Django 2.1.5 on 2019-05-31 20:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("events", "0025_exhibition_contact_name"),
    ]

    operations = [
        migrations.RenameField(
            model_name="association",
            old_name="created",
            new_name="inserted",
        ),
        migrations.RemoveField(
            model_name="association",
            name="created_by",
        ),
    ]