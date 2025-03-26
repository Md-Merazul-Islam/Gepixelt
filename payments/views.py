from utils.IsAdminOrStaff import IsAdminOrHasRoleAdmin
from utils.IsAdminOrStaff import IsAdminOrStaff
from rest_framework.pagination import PageNumberPagination
from . serializers import UserSubscriptionSerializer
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
from .models import Product, UserSubscription, SubscriptionPlan
from .serializers import ProductSerializer, UserSubscriptionSerializer, SubscriptionPlanSerializer, TransactionSerializer
from django.shortcuts import get_object_or_404
from django.db import transaction
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.template.loader import render_to_string
from django.core.mail import EmailMessage

User = get_user_model()

stripe.api_key = settings.STRIPE_TEST_SECRET_KEY


def success_response(message, data, status_code=status.HTTP_200_OK):
    return Response({
        "success": True,
        "statusCode": status_code,
        "message": message,
        "data": data
    }, status=status_code)


def failure_response(message, error, status_code=status.HTTP_400_BAD_REQUEST):
    return Response({
        "success": False,
        "statusCode": status_code,
        "message": message,
        "error": error
    }, status=status_code)

# Product ViewSet to list and retrieve products


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    # permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return success_response("Products fetched successfully.", serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return success_response("Product retrieved successfully.", serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return success_response("Product created successfully.", serializer.data, status.HTTP_201_CREATED)
        return failure_response("Product creation failed.", serializer.errors)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial)
        if serializer.is_valid():
            self.perform_update(serializer)
            return success_response("Product updated successfully.", serializer.data)
        return failure_response("Product update failed.", serializer.errors)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return success_response("Product deleted successfully.", {})


# SubscriptionPlan ViewSet to list and retrieve subscription plans


