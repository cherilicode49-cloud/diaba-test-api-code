from django.db import models
from .customer_models import CustomerDetail


class CustomerWallet(models.Model):
    customer = models.OneToOneField(CustomerDetail, on_delete=models.CASCADE, related_name='wallet', verbose_name="Customer")
    balance = models.DecimalField(max_digits=14, decimal_places=2, default=0.00, verbose_name="Wallet Balance")
    currency = models.CharField(max_length=10, default='USD', verbose_name="Base Currency")
    status = models.CharField(max_length=20, default='Active', verbose_name="Wallet Status")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")

    class Meta:
        verbose_name = "Customer Wallet"
        verbose_name_plural = "Customer Wallets"
        db_table = "diabaApp_customerwallet"

    def __str__(self):
        return f"Wallet for Customer {self.customer_id}: {self.balance} {self.currency}"


class WalletTransaction(models.Model):
    TRANSACTION_TYPES = (
        ('Credit', 'Credit'),
        ('Debit', 'Debit'),
    )

    wallet = models.ForeignKey(CustomerWallet, on_delete=models.CASCADE, related_name='transactions', verbose_name="Wallet")
    customer = models.ForeignKey(CustomerDetail, on_delete=models.CASCADE, related_name='wallet_transactions', verbose_name="Customer")
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES, verbose_name="Transaction Type")
    amount = models.DecimalField(max_digits=14, decimal_places=2, verbose_name="Amount in Base Currency")
    currency = models.CharField(max_length=10, default='USD', verbose_name="Base Currency")
    balance_before = models.DecimalField(max_digits=14, decimal_places=2, default=0.00, verbose_name="Balance Before")
    balance_after = models.DecimalField(max_digits=14, decimal_places=2, default=0.00, verbose_name="Balance After")
    source_type = models.CharField(max_length=50, default='Inquiry_Transfer', verbose_name="Source Type")
    source_id = models.CharField(max_length=100, null=True, blank=True, verbose_name="Source Reference ID")
    transaction_ref = models.CharField(max_length=100, unique=True, verbose_name="Transaction Reference")
    description = models.TextField(null=True, blank=True, verbose_name="Transaction Description")

    # Multi-currency snapshot of all system exchange rates at the time of transaction
    rates_snapshot = models.JSONField(default=dict, blank=True, verbose_name="Exchange Rates Snapshot")
    # Exact converted values in all supported currencies at the time of transaction
    locked_values = models.JSONField(default=dict, blank=True, verbose_name="Locked Currency Values")

    status = models.CharField(max_length=20, default='Success', verbose_name="Status")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")

    class Meta:
        verbose_name = "Wallet Transaction"
        verbose_name_plural = "Wallet Transactions"
        ordering = ['-created_at']
        db_table = "diabaApp_wallettransaction"

    def __str__(self):
        return f"{self.transaction_ref} - {self.transaction_type} {self.amount} {self.currency} ({self.status})"
