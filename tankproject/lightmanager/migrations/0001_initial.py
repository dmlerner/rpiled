# Generated by Django 3.2.10 on 2021-12-12 19:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="PCA9685",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("frequency", models.IntegerField(default=2441)),
            ],
        ),
        migrations.CreateModel(
            name="PWMChannel",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("index", models.IntegerField(unique=True)),
                ("duty_cycle", models.IntegerField(default=0)),
                ("color", models.CharField(max_length=30)),
                ("driver_current", models.IntegerField(default=700)),
                ("color_abbreviation", models.CharField(max_length=20)),
                (
                    "controller",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="lightmanager.pca9685",
                    ),
                ),
            ],
        ),
    ]
