# models.py
from django.db import models

from products.models import Product


class WeeklyOrder(models.Model):
    # Saturday, Monday, Friday, etc.
    day_of_week = models.CharField(max_length=10)
    number_of_people = models.PositiveIntegerField()

    def total_price(self):
        total = 0
        for order_item in self.order_items_week.all():  # Use 'order_items_week' here
            total += order_item.total_price()
        return total


# models.py
class OrderItem(models.Model):
    weekly_order = models.ForeignKey(
        WeeklyOrder, related_name='order_items_week', on_delete=models.CASCADE)
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='order_items_week')

    quantity = models.PositiveIntegerField()

    def total_price(self):
        if self.product.price is None:
            return 0  # Handle None for price safely
        return self.product.price * self.quantity

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
