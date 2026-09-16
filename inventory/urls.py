from django.urls import path

from . import views

app_name = "inventory"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("api/products/", views.products_list, name="products_list"),
    path("api/products/<int:pk>/", views.product_detail, name="product_detail"),
]
