from django.urls import path

from api.views import get_health_check

# TODO: 5 for routing

urlpatterns = [
    path("health-check/", get_health_check, name="health-check"),
]