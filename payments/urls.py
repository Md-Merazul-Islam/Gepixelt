from django.urls import path
from .views import create_checkout_session, stripe_webhook, success, cancel

urlpatterns = [
    path('checkout/', create_checkout_session, name='checkout'),
    path('web-hook/', stripe_webhook, name='checkout'),

    path('success/', success, name='success'),
    path('cancel/', cancel, name='cancel'),
]
