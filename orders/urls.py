from django.urls import path
from django.utils.translation import gettext_lazy as _

from . import views

app_name = "orders"
urlpatterns = [
    path(_("create"), views.create_order, name="create_order"),
    path(
        "admin/orders/<int:order_id>/pdf/",
        views.admin_order_pdf,
        name="admin_order_pdf",
    ),
    path(
        "admin/orders/<int:order_id>/",
        views.admin_order_detail,
        name="admin_order_detail",
    ),
]
