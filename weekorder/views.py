from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import WeeklyOrder, Product, OrderItem
from django.conf import settings
import stripe

# Initialize Stripe
stripe.api_key = settings.STRIPE_TEST_SECRET_KEY

class WeeklyOrderCreateView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Extract payment info from the request body
            payment_info = request.data.get('payment_info')  # Payment details: name, email, etc.
            total_amount = request.data.get('total_amount')  # Total amount for the payment

            if total_amount is None or total_amount <= 0:
                return Response({"error": "Invalid total amount."}, status=status.HTTP_400_BAD_REQUEST)

            # Step 1: Create Payment Intent using Stripe
            payment_intent = stripe.PaymentIntent.create(
                amount=int(total_amount * 100),  # Convert amount to cents
                currency='usd',
            )

            client_secret = payment_intent.client_secret  # Return this to the frontend to complete payment

            # Respond with the client_secret to complete the payment
            return Response({
                'client_secret': client_secret,
                'message': 'Payment intent created successfully. Please complete the payment.'
            }, status=status.HTTP_200_OK)

        except stripe.error.StripeError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class WeeklyOrderConfirmPaymentView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Extract the payment status and order data from the request
            payment_status = request.data.get('payment_status')
            order_data = request.data.get('order_data')
            payment_info = request.data.get('payment_info')

            if payment_status != 'success':
                return Response({"error": "Payment failed"}, status=status.HTTP_400_BAD_REQUEST)

            stripe_payment_id = request.data.get('stripe_payment_id')
            created_orders = []
            total_week_price = 0

            # Process the order data and save it to the database
            for weekly_order_data in order_data:
                weekly_order = WeeklyOrder.objects.create(
                    day_of_week=weekly_order_data['day_of_week'],
                    number_of_people=weekly_order_data['number_of_people'],
                    customer_name=payment_info['name'],
                    customer_email=payment_info['email'],
                    customer_phone=payment_info['phone'],
                    customer_address=payment_info['address'],
                    customer_postal_code=payment_info['postal_code'],
                    stripe_payment_id=stripe_payment_id
                )

                order_items = []
                for item in weekly_order_data['order_items']:
                    product = Product.objects.get(id=item['product'])
                    if product.price is None:
                        total_price = 0
                    else:
                        total_price = product.price * item['quantity']

                    order_item = OrderItem.objects.create(
                        weekly_order=weekly_order,
                        product=product,
                        quantity=item['quantity']
                    )
                    order_items.append({
                        'product': product.name,
                        'quantity': order_item.quantity,
                        'total_price': total_price
                    })

                total_week_price += weekly_order.total_price()

                created_orders.append({
                    'day_of_week': weekly_order.day_of_week,
                    'number_of_people': weekly_order.number_of_people,
                    'order_items': order_items,
                    'total_order_price': weekly_order.total_price()  # Total price of the order
                })

            return Response({
                "message": "Orders created successfully",
                "orders": created_orders,
                "total_week_price": total_week_price
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
