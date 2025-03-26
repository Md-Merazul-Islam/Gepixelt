from django.contrib import admin
from .models import  SubscriptionPlan, UserSubscription, Transaction

# Register the OrderProduct model to manage it in the admin interface
# class OrderProductInline(admin.TabularInline):
#     model = OrderProduct
#     extra = 1  # Number of empty forms to display

# # Register the Order model
# class OrderAdmin(admin.ModelAdmin):
#     list_display = ('id', 'customer', 'order_date', 'create_date', 'total_price', 'place_order')
#     search_fields = ['customer__username', 'id']
#     list_filter = ['order_date', 'create_date']
#     inlines = [OrderProductInline]

#     def place_order(self, obj):
#         return obj.place_order()
#     place_order.short_description = 'Place Order'


# Register the SubscriptionPlan model
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'duration_days', 'price')
    search_fields = ['name']
    list_filter = ['duration_days']


# Register the UserSubscription model
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'balance', 'status', 'start_date', 'end_date')
    search_fields = ['user__email', 'plan__name']
    list_filter = ['status', 'plan__name']

    def renew_subscription(self, obj):
        obj.renew_subscription()


# Register the Transaction model
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'user', 'plan', 'amount', 'payment_status', 'created_at')
    search_fields = ['transaction_id', 'user__email', 'plan__name']
    list_filter = ['payment_status', 'created_at']


# Register the models with the admin interface
# admin.site.register(Order, OrderAdmin)
admin.site.register(SubscriptionPlan, SubscriptionPlanAdmin)
admin.site.register(UserSubscription, UserSubscriptionAdmin)
admin.site.register(Transaction, TransactionAdmin)

