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
            Category.objects.get_or_create(name=c["name"])

        self.stdout.write(self.style.SUCCESS("Categories inserted"))

        users = [
            {
                "name": "Brent Mercado",
                "email": "name1@email.com",
                "address": "Dasmarinas, Cavite",
                "contactNumber": "09170000001",
                "password": make_password("password"),
            },
            {
                "name": "JC",
                "email": "name2@email.com",
                "address": "Imus, Cavite",
                "contactNumber": "09170000002",
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
                    "password": u["password"],
                },
            )

        self.stdout.write(self.style.SUCCESS("Users inserted"))