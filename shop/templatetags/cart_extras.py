from django import template

register = template.Library()


@register.filter
def cart_plural(count):
    """Склоняет в нужном падеже русские слова (аналог pluralize)"""
    variants = ("товар", "товара", "товаров")

    if count % 10 == 1 and count % 100 != 11:
        return variants[0]
    elif 2 <= count % 10 <= 4 and (count % 100 < 10 or count % 100 >= 20):
        return variants[1]
    else:
        return variants[2]
