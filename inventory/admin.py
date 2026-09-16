from django.contrib import admin

from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "quantity", "price", "low_stock_threshold", "is_low_stock")
    list_filter = ("category",)
    search_fields = ("name", "category")
