from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.response import Response

from main.models import Experiment
from main.serializers import ExperimentSerializer, ExperimentUpdateSerializer


class ExperimentViewSet(viewsets.ModelViewSet):
    """
    /api/v1/experiments
    """
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