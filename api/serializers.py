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
        fields = ["id", "image", "isPrimary"]

class ItemSerializer(serializers.ModelSerializer):
    owner_name = serializers.CharField(source="owner.name", read_only=True)
    owner_image = serializers.ImageField(source="owner.image", read_only=True)
    category_name = serializers.CharField(source="category.name", read_only=True)
    expected_return_date = serializers.SerializerMethodField()
    images = ItemImageSerializer(many=True, read_only=True)

    borrower_name = serializers.SerializerMethodField()
    borrower_email = serializers.SerializerMethodField()
    borrower_address = serializers.SerializerMethodField()
    borrower_image = serializers.SerializerMethodField()
    borrow_form_id = serializers.SerializerMethodField()
    startDate = serializers.SerializerMethodField()
    borrowingFeeSnapshot = serializers.SerializerMethodField()
    securityDepositSnapshot = serializers.SerializerMethodField()

    class Meta:
        model = Item
        fields = [
            "id",
            "category",
            "category_name",
            "owner",
            "owner_name",
            "owner_image",
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

            "borrower_name",
            "borrower_email",
            "borrower_address",
            "borrower_image",
            "borrow_form_id",
            "startDate",
            "borrowingFeeSnapshot",
            "securityDepositSnapshot",
        ]
        read_only_fields = ["owner", "createdAt", "updatedAt"]

    def get_active_borrow(self, obj):
        if obj.status != "BORROWED":
            return None

        return BorrowForm.objects.select_related("borrower").filter(
            item=obj,
            status="APPROVED",
            returnform__isnull=True
        ).order_by("-createdAt").first()

    def get_expected_return_date(self, obj):
        active_borrow = self.get_active_borrow(obj)
        return active_borrow.returnDate if active_borrow else None

    def get_borrower_name(self, obj):
        active_borrow = self.get_active_borrow(obj)
        return active_borrow.borrower.name if active_borrow and active_borrow.borrower else None

    def get_borrower_email(self, obj):
        active_borrow = self.get_active_borrow(obj)
        return active_borrow.borrower.email if active_borrow and active_borrow.borrower else None

    def get_borrower_address(self, obj):
        active_borrow = self.get_active_borrow(obj)
        return active_borrow.borrower.address if active_borrow and active_borrow.borrower else None

    def get_borrower_image(self, obj):
        active_borrow = self.get_active_borrow(obj)
        if active_borrow and active_borrow.borrower and active_borrow.borrower.image:
            request = self.context.get("request")
            image_url = active_borrow.borrower.image.url
            return request.build_absolute_uri(image_url) if request else image_url
        return None

    def get_borrow_form_id(self, obj):
        active_borrow = self.get_active_borrow(obj)
        return active_borrow.id if active_borrow else None

    def get_startDate(self, obj):
        active_borrow = self.get_active_borrow(obj)
        return active_borrow.startDate if active_borrow else None

    def get_borrowingFeeSnapshot(self, obj):
        active_borrow = self.get_active_borrow(obj)
        return active_borrow.borrowingFeeSnapshot if active_borrow else None

    def get_securityDepositSnapshot(self, obj):
        active_borrow = self.get_active_borrow(obj)
        return active_borrow.securityDepositSnapshot if active_borrow else None

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
    item_category_name = serializers.CharField(source="item.category.name", read_only=True)
    condition = serializers.CharField(source="item.condition", read_only=True)
    item_images = ItemImageSerializer(source="item.images", many=True, read_only=True)

    class Meta:
        model = BorrowForm
        fields = [
            "id",
            "borrower",
            "borrower_name",
            "item",
            "item_name",
            "item_category_name",
            "condition",
            "item_images",
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
    item_category_name = serializers.CharField(source="item.category.name", read_only=True)
    condition = serializers.CharField(source="item.condition", read_only=True)
    item_images = ItemImageSerializer(source="item.images", many=True, read_only=True)

    class Meta:
        model = BorrowForm
        fields = [
            "id",
            "item",
            "item_name",
            "owner_name",
            "item_category_name",
            "condition",
            "item_images",
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
