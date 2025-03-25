from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from .models import Order
from .serializers import OrderSerializer
# Import your response methods
from utils  .utils import success_response, failure_response


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().order_by('-order_date')
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        """Override to set the user for the order."""
        serializer.save(user=self.request.user)

    def list(self, request, *args, **kwargs):
        """Override list to use success_response."""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return success_response("All orders retrieved successfully", serializer.data)

    def create(self, request, *args, **kwargs):
        """Override create to use success_response."""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return success_response("Order created successfully", serializer.data, status.HTTP_201_CREATED)
        return failure_response("Order creation failed", serializer.errors)

    def retrieve(self, request, *args, **kwargs):
        """Override retrieve to use success_response."""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return success_response("Order details retrieved successfully", serializer.data)

    def update(self, request, *args, **kwargs):
        """Override update to use success_response."""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return success_response("Order updated successfully", serializer.data)
        return failure_response("Order update failed", serializer.errors)

    def destroy(self, request, *args, **kwargs):
        """Override destroy to use success_response."""
        instance = self.get_object()
        instance.delete()
        return success_response("Order deleted successfully", None, status.HTTP_204_NO_CONTENT)

class OrderAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, order_id=None):
        """Retrieve a list of orders or a single order for the authenticated user."""
        if order_id:
            # Retrieve a specific order by ID
            try:
                order = Order.objects.get(id=order_id, user=request.user)
                serializer = OrderSerializer(order)
                return success_response("Order retrieved successfully", serializer.data, status_code=status.HTTP_200_OK)
            except Order.DoesNotExist:
                return failure_response("Order not found", "Order with this ID doesn't exist or you don't have permission to view it.", status_code=status.HTTP_404_NOT_FOUND)
        else:
            # Retrieve all orders for the authenticated user
            orders = Order.objects.filter(user=request.user)
            serializer = OrderSerializer(orders, many=True)
            return success_response("My Orders retrieved successfully", serializer.data, status_code=status.HTTP_200_OK)

    def post(self, request):
        """Create a new order for the authenticated user."""
        # Pass the request into the serializer context
        serializer = OrderSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(user=request.user)  # Associate the order with the authenticated user
            return success_response("Order created successfully", serializer.data, status_code=status.HTTP_201_CREATED)
        return failure_response("Order creation failed", serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)

    def put(self, request, order_id):
        """Update an existing order for the authenticated user."""
        try:
            order = Order.objects.get(id=order_id, user=request.user)
        except Order.DoesNotExist:
            return failure_response("Order not found", "Order with this ID doesn't exist or you don't have permission to update it.", status_code=status.HTTP_404_NOT_FOUND)

        serializer = OrderSerializer(order, data=request.data, partial=False)  # Full update
        if serializer.is_valid():
            serializer.save()
            return success_response("Order updated successfully", serializer.data, status_code=status.HTTP_200_OK)
        return failure_response("Order update failed", serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, order_id):
        """Partially update an existing order for the authenticated user."""
        try:
            order = Order.objects.get(id=order_id, user=request.user)
        except Order.DoesNotExist:
            return failure_response("Order not found", "Order with this ID doesn't exist or you don't have permission to update it.", status_code=status.HTTP_404_NOT_FOUND)

        serializer = OrderSerializer(order, data=request.data, partial=True)  # Partial update
        if serializer.is_valid():
            serializer.save()
            return success_response("Order updated successfully", serializer.data, status_code=status.HTTP_200_OK)
        return failure_response("Order update failed", serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, order_id):
        """Delete an existing order for the authenticated user."""
        try:
            order = Order.objects.get(id=order_id, user=request.user)
            order.delete()
            return success_response("Order deleted successfully", None, status_code=status.HTTP_204_NO_CONTENT)
        except Order.DoesNotExist:
            return failure_response("Order not found", "Order with this ID doesn't exist or you don't have permission to delete it.", status_code=status.HTTP_404_NOT_FOUND)