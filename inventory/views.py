import json

from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods

from .models import Product


@ensure_csrf_cookie
def dashboard(request):
    """Serves the SPA shell. The CSRF cookie is set here so the frontend
    JS can read it and attach it to POST/PUT/DELETE requests."""
    return render(request, "inventory/dashboard.html")


def _dashboard_summary():
    products = Product.objects.all()
    total_products = products.count()
    current_stock = sum(p.quantity for p in products)
    low_stock_count = sum(1 for p in products if p.is_low_stock)
    total_value = sum(p.stock_value for p in products)
    return {
        "total_products": total_products,
        "current_stock": current_stock,
        "low_stock_count": low_stock_count,
        "total_value": float(total_value),
    }


@require_http_methods(["GET", "POST"])
def products_list(request):
    if request.method == "GET":
        products = Product.objects.all()
        return JsonResponse(
            {
                "products": [p.to_dict() for p in products],
                "summary": _dashboard_summary(),
            }
        )

    # POST - create a new product
    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON body."}, status=400)

    name = (payload.get("name") or "").strip()
    category = (payload.get("category") or "").strip()
    quantity = payload.get("quantity")
    price = payload.get("price")
    threshold = payload.get("threshold", 5)

    errors = {}
    if not name:
        errors["name"] = "Product name is required."
    if not category:
        errors["category"] = "Category is required."
    try:
        quantity = int(quantity)
        if quantity < 0:
            raise ValueError
    except (TypeError, ValueError):
        errors["quantity"] = "Quantity must be a non-negative whole number."
    try:
        price = float(price)
        if price < 0:
            raise ValueError
    except (TypeError, ValueError):
        errors["price"] = "Price must be a non-negative number."
    try:
        threshold = int(threshold)
        if threshold < 0:
            raise ValueError
    except (TypeError, ValueError):
        errors["threshold"] = "Threshold must be a non-negative whole number."

    if errors:
        return JsonResponse({"errors": errors}, status=400)

    product = Product.objects.create(
        name=name,
        category=category,
        quantity=quantity,
        price=price,
        low_stock_threshold=threshold,
    )
    return JsonResponse(
        {"product": product.to_dict(), "summary": _dashboard_summary()},
        status=201,
    )


@require_http_methods(["GET", "PUT", "PATCH", "DELETE"])
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == "GET":
        return JsonResponse({"product": product.to_dict()})

    if request.method == "DELETE":
        product.delete()
        return JsonResponse({"deleted": True, "summary": _dashboard_summary()})

    # PUT / PATCH - update fields
    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON body."}, status=400)

    for field, attr in (
        ("name", "name"),
        ("category", "category"),
        ("quantity", "quantity"),
        ("price", "price"),
        ("threshold", "low_stock_threshold"),
    ):
        if field in payload:
            setattr(product, attr, payload[field])
    product.save()

    return JsonResponse(
        {"product": product.to_dict(), "summary": _dashboard_summary()}
    )
