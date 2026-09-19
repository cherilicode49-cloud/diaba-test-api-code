from django.db import models
from diabaApp import validators
from datetime import datetime


class ContainerRequest(models.Model):
    customer = models.ForeignKey('diabaApp.CustomerDetail', null=True,verbose_name="customer", on_delete=models.SET_NULL)
    departure_city = models.CharField(max_length=100)
    customer_shipping_mark = models.CharField(max_length=100)
    quantity_cbm = models.DecimalField(max_digits=10,decimal_places=2)
    weight_kg = models.DecimalField(max_digits=10,decimal_places=2)
    destination_country = models.ForeignKey('diabaApp.CountryWithCurrency',on_delete=models.SET_NULL,
        null=True,blank=True,related_name='container_requests')
    product_type = models.CharField(max_length=100)
    sponsor = models.CharField(max_length=100,blank=True,null=True)
    customer_note = models.TextField(blank=True,null=True)
    status = models.CharField(verbose_name='Status', null=True, blank=True, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.departure_city} - {self.customer_shipping_mark}"