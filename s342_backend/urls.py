from django.contrib import admin
from django.urls import path, include
from rest_framework import routers

from main.views import AuthenticationView, FinancialSimulation, ExperimentViewSet, BuildingViewSet

router = routers.DefaultRouter()
router.register(r'auth', AuthenticationView, basename='auth')
router.register(r'financial', FinancialSimulation, basename='financial')

# v1 domain endpoints
router.register(r'experiments', ExperimentViewSet, basename='experiments')
router.register(
    r'experiments/(?P<experiment_id>[^/.]+)/buildings',
    BuildingViewSet,
    basename='experiment-buildings'
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include(router.urls)),
]