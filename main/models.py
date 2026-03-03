import secrets
from django.contrib.auth.models import AbstractUser
from django.db import models


def generate_experiment_id():
    return "exp_" + secrets.token_hex(8)


def generate_building_id():
    return "bld_" + secrets.token_hex(8)


class User(AbstractUser):
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "users"
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return self.username


class Experiment(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        READY = "ready", "Ready"
        RUNNING = "running", "Running"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"

    id = models.CharField(primary_key=True, max_length=32, default=generate_experiment_id, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="experiments")

    name = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "experiments"
        indexes = [
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["user", "status"]),
        ]

    def __str__(self):
        return f"{self.id} ({self.name})"


class Building(models.Model):
    id = models.CharField(primary_key=True, max_length=32, default=generate_building_id, editable=False)
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE, related_name="buildings")

    name = models.CharField(max_length=200)
    country = models.CharField(max_length=2)  # ISO-3166-1 alpha-2 (e.g. GR)
    region = models.CharField(max_length=120, blank=True, default="")
    year_of_construction = models.PositiveIntegerField()
    floor_area = models.DecimalField(max_digits=12, decimal_places=2)

    # v1 aggregated EEM fields embedded in Building
    eem_capex = models.DecimalField(max_digits=14, decimal_places=2)
    eem_energy_savings = models.DecimalField(max_digits=7, decimal_places=4)  # 0..1
    eem_maintenance_cost = models.DecimalField(max_digits=14, decimal_places=2)
    eem_lifetime = models.PositiveIntegerField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "buildings"
        indexes = [
            models.Index(fields=["experiment", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.id} ({self.name})"