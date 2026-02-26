from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from main.views import AuthenticationView, FinancialSimulation

router = routers.DefaultRouter()
router.register(r'auth', AuthenticationView, basename='auth')
router.register(r'financial', FinancialSimulation, basename='financial')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
]
