from datetime import date
from decimal import Decimal
from .models import Order, Product, OrderProduct
from rest_framework import serializers
import stripe
from rest_framework.views import APIView
from django.conf import settings
from .serializers import SubscriptionSerializer
from .models import Subscription
from django.shortcuts import render

# Create your views here.
from rest_framework import status, generics
from rest_framework.response import Response
from .models import Order
from .serializers import OrderSerializer,OrderProductSerializer


class CreateOrderView(generics.CreateAPIView):
    serializer_class = OrderSerializer

    def post(self, request, *args, **kwargs):
        data = request.data
        # Assign the logged-in user as the customer
        data['customer'] = request.user.id

        # Calculate total price (product price * quantity) inside the serializer
        serializer = self.get_serializer(data=data)

        if serializer.is_valid():
            order = serializer.save()
            # Check if the balance is sufficient before placing the order
            if order.place_order():  # If balance is available and order is placed
                return Response({'message': 'Order placed successfully!', 'order_id': order.id}, status=status.HTTP_201_CREATED)
            else:
                return Response({'message': 'Insufficient balance to place the order.'}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CreateSubscriptionView(generics.CreateAPIView):
    serializer_class = SubscriptionSerializer

    def post(self, request, *args, **kwargs):
        data = {
            'customer': request.user.id,  # Use the logged-in user for subscription
            'plan_type': 'weekly',  # Default to weekly subscription
            'price': 20.00,  # Set price
        }

        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            subscription = serializer.save()
            # Add balance to customer after subscription
            subscription.add_balance_to_customer()
            return Response({'message': 'Subscription created successfully!', 'subscription_id': subscription.id}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


stripe.api_key = settings.STRIPE_TEST_SECRET_KEY


class StripeCheckoutView(APIView):
    def post(self, request, *args, **kwargs):
        # Get the order
        order_id = request.data.get('order_id')
        order = Order.objects.get(id=order_id)

        # Create a Stripe checkout session
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': order.product.name,
                    },
                    # Stripe requires the amount in cents
                    'unit_amount': int(order.total_price * 100),
                },
                'quantity': order.quantity,
            }],
            mode='payment',
            success_url=request.build_absolute_uri('/success/'),
            cancel_url=request.build_absolute_uri('/cancel/'),
        )

        return Response({'session_id': session.id}, status=200)


class OrderSerializer(serializers.ModelSerializer):
    products = OrderProductSerializer(many=True)
    total_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Order
        fields = ['customer', 'products', 'postal_code', 'address',
                  'email', 'phone_number', 'city', 'total_price']

    def create(self, validated_data):
        products_data = validated_data.pop('products')
        order = Order.objects.create(**validated_data)

        total_price = Decimal(0.0)

        # Add the products and their quantities to the order, and calculate the total price
        for product_data in products_data:
            product = product_data['product']
            quantity = product_data['quantity']
            price_per_item = product.price_per_item
            total_price += price_per_item * quantity

            # Create an OrderProduct entry for each product in the order
            order_product = OrderProduct.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price_per_item=price_per_item
            )

        # Update the order's total price
        order.total_price = total_price
        order.save()

        return order
