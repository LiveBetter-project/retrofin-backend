from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

from django.utils import timezone
from rest_framework import serializers

from main.models import Experiment, Building

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'created_at']
        read_only_fields = ['id', 'created_at']


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2', 'first_name', 'last_name']

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user


class LoginSerializer(serializers.Serializer):
    """Serializer for user login"""
    username = serializers.CharField(required=True)
    password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )


class RefreshTokenSerializer(serializers.Serializer):
    """Serializer for token refresh"""
    refresh_token = serializers.CharField(required=True)


class ExperimentSerializer(serializers.ModelSerializer):
    last_run = serializers.SerializerMethodField()

    class Meta:
        model = Experiment
        fields = ["id", "name", "created_at", "status", "last_run"]

    def get_last_run(self, obj):
        # v1: runs model not implemented yet
        return None

    def validate_name(self, value):
        if value is None:
            return value
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Name cannot be blank.")
        return value

    def create(self, validated_data):
        # Default name if omitted
        name = validated_data.get("name")
        if not name or not str(name).strip():
            ts = timezone.now().replace(microsecond=0).isoformat().replace("+00:00", "Z")
            validated_data["name"] = f"Experiment_{ts}"
        # status defaults to draft in model
        return super().create(validated_data)


class ExperimentUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Experiment
        fields = ["name"]

    def validate_name(self, value):
        value = (value or "").strip()
        if not value:
            raise serializers.ValidationError("Name cannot be blank.")
        return value


class BuildingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Building
        fields = [
            "id",
            "experiment",
            "name",
            "country",
            "region",
            "year_of_construction",
            "floor_area",
            "eem_capex",
            "eem_energy_savings",
            "eem_maintenance_cost",
            "eem_lifetime",
        ]
        read_only_fields = ["id", "experiment"]

    def validate_country(self, value):
        v = (value or "").strip().upper()
        if len(v) != 2:
            raise serializers.ValidationError("Country must be a 2-letter code (e.g., GR).")
        return v

    def validate_eem_energy_savings(self, value):
        # Decimal comes in as Decimal; comparisons are fine
        if value < 0 or value > 1:
            raise serializers.ValidationError("eem_energy_savings must be between 0 and 1.")
        return value

    def validate_year_of_construction(self, value):
        if value < 1800 or value > 2100:
            raise serializers.ValidationError("year_of_construction out of supported range.")
        return value