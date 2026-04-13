from django.urls import path

from api.views import get_health_check, CategoryListAPIView, UserListAPIView, ItemListAPIView, RegisterUserAPIView

# TODO: 5 for routing

urlpatterns = [
    path("health-check/", get_health_check, name="health-check"),
    path("categories/", CategoryListAPIView.as_view(), name="categories"),
    path("users/", UserListAPIView.as_view(), name="users"),
    path("items/", ItemListAPIView.as_view(), name="items"),
    path("users/register/", RegisterUserAPIView.as_view(), name="register"),
]