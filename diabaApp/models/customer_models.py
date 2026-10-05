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


class UserActivity(models.Model):
    ACTION_CHOICES = [
        ('PRODUCT_VIEW', 'Product View'),
        ('PRODUCT_WISHLIST', 'Product Wishlist'),
        ('ADD_TO_CART', 'Add to Cart'),
        ('REMOVE_FROM_CART', 'Remove from Cart'),
        ('SEARCH', 'Search Query'),
        ('CATEGORY_VIEW', 'Category View'),
        ('CHECKOUT_INITIATE', 'Checkout Initiate'),
        ('PAYMENT_METHOD_SELECT', 'Payment Method Select'),
        ('ORDER_PLACED', 'Order Placed'),
        ('BANNER_CLICK', 'Banner Click'),
        ('APP_OPEN', 'App Open'),
    ]

    customer = models.ForeignKey(CustomerDetail, null=True, blank=True, on_delete=models.SET_NULL, related_name='user_activities')
    action_type = models.CharField(max_length=50, choices=ACTION_CHOICES, db_index=True)

    # Product details (stored as text/id to preserve history even after product deletion)
    product_id = models.CharField(max_length=100, null=True, blank=True, db_index=True)
    product_name = models.CharField(max_length=255, null=True, blank=True, db_index=True)

    # Payment details
    payment_method = models.CharField(max_length=100, null=True, blank=True, db_index=True)

    # Search & Category
    search_keyword = models.CharField(max_length=255, null=True, blank=True)
    category_name = models.CharField(max_length=255, null=True, blank=True)

    # Metadata dictionary for flexible extra properties
    metadata = models.JSONField(null=True, blank=True, default=dict)

    # Device & client info (optional)
    device_id = models.CharField(max_length=150, null=True, blank=True)
    device_type = models.CharField(max_length=50, null=True, blank=True)
    ip_address = models.CharField(max_length=50, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=['action_type', 'created_at']),
            models.Index(fields=['customer', 'action_type']),
            models.Index(fields=['product_name', 'action_type']),
            models.Index(fields=['payment_method', 'created_at']),
        ]
        verbose_name = 'User Activity'
        verbose_name_plural = 'User Activities'

    def __str__(self):
        user_id = self.customer.name if (self.customer and self.customer.name) else (self.customer_id or self.device_id or 'Guest')
        return f"{user_id} - {self.action_type} ({self.created_at})"


