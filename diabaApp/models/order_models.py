from django.db import models
from diabaApp import validators
from datetime import datetime
# from .customer_models import CustomerDetail, CustomerAddressDetail
# from .product_models import ProductDetail, ProductModelVariant
# from .vendor_models import VendorDetail
# from .cargo_models import CargoDetail
# from .influencer_models import PromocodeDetail
# from .warehouse_models import WarehouseDetail

class OrderDetail(models.Model):
    customer = models.ForeignKey('diabaApp.CustomerDetail', null=True,verbose_name="customer", on_delete=models.SET_NULL)
    promocode = models.ForeignKey('diabaApp.PromocodeDetail', null=True, on_delete=models.SET_NULL)
    customer_address = models.ForeignKey('diabaApp.CustomerAddressDetail', null=True,verbose_name="CustomerAddressDetail", on_delete=models.SET_NULL)
    cargo = models.ForeignKey('diabaApp.CargoDetail', null=True,verbose_name="CargoDetail", on_delete=models.SET_NULL)
    order_id = models.CharField(max_length=100, verbose_name="order_id ")
    payment_type = models.CharField(max_length=100, verbose_name="payment_type", null=True)
    payment_id = models.CharField(max_length=100, verbose_name="payment_id", null=True, blank=True)
    order_status = models.CharField(max_length=100, verbose_name="order_status", null=True)
    air_shipping_price = models.CharField(max_length=100, verbose_name="air_shipping_price", null=True)
    ship_shipping_price = models.CharField(max_length=100, verbose_name="ship_shipping_price", null=True)
    express_shipping_price = models.CharField(max_length=100, verbose_name="express_shipping_price", null=True)
    total_price = models.BigIntegerField(verbose_name="total_price", blank=True, null=True)
    original_amount_paid = models.CharField(max_length=100, verbose_name="original_amount_paid", null=True, blank=True)
    original_total_amount = models.CharField(max_length=100, verbose_name="original_total_amount", null=True)
    discount_price = models.CharField(max_length=100, verbose_name="discount_price", null=True)
    tax_price = models.CharField(max_length=100, verbose_name="tax_price", null=True)
    currency = models.CharField(max_length=100, verbose_name="payment currency", null=True)
    currency_name = models.CharField(max_length=100, verbose_name="currency_name", null=True)
    invoice = models.FileField(upload_to='image/invoice', verbose_name='invoice', null=True, blank=True,
                        validators=[validators.validate_file_extension_pdf]) 
    status = models.CharField(max_length=100, verbose_name="status", null=True)
    order_from = models.CharField(max_length=100, verbose_name="order_from", null=True, default='App')
    is_order_track = models.BooleanField(default=False, verbose_name="is_order_track", null=True)
    
    created_at = models.DateTimeField(verbose_name="created at",auto_now_add=True, null= True)
    expire_at = models.DateTimeField(verbose_name='Expire At', null=True, blank=True)

    def __str__(self):
        return "%s" % self.id +"-->--> "+ str(self.customer )

class OrderPaymentReceivingBankDetail(models.Model):
    order = models.ForeignKey(OrderDetail, null=True,verbose_name="OrderDetail", on_delete=models.CASCADE)
    holder_name = models.CharField(verbose_name="Account Holder Name", null=True, blank=True)
    bank_name = models.CharField(verbose_name="Bank Name", null=True, blank=True)
    account_number = models.CharField(verbose_name="Account Number", null=True, blank=True)
    branch_name = models.CharField(verbose_name="Branch/Agency Name", null=True, blank=True)
    branch_code = models.CharField(verbose_name="Branch/Bank Code", null=True, blank=True)

    def __str__(self):
        return "%s" % str(self.id)+"<--id--"+"--ORDER ID-->"+str(self.order)+ '-->'+ str(self.bank_name)


