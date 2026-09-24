from django.db import models
from diabaApp import validators
from datetime import datetime


class ContainerRequest(models.Model):
    customer = models.ForeignKey('diabaApp.CustomerDetail', null=True,verbose_name="customer", on_delete=models.SET_NULL)
    transport_type = models.CharField(max_length=100, default='sea', null=True)
    departure_city = models.CharField(max_length=100)
    customer_shipping_mark = models.CharField(max_length=100)
    quantity_cbm = models.DecimalField(max_digits=10,decimal_places=2)
    weight_kg = models.DecimalField(max_digits=10,decimal_places=2)
    destination_country = models.ForeignKey('diabaApp.CountryWithCurrency',on_delete=models.SET_NULL,
        null=True,blank=True,related_name='container_requests')
    # product_type = models.CharField(max_length=100)
    product_type = models.ManyToManyField('diabaApp.CategoryDetail',blank=True,related_name='container_requests')
    
    sponsor = models.CharField(max_length=100,blank=True,null=True)
    customer_note = models.TextField(blank=True,null=True)
    volume = models.CharField(max_length=100,blank=True,null=True)

    is_fragile = models.BooleanField(default=False, verbose_name="is_fragile", null=True)
    is_battery = models.BooleanField(default=False, verbose_name="is_battery", null=True)
    is_flammable = models.BooleanField(default=False, verbose_name="is_flammable", null=True)
    is_liquid = models.BooleanField(default=False, verbose_name="is_liquid", null=True)
    status = models.CharField(verbose_name='Status', null=True, blank=True, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.departure_city} - {self.customer_shipping_mark}"


class ContainerTerms(models.Model):
    terms_en = models.TextField(verbose_name="description_en",null=True,blank=True)
    terms_fr = models.TextField(verbose_name="description_fr",null=True,blank=True)
    status = models.CharField(max_length=100,default="active")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)