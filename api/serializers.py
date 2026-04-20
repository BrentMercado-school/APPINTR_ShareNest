from rest_framework import serializers, generics
from django.contrib.auth.hashers import make_password, check_password

from api.models import Category, User, Item, BorrowForm, ReturnForm, ItemImage

# JC was here.
# TODO: 3 for converting models to usable data on frontend
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "name",
            "email",
            "address",
            "contactNumber",
            "image",
            "createdAt",
        ]
class ItemImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemImage
        fields = ["image", "isPrimary"]

class ItemSerializer(serializers.ModelSerializer):
    owner_name = serializers.CharField(source="owner.name", read_only=True)
    category_name = serializers.CharField(source="category.name", read_only=True)
    expected_return_date = serializers.SerializerMethodField()
    images = ItemImageSerializer(many=True, read_only=True)

    class Meta:
        model = Item
        fields = [
            "id",
            "category",
            "category_name",
            "owner",
            "owner_name",
            "name",
            "description",
            "condition",
            "security_deposit",
            "note",
            "status",
            "borrowingFee",
            "createdAt",
            "updatedAt",
            "expected_return_date",
            "images",
        ]
        read_only_fields = ["owner", "createdAt", "updatedAt"]

    def get_expected_return_date(self, obj):
        if obj.status != "BORROWED":
            return None

        active_borrow = BorrowForm.objects.filter(
            item=obj,
            status="APPROVED",
            returnform__isnull=True
        ).order_by("-createdAt").first()

        return active_borrow.returnDate if active_borrow else None

class RegisterUserSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("id", "name", "email", "password", "createdAt", "updatedAt")
        read_only_fields = ('id', 'email', 'createdAt', 'updatedAt')

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])

        return User.objects.create(**validated_data)

class LoginUserSerializer(serializers.Serializer):
    name = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        name = attrs.get('name')
        password = attrs.get('password')

        try:
            existing_user = User.objects.get(name=name)
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found")

        if not check_password(password, existing_user.password):
            raise serializers.ValidationError("Incorrect password")

        attrs['user'] = existing_user
        return attrs

class BorrowFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = BorrowForm
        fields = [
            "id",
            "borrower",
            "item",
            "startDate",
            "returnDate",
            "status",
            "declineReason",
            "createdAt",
            "borrowingFeeSnapshot",
            "securityDepositSnapshot",
        ]
        read_only_fields = [
            "borrower",
            "item",
            "status",
            "declineReason",
            "createdAt",
            "borrowingFeeSnapshot",
            "securityDepositSnapshot",
        ]

class BorrowFormListSerializer(serializers.ModelSerializer):
    borrower_name = serializers.CharField(source="borrower.name", read_only=True)
    item_name = serializers.CharField(source="item.name", read_only=True)

    class Meta:
        model = BorrowForm
        fields = [
            "id",
            "borrower",
            "borrower_name",
            "item",
            "item_name",
            "startDate",
            "returnDate",
            "status",
            "declineReason",
            "createdAt",
            "borrowingFeeSnapshot",
            "securityDepositSnapshot",
        ]

class MyBorrowRequestSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source="item.name", read_only=True)
    owner_name = serializers.CharField(source="item.owner.name", read_only=True)

    class Meta:
        model = BorrowForm
        fields = [
            "id",
            "item",
            "item_name",
            "owner_name",
            "startDate",
            "returnDate",
            "status",
            "declineReason",
            "createdAt",
            "borrowingFeeSnapshot",
            "securityDepositSnapshot",
        ]

class MyBorrowedItemSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source="item.name", read_only=True)
    owner_name = serializers.CharField(source="item.owner.name", read_only=True)
    category_name = serializers.CharField(source="item.category.name", read_only=True)
    item_description = serializers.CharField(source="item.description", read_only=True)
    item_condition = serializers.CharField(source="item.condition", read_only=True)

    class Meta:
        model = BorrowForm
        fields = [
            "id",
            "item",
            "item_name",
            "owner_name",
            "category_name",
            "item_description",
            "item_condition",
            "startDate",
            "returnDate",
            "borrowingFeeSnapshot",
            "securityDepositSnapshot",
            "status",
        ]

class ReturnFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReturnForm
        fields = [
            "id",
            "borrowForm",
            "actualReturnDate",
            "damageFee",
            "latePenaltyFee",
            "refundAmount",
            "createdAt",
        ]
        read_only_fields = ["borrowForm", "latePenaltyFee", "refundAmount", "createdAt"]

class UpdateProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["name", "email", "address", "contactNumber", "image"]
