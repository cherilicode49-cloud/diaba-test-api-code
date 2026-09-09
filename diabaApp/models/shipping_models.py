from django.db import models
from diabaApp import validators
from datetime import datetime
from .country_models import CountryWithCurrency

class DeliveryDayDetail(models.Model):
    express_delivery = models.IntegerField(verbose_name='express_delivery', null=True, blank=True)
    air_delivery = models.IntegerField(verbose_name='express_delivery', null=True, blank=True)
    ship_delivery = models.IntegerField(verbose_name='note_french', null=True, blank=True)

    def __str__(self):
        return "%s" % self.id



class DailyPrice(models.Model): #done
    country = models.ForeignKey(CountryWithCurrency, verbose_name='Country With Currency', null=True, blank = True, on_delete=models.CASCADE)
    price_by_air = models.CharField(verbose_name='price_by_air', null=True, blank=True)
    price_by_ship = models.CharField(verbose_name='price_by_ship', null=True, blank=True)

    def __str__(self):
        return "%s" % str(self.id) +"--country with currency-->"+str(self.country)

