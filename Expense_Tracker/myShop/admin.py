from django.contrib import admin
from .models import Succulent, Pot, Order, OrderItem


admin.site.register(Succulent)
admin.site.register(Pot)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    readonly_fields = ('product_name', 'product_price', 'product_type', 'quantity')
    extra = 0
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'phone', 'total_amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('phone', 'razorpay_order_id', 'payment_id')
    readonly_fields = (
        'razorpay_order_id', 'payment_id',
        'created_at', 'updated_at',
    )
    inlines = [OrderItemInline]