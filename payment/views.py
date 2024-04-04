from decimal import Decimal

import stripe
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect, render, reverse

from orders.models import Order

# Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY
stripe.api_version = settings.STRIPE_API_VERSION


def payment_process(request):
    """Процесс оплаты пользователем заказа"""
    order_id = request.session.get("order_id", None)
    order = get_object_or_404(Order, pk=order_id)

    if request.method == "POST":
        success_url = request.build_absolute_uri(reverse("payment:payment_success"))
        cancel_url = request.build_absolute_uri(reverse("payment:payment_canceled"))

        # Данные платежа дял stripe
        session_data = {
            "mode": "payment",
            "client_reference_id": order_id,
            "success_url": success_url,
            "cancel_url": cancel_url,
            "line_items": [],
        }

        # Заполнение позиций
        for item in order.items.all():
            session_data["line_items"].append(
                {
                    "price_data": {
                        "unit_amount": int(item.price * Decimal("100")),
                        "currency": "rub",
                        "product_data": {"name": item.product.name},
                    },
                    "quantity": item.quantity,
                }
            )

        # Создание сеанса оформления платежа stripe
        session = stripe.checkout.Session.create(**session_data)

        # купон Stripe
        if order.coupon:
            stripe_coupon = stripe.Coupon.create(
                name=order.coupon.code, percent_off=order.discount, duration="once"
            )
            session_data["discounts"] = [
                {"coupon": stripe_coupon.id}
            ]  # создать сеанс оформления платежа Stripe
            session = stripe.checkout.Session.create(**session_data)
            # перенаправить к форме для платежа Stripe
            return redirect(session.url, code=303)
        else:
            return render(request, "payment/process.html", locals())


def payment_success(request):
    """Успешная оплата"""
    return render(request, "payment/completed.html")


def payment_canceled(request):
    """Отмена оплаты"""
    return render(request, "payment/canceled.html")
