from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(
            name="UploadedFile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("file_name", models.CharField(max_length=255)),
                ("file_path", models.FileField(upload_to="uploads/")),
                ("upload_time", models.DateTimeField(auto_now_add=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("uploaded", "Uploaded"),
                            ("extracted", "Extracted"),
                            ("validated", "Validated"),
                            ("failed", "Failed"),
                        ],
                        default="uploaded",
                        max_length=20,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ValidationRun",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("total_checks", models.PositiveIntegerField(default=0)),
                ("passed_checks", models.PositiveIntegerField(default=0)),
                ("failed_checks", models.PositiveIntegerField(default=0)),
                (
                    "status",
                    models.CharField(
                        choices=[("passed", "Passed"), ("failed", "Failed"), ("warning", "Warning")],
                        default="passed",
                        max_length=20,
                    ),
                ),
                ("report_file", models.FileField(blank=True, null=True, upload_to="reports/")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "uploaded_file",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="validation_runs",
                        to="verifier.uploadedfile",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ValidationIssue",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("issue_type", models.CharField(max_length=80)),
                ("severity", models.CharField(choices=[("low", "Low"), ("medium", "Medium"), ("high", "High")], max_length=20)),
                ("description", models.TextField()),
                ("expected_value", models.CharField(blank=True, max_length=255)),
                ("actual_value", models.CharField(blank=True, max_length=255)),
                ("row_number", models.PositiveIntegerField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "validation_run",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="issues",
                        to="verifier.validationrun",
                    ),
                ),
            ],
        ),
    ]
