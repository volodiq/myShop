from decimal import Decimal

from django.conf import settings
from django.http import HttpRequest

from coupons.models import Coupon
from shop.models import Product


class Cart:
    """Корзина пользователя"""

    def __init__(self, request: HttpRequest):
        """
        Инициализация корзины
        """
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)

        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}

        # Id купона
        self.coupon_id = self.session.get("coupon_id")

        self.cart = cart

    def add(
        self, product: Product, quantity: int = 1, override_quantity: bool = False
    ) -> None:
        """Добавление товара в корзину или обновление его количества"""
        product_id = str(product.id)

        if product_id not in self.cart:
            self.cart[product_id] = {"quantity": 0, "price": float(product.price)}

        if override_quantity:
            self.cart[product_id]["quantity"] = quantity
        else:
            self.cart[product_id]["quantity"] += quantity

        self.save()

    def save(self) -> None:
        """Сохранение"""
        self.session.modified = True

    def remove(self, product: Product) -> None:
        """Удаление товара из корзины"""
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def get_total_price(self):
        """Цена всех товаров в корзине"""
        return sum(
            Decimal(item["price"]) * item["quantity"] for item in self.cart.values()
        )

    def clear(self):
        """Удалить корзину из сеанса"""
        del self.session[settings.CART_SESSION_ID]
        self.save()

    def __iter__(self):
        """Получение товаров корзины из БД"""

        product_ids = self.cart.keys()

        # получить объекты product и добавить их в корзину
        products = Product.objects.filter(id__in=product_ids)
        cart = self.cart.copy()

        for product in products:
            cart[str(product.id)]["product"] = product

        for item in cart.values():
            item["price"] = Decimal(item["price"])
            item["total_price"] = item["price"] * item["quantity"]
            yield item

    def __len__(self):
        """Количество товаров в корзине"""
        return sum(item["quantity"] for item in self.cart.values())

    @property
    def coupon(self):
        if self.coupon_id:
            try:
                return Coupon.objects.get(id=self.coupon_id)
            except Coupon.DoesNotExist:
                pass
        return None

    def get_discount(self):
        if self.coupon:
            return (self.coupon.discount / Decimal(100)) * self.get_total_price()
        return Decimal(0)

    def get_total_price_after_discount(self):
        return self.get_total_price() - self.get_discount()
