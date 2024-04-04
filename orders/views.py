import weasyprint
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse

from cart.cart import Cart
from shop.recommender import Recommender

from .forms import OrderCreateForm
from .models import Order, OrderItem
from .tasks import order_created


def create_order(request):
    """Создание заказа"""
    cart = Cart(request)

    # Обновление рекомендаций
    products = [item["product"] for item in cart]
    r = Recommender()
    r.product_bought(products)

    if request.method == "POST":
        form = OrderCreateForm(request.POST)

        if form.is_valid():
            order = form.save()

            # Применение скидочного купона
            if cart.coupon:
                order.coupon = cart.coupon
                order.discount = cart.coupon.discount
            order.save()

            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product=item["product"],
                    quantity=item["quantity"],
                    price=item["price"],
                )
            cart.clear()

            # Отправка письма
            order_created.delay(order.id)

            request.session["order_id"] = order.id

            return redirect(reverse("payment:payment_process"))
    else:
        form = OrderCreateForm()

    return render(request, "orders/order/create.html", {"cart": cart, "form": form})


@staff_member_required
def admin_order_detail(request, order_id):
    """Детали заказа доступные для просмотра администраторам сайта"""
    order = get_object_or_404(Order, pk=order_id)
    return render(request, "admin/orders/order/detail.html", {"order": order})


@staff_member_required
def admin_order_pdf(request, order_id):
    """Генерация PDF с информацией о заказе"""
    order = get_object_or_404(Order, pk=order_id)
    html = render_to_string("orders/order/pdf.html", {"order": order})

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f"filename={order_id}.pdf"

    weasyprint.HTML(string=html).write_pdf(
        response, stylesheets=[weasyprint.CSS(settings.BASE_DIR / "static/css/pdf.css")]
    )

    return response
