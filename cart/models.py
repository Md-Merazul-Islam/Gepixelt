from django.db import models
from products.models import Product
from django.contrib.auth import login, get_user_model

User = get_user_model()


class Card(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='card')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email}'s Card"

    def total_price(self):
        return sum(item.total_price() for item in self.items.all())


class CardItem(models.Model):
    card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def total_price(self):
        return self.product.price * self.quantity

    def __str__(self):
        return f"{self.quantity}x {self.product.name}"
