from django.contrib import admin
from django.contrib.auth import get_user_model
from main.models import Experiment, Building

User = get_user_model()


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "username", "email", "is_staff", "is_active", "created_at")
    search_fields = ("username", "email")


@admin.register(Experiment)
class ExperimentAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "user", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("id", "name", "user__username")


@admin.register(Building)
class BuildingAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "experiment", "country", "year_of_construction", "floor_area", "created_at")
    search_fields = ("id", "name", "experiment__id")