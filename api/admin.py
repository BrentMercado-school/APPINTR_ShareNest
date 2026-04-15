from django.contrib import admin
from .models import Category, User, Item

# TODO: 2 for admin testing
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'createdAt')
    search_fields = ('name',)

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "email",
        "address",
        "contactNumber",
        "imageUrl",
        "password",
        "createdAt",
        "updatedAt",
        "isActive",
    )
    search_fields = ("name",)

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "description",
        "condition",
        "security_deposit",
        "note",
        "status",
        "borrowingFee",
        "createdAt",
        "updatedAt",
    )
    search_fields = ("name",)



