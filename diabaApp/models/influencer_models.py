from django.db import models
from diabaApp import validators
from datetime import datetime
from .customer_models import CustomerDetail

class InfluencerDetail(models.Model):
    email = models.CharField(max_length=200, verbose_name="User Email",  null=True)
    countryCode = models.CharField(max_length=15, verbose_name="Country Code",  null=True)
    mobileNumber = models.CharField(max_length=35, verbose_name="Mobile Number",  null=True)
    name = models.CharField(max_length=200, verbose_name="Name", null=True)
    commission  = models.CharField(verbose_name='Commission', null=True)
    country = models.CharField(max_length=50, blank=True, null=True)      
    prefer_currency = models.CharField(max_length=50, blank=True, null=True)      
    password = models.CharField(max_length=50, blank=True, null=True, verbose_name='password')
    status = models.CharField(max_length=10, verbose_name="is User Active", default='Active', null= True)
    created_at = models.CharField(max_length=100, verbose_name="created at", null= True)
    
    
    def __str__(self):
        return "%s" % str(self.name) 

class PromocodeDetail(models.Model):
    influencer = models.ForeignKey(InfluencerDetail, blank=True, null=True, on_delete=models.CASCADE)
    promocode = models.CharField(max_length=200, verbose_name="promocode",  null=True)
    no_of_promocode = models.CharField(max_length=35, verbose_name="no_of_promocode",  null=True)
    remaining_promocode = models.CharField(max_length=35, verbose_name="remaining_promocode",  null=True)
    expiry_date = models.CharField(max_length=200, verbose_name="expiry_date", null=True)
    discount  = models.CharField(verbose_name='discount', null=True)
    status = models.CharField(max_length=10, verbose_name="is User Active", default='Active', null= True)
    created_at = models.CharField(max_length=100, verbose_name="created at", null= True)
    
    
    def __str__(self):
        return "%s" % str(self.promocode) 


class PromocodeTracking(models.Model):
    order = models.ForeignKey(
        "diabaApp.OrderDetail",
        null=True,
        on_delete=models.SET_NULL
    )
    # order = models.ForeignKey(OrderDetail, null=True,verbose_name="OrderDetail", on_delete=models.SET_NULL)
    promocode = models.ForeignKey(PromocodeDetail, null=True,verbose_name="variant", on_delete=models.CASCADE)
    customer = models.ForeignKey(CustomerDetail, null=True,verbose_name="customer", on_delete=models.SET_NULL)
    created_at = models.CharField(max_length=100, verbose_name="created at", null= True)

    def __str__(self):
        return "%s" % self.id


class PromocodeCommissionDetail(models.Model):
    order = models.ForeignKey(
        "diabaApp.OrderDetail",
        null=True,
        on_delete=models.SET_NULL
    )
    # order = models.ForeignKey(OrderDetail, null=True,verbose_name="OrderDetail", on_delete=models.SET_NULL)
    promocode = models.ForeignKey(PromocodeDetail, null=True,verbose_name="variant", on_delete=models.CASCADE)
    original_currency = models.CharField(max_length=100, verbose_name="original_currency",null=True,)
    original_total_amount = models.CharField(max_length=100, verbose_name="original_total_amount",null=True,)
    original_amount_paid = models.CharField(max_length=100, verbose_name="original_amount_paid",null=True,)
    converted_currency = models.CharField(max_length=100, verbose_name="converted_currency",null=True,)
    converted_total_amount = models.CharField(max_length=100, verbose_name="converted_total_amount",null=True,)
    converted_amount_paid = models.CharField(max_length=100, verbose_name="converted_amount_paid",null=True,)
    commission_percentage = models.CharField(max_length=100, verbose_name="commission_percentage",null=True,)
    total_commission = models.CharField(max_length=100, verbose_name="total_commission",null=True,)
    created_at = models.CharField(max_length=100, verbose_name="created at", null= True)

    def __str__(self):
        return "%s" % self.id

