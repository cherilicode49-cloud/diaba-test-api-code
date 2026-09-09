from django.db import models
from diabaApp import validators
from datetime import datetime
from .customer_models import CustomerDetail, CustomerAddressDetail

class ProductInquiry(models.Model):
    transaction = models.ForeignKey('diabaApp.ProductRequestTransaction', null=True,verbose_name="Transaction", on_delete=models.CASCADE)
    customer = models.ForeignKey(CustomerDetail, verbose_name='CustomerDetail', blank=True, null=True, on_delete=models.CASCADE)
    inquiry_code = models.CharField(verbose_name='inquiry_code', null=True, blank=True)

    product_name = models.CharField(verbose_name='product_name', null=True, blank=True)
    description = models.TextField(verbose_name='description', null=True, blank=True)
    quantity = models.IntegerField(verbose_name='quantity', null=True, blank=True)
    created_at = models.DateTimeField(verbose_name='Created At', null=True, blank=True)

    status = models.CharField(verbose_name='Status', null=True, blank=True, default='Pending')

    def __str__(self):
        return "%s" % self.id
    
class ProductInquiryImages(models.Model):
    inquiry = models.ForeignKey(ProductInquiry, verbose_name='Product Inquiry', null=True, blank=True, on_delete=models.CASCADE)
    image = models.FileField(upload_to='image/productInquiry/image', verbose_name='Product Inquiry Image', null=True, blank=True,
                        validators=[validators.validate_file_extension_image])

    def __str__(self):
        return "%s" % self.id


class ProductRequestTransaction(models.Model):
    customer = models.ForeignKey('diabaApp.CustomerDetail', null=True,verbose_name="customer", on_delete=models.SET_NULL)
    payment_type = models.CharField(max_length=100, verbose_name="payment_type", null=True)    
    payment_id = models.CharField(max_length=100, verbose_name="payment_id", null=True)
    reference_id = models.CharField(max_length=100, verbose_name="reference_id", null=True)
    total_amount = models.CharField(max_length=100, verbose_name="total_amount", null=True)
    currency = models.CharField(max_length=100, verbose_name="payment currency", null=True)
    status = models.CharField(max_length=100, verbose_name="status ")
    created_at = models.CharField(max_length=100, verbose_name="created at", null= True)

    def __str__(self):
        return "%s" % self.id    
