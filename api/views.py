from decimal import Decimal

from django.db.models import ProtectedError
from rest_framework import generics, status, request
from django.http import JsonResponse
from rest_framework.generics import ListAPIView
from rest_framework.parsers import MultiPartParser, JSONParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.models import Category, User, Item, BorrowForm, ReturnForm
from api.serializers import CategorySerializer, UserSerializer, ItemSerializer, RegisterUserSerializer, \
    LoginUserSerializer, BorrowFormSerializer, BorrowFormListSerializer, MyBorrowRequestSerializer, \
    MyBorrowedItemSerializer, ReturnFormSerializer, UpdateProfileSerializer


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
    queryset = Item.objects.filter(isActive=True)
    serializer_class = ItemSerializer

class RegisterUserAPIView(generics.CreateAPIView):
    serializer_class = RegisterUserSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]

class LoginUserAPIView(generics.GenericAPIView):
    serializer_class = LoginUserSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = UserSerializer(serializer.validated_data['user']).data

        request.session["user_id"] = user.get("id")

        return Response({
            "user": {
                "id": user.get('id'),
                "name": user.get('name'),
                "email": user.get('email'),
            },
            "message": "Login Successful",
        })

class CurrentUserAPIView(generics.GenericAPIView):
    def get(self, request, *args, **kwargs):

        userId = request.session.get("user_id")

        if not userId:
            return Response(
                {"detail": "Not authenticated."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            currentUser = User.objects.get(id=userId)
        except User.DoesNotExist:
            return Response(
                {"detail": "User not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(UserSerializer(currentUser).data)

class UserItemsAPIView(generics.ListAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer

    def get_queryset(self):
        user_id = self.request.session.get("user_id")
        return Item.objects.filter(owner_id=user_id, isActive=True)

class LogoutUserAPIView(generics.GenericAPIView):
    def post(self, request, *args, **kwargs):
        request.session.flush()

        return Response(
            {"message": "Logout successful."},
            status=status.HTTP_200_OK
        )

class CreateItemAPIView(generics.CreateAPIView):
    serializer_class = ItemSerializer

    def perform_create(self, serializer):
        user_id = self.request.session.get("user_id")
        serializer.save(owner_id=user_id)

class UpdateItemAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = ItemSerializer

    def get_queryset(self):
        user_id = self.request.session.get("user_id")
        return Item.objects.filter(owner_id=user_id, isActive=True)

    def update(self, request, *args, **kwargs):
        item = self.get_object()

        if item.status == "BORROWED":
            return Response(
                {"detail": "Borrowed items cannot be edited."},
                status=status.HTTP_400_BAD_REQUEST
            )

        return super().update(request, *args, **kwargs)

class DeleteItemAPIView(generics.GenericAPIView):
    def delete(self, request, *args, **kwargs):
        user_id = request.session.get("user_id")

        if not user_id:
            return Response(
                {"detail": "Not authenticated."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        item_id = kwargs.get("pk")

        try:
            item = Item.objects.get(pk=item_id, owner_id=user_id, isActive=True)
        except Item.DoesNotExist:
            return Response(
                {"detail": "Item not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        if item.status == "BORROWED":
            return Response(
                {"detail": "Borrowed items cannot be deleted."},
                status=status.HTTP_400_BAD_REQUEST
            )

        item.isActive = False
        item.save()

        return Response(
            {"message": "Item deleted successfully."},
            status=status.HTTP_200_OK
        )

class ItemDetailAPIView(generics.RetrieveAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer

class CreateBorrowFormAPIView(generics.CreateAPIView):
    serializer_class = BorrowFormSerializer

    def create(self, request, *args, **kwargs):
        user_id = request.session.get("user_id")

        if not user_id:
            return Response(
                {"detail": "Not authenticated."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        item_id = self.kwargs.get("pk")

        try:
            item = Item.objects.get(pk=item_id)
        except Item.DoesNotExist:
            return Response(
                {"detail": "Item not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        if item.owner_id == user_id:
            return Response(
                {"detail": "You cannot borrow your own item."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if item.status != "AVAILABLE":
            return Response(
                {"detail": "This item is not available for borrowing."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        start_date = serializer.validated_data["startDate"]
        return_date = serializer.validated_data["returnDate"]

        if return_date < start_date:
            return Response(
                {"detail": "Return date must be after or equal to start date."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer.save(
            borrower_id=user_id,
            item=item,
            borrowingFeeSnapshot=item.borrowingFee,
            securityDepositSnapshot=item.security_deposit,
        )

        return Response(
            {
                "message": "Borrow request submitted successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_201_CREATED
        )

class BorrowListAPIView(generics.ListAPIView):
    queryset = BorrowForm.objects.all()
    serializer_class = BorrowFormSerializer

class OwnedItemBorrowRequestsAPIView(generics.ListAPIView):
    serializer_class = BorrowFormListSerializer

    def get_queryset(self):
        user_id = self.request.session.get("user_id")

        if not user_id:
            return BorrowForm.objects.none()

        return BorrowForm.objects.filter(item__owner_id=user_id).order_by("-createdAt")

class AcceptBorrowRequestAPIView(generics.GenericAPIView):
    def post(self, request, pk):
        user_id = request.session.get("user_id")

        if not user_id:
            return Response(
                {"detail": "Authentication credentials were not provided."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        try:
            owner = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response(
                {"detail": "User not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            borrow_form = BorrowForm.objects.select_related("item").get(pk=pk)
        except BorrowForm.DoesNotExist:
            return Response(
                {"detail": "Borrow request not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        if borrow_form.item.owner != owner:
            return Response(
                {"detail": "You are not allowed to accept this request."},
                status=status.HTTP_403_FORBIDDEN
            )

        if borrow_form.status != "PENDING":
            return Response(
                {"detail": "Only pending requests can be accepted."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # very important check
        if borrow_form.item.status == "BORROWED":
            return Response(
                {"detail": "Item is already borrowed."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # optional stronger check in case status gets out of sync
        existing_approved = BorrowForm.objects.filter(
            item=borrow_form.item,
            status="APPROVED",
            returnform__isnull=True
        ).exclude(pk=borrow_form.pk).exists()

        if existing_approved:
            return Response(
                {"detail": "Item is already borrowed."},
                status=status.HTTP_400_BAD_REQUEST
            )

        borrow_form.status = "APPROVED"
        borrow_form.save()

        item = borrow_form.item
        item.status = "BORROWED"
        item.save()

        return Response(
            {"message": "Borrow request approved successfully."},
            status=status.HTTP_200_OK
        )

class DeclineBorrowRequestAPIView(generics.GenericAPIView):
    def post(self, request, *args, **kwargs):
        user_id = request.session.get("user_id")

        if not user_id:
            return Response(
                {"detail": "Not authenticated."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        borrow_request_id = kwargs.get("pk")

        try:
            borrow_request = BorrowForm.objects.get(
                pk=borrow_request_id,
                item__owner_id=user_id
            )
        except BorrowForm.DoesNotExist:
            return Response(
                {"detail": "Borrow request not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        if borrow_request.status != "PENDING":
            return Response(
                {"detail": "Only pending requests can be declined."},
                status=status.HTTP_400_BAD_REQUEST
            )

        decline_reason = request.data.get("declineReason", "")

        borrow_request.status = "DECLINED"
        borrow_request.declineReason = decline_reason
        borrow_request.save()

        return Response(
            {"message": "Borrow request declined successfully."},
            status=status.HTTP_200_OK
        )

class MyBorrowRequestsAPIView(generics.ListAPIView):
    serializer_class = MyBorrowRequestSerializer

    def get_queryset(self):
        user_id = self.request.session.get("user_id")

        if not user_id:
            return BorrowForm.objects.none()

        return BorrowForm.objects.filter(borrower_id=user_id).order_by("-createdAt")

class MyBorrowedItemsAPIView(generics.ListAPIView):
    serializer_class = MyBorrowedItemSerializer

    def get_queryset(self):
        user_id = self.request.session.get("user_id")

        if not user_id:
            return BorrowForm.objects.none()

        return BorrowForm.objects.filter(
            borrower_id=user_id,
            status="APPROVED"
        ).order_by("-createdAt")

class CreateReturnFormAPIView(generics.CreateAPIView):
    serializer_class = ReturnFormSerializer

    def create(self, request, *args, **kwargs):
        user_id = request.session.get("user_id")

        if not user_id:
            return Response(
                {"detail": "Not authenticated."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        item_id = self.kwargs.get("pk")

        try:
            item = Item.objects.get(pk=item_id, owner_id=user_id)
        except Item.DoesNotExist:
            return Response(
                {"detail": "Item not found or not owned by you."},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            borrow_form = BorrowForm.objects.get(
                item_id=item_id,
                status="APPROVED",
                returnform__isnull=True
            )
        except BorrowForm.DoesNotExist:
            return Response(
                {"detail": "No active approved borrow form found for this item."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        actual_return_date = serializer.validated_data["actualReturnDate"]
        damage_fee = serializer.validated_data["damageFee"]

        expected_return_date = borrow_form.returnDate
        late_days = max(0, (actual_return_date - expected_return_date).days)
        late_penalty_fee = Decimal(late_days) * Decimal("50.00")

        refund_amount = (
            borrow_form.securityDepositSnapshot
            - late_penalty_fee
            - damage_fee
        )

        serializer.save(
            borrowForm=borrow_form,
            latePenaltyFee=late_penalty_fee,
            refundAmount=refund_amount
        )

        item.status = "AVAILABLE"
        item.save()

        return Response(
            {
                "message": "Return form created successfully.",
                "latePenaltyFee": str(late_penalty_fee),
                "refundAmount": str(refund_amount),
            },
            status=status.HTTP_201_CREATED
        )

class UpdateCurrentUserAPIView(generics.GenericAPIView):
    serializer_class = UpdateProfileSerializer

    def put(self, request, *args, **kwargs):
        user_id = request.session.get("user_id")

        if not user_id:
            return Response(
                {"detail": "Not authenticated."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {"detail": "User not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {
                "message": "Profile updated successfully.",
                "user": UserSerializer(user).data
            },
            status=status.HTTP_200_OK
        )

class LatestItemsAPIView(generics.ListAPIView):
    serializer_class = ItemSerializer

    def get_queryset(self):
        user_id = self.request.session.get("user_id")

        queryset = Item.objects.all()

        if user_id:
            queryset = queryset.exclude(owner_id=user_id)

        return queryset.order_by("-createdAt")[:5]

class AllItemsDashboardAPIView(generics.ListAPIView):
    serializer_class = ItemSerializer

    def get_queryset(self):
        user_id = self.request.session.get("user_id")

        queryset = Item.objects.all()

        if user_id:
            queryset = queryset.exclude(owner_id=user_id)

        return queryset

class SportsCategoryAPIView(generics.ListAPIView):
    serializer_class = ItemSerializer

    def get_queryset(self):
        user_id = self.request.session.get("user_id")

        queryset = Item.objects.all()

        if user_id:
            queryset = queryset.exclude(owner_id=user_id)

        return queryset.filter(category__name__iexact="Sports")

class ElectronicsCategoryAPIView(generics.ListAPIView):
    serializer_class = ItemSerializer

    def get_queryset(self):
        user_id = self.request.session.get("user_id")

        queryset = Item.objects.all()

        if user_id:
            queryset = queryset.exclude(owner_id=user_id)

        return queryset.filter(category__name__iexact="Electronics")

class BooksCategoryAPIView(generics.ListAPIView):
    serializer_class = ItemSerializer

    def get_queryset(self):
        user_id = self.request.session.get("user_id")

        queryset = Item.objects.all()

        if user_id:
            queryset = queryset.exclude(owner_id=user_id)

        return queryset.filter(category__name__iexact="Books")

class MusicCategoryAPIView(generics.ListAPIView):
    serializer_class = ItemSerializer

    def get_queryset(self):
        user_id = self.request.session.get("user_id")

        queryset = Item.objects.all()

        if user_id:
            queryset = queryset.exclude(owner_id=user_id)

        return queryset.filter(category__name__iexact="Music")

class OutdoorCategoryAPIView(generics.ListAPIView):
    serializer_class = ItemSerializer

    def get_queryset(self):
        user_id = self.request.session.get("user_id")

        queryset = Item.objects.all()

        if user_id:
            queryset = queryset.exclude(owner_id=user_id)

        return queryset.filter(category__name__iexact="Outdoor")

class ApplianceCategoryAPIView(generics.ListAPIView):
    serializer_class = ItemSerializer

    def get_queryset(self):
        user_id = self.request.session.get("user_id")

        queryset = Item.objects.all()

        if user_id:
            queryset = queryset.exclude(owner_id=user_id)

        return queryset.filter(category__name__iexact="Appliance")

class CancelBorrowRequestAPIView(generics.GenericAPIView):
    def patch(self, request, pk):
        user_id = request.session.get("user_id")

        if not user_id:
            return Response(
                {"detail": "Authentication credentials were not provided."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response(
                {"detail": "User not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            borrow_form = BorrowForm.objects.get(pk=pk, borrower=user)
        except BorrowForm.DoesNotExist:
            return Response(
                {"detail": "Borrow request not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        if borrow_form.status != "PENDING":
            return Response(
                {"detail": "Only pending requests can be cancelled."},
                status=status.HTTP_400_BAD_REQUEST
            )

        borrow_form.status = "CANCELLED"
        borrow_form.save()

        return Response(
            {"message": "Borrow request cancelled successfully."},
            status=status.HTTP_200_OK
        )