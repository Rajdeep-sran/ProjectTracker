# Generated by Django 5.2.3 on 2025-07-08 12:49

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app1", "0002_rename_deadline_project_end_date_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="Milestone",
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
                ("title", models.CharField(max_length=100)),
                ("due_date", models.DateField(blank=True, null=True)),
                ("is_completed", models.BooleanField(default=False)),
                (
                    "priority",
                    models.CharField(
                        choices=[
                            ("High", "High"),
                            ("Medium", "Medium"),
                            ("Low", "Low"),
                        ],
                        default="Medium",
                        max_length=10,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "project",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="milestones",
                        to="app1.project",
                    ),
                ),
            ],
        ),
    ]
