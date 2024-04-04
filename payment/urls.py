from django.urls import path
from django.utils.translation import gettext_lazy as _

from . import views

app_name = "payment"
urlpatterns = [
    path(_("process/"), views.payment_process, name="payment_process"),
    path(_("success/"), views.payment_success, name="payment_success"),
    path(_("canceled/"), views.payment_canceled, name="payment_canceled"),
]
