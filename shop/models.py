from django.db import models


class Category(models.Model):
    """Категории товаров"""
    name = models.CharField(
        verbose_name="Имя категории",
        max_length=50,
    )
    slug = models.SlugField(
        verbose_name="Slug категории",
        max_length=50,
        unique=True,
    )

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name
