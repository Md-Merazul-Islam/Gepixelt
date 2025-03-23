from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Subscription(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    stripe_customer_id = models.CharField(max_length=255)
    stripe_subscription_id = models.CharField(max_length=255)
    payment_email = models.EmailField()  # Store the email used for payment
    status = models.CharField(max_length=50, choices=[('active', 'Active'), ('canceled', 'Canceled')])
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # Amount charged
    total_price = models.DecimalField(max_digits=10, decimal_places=2)  # Total price of the subscription
    payment_status = models.CharField(max_length=50, choices=[('succeeded', 'Succeeded'), ('failed', 'Failed')], default='succeeded')  # Payment status
    
    def __str__(self):
        return f"{self.user.email} - {self.status} Subscription"

from django.db import models

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=50, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} - {self.payment_status}"
