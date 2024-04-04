from .cart import Cart


def cart(request):
    """Отображает количество товаров в корзине"""
    return {
        "cart": Cart(request),
    }
