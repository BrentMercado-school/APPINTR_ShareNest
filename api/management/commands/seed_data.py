from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from api.models import Category, User, Item


class Command(BaseCommand):
    help = "Insert dummy data"

    def handle(self, *args, **kwargs):
        categories = [
            {"name": "Sports"},
            {"name": "Electronics"},
            {"name": "Books"},
            {"name": "Music"},
            {"name": "Outdoor"},
            {"name": "Appliance"},
        ]

        for c in categories:
            Category.objects.get_or_create(
                name=c["name"],
            )

        self.stdout.write(self.style.SUCCESS("Categories inserted"))

        users = [
            {
                "name": "Name1",
                "email": "name1@email.com",
                "address": "Dasmarinas, Cavite",
                "contactNumber": "09170000001",
                "imageUrl": "https://example.com/juan.jpg",
                "password": make_password("password"),
            },
            {
                "name": "Name2",
                "email": "name2@email.com",
                "address": "Imus, Cavite",
                "contactNumber": "09170000002",
                "imageUrl": "https://example.com/maria.jpg",
                "password": make_password("password"),
            },
        ]

        for u in users:
            User.objects.get_or_create(
                email=u["email"],
                defaults={
                    "name": u["name"],
                    "address": u["address"],
                    "contactNumber": u["contactNumber"],
                    "imageUrl": u["imageUrl"],
                    "password": u["password"],
                },
            )

        self.stdout.write(self.style.SUCCESS("Users inserted"))

        items = [
            {
                "category": "Sports",
                "owner_name": "Name1",
                "name": "Basketball",
                "description": "Official size basketball for indoor and outdoor use",
                "condition": "Good",
                "security_deposit": 500.00,
                "note": "Return properly inflated",
                "status": "AVAILABLE",
                "borrowingFee": 50.00,
            },
            {
                "category": "Electronics",
                "owner_name": "Name2",
                "name": "Bluetooth Speaker",
                "description": "Portable speaker with strong bass",
                "condition": "Very Good",
                "security_deposit": 1000.00,
                "note": "Handle with care",
                "status": "AVAILABLE",
                "borrowingFee": 50.00,
            },
        ]

        for i in items:
            category = Category.objects.get(name=i["category"])
            owner = User.objects.get(name=i["owner_name"])

            Item.objects.get_or_create(
                name=i["name"],
                owner=owner,
                defaults={
                    "category": category,
                    "description": i["description"],
                    "condition": i["condition"],
                    "security_deposit": i["security_deposit"],
                    "note": i["note"],
                    "status": i["status"],
                    "borrowingFee": i["borrowingFee"],
                },
            )

        self.stdout.write(self.style.SUCCESS("Items inserted"))