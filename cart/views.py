from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from coupons.forms import CouponForm
from shop.models import Product
from shop.recommender import Recommender

from .cart import Cart
from .forms import CartAddProductForm


@require_POST
def cart_add(request, product_id):
    """Добавление товара в корзину"""
    cart = Cart(request)
    product = get_object_or_404(Product, pk=product_id)
    form = CartAddProductForm(request.POST)

    if form.is_valid():
        cd = form.cleaned_data
        cart.add(product, quantity=cd["quantity"], override_quantity=cd["override"])

    return redirect("cart:cart_detail")


@require_POST
def cart_remove(request, product_id):
    """Удаление товара из корзины"""
    cart = Cart(request)
    product = get_object_or_404(Product, pk=product_id)
    cart.remove(product)

    return redirect("cart:cart_detail")


def cart_detail(request):
    """Корзина"""
    cart = Cart(request)
    coupon_form = CouponForm()
    r = Recommender()
    cart_products = [item["product"] for item in cart]
    if cart_products:
        recommendation = r.suggest_products_for(cart_products, max_products=4)
    else:
        recommended_products = []

    for item in cart:
        item["update_quantity_form"] = CartAddProductForm(
            initial={"quantity": item["quantity"], "override": True}
        )

    return render(
        request,
        "cart/detail.html",
        {"cart": cart, "coupon_form": coupon_form, "recommendation": recommendation},
    )
