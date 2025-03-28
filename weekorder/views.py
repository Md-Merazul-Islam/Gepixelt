# views.py
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Product, WeeklyOrder, OrderItem
from .serializers import WeeklyOrderSerializer
# views.py
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import WeeklyOrder, Product, OrderItem
from .serializers import WeeklyOrderSerializer

class WeeklyOrderCreateView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            data = request.data
            created_orders = []
            total_week_price = 0  # Variable to keep track of the total price for the whole week

            # Create weekly order for each day
            for weekly_order_data in data:
                weekly_order = WeeklyOrder.objects.create(
                    day_of_week=weekly_order_data['day_of_week'],
                    number_of_people=weekly_order_data['number_of_people']
                )

                order_items = []
                # Create order items for each product in the order
                for item in weekly_order_data['order_items']:
                    product = Product.objects.get(id=item['product'])
                    order_item = OrderItem.objects.create(
                        weekly_order=weekly_order,
                        product=product,
                        quantity=item['quantity']
                    )
                    order_items.append({
                        'product': product.name,
                        'quantity': order_item.quantity,
                        'total_price': order_item.total_price()
                    })

                # Calculate the total price for this weekly order
                total_week_price += weekly_order.total_price()

                # Store the created weekly order info for the response
                created_orders.append({
                    'day_of_week': weekly_order.day_of_week,
                    'number_of_people': weekly_order.number_of_people,
                    'order_items': order_items,
                    'total_order_price': weekly_order.total_price()  # Total price of the order for this day
                })

            # Include the total price of all orders for the week in the response
            return Response({
                "message": "Orders created successfully",
                "orders": created_orders,
                "total_week_price": total_week_price  # Total price for the whole week
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)