class ProductOrderDetail(models.Model):
    order = models.ForeignKey(OrderDetail, null=True,verbose_name="OrderDetail", on_delete=models.CASCADE)
    product = models.ForeignKey('diabaApp.ProductDetail', null=True,verbose_name="ProductDetail", on_delete=models.SET_NULL)
    variant = models.ForeignKey('diabaApp.ProductModelVariant', null=True,verbose_name="ProductModelVariant", on_delete=models.SET_NULL)
    warehouse = models.ForeignKey('diabaApp.WarehouseDetail', null=True,verbose_name="WarehouseDetail", on_delete=models.SET_NULL)
    quantity = models.IntegerField(verbose_name="quantity ")
    price = models.CharField(max_length=100, verbose_name="price", null=True)
    total_price = models.CharField(max_length=100, verbose_name="total_price")
    vendor_price = models.IntegerField(verbose_name="vendor price", null=True)
    total_vendor_price = models.IntegerField(verbose_name="total vendor price", null=True, blank=True)
    currency = models.CharField(max_length=100, verbose_name="payment currency", null=True)
    currency_name = models.CharField(max_length=100, verbose_name="payment currency name", null=True)
    product_shipping_price = models.CharField(max_length=100, verbose_name="product_shipping_price", null=True)
    shipping_via = models.CharField(max_length=100, verbose_name="shipping_via", null=True)
    container_id = models.CharField(max_length=100, verbose_name="container_id", null=True)
    status = models.CharField(max_length=100, verbose_name="status", null=True)
    vendor_status = models.CharField(max_length=100, verbose_name="vendor_status", null=True)
    created_at = models.DateTimeField(max_length=100, verbose_name="created at",auto_now_add=True, null= True)

    def __str__(self):
        return "%s" % str(self.id)+"---->"+str(self.shipping_via)+"---order_status-->"+str(self.order.order_status)+"---order_id-->"+str(self.order.order_id)



class VendorOrderDetail(models.Model):
    order = models.ForeignKey(OrderDetail, null=True,verbose_name="OrderDetail", on_delete=models.SET_NULL, blank=True)
    variant = models.ForeignKey(ProductOrderDetail, null=True,verbose_name="variant", on_delete=models.CASCADE, blank=True)
    vendor = models.ForeignKey('diabaApp.VendorDetail', null=True,verbose_name="vendor", on_delete=models.SET_NULL, blank=True)
    created_at = models.DateTimeField(max_length=100, verbose_name="created at", auto_now_add=True, null= True, blank=True)

    def __str__(self):
        return "%s" % self.id

class VendorOrderTracking(models.Model):
    order = models.ForeignKey(OrderDetail, null=True,verbose_name="OrderDetail", on_delete=models.SET_NULL)
    variant = models.ForeignKey(ProductOrderDetail, null=True,verbose_name="variant", on_delete=models.CASCADE)
    status = models.CharField(max_length=100, verbose_name="quantity ")
    created_at = models.CharField(max_length=100, verbose_name="created at", null= True)

    def __str__(self):
        return "%s" % self.id


class OrderTracking(models.Model):
    order = models.ForeignKey(OrderDetail, null=True,verbose_name="OrderDetail", on_delete=models.SET_NULL)
    variant = models.ForeignKey(ProductOrderDetail, null=True,verbose_name="variant", on_delete=models.CASCADE)
    status = models.CharField(max_length=100, verbose_name="quantity ")
    created_at = models.CharField(max_length=100, verbose_name="created at", null= True)

    def __str__(self):
        return "%s" % self.id

class OrderTransaction(models.Model):
    order = models.ForeignKey(OrderDetail, null=True,verbose_name="OrderDetail", on_delete=models.CASCADE)
    customer = models.ForeignKey('diabaApp.CustomerDetail', null=True,verbose_name="customer", on_delete=models.SET_NULL)
    payment_type = models.CharField(max_length=100, verbose_name="payment_type", null=True)
    cash_status = models.CharField(max_length=100, verbose_name="cash_status", null=True)
    payment_id = models.CharField(max_length=100, verbose_name="payment_id", null=True)
    reference_id = models.CharField(max_length=100, verbose_name="reference_id", null=True)
    fee_amount = models.CharField(max_length=100, verbose_name="fee_amount", null=True)
    net_amount = models.CharField(max_length=100, verbose_name="net_amount", null=True)
    total_amount = models.CharField(max_length=100, verbose_name="total_amount", null=True)
    tax_price = models.CharField(max_length=100, verbose_name="tax_price", null=True)
    currency = models.CharField(max_length=100, verbose_name="payment currency", null=True)
    status = models.CharField(max_length=100, verbose_name="status ")
    created_at = models.CharField(max_length=100, verbose_name="created at", null= True)

    def __str__(self):
        return "%s" % self.id    

