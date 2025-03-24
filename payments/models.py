from django.db import models
from products.models import Product
from django.contrib.auth import get_user_model
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

# Order Model
class Order(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, through='OrderProduct')
    order_date = models.DateField()  # Date chosen by the user
    create_date = models.DateField(auto_now_add=True, blank=True, null=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Order {self.id} by {self.customer.username}"

    def place_order(self):
        """Check if balance is sufficient to place the order, deduct balance if available."""
        if self.customer.deduct_balance(self.total_price):
            self.save()
            return True
        return False

    def calculate_total_price(self):
        """Method to calculate the total price for the order."""
        total = Decimal(0.0)  # Start with 0.0 for accurate calculation
        for order_product in self.orderproduct_set.all():
            total += order_product.quantity * order_product.price_per_item
        self.total_price = total
        self.save()  # Save the updated total_price to the order


# OrderProduct Model (for relationship between products and orders)
class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price_per_item = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} x {self.quantity} for Order {self.order.id}"


# Subscription Plan Model
class SubscriptionPlan(models.Model):
    name = models.CharField(max_length=100)
    duration_days = models.IntegerField()  # Number of days in the plan (e.g., 7 for weekly)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name

class UserSubscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=[('active', 'Active'), ('inactive', 'Inactive')], default='inactive')

    def __str__(self):
        return f"{self.user.email} - {self.plan.name}"

    def renew_subscription(self):
        """Renew subscription based on the plan's duration."""
        self.end_date = timezone.now() + timedelta(days=self.plan.duration_days)
        self.save()

    def deduct_balance(self, amount):
        """Deduct balance if the user has enough."""
        if self.balance >= amount:
            self.balance -= amount
            self.save()
            return True
        return False



# Add method to the User model to check balance deduction
User.add_to_class('deduct_balance', lambda self, amount: self.usersubscription.deduct_balance(amount))

class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    transaction_id = models.CharField(max_length=255, null=True, blank=True)
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=20, choices=[('SUCCESS', 'Success'), ('FAILED', 'Failed')], default='FAILED')
    payment_intent_id = models.CharField(max_length=255)
    subscription_expiry_date = models.DateTimeField(blank=True,null=True)  # This will store the subscription expiration date
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Automatically calculate subscription expiration date based on the plan's duration
        if not self.subscription_expiry_date:
            # If the expiration date is not set, calculate it using the plan's duration
            self.subscription_expiry_date = timezone.now() + timedelta(days=self.plan.duration_days)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Transaction {self.payment_intent_id} for {self.user.username}"
