import redis
from django.conf import settings

from shop.models import Product

r = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
)


class Recommender:
    def get_product_key(self, product_id):
        return f"product:{product_id}:purchased_with"

    def product_bought(self, products):
        products_ids = [product.id for product in products]
        for product_id in products_ids:
            for with_id in products_ids:
                if product_id != with_id:
                    r.zincrby(self.get_product_key(product_id), 1, with_id)

    def suggest_products_for(self, products, max_products=6):
        """Возвращает продукты покупаемые вместе"""
        product_ids = [product.id for product in products]

        # Для подробностей товара или если в корзине один товар
        if len(product_ids) == 1:
            suggestions = r.zrange(
                self.get_product_key(product_ids[0]),
                0,
                -1,
                desc=True,
            )[:max_products]

        # Для корзины, в которой много товаров
        else:
            flat_ids = "".join([str(product_id) for product_id in product_ids])
            tmp_key = f"temp_{flat_ids}"

            # Добавляем все подсказки каждого товара
            keys = [self.get_product_key(product_id) for product_id in product_ids]
            r.zunionstore(tmp_key, keys)

            # Удаляем товары для которых дается рекомендации
            r.zrem(tmp_key, *product_ids)

            suggestions = r.zrange(tmp_key, 0, -1, desc=True)[:max_products]

            r.delete(tmp_key)

        suggestion_ids = [int(suggestion) for suggestion in suggestions]
        suggestion_products = list(Product.objects.filter(id__in=suggestion_ids))

        suggestion_products.sort(key=lambda x: suggestion_ids.index(x.id))

        return suggestion_products

    def clear_recommendations(self):
        for product_id in Product.objects.values_list("id", flat=True):
            r.delete(self.get_product_key(product_id))
