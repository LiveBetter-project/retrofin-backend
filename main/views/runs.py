from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from main.models import Experiment, Run


class RunViewSet(viewsets.ViewSet):
    """
    GET /api/experiments/{experiment_id}/runs/{pk}/
    Poll the status of a specific run.
    """
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, experiment_id=None, pk=None):
        experiment = get_object_or_404(Experiment, id=experiment_id, user=request.user)
        run = get_object_or_404(Run, id=pk, experiment=experiment)
        return Response({
            "run_id": run.id,
            "status": run.status,
            "started_at": run.started_at,
            "finished_at": run.finished_at,
        })
