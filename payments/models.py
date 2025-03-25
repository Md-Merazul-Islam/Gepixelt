
from django.db import models
from products.models import Product
from django.contrib.auth import get_user_model
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


# Subscription Plan Model
class SubscriptionPlan(models.Model):
    name = models.CharField(max_length=100)
    # Number of days in the plan (e.g., 7 for weekly)
    duration_days = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name


class UserSubscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    # This will store the subscription start date
    start_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    # This will store the subscription expiration date
    end_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=[('active', 'Active'), ('inactive', 'Inactive')], default='inactive')

    def __str__(self):
        return f"{self.user.email} - {self.plan.name}"

    def renew_subscription(self):
        """Renew subscription based on the plan's duration."""
        self.end_date = timezone.now() + timedelta(days=self.plan.duration_days)
        self.save()

    def deduct_balance(self, amount):
        """Deduct balance if the user has enough."""
        if self.balance is None:  # Check for None
            self.balance = Decimal('0.00')  # Set balance to 0 if it is None

        if self.balance >= amount:
            self.balance -= amount
            self.save()
            return True
        return False


class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    transaction_id = models.CharField(max_length=255, null=True, blank=True)
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=20, choices=[(
        'SUCCESS', 'Success'), ('FAILED', 'Failed')], default='FAILED')
    payment_intent_id = models.CharField(max_length=255)
    # This will store the subscription expiration date
    subscription_expiry_date = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Automatically calculate subscription expiration date based on the plan's duration
        if not self.subscription_expiry_date:
            # If the expiration date is not set, calculate it using the plan's duration
            self.subscription_expiry_date = timezone.now(
            ) + timedelta(days=self.plan.duration_days)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Transaction {self.payment_intent_id} for {self.user.username}"

