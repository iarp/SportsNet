# Generated by Django 2.1.5 on 2019-04-10 19:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("events", "0024_auto_20181127_1821"),
    ]

    operations = [
        migrations.AddField(
            model_name="exhibition",
            name="contact_name",
            field=models.CharField(
                blank=True,
                help_text="Whose phone number are you supplying above?",
                max_length=255,
            ),
        ),
    ]
