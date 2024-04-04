from django.shortcuts import get_object_or_404, render

from cart.forms import CartAddProductForm

from .models import Category, Product
from .recommender import Recommender


def product_list(request, category_slug=None):
    """Товары все/в категории магазина"""
    category = None

    categories = Category.objects.all()
    products = Product.objects.filter(available=True)

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)

    context = {
        "products": products,
        "category": category,
        "categories": categories,
    }

    return render(request, "shop/product/list.html", context)


def product_detail(request, product_id, product_slug):
    """Подробности товара"""
    product = get_object_or_404(
        Product,
        id=product_id,
        slug=product_slug,
        available=True,
    )

    cart_product_add = CartAddProductForm()

    r = Recommender()
    recommendation = r.suggest_products_for([product])

    return render(
        request,
        "shop/product/detail.html",
        {
            "product": product,
            "cart_product_add": cart_product_add,
            "recommendation": recommendation,
        },
    )
