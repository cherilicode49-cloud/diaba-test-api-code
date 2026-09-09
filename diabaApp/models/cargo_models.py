from django.db import models
from diabaApp import validators
from datetime import datetime
from .country_models import CountryWithCurrency

class CargoDetail(models.Model):
    country = models.ForeignKey(CountryWithCurrency, verbose_name='country', blank=True, null=True, on_delete=models.CASCADE)
    cargo_name = models.CharField(verbose_name='cargo_name', null=True, blank=True)
    email = models.CharField(verbose_name='email', null=True, blank=True)
    air_express_address = models.CharField(verbose_name='air_express_address', null=True, blank=True)
    air_express_number = models.CharField(verbose_name='air_express_number', null=True, blank=True)
    air_express_postal_code = models.CharField(verbose_name='destination_cargo_address', null=True, blank=True)
    ship_address = models.CharField(verbose_name='ship_address', null=True, blank=True)
    ship_number = models.CharField(verbose_name='ship_number', null=True, blank=True)
    ship_postal_code = models.CharField(verbose_name='ship_address', null=True, blank=True)
    status = models.CharField(verbose_name='status', null=True, blank=True)
    is_cargo_for_all = models.BooleanField(verbose_name="is_cargo_for_all", null=True, blank=True, default=False)
    created_at = models.CharField(verbose_name='Created At', null=True, blank=True)

    def __str__(self):
        return "%s" % self.id

class PaymentCargoSlider(models.Model):
    banner = models.FileField(upload_to='image/PaymentCargo/image', verbose_name='banner', null=True, blank=True,
                        validators=[validators.validate_file_extension_image_and_video])
    status = models.CharField(verbose_name='status', null=True, blank=True)
    created_at = models.CharField(verbose_name='Created At', null=True, blank=True)

    def __str__(self):
        return "%s" % str(self.id)