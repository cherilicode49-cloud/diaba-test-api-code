from django.db import models
from diabaApp import validators
from datetime import datetime
from .common_models import Role
from .product_models import ProductDetail, ProductModelVariant

class CustomerDetail(models.Model):
    email = models.CharField(max_length=200, verbose_name="User Email",  null=True)
    countryCode = models.CharField(max_length=15, verbose_name="Country Code",  null=True)
    mobileNumber = models.CharField(max_length=35, verbose_name="Mobile Number",  null=True)
    userType = models.ForeignKey(Role, null=True,verbose_name="User Role", on_delete=models.SET_NULL)
    name = models.CharField(max_length=200, verbose_name="Name", null=True)
    gender = models.CharField(max_length=200, verbose_name="gender", null=True)
    FCMToken  = models.CharField(verbose_name='FCMToken', null=True)
    deviceId  = models.CharField(max_length=100, verbose_name='deviceId', null=True)
    deviceType  = models.CharField(max_length=100, verbose_name='deviceType', null=True)
    social_token  = models.CharField( verbose_name='social_token', null=True)
    socialType  = models.CharField(verbose_name='socialType', null=True)
    ip_address  = models.CharField(verbose_name='ip address', null=True)
    country  = models.CharField(verbose_name='Country', null=True,db_index=True)
    socialType  = models.CharField(verbose_name='socialType', null=True)
    lastLoginDate  = models.CharField(max_length=100, verbose_name='Last Login Date', null=True)
    OTP = models.CharField(max_length=50, blank=True, null=True, verbose_name='OTP')
    password = models.CharField(max_length=50, blank=True, null=True, verbose_name='password')
    status = models.CharField(max_length=10, verbose_name="is User Active", default='Active', null= True)
    created_at = models.CharField(max_length=100, verbose_name="created at", null= True)
    created_at_datetime = models.DateTimeField(verbose_name="created at", null= True, blank=True, default=datetime.now())
    
     
    def __str__(self):
        # return "%s" % (self.mobileNumber)+"---ID--->"+str(self.countryCode)
        return "%s" % self.id


class CustomerLogin(models.Model):
    customer = models.ForeignKey(CustomerDetail, null=True,verbose_name="User Role", on_delete=models.SET_NULL)
    login_time = models.CharField(max_length=100, verbose_name="Login Time",  null=True)

    def __str__(self):
        return "%s" % self.id


class CustomerLoginHistory(models.Model):
    email = models.CharField(max_length=100, verbose_name="Email",  null=True)
    login_time = models.CharField(max_length=100, verbose_name="Login Time",  null=True)

    def __str__(self):
        return "%s" % self.id

class CustomerAddressDetail(models.Model):
    customer = models.ForeignKey(CustomerDetail, null=True,verbose_name="User Role", on_delete=models.SET_NULL)
    recipient_name = models.CharField(max_length=100, verbose_name="recipient_name",  null=True)
    street_address = models.CharField(max_length=250, verbose_name="street_address ",  null=True)
    city = models.CharField(max_length=100, verbose_name="city ",  null=True)
    region = models.CharField(max_length=100, verbose_name="region ",  null=True)
    postal_code = models.CharField(max_length=100, verbose_name="postal_code ",  null=True)
    country = models.CharField(max_length=100, verbose_name="country ",  null=True)
    address_type = models.CharField(max_length=100, verbose_name="address_type ",  null=True)
    mobile_number = models.CharField(max_length=100, verbose_name="mobile_number ",  null=True)
    is_default = models.CharField(max_length=100, verbose_name="is_default ",  null=True)
    created_at = models.CharField(max_length=100, verbose_name="created at", null= True)

    def __str__(self):
        return "%s" % self.id

class WishlistDetail(models.Model):
    customer = models.ForeignKey(CustomerDetail, null=True,verbose_name="User Role", on_delete=models.SET_NULL)
    product = models.ForeignKey(ProductDetail, null=True,verbose_name="ProductDetail", on_delete=models.SET_NULL)
    created_at = models.CharField(max_length=100, verbose_name="created at", null= True)

    def __str__(self):
        return "%s" % str(self.id)+'----product--->'+str(self.product)


class CartDetail(models.Model):
    customer = models.ForeignKey(CustomerDetail, null=True,verbose_name="User Role", on_delete=models.SET_NULL)
    product = models.ForeignKey(ProductDetail, null=True,verbose_name="ProductDetail", on_delete=models.SET_NULL)
    variant = models.ForeignKey(ProductModelVariant, null=True,verbose_name="ProductModelVariant", on_delete=models.SET_NULL)
    quantity = models.CharField(max_length=100, verbose_name="quantity ")
    shipping_via = models.CharField(max_length=100, verbose_name="shipping_via " , null= True)
    created_at = models.CharField(max_length=100, verbose_name="created at", null= True)

    def __str__(self):
        return "%s" % self.id

    
class RecentlyViewProduct(models.Model):
    customer = models.ForeignKey(CustomerDetail, verbose_name='CustomerDetail', blank=True, null=True, on_delete=models.CASCADE)
    product = models.ForeignKey(ProductDetail, verbose_name='Product', blank=True, null=True, on_delete=models.CASCADE)
    created_at = models.CharField(verbose_name='Created At', null=True, blank=True)

    def __str__(self):
        return "%s" % self.id

