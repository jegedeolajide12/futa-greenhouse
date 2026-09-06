from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

# Create your models here.
class Transaction(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    PAYMENT_METHODS = [
        ('paystack', 'Paystack'),
        ('flutterwave', 'Flutterwave'),
        ('bank', 'Bank Transfer'),
        ('cash', 'Cash'),
    ]

    transaction_id = models.CharField(max_length=50, unique=True)
    session_id = models.CharField(max_length=100, blank=True, null=True)
    payer_name = models.CharField(max_length=100, blank=True, help_text="Name of the payer (manual entry)")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='cash')
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Transactions'

    def __str__(self):
        return f"{self.transaction_id} - {self.amount}"