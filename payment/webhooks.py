import stripe
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from orders.models import Order
from payment.tasks import post_payment_mail


@csrf_exempt
def stripe_webhook(request):
    """Получение уведомлений от Stripe, для отметки оплаченных заказов"""
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        # Недопустимая полезная нагрузка
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Недопустимая подпись
        return HttpResponse(status=400)

    if event.type == "checkout.session.completed":
        session = event.data.object
        if session.mode == "payment" and session.payment_status == "paid":
            try:
                order = Order.objects.get(pk=session.client_reference_id)
            except Order.DoesNotExist:
                return HttpResponse(status=404)
            # Помечаем заказ как оплаченный
            order.paid = True
            order.stripe_id = session.payment_intent
            order.save()
            # Отправка письма клиенту
            post_payment_mail(order.id)

    return HttpResponse(status=200)
