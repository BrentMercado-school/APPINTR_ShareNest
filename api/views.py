from rest_framework import generics
from django.http import JsonResponse
from rest_framework.parsers import MultiPartParser, JSONParser, FormParser
from rest_framework.response import Response

# TODO: 4 for controlling what data the API returns

def get_health_check(request):
    return JsonResponse(
        {
            "status": "ok",
            "message": "API is running"
        },
        status=200
    )