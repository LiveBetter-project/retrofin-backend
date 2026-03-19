from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from main.models import Building, Experiment
from main.serializers import BuildingSerializer


class BuildingViewSet(viewsets.ModelViewSet):
    """
    /api/experiments/{experimentId}/buildings
    """
    permission_classes = [IsAuthenticated]
    serializer_class = BuildingSerializer

    def _get_experiment(self):
        return get_object_or_404(
            Experiment,
            id=self.kwargs["experiment_id"],
            user=self.request.user,
        )

    def get_queryset(self):
        exp = self._get_experiment()
        return Building.objects.filter(experiment=exp).order_by("-created_at")

    def perform_create(self, serializer):
        exp = self._get_experiment()
        serializer.save(experiment=exp)