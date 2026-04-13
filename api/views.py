from rest_framework import generics
from django.http import JsonResponse
from rest_framework.generics import ListAPIView
from rest_framework.parsers import MultiPartParser, JSONParser, FormParser
from rest_framework.response import Response

from api.models import Category, User, Item
from api.serializers import CategorySerializer, UserSerializer, ItemSerializer


# TODO: 4 for controlling what data the API returns

def get_health_check(request):
    return JsonResponse(
        {
            "status": "ok",
            "message": "API is running"
        },
        status=200
    )

class CategoryListAPIView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class UserListAPIView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class ItemListAPIView(generics.ListAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer