from django.views.decorators.csrf import csrf_exempt
import stripe
from django.conf import settings
from django.http import JsonResponse
from rest_framework.decorators import api_view
from .models import Subscription
from django.shortcuts import get_object_or_404
from django.utils import timezone
from cart.models import Card  # Assuming you have a Cart model in your app

# Set your Stripe secret key
stripe.api_key = settings.STRIPE_TEST_SECRET_KEY

from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
# from .models import Card
import stripe
from django.conf import settings

# Set your secret key
stripe.api_key = settings.STRIPE_TEST_SECRET_KEY

@api_view(['POST'])
def create_checkout_session(request):
    """
    Create a Stripe checkout session for the cart.
    """
    # Ensure the user is authenticated
    if not request.user.is_authenticated:
        return Response({"error": "Authentication required"}, status=401)

    # Get the user's cart (card)
    cart = get_object_or_404(Card, user=request.user)
    total_price = cart.total_price()  # Get the total price of the cart

    try:
        # Create the Stripe Checkout session
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',  # Currency (can be changed to your desired currency)
                        'product_data': {
                            'name': 'Weekly Food Subscription',  # Subscription name
                        },
                        'unit_amount': int(total_price * 100),  # Amount in cents (Stripe requires this)
                    },
                    'quantity': 1,  # Only 1 subscription for the user
                },
            ],
            mode='payment',  # 'payment' mode for one-time payments
            success_url=request.build_absolute_uri('/api/v1/payment/success/'),  # Redirect to success page on successful payment
            cancel_url=request.build_absolute_uri('/api/v1/payment/cancel/'),    # Redirect to cancel page if payment is canceled
        )

        # Return the session ID to the frontend
        return Response({
            'id': session.id
        })

    except Exception as e:
        return Response({'error': str(e)}, status=400)

# Webhook to handle Stripe events

stripe.api_key = settings.STRIPE_SECRET_KEY  # Your Stripe Secret Key

@csrf_exempt
@require_POST  # Ensure this view only handles POST requests
def stripe_webhook(request):
    # The endpoint secret you get when you set up your webhook in Stripe Dashboard
    endpoint_secret = settings.STRIPE_ENDPOINT_SECRET

    # Retrieve the request's body and signature header
    payload = request.body
    sig_header = request.headers.get('Stripe-Signature')

    if sig_header is None:
        return JsonResponse({'error': 'Missing Stripe-Signature header'}, status=400)

    # Verify the webhook signature
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        return JsonResponse({'error': 'Invalid payload'}, status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return JsonResponse({'error': 'Invalid signature'}, status=400)

    # Handle the event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        # Handle checkout.session.completed event (payment was successful)
        order_id = session['metadata']['order_id']  # Assuming you're passing an order_id in metadata
        try:
            order = Order.objects.get(id=order_id)
            order.payment_status = 'Paid'
            order.save()
        except Order.DoesNotExist:
            return JsonResponse({'error': 'Order not found'}, status=404)

    # Other event types can be handled here
    else:
        # Unexpected event type
        return JsonResponse({'error': 'Unhandled event type'}, status=400)

    return JsonResponse({'status': 'success'})

from django.shortcuts import render

def success(request):
    return render(request, 'success.html')  # Render the success.html template

def cancel(request):
    return render(request, 'cancel.html') 