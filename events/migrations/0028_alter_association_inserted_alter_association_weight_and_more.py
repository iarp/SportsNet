# Generated by Django 4.0.3 on 2022-03-24 13:49

from django.db import migrations, models
import django.db.models.functions.text
import django.utils.timezone
import positions.fields


class Migration(migrations.Migration):

    dependencies = [
        ("events", "0027_remove_exhibition_created_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="association",
            name="inserted",
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name="association",
            name="weight",
            field=positions.fields.PositionField(default=-1),
        ),
        migrations.AlterField(
            model_name="rink",
            name="weight",
            field=positions.fields.PositionField(default=-1),
        ),
        migrations.AddConstraint(
            model_name="association",
            constraint=models.UniqueConstraint(
                django.db.models.functions.text.Lower("name"),
                name="association_name_uniqueness",
            ),
        ),
        migrations.AddConstraint(
            model_name="rink",
            constraint=models.UniqueConstraint(
                django.db.models.functions.text.Lower("name"),
                django.db.models.functions.text.Lower("city"),
                django.db.models.functions.text.Lower("province"),
                name="rink_name_city_province_uniqueness",
            ),
        ),
    ]