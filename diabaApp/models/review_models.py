from django.db import models
from diabaApp import validators
from datetime import datetime
from .customer_models import CustomerDetail, CustomerAddressDetail
from .product_models import ProductDetail


class ProductReview(models.Model):
    customer = models.ForeignKey(CustomerDetail, verbose_name='CustomerDetail', blank=True, null=True, on_delete=models.CASCADE)
    product = models.ForeignKey(ProductDetail, verbose_name='Product', blank=True, null=True, on_delete=models.CASCADE)
    customer_name = models.CharField(verbose_name='customer_name', null=True, blank=True)
    rating = models.IntegerField(verbose_name='rating', null=True, blank=True)
    review = models.TextField(verbose_name='review', null=True, blank=True)
    
    created_at = models.CharField(verbose_name='Created At', null=True, blank=True)
 
    def __str__(self):
        return "%s" % self.id
