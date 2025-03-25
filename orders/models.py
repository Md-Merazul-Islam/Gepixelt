from products.models import Product
from django.db import models
from django.contrib.auth import login, get_user_model, update_session_auth_hash
from django.core.exceptions import ValidationError
User = get_user_model()
# Create your models here.

from decimal import Decimal
from django.core.exceptions import ValidationError

class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('delivered', 'Delivered'),
    )

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="orders", null=True, blank=True)
    order_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    receive_date = models.DateField(null=True, blank=True)
    total_price = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal('0.00'), null=True, blank=True)
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default='pending', null=True, blank=True)

    def __str__(self):
        return f"Order {self.id} - {self.user.username}"

    def calculate_total_price(self):
        """
        Recalculate the total price of the order based on OrderItems.
        """
        self.total_price = sum(
            item.price for item in self.items.all())  # Sum up OrderItem prices
        self.save(update_fields=['total_price'])

    def save(self, *args, **kwargs):
        """
        Before saving, check if the user has enough balance.
        """
        # Ensure both total_price and balance are Decimals before comparison
        total_price = Decimal(self.total_price)  # Convert to Decimal if it's a float
        balance = Decimal(self.user.balance)  # Ensure the balance is Decimal

        if balance < total_price:
            raise ValidationError("Insufficient balance to place the order.")

        # Deduct the total price from user's balance when the order is placed
        self.user.balance -= total_price
        self.user.save(update_fields=['balance'])

        super(Order, self).save(*args, **kwargs)


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        """
        Automatically set the price based on product price and quantity.
        """
        self.price = self.product.price * self.quantity
        super(OrderItem, self).save(*args, **kwargs)

        # Recalculate total price for the order
        self.order.calculate_total_price()
        self.order.save(update_fields=['total_price'])
