# admin.py
from django.contrib import admin
from .models import SubscriptionPlan, UserSubscription, Transaction, Order, OrderProduct

admin.site.register(SubscriptionPlan)
admin.site.register(UserSubscription)
admin.site.register(Transaction)
admin.site.register(Order)
admin.site.register(OrderProduct)
