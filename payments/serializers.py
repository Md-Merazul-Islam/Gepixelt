from rest_framework import serializers
from .models import  Subscription

class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ['user', 'stripe_customer_id', 'stripe_subscription_id', 'status', 'start_date', 'end_date', 'amount']