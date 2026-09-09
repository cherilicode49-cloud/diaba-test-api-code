from django.db import models
from diabaApp import validators
from datetime import datetime


class Country(models.Model):
    country_name = models.CharField(max_length=100, verbose_name="Role Name")
    image = models.FileField(upload_to='image/country', verbose_name='Image', null=True, blank=True,
                        validators=[validators.validate_file_extension_image])
    
    def __str__(self):
        return "%s" % self.country_name
    
class CountryMoneyNetwork(models.Model):
    country_name = models.CharField(max_length=100, verbose_name="Role Name")
    key = models.CharField(max_length=100, verbose_name="Key",null=True)
    # image = models.FileField(upload_to='image/country/network', verbose_name='Image', null=True, blank=True,
    #                     validators=[validators.validate_file_extension_image])
    
    def __str__(self):
        return "%s" % self.country_name +"---->"+ self.key


    
class MoneyNetwork(models.Model):
    country = models.ForeignKey(CountryMoneyNetwork, null=True,verbose_name="User Role", on_delete=models.CASCADE)
    label = models.CharField(max_length=100, verbose_name="Label", null=True)
    value = models.CharField(max_length=100, verbose_name="value",null=True)
    icon = models.FileField(upload_to='image/network_icon', verbose_name='icon', null=True, blank=True,
                        validators=[validators.validate_file_extension_image])
    status = models.CharField(max_length=100, verbose_name="Status", null=True, default="Inactive")
    
    def __str__(self):
        return "%s" % str(self.id)+"<--id--"+str(self.country) + '-->'+ str(self.label) + ' ' + str(self.value)
  
    
class CurrencyConverter(models.Model):
    currency_code = models.CharField(verbose_name="Currency Code", null= True, blank=True)
    system_rate = models.DecimalField(verbose_name="System Rate", null= True, blank=True, default = 0, max_digits=6, decimal_places=2)
        
    def __str__(self):
        return "%s" % str(self.id)+'--currency_code->'+str(self.currency_code)+'-system_rate->'+str(self.system_rate)

class CountryWithCurrency(models.Model):
    country_calling_code = models.CharField(max_length=100, verbose_name="Country Calling Code", null=True)
    country_name = models.CharField(max_length=100, verbose_name="Country Name", null=True)
    country_iso_alphaTwo_key= models.CharField(max_length=100, verbose_name="Country ISO Alpha-2 Key", null=True)

    currency_code = models.CharField(max_length=100, verbose_name="Currency Code", null=True)
    currency_symbol = models.CharField(max_length=100, verbose_name="Currency Symbol", null=True)

    price_by_air = models.CharField(verbose_name='price_by_air', null=True, blank=True)
    price_by_ship = models.CharField(verbose_name='price_by_ship', null=True, blank=True)
    express_shipping = models.CharField(verbose_name='express_shipping', null=True, blank=True)
    status = models.CharField(max_length=10, verbose_name="is User Active", default='Inactive', null= True)
    
    def __str__(self):
        return "%s" % str(self.currency_code)+"--country-->"+str(self.country_name)


class CountryCashLimit(models.Model):
    country = models.ForeignKey(CountryWithCurrency, null=True,verbose_name="country", on_delete=models.CASCADE)
    cash_limit = models.CharField(max_length=100, verbose_name="cash_limit",null=True)
    
    def __str__(self):
        return "%s" % self.cash_limit
  
class CountryWiseBankDetail(models.Model):
    country = models.ForeignKey(CountryWithCurrency, null=True,verbose_name="Country", on_delete=models.CASCADE)
    holder_name = models.CharField(verbose_name="Account Holder Name", null=True, blank=True)
    bank_name = models.CharField(verbose_name="Bank Name", null=True, blank=True)
    account_number = models.CharField(verbose_name="Account Number", null=True, blank=True)
    branch_name = models.CharField(verbose_name="Branch/Agency Name", null=True, blank=True)
    branch_code = models.CharField(verbose_name="Branch/Bank Code", null=True, blank=True)

    def __str__(self):
        return "%s" % str(self.id)+"<--id--"+str(self.country) + '-->'+ str(self.bank_name)

