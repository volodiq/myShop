from io import BytesIO

import weasyprint
from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

from orders.models import Order


@shared_task
def post_payment_mail(order_id):
    """Отправляет e-mail письмо после успешной оплаты заказа"""
    order = Order.objects.get(pk=order_id)

    subject = "Myshop Order"
    message = f"Заказ номер {order.id} успешно оплачен"

    email = EmailMessage(
        subject=subject, body=message, from_email="admin@shop.com", to=[order.email]
    )

    # PDF
    html = render_to_string("orders/order/pdf.html", {"order": order})
    out = BytesIO()
    style = weasyprint.CSS(settings.BASE_DIR / "static/css/pdf.css")
    weasyprint.HTML(string=html).write_pdf(out, style=style)

    email.attach(f"order_{order_id}.pdf", out.getvalue(), "application/pdf")
    email.send()
