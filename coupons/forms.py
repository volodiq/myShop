from django import forms
from django.utils.translation import gettext_lazy as _


class CouponForm(forms.Form):
    """Ввод купона пользователем"""

    code = forms.CharField(max_length=250, label=_("Код купона"))
