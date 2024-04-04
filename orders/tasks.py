from celery import shared_task
from django.core.mail import send_mail

from orders.models import Order


@shared_task
def order_created(order_id):
    """Отправляет e-mail письмо при создании заказа"""

    order = Order.objects.get(pk=order_id)

    subject = f"Myshop {order.id}"
    message = (
        f"{order.first_name}, ваш заказ успешно передан в обработку"
        f"Номер заказа {order_id}."
    )

    mail_sent = send_mail(
        subject,
        message,
        "admin@shop.com",
        [order.email],
    )

    return mail_sent
