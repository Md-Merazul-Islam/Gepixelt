from decimal import Decimal
import logging
from products.models import Product
from django.db import models,transaction
from django.contrib.auth import login, get_user_model, update_session_auth_hash
from django.core.exceptions import ValidationError
User = get_user_model()
# Create your models here.
logger = logging.getLogger(__name__)


class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('canceled', 'Canceled'),
        ('delivered', 'Delivered'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders", null=True, blank=True)
    order_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    receive_date = models.DateField(null=True, blank=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending', null=True, blank=True)
    
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
