from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from main.models import Experiment, Run
from main.serializers import ExperimentSerializer, ExperimentUpdateSerializer
from main.views.financial_simulation import *


class ExperimentViewSet(viewsets.ModelViewSet):
    """
    /api/experiments
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ExperimentSerializer

    def get_queryset(self):
        return Experiment.objects.filter(user=self.request.user).order_by("-created_at")

    def get_serializer_class(self):
        if self.action in ("partial_update", "update"):
            return ExperimentUpdateSerializer
        return ExperimentSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        # Keep response shape identical to serializer (includes default name)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, *args, **kwargs):
        # Rename only (and future editable metadata)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        # Return full experiment shape
        return Response(ExperimentSerializer(instance).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"], url_path="readiness")
    def readiness(self, request, pk=None):
        experiment = self.get_object()
        missing = []
        if not experiment.buildings.exists():
            missing.append({"path": "buildings", "message": "At least one building is required."})
        if not experiment.schemes.exists():
            missing.append({"path": "financing_schemes", "message": "Select at least one financing scheme."})
        return Response({"is_ready": len(missing) == 0, "missing": missing})

    @action(detail=True, methods=["post"], url_path="run")
    def run(self, request, pk=None):
        experiment = self.get_object()

        # Readiness guard
        missing = []
        if not experiment.buildings.exists():
            missing.append({"path": "buildings", "message": "At least one building is required."})
        if not experiment.schemes.exists():
            missing.append({"path": "financing_schemes", "message": "Select at least one financing scheme."})
        if missing:
            return Response(
                {"error": {"code": "NOT_READY", "message": "Experiment is not ready to run.", "details": missing}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        run = Run.objects.create(experiment=experiment)
        experiment.status = Experiment.Status.RUNNING
        experiment.save(update_fields=["status", "updated_at"])
        run_experiment(experiment, run)
        return Response(
            {"run_id": run.id, "status": run.status, "started_at": run.started_at},
            status=status.HTTP_201_CREATED,
        )