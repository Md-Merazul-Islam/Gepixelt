# serializers.py

from auths.serializers import UserSerializer
from rest_framework import serializers
from .models import Product, SubscriptionPlan, UserSubscription, Transaction
from django.contrib.auth import get_user_model
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

# Product Serializer


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        # Add any other fields you want to expose
        fields = ['id', 'name', 'price', 'description']


# SubscriptionPlan Serializer
class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = ['id', 'name', 'duration_days', 'price']


# UserSubscription Serializer
class UserSubscriptionSerializer(serializers.ModelSerializer):
    plan = SubscriptionPlanSerializer()

    class Meta:
        model = UserSubscription
        fields = ['user', 'plan', 'balance', 'start_date', 'end_date']

    def update(self, instance, validated_data):
        # Update user subscription balance or other details
        plan_data = validated_data.pop('plan', None)
        if plan_data:
            instance.plan = plan_data
        instance.balance = validated_data.get('balance', instance.balance)
        instance.end_date = validated_data.get('end_date', instance.end_date)
        instance.save()
        return instance


class TransactionSerializer(serializers.ModelSerializer):
    # to get the username instead of the user ID
    user = serializers.StringRelatedField()
    plan = SubscriptionPlanSerializer()
    user_subscription = UserSubscriptionSerializer(
        source='user.usersubscription', read_only=True)

    class Meta:
        model = Transaction
        fields = ['id', 'transaction_id', 'plan', 'amount', 'payment_status', 'payment_intent_id','created_at', 'subscription_expiry_date', 'user', 'user_subscription']


class UserSubscriptionSerializer(serializers.ModelSerializer):
    plan = SubscriptionPlanSerializer()
    user = UserSerializer()

    class Meta:
        model = UserSubscription
        fields = ['user', 'plan', 'balance','start_date', 'end_date', 'status']
