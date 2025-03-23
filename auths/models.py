from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
now = timezone.now()


class Role(models.TextChoices):
    ADMIN = 'admin', 'Admin'
    USER = 'user', 'User'


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True, db_index=True)
    role = models.CharField(max_length=10, choices=Role.choices,
                            default=Role.USER, null=True, blank=True, db_index=True)
    address = models.CharField(
        max_length=255, null=True, blank=True, db_index=True)
    city = models.CharField(max_length=255, null=True,
                            blank=True, db_index=True)
    postal_code = models.CharField(
        max_length=255, null=True, blank=True, db_index=True)
    phone_number = models.CharField(
        max_length=15, null=True, blank=True, db_index=True)
    photo = models.CharField(max_length=255, blank=True, null=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    stripe_customer_id = models.CharField(max_length=100, null=True)
    trial_status = models.BooleanField(default=True)
    # subscription_plan = models.ForeignKey('UserSubscription', on_delete=models.SET_NULL, null=True, blank=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email


    def add_balance(self, amount):
        """Add balance to the customer account."""
        self.balance += amount
        self.save()

    def deduct_balance(self, amount):
        """Deduct balance from the customer account."""
        if self.balance >= amount:
            self.balance -= amount
            self.save()
            return True
        return False


class UserProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6, null=True, blank=True)
    otp_created_at = models.DateTimeField(auto_now_add=True)

    def is_otp_expired(self):
        if self.otp_created_at:
            return timezone.now() > self.otp_created_at + timezone.timedelta(minutes=10)
        return True

    def __str__(self):
        return f"Profile of {self.user.email}"
