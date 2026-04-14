from django.urls import path

from api.views import get_health_check, CategoryListAPIView, UserListAPIView, ItemListAPIView, RegisterUserAPIView, \
    LoginUserAPIView, CurrentUserAPIView, UserItemsAPIView, LogoutUserAPIView, CreateItemAPIView, UpdateItemAPIView, \
    DeleteItemAPIView, ItemDetailAPIView, CreateBorrowFormAPIView, BorrowListAPIView, OwnedItemBorrowRequestsAPIView, \
    AcceptBorrowRequestAPIView, DeclineBorrowRequestAPIView, MyBorrowRequestsAPIView, MyBorrowedItemsAPIView, \
    CreateReturnFormAPIView, UpdateCurrentUserAPIView

# TODO: 5 for routing

urlpatterns = [
    path("health-check/", get_health_check, name="health-check"),
    path("categories/", CategoryListAPIView.as_view(), name="categories"),
    path("users/", UserListAPIView.as_view(), name="users"),
    path("items/", ItemListAPIView.as_view(), name="items"),
    path("users/register/", RegisterUserAPIView.as_view(), name="register"),
    path("users/login/", LoginUserAPIView.as_view(), name="login"),
    path("users/me/", CurrentUserAPIView.as_view(), name="current-user"),
    path("users/owned-items/", UserItemsAPIView.as_view(), name="owned-items"),
    path("users/logout/", LogoutUserAPIView.as_view(), name="logout"),
    path("items/create/", CreateItemAPIView.as_view(), name="create-item"),
    path("items/<int:pk>/update/", UpdateItemAPIView.as_view(), name="update-item"),
    path("items/<int:pk>/delete/", DeleteItemAPIView.as_view(), name="delete-item"),
    path("items/<int:pk>/", ItemDetailAPIView.as_view(), name="item-detail"),
    path("items/<int:pk>/borrow/", CreateBorrowFormAPIView.as_view(), name="borrow-item"),
    path("borrows/", BorrowListAPIView.as_view(), name="borrows"),
    path("users/owned-item-borrow-requests/", OwnedItemBorrowRequestsAPIView.as_view(), name="owned-item-borrow-requests"),
    path("borrow-requests/<int:pk>/accept/", AcceptBorrowRequestAPIView.as_view(), name="accept-borrow-request"),
    path("borrow-requests/<int:pk>/decline/", DeclineBorrowRequestAPIView.as_view(), name="decline-borrow-request"),
    path("users/my-borrow-requests/", MyBorrowRequestsAPIView.as_view(), name="my-borrow-requests"),
    path("users/my-borrowed-items/", MyBorrowedItemsAPIView.as_view(), name="my-borrowed-items"),
    path("items/<int:pk>/return/", CreateReturnFormAPIView.as_view(), name="create-return-form"),
    path("users/me/update/", UpdateCurrentUserAPIView.as_view(), name="update-current-user"),
]