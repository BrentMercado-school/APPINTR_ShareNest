from django.db import models

# TODO: 1 for sql models
# python manage.py makemigrations
# python manage.py migrate
# python manage.py createsuperuser
# python manage.py runserver
# python manage.py flush --for resetting the database

class Category(models.Model):
    name = models.CharField(max_length=100)
    createdAt = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class User(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    contactNumber = models.CharField(max_length=20,  blank=True, null=True)
    imageUrl = models.URLField(blank=True, null=True)
    password = models.CharField(max_length=255)

    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)
    isActive = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Item(models.Model):
    STATUS_CHOICES = [
        ("AVAILABLE", "Available"),
        ("BORROWED", "Borrowed"),
        ("UNAVAILABLE", "Unavailable"),
    ]

    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    owner = models.ForeignKey(User, on_delete=models.PROTECT, related_name="items")

    name = models.CharField(max_length=100)
    description = models.TextField()
    condition = models.TextField()
    security_deposit = models.DecimalField(max_digits=10, decimal_places=2)
    note = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="AVAILABLE")
    borrowingFee = models.DecimalField(max_digits=10, decimal_places=2)

    isActive = models.BooleanField(default=True)

    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class ItemImage(models.Model):
    item = models.ForeignKey(Item, on_delete=models.PROTECT)
    imageUrl = models.URLField(blank=True, null=True)

    isPrimary = models.BooleanField(default=False)
    createdAt = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.item.name} image"


class BorrowForm(models.Model):
    STATUS_CHOICES = [
        ("APPROVED", "Approved"),
        ("DECLINED", "Declined"),
        ("PENDING", "Pending"),
    ]

    borrower = models.ForeignKey(User, on_delete=models.PROTECT)
    item = models.ForeignKey(Item, on_delete=models.PROTECT)

    startDate = models.DateField()
    returnDate = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    declineReason = models.TextField(blank=True, null=True)

    createdAt = models.DateTimeField(auto_now_add=True)
    borrowingFeeSnapshot = models.DecimalField(max_digits=10, decimal_places=2)
    securityDepositSnapshot = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.borrower.name} - {self.item.name}"


class ReturnForm(models.Model):
    borrowForm = models.OneToOneField(BorrowForm, on_delete=models.PROTECT)

    actualReturnDate = models.DateField()
    damageFee = models.DecimalField(max_digits=10, decimal_places=2)
    latePenaltyFee = models.DecimalField(max_digits=10, decimal_places=2)
    refundAmount = models.DecimalField(max_digits=10, decimal_places=2)

    createdAt = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Return - {self.borrowForm}"
