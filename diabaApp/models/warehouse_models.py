
from django.db import models
from diabaApp import validators
from datetime import datetime


class WarehouseDetail(models.Model):
    name = models.CharField(max_length=100)
    contact_person = models.CharField(max_length=50, null=True)
    phone = models.CharField(max_length=20, blank=True)
    alternate_phone = models.CharField(max_length=50, null=True)

    province = models.CharField(max_length=50, null=True)
    city = models.CharField(max_length=50, null=True)
    district = models.CharField(max_length=50, null=True)
    street = models.CharField(max_length=200, null=True)    
    building = models.CharField(max_length=50, blank=True, null=True)  
    unit = models.CharField(max_length=50, blank=True, null=True)      
    room = models.CharField(max_length=50, blank=True, null=True)      
    postal_code = models.CharField(max_length=15)
    country = models.CharField(max_length=50, blank=True, null=True)      
    location_link = models.CharField(max_length=50, blank=True, null=True)      
    status = models.CharField(max_length=50, blank=True, null=True)      

    def __str__(self):
        return self.name
