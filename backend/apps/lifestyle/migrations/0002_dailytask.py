import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("body_shape", "0001_initial"),
        ("lifestyle", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="DailyTask",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=120)),
                ("description", models.CharField(blank=True, max_length=400)),
                ("task_date", models.DateField()),
                ("duration_minutes", models.PositiveIntegerField()),
                ("is_completed", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("daily_plan", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="tasks", to="lifestyle.dailyplan")),
                ("profile", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="daily_tasks", to="body_shape.profile")),
            ],
            options={"ordering": ["task_date", "created_at", "id"]},
        ),
        migrations.AddConstraint(
            model_name="dailytask",
            constraint=models.CheckConstraint(condition=models.Q(("duration_minutes__gt", 0)), name="daily_task_duration_positive"),
        ),
    ]
