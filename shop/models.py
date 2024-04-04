from django.db import models
from django.urls import reverse


class Category(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("shop:product_list_by_category", args=[self.slug])


class Product(models.Model):
    """Товары"""

    name = models.CharField(verbose_name="Имя товара", max_length=50)
    slug = models.SlugField(verbose_name="Slug товара", max_length=50, unique=True)
    description = models.TextField(verbose_name="Описание товара")

    price = models.DecimalField(
        verbose_name="Цена товара",
        max_digits=10,
        decimal_places=2,
    )

    available = models.BooleanField(verbose_name="Наличие товара", default=True)

    category = models.ForeignKey(
        verbose_name="Категория товара",
        related_name="products",
        to=Category,
        on_delete=models.CASCADE,
    )

    image = models.ImageField(
        verbose_name="Картинка товара",
        upload_to="products/%Y/%m/%d",
        blank=True,
    )

    created = models.DateTimeField(
        verbose_name="Дата добавления товара", auto_now_add=True
    )

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("shop:product_detail", args=[self.id, self.slug])
