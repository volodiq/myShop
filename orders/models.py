from decimal import Decimal

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from coupons.models import Coupon
from shop.models import Product


class Order(models.Model):
    """Заказы пользователей"""

    first_name = models.CharField(verbose_name=_("Имя"), max_length=50)
    last_name = models.CharField(verbose_name=_("Фамилия"), max_length=50)
    email = models.EmailField(verbose_name=_("e-mail"))
    address = models.CharField(verbose_name=_("Адрес"), max_length=250)
    postal_code = models.CharField(verbose_name=_("Почтовый индекс"), max_length=20)
    city = models.CharField(verbose_name=_("Город"), max_length=100)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    paid = models.BooleanField(default=False)
    stripe_id = models.CharField("Id платежа stripe", blank=True, max_length=250)

    coupon = models.ForeignKey(
        verbose_name="Купон примененный к заказу",
        related_name="orders",
        to=Coupon,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    discount = models.IntegerField(
        verbose_name="Скидка в процентах",
        default=0,
        validators=[MaxValueValidator(100), MinValueValidator(0)],
    )

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ["-created"]
        indexes = (models.Index(fields=["-created"]),)

    def __str__(self):
        return f"Заказ {self.id}"

    def get_total_cost_before_discount(self) -> int:
        return sum(item.get_cost() for item in self.items.all())

    def get_stripe_url(self):
        if not self.stripe_id:
            return ""
        # Тестовые платежи
        if "_test_" in settings.STRIPE_SECRET_KEY:
            path = "/test/"
        # Настоящие платежи
        else:
            path = "/"

        return f"https://dashboard.stripe.com{path}payments/{self.stripe_id}"

    def get_discount(self):
        """Получение скидки на товар"""
        total_cost = self.get_total_cost_before_discount()
        if self.discount:
            return total_cost * self.discount / Decimal(100)
        return Decimal(0)

    def get_total_cost(self):
        """Итоговая стоимость"""
        total_cost = self.get_total_cost_before_discount()
        return total_cost - self.get_discount()


class OrderItem(models.Model):
    """Товары заказа"""

    order = models.ForeignKey(
        verbose_name="Заказ",
        related_name="items",
        to=Order,
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        verbose_name="Товар",
        related_name="order_items",
        to=Product,
        on_delete=models.CASCADE,
    )
    price = models.DecimalField(
        verbose_name="Цена товара", max_digits=10, decimal_places=2
    )
    quantity = models.PositiveIntegerField(verbose_name="Количество товара", default=1)

    def __str__(self):
        return str(self.id)

    def get_cost(self):
        return self.price * self.quantity
