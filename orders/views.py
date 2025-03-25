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
        return success_response("Orders retrieved successfully", serializer.data)

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
