# serializers.py

from rest_framework import serializers
from .models import Order, OrderProduct, Product, SubscriptionPlan, UserSubscription, Transaction
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


# OrderProduct Serializer (many-to-many relationship between Order and Product)
class OrderProductSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())  # Just use the product ID

    class Meta:
        model = OrderProduct
        fields = ['product', 'quantity', 'price_per_item']

# Order Serializer


class OrderSerializer(serializers.ModelSerializer):
    customer = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    products = OrderProductSerializer(many=True)

    class Meta:
        model = Order
        fields = ['id', 'customer', 'order_date', 'products', 'total_price']

    def create(self, validated_data):
        # Pop the products from validated data
        products_data = validated_data.pop('products')
        # customer = validated_data['customer']  # Ensure customer is passed and correctly handled
        order = Order.objects.create(**validated_data)  # Create the order

        total_price = Decimal(0.0)  # Initialize total price
        for product_data in products_data:
            product = Product.objects.get(id=product_data['product'])
            price_per_item = product.price
            quantity = product_data['quantity']
            order_product = OrderProduct.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price_per_item=price_per_item
            )
            total_price += price_per_item * quantity

        order.total_price = total_price
        order.save()
        return order


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
        fields = ['id', 'transaction_id', 'plan', 'amount', 'payment_status', 'payment_intent_id',
                  'created_at', 'subscription_expiry_date', 'user', 'user_subscription']


class UserSubscriptionSerializer(serializers.ModelSerializer):
    plan = SubscriptionPlanSerializer()

    class Meta:
        model = UserSubscription
        fields = ['user', 'plan', 'balance',
                  'start_date', 'end_date', 'status']
