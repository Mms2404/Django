from django.db import models


# --------------------------------------------------------------------------
# Catalog
# --------------------------------------------------------------------------

class Succulent(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='succulents/')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()

    def __str__(self):
        return self.name


class Pot(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='pots/')
    material = models.CharField(max_length=100)
    height = models.CharField(max_length=20)
    width = models.CharField(max_length=20)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()

    def __str__(self):
        return self.name


# --------------------------------------------------------------------------
# Orders
# --------------------------------------------------------------------------

class Order(models.Model):
    """
    One customer order.

    Online payments:
        Created with status='pending' → updated to 'confirmed' once
        Razorpay payment is verified (via /verify/ or webhook, whichever lands first).

    Cash on delivery:
        Created directly with status='pending_cod'. No Razorpay involvement.
        Admin changes status to 'confirmed' manually after physical collection.
    """

    STATUS_CHOICES = [
        ('pending',     'Pending'),          # online order, payment not yet confirmed
        ('pending_cod', 'Pending COD'),      # COD order placed, not yet collected
        ('confirmed',   'Confirmed'),        # payment verified / admin confirmed COD
        ('shipped',     'Shipped'),
        ('delivered',   'Delivered'),
        ('cancelled',   'Cancelled'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('online', 'Online (Razorpay)'),
        ('cod',    'Cash on Delivery'),
    ]

    phone    = models.CharField(max_length=15, db_index=True)
    address  = models.TextField()
    latitude  = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    # Only set for online orders.
    razorpay_order_id = models.CharField(max_length=100, db_index=True, blank=True)
    payment_id        = models.CharField(max_length=100, blank=True)

    # NEW — which payment method the customer chose.
    payment_method = models.CharField(
        max_length=10,
        choices=PAYMENT_METHOD_CHOICES,
        default='online',
    )

    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='pending'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Order #{self.id} ({self.phone}, {self.status})'


class OrderItem(models.Model):
    """
    A line in an order. Stores SNAPSHOT product info so future price changes
    or product deletions don't retroactively rewrite history.
    """

    PRODUCT_TYPE_CHOICES = [
        ('succulent', 'Succulent'),
        ('pot',       'Pot'),
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')

    product_name  = models.CharField(max_length=100)
    product_price = models.DecimalField(max_digits=10, decimal_places=2)
    product_type  = models.CharField(max_length=20, choices=PRODUCT_TYPE_CHOICES)
    quantity      = models.PositiveIntegerField(default=1)

    @property
    def line_total(self):
        return self.product_price * self.quantity

    def __str__(self):
        return f'{self.product_name} × {self.quantity}'
