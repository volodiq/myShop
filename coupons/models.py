from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Coupon(models.Model):
    """Скидочные купоны"""

    code = models.CharField(verbose_name="Код купона", max_length=50, unique=True)

    valid_from = models.DateTimeField(verbose_name="Дата начала действия купона")
    valid_to = models.DateTimeField(verbose_name="Дата конца действия купона")

    discount = models.IntegerField(
        verbose_name="Скидка в процентах",
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Скидка в процентах от 0 до 100",
    )

    active = models.BooleanField(verbose_name="Активен")

    class Meta:
        verbose_name = "Купон"
        verbose_name_plural = "Купоны"

    def __str__(self):
        return self.code
