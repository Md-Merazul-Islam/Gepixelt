from django.db import models

# Create your models here.
from django.db import models
from products.models import Product

from django.contrib.auth import get_user_model

User = get_user_model()


class Order(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, through='OrderProduct')
    quantity = models.PositiveIntegerField()
    order_date = models.DateField()
    postal_code = models.CharField(max_length=10)
    address = models.CharField(max_length=255)
    email = models.EmailField()
    phone_number = models.CharField(max_length=15)
    city = models.CharField(max_length=100)
    total_price = models.DecimalField(
        max_digits=10, decimal_places=2)  # Calculated total price

    def __str__(self):
        return f"Order {self.id} by {self.customer.username}"

    def place_order(self):
        """Check if balance is sufficient to place the order, deduct balance if available."""
        if self.customer.customer.deduct_balance(self.total_price):
            self.save()
            return True
        return False

class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price_per_item = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} x {self.quantity} for Order {self.order.id}"

class Subscription(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    plan_type = models.CharField(max_length=20, choices=[
                                 ('weekly', 'Weekly'), ('monthly', 'Monthly')])
    price = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return f"{self.customer.username} - {self.plan_type} Subscription"
