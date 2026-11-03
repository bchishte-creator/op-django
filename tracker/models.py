from django.db import models
from django.core.validators import FileExtensionValidator

from .validators import validate_image_size


class TeamMember(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=80, unique=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name


class Food(models.Model):
    name = models.CharField(max_length=120, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class FoodEvent(models.Model):
    food = models.ForeignKey(Food, on_delete=models.PROTECT, related_name='events')
    consumer = models.ForeignKey(
        TeamMember,
        on_delete=models.PROTECT,
        related_name='food_events',
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='food_events',
    )
    consumed_at = models.DateTimeField(db_index=True)
    notes = models.TextField(blank=True)
    photo = models.ImageField(
        upload_to='food-events/%Y/%m/%d/',
        blank=True,
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'webp']),
            validate_image_size,
        ],
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-consumed_at', '-pk']
        indexes = [
            models.Index(fields=['category', '-consumed_at']),
            models.Index(fields=['consumer', '-consumed_at']),
        ]

    def __str__(self):
        return f'{self.food} eaten by {self.consumer} at {self.consumed_at:%Y-%m-%d %H:%M}'
