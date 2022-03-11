# Generated by Django 4.0.3 on 2022-03-11 17:30

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    replaces = [
        ("core", "0010_alter_user_options_user_inserted_by_user_old_sk_id_and_more"),
        ("core", "0011_alter_user_inserted_alter_user_updated"),
    ]

    dependencies = [
        ("core", "0009_alter_division_inserted_alter_division_updated_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="user",
            options={},
        ),
        migrations.AddField(
            model_name="user",
            name="inserted_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="old_sk_id",
            field=models.PositiveIntegerField(
                blank=True,
                help_text="The old primary id for the entry",
                null=True,
                unique=True,
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="updated_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="user",
            name="inserted",
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name="user",
            name="updated",
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
