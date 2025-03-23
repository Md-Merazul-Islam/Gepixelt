from django.urls import path
from .views import CreateOrderView, CreateSubscriptionView, StripeCheckoutView

urlpatterns = [
    path('order/', CreateOrderView.as_view(), name='create-order'),
    path('subscribe/', CreateSubscriptionView.as_view(), name='create-subscription'),
    path('payment/checkout/', StripeCheckoutView.as_view(), name='stripe-checkout'),
]
