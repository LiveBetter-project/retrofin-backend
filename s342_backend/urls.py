from django.contrib import admin
from django.urls import path, include
from rest_framework import routers

from main.views import (
    AuthenticationView,
    ExperimentViewSet,
    BuildingViewSet,
    FinancingSchemeCatalogViewSet,
    ExperimentSchemesViewSet,
    RunViewSet,
)

router = routers.DefaultRouter()
router.register(r'auth', AuthenticationView, basename='auth')
# router.register(r'financial', FinancialSimulation, basename='financial')

# Financing scheme catalog (static, no experiment scope)
router.register(r'financing-schemes', FinancingSchemeCatalogViewSet, basename='financing-schemes')

# v1 domain endpoints
router.register(r'experiments', ExperimentViewSet, basename='experiments')
router.register(
    r'experiments/(?P<experiment_id>[^/.]+)/buildings',
    BuildingViewSet,
    basename='experiment-buildings',
)
router.register(
    r'experiments/(?P<experiment_id>[^/.]+)/financing-schemes',
    ExperimentSchemesViewSet,
    basename='experiment-financing-schemes',
)
router.register(
    r'experiments/(?P<experiment_id>[^/.]+)/runs',
    RunViewSet,
    basename='experiment-runs',
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
]