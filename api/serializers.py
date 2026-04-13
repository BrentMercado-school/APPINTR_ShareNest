from rest_framework import serializers, generics
from django.contrib.auth.hashers import make_password, check_password

from api.models import Category, User, Item


# TODO: 3 for converting models to usable data on frontend
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = '__all__'

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = '__all__'
