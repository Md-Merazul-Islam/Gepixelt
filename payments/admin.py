from django.contrib import admin
from .models import  Subscription
from cart.models import Card, CardItem

class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'payment_email', 'status', 'amount', 'payment_status', 'start_date', 'end_date']
    search_fields = ['user__email', 'payment_email']  # Allow searching by user email or payment email
    list_filter = ['status', 'payment_status']  # Filter by subscription status and payment status

admin.site.register(Card)
admin.site.register(CardItem)
admin.site.register(Subscription, SubscriptionAdmin)