class SubscriptionPlanViewSet(viewsets.ModelViewSet):
    queryset = SubscriptionPlan.objects.all()
    serializer_class = SubscriptionPlanSerializer
    permission_classes = [IsAdminOrHasRoleAdmin]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return success_response("Subscription plans fetched successfully.", serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return success_response("Subscription plan retrieved successfully.", serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return success_response("Subscription plan created successfully.", serializer.data, status.HTTP_201_CREATED)
        return failure_response("Subscription plan creation failed.", serializer.errors)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial)
        if serializer.is_valid():
            self.perform_update(serializer)
            return success_response("Subscription plan updated successfully.", serializer.data)
        return failure_response("Subscription plan update failed.", serializer.errors)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return success_response("Subscription plan deleted successfully.", {})


class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class UserSubscriptionList(viewsets.ReadOnlyModelViewSet):
    queryset = UserSubscription.objects.all()
    serializer_class = UserSubscriptionSerializer
    permission_classes = [IsAdminOrStaff]
    pagination_class = CustomPagination

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset().filter()

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            paginated_response = self.get_paginated_response(serializer.data)

            # Customize paginated response
            return Response({
                "success": True,
                "statusCode": status.HTTP_200_OK,
                "message": "All User subscriptions fetched successfully.",
                "data": paginated_response.data  # includes pagination metadata
            }, status=status.HTTP_200_OK)

        # Fallback if no pagination
        serializer = self.get_serializer(queryset, many=True)
        return success_response("All User subscriptions fetched successfully.", serializer.data)

# UserSubscription ViewSet to handle user subscriptions (create and view)


# class UserSubscriptionViewSet(viewsets.ModelViewSet):
class UserSubscriptionViewSet(viewsets.ModelViewSet):
    serializer_class = UserSubscriptionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return only the subscriptions for the logged-in user"""
        return UserSubscription.objects.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        """Return the current user's subscriptions with metadata"""
        queryset = self.get_queryset()  # This already filters by user
        serializer = self.get_serializer(queryset, many=True)

        # Generate metadata
        total = queryset.count()
        active = queryset.filter(status='active').count()
        inactive = queryset.filter(status='inactive').count()

        return success_response(
            "Your subscriptions fetched successfully.",
            {
                "total": total,
                "active": active,
                "inactive": inactive,
                "subscriptions": serializer.data
            }
        )

    def create(self, request, *args, **kwargs):
        plan_id = request.data.get('plan_id')

        if not plan_id:
            return failure_response("Plan ID is required.", {"detail": "Please provide a valid plan_id."}, status.HTTP_400_BAD_REQUEST)

        plan = get_object_or_404(SubscriptionPlan, id=plan_id)
        user = request.user

        subscription, created = UserSubscription.objects.get_or_create(
            user=user, plan=plan)

        if not created:
            subscription.plan = plan
            subscription.save()

        return success_response("Subscription created or updated successfully.", UserSubscriptionSerializer(subscription).data, status.HTTP_201_CREATED)

    def retrieve(self, request, *args, **kwargs):
        """Retrieve only the current user's subscription (single, if exists)"""
        user = request.user
        try:
            user_subscription = UserSubscription.objects.get(user=user)
            serializer = UserSubscriptionSerializer(user_subscription)
            return success_response("Your subscription retrieved successfully.", serializer.data)
        except UserSubscription.DoesNotExist:
            return failure_response("No subscription found for your account.", {"detail": "You don't have any active subscriptions."}, status.HTTP_404_NOT_FOUND)


# CompletePaymentView handles the payment process and subscription activation
class CompletePaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, plan_id):
        user = request.user
        user_email = request.data.get("email")
        payment_method_id = request.data.get("payment_method_id")

        # Retrieve the selected plan
        plan = get_object_or_404(SubscriptionPlan, id=plan_id)

        # Ensure `payment_method_id` is provided
        if not payment_method_id:
            return Response({"detail": "Payment method ID is required."}, status=400)

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
                customer=user.stripe_customer_id,  # Use the stored Customer ID
                payment_method=payment_method_id,
                confirm=True,
                receipt_email=user_email,  # Send receipt to email
                automatic_payment_methods={
                    "enabled": True, "allow_redirects": "never"
                }
            )

            # Check if the payment was successful
            if payment_intent.status == 'succeeded':
                # Save Transaction Data in Database
                transaction = Transaction.objects.create(
                    user=user,
                    plan=plan,
                    transaction_id=payment_intent.id,
                    amount=plan.price,
                    payment_status="SUCCESS",  # Correct field
                    payment_intent_id=payment_intent.id,
                    created_at=timezone.now()  # Use current time for transaction creation
                )

                # Create or Update User Subscription (Enrollment in Subscription Plan)
                user_subscription, created = UserSubscription.objects.get_or_create(
                    user=user, plan=plan)

                # If subscription exists, update the subscription details
                if not created:
                    user_subscription.balance += plan.price  # Add plan price to the balance
                    user_subscription.status = 'active'  # Mark as active
                    user_subscription.end_date = timezone.now(
                    ) + timedelta(days=plan.duration_days)  # Set end date
                    user_subscription.save()
                else:
                    # If it's a new subscription, set it to active and initial balance
                    user_subscription.balance = plan.price
                    user_subscription.status = 'active'
                    user_subscription.end_date = timezone.now(
                    ) + timedelta(days=plan.duration_days)  # Set end date
                    user_subscription.save()

                # Update the user's balance after the transaction
                user.balance += plan.price  # Add the subscription cost to the user balance
                user.save()  # Save the updated user balance

                # Send Subscription Confirmation Email
                subject = f"Subscription Confirmation: {plan.name}"
                end_date = user_subscription.end_date.strftime('%d.%m.%Y')
                message = render_to_string(
                    'subscription_confirmation.html', {
                        'user': user,
                        'plan': plan,
                        'transaction': transaction
                    })

                # Send Subscription Confirmation Email
                email = EmailMessage(
                    subject,
                    message,
                    settings.EMAIL_HOST_USER,
                    [user.email],  # user.email should be the recipient's email
                )
                email.content_subtype = "html"  # This is important to send as HTML email
                email.send(fail_silently=False)

                return Response({
                    "detail": f"Successfully subscribed to {plan.name}.",
                    "transaction_id": transaction.transaction_id,
                    "plan": plan.name,
                    "amount": str(plan.price),
                    "subscription_status": user_subscription.status,
                    "user_balance": user.balance  # Show updated user balance
                }, status=201)

            else:
                return Response({"detail": "Payment failed."}, status=400)

        except stripe.error.CardError as e:
            return Response({"detail": f"Card error: {str(e)}"}, status=400)
        except stripe.error.StripeError as e:
            return Response({"detail": f"Stripe error: {str(e)}"}, status=500)
        except Exception as e:
            return Response({"detail": f"An error occurred: {str(e)}"}, status=500)


class TransactionListView(APIView):
    permission_classes = [IsAdminOrStaff]

    def get(self, request):
        user = request.user
        transactions = Transaction.objects.filter(user=user).order_by('-id')

        # Serialize the data
        serializer = TransactionSerializer(transactions, many=True)

        return success_response("Transaction list retrieved successfully.", serializer.data, status_code=200)


class UserSubscriptionDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        user_subscriptions = UserSubscription.objects.filter(user=user)

        if not user_subscriptions:
            return Response({
                "detail": "No subscription found for the user."
            }, status=status.HTTP_404_NOT_FOUND)

        user_subscription = user_subscriptions.order_by(
            '-start_date').first()

        serializer = UserSubscriptionSerializer(user_subscription)

        return Response({
            "detail": "User subscription data retrieved successfully.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)
