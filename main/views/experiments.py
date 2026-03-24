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

    @action(detail=True, methods=["get"], url_path="results")
    def results(self, request, pk=None):
        experiment = self.get_object()
        latest_run = experiment.runs.order_by("-started_at").first()
        if latest_run is None:
            return Response({"run_id": None, "run_status": None, "items": []})

        def _f(v):
            return float(v) if v is not None else None

        items = []
        for sr in latest_run.scheme_results.select_related("scheme").all():
            items.append({
                "scheme_id": sr.scheme.id,
                "scheme_type": sr.scheme.scheme_type,
                "irr_p5":  _f(sr.irr_p5),  "irr_p10":  _f(sr.irr_p10),  "irr_p25":  _f(sr.irr_p25),
                "irr_p50": _f(sr.irr_p50), "irr_p75":  _f(sr.irr_p75),  "irr_p90":  _f(sr.irr_p90),  "irr_p95":  _f(sr.irr_p95),
                "npv_p5":  _f(sr.npv_p5),  "npv_p10":  _f(sr.npv_p10),  "npv_p25":  _f(sr.npv_p25),
                "npv_p50": _f(sr.npv_p50), "npv_p75":  _f(sr.npv_p75),  "npv_p90":  _f(sr.npv_p90),  "npv_p95":  _f(sr.npv_p95),
                "pbp_p5":  _f(sr.pbp_p5),  "pbp_p10":  _f(sr.pbp_p10),  "pbp_p25":  _f(sr.pbp_p25),
                "pbp_p50": _f(sr.pbp_p50), "pbp_p75":  _f(sr.pbp_p75),  "pbp_p90":  _f(sr.pbp_p90),  "pbp_p95":  _f(sr.pbp_p95),
                "dpp_p5":  _f(sr.dpp_p5),  "dpp_p10":  _f(sr.dpp_p10),  "dpp_p25":  _f(sr.dpp_p25),
                "dpp_p50": _f(sr.dpp_p50), "dpp_p75":  _f(sr.dpp_p75),  "dpp_p90":  _f(sr.dpp_p90),  "dpp_p95":  _f(sr.dpp_p95),
                "roi_p5":  _f(sr.roi_p5),  "roi_p10":  _f(sr.roi_p10),  "roi_p25":  _f(sr.roi_p25),
                "roi_p50": _f(sr.roi_p50), "roi_p75":  _f(sr.roi_p75),  "roi_p90":  _f(sr.roi_p90),  "roi_p95":  _f(sr.roi_p95),
                "pr_npv_positive":        _f(sr.pr_npv_positive),
                "pr_pbp_within_lifetime": _f(sr.pr_pbp_within_lifetime),
                "pr_dpp_within_lifetime": _f(sr.pr_dpp_within_lifetime),
                "disc_target_used":       _f(sr.disc_target_used),
                "n_sims": sr.n_sims,
            })
        return Response({"run_id": latest_run.id, "run_status": latest_run.status, "items": items})

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