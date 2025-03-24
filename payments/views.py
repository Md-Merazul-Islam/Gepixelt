from rest_framework.views import APIView
from .models import SubscriptionPlan, UserSubscription, Transaction
from rest_framework import status
from .models import Transaction, UserSubscription, SubscriptionPlan
from .models import SubscriptionPlan, UserSubscription
from django.conf import settings
from rest_framework.decorators import api_view
import stripe
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Order, Product, UserSubscription, SubscriptionPlan, OrderProduct
from .serializers import OrderSerializer, ProductSerializer, UserSubscriptionSerializer, SubscriptionPlanSerializer
from django.shortcuts import get_object_or_404
from django.db import transaction
from decimal import Decimal


# Product ViewSet to list and retrieve products
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    # Only authenticated users can access products
    # permission_classes = [IsAuthenticated]


# SubscriptionPlan ViewSet to list and retrieve subscription plans
class SubscriptionPlanViewSet(viewsets.ModelViewSet):
    queryset = SubscriptionPlan.objects.all()
    serializer_class = SubscriptionPlanSerializer
    # Only authenticated users can access subscription plans
    # permission_classes = [IsAuthenticated]


# UserSubscription ViewSet to handle user subscriptions (create and view)
class UserSubscriptionViewSet(viewsets.ModelViewSet):
    queryset = UserSubscription.objects.all()
    serializer_class = UserSubscriptionSerializer
    # Only authenticated users can access their subscription
    # permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return the subscription for the logged-in user"""
        return self.queryset.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        """Handle subscription creation for a user"""
        plan_id = request.data.get('plan_id')
        plan = get_object_or_404(SubscriptionPlan, id=plan_id)
        user = request.user

        # Create or update the subscription
        subscription, created = UserSubscription.objects.get_or_create(
            user=user, plan=plan)

        # If the subscription exists, we may want to update it or just return the existing one
        if not created:
            subscription.plan = plan
            subscription.save()

        return Response(UserSubscriptionSerializer(subscription).data)


# Order ViewSet to create and list orders
class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    # Only authenticated users can create/view orders
    # permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return orders for the logged-in user"""
        return self.queryset.filter(customer=self.request.user)

    def create(self, request, *args, **kwargs):
        """Create a new order for a user"""
        # Ensure that the total_price is correctly calculated before creating the order
        order_data = request.data
        products_data = order_data.get('products', [])

        # Create the order with temporary data
        order = Order(customer=request.user,
                      order_date=order_data.get('order_date'))
        order.save()

        # Calculate the total price and create OrderProduct instances
        total_price = Decimal(0)
        for product_data in products_data:
            product = get_object_or_404(Product, id=product_data['product'])
            quantity = product_data['quantity']
            price_per_item = product.price
            total_price += price_per_item * quantity
            # Create OrderProduct instances
            OrderProduct.objects.create(
                order=order, product=product, quantity=quantity, price_per_item=price_per_item)

        # Save the total price to the order
        order.total_price = total_price
        order.save()

        return Response(OrderSerializer(order).data)



from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import SubscriptionPlan, UserSubscription, Transaction
import stripe
from django.conf import settings
from django.core.mail import send_mail

stripe.api_key = settings.STRIPE_TEST_SECRET_KEY

# Utility functions for response
def failure_response(message, data=None, status_code=400):
    return Response({"detail": message, "data": data}, status=status_code)

def success_response(message, data=None, status_code=200):
    return Response({"detail": message, "data": data}, status=status_code)


class CompletePaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, plan_id):
        user = request.user
        user_email = request.data.get("email")
        payment_method_id = request.data.get("payment_method_id")
        plan = get_object_or_404(SubscriptionPlan, id=plan_id)

        # Ensure payment_method_id is provided
        if not payment_method_id:
            return failure_response("Payment method ID is required.", {}, status_code=400)

        try:
            # Check if the user already has a Stripe Customer ID
            if not user.stripe_customer_id:
                customer = stripe.Customer.create(
                    email=user_email,
                    name=user.username
                )
                user.stripe_customer_id = customer.id
                user.save()

            # Attach PaymentMethod to the Customer
            stripe.PaymentMethod.attach(
                payment_method_id,
                customer=user.stripe_customer_id
            )

            # Create a PaymentIntent using the Customer and attached PaymentMethod
            payment_intent = stripe.PaymentIntent.create(
                amount=int(plan.price * 100),  # Convert to cents
                currency="usd",
                customer=user.stripe_customer_id,
                payment_method=payment_method_id,
                confirm=True,
                receipt_email=user_email,
                automatic_payment_methods={
                    "enabled": True, "allow_redirects": "never"
                }
            )

            # Save Payment Data in Database
            payment = Transaction.objects.create(
                user=user,
                plan=plan,
                transaction_id=payment_intent.id,
                amount=plan.price,
                payment_status="SUCCESS"
            )

            # Create UserSubscription
            UserSubscription.objects.create(user=user, plan=plan)

            # Send Subscription Confirmation Email
            subject = f"Subscription Confirmation: {plan.name}"
            message = f"""
            Hello {user.username},

            Congratulations! You have successfully subscribed to the "{plan.name}" plan.

            Here are your payment details:
            - Plan: {plan.name}
            - Amount Paid: ${plan.price}
            - Transaction ID: {payment.transaction_id}

            You can now access the benefits of your subscription.

            Best Regards,
            Your Subscription Team
            """
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user_email],
                fail_silently=False,
            )

            return success_response(f"Successfully subscribed to {plan.name}.", {
                "user_id": user.id,
                "username": user.username,
                "email": user_email,
                "plan_id": plan.id,
                "transaction_id": payment.transaction_id
            }, status_code=201)

        except stripe.error.CardError as e:
            return failure_response("Card error. Payment failed.", {"error": str(e)}, status_code=400)

        except stripe.error.StripeError as e:
            return failure_response("Payment processing error. Try again later.", {"error": str(e)}, status_code=500)

        except Exception as e:
            return failure_response(f"An error occurred: {str(e)}", {}, status_code=500)
