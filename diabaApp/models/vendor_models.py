from django.db import models
from diabaApp import validators
from datetime import datetime
from .category_models import CategoryDetail, SubCategoryDetail
# from .product_models import ProductDetail, ProductModel, ProductModelVariant

class VendorDetail(models.Model):
    category = models.ForeignKey(CategoryDetail, null=True,verbose_name="CategoryDetail", on_delete=models.CASCADE)
    subcategory = models.ForeignKey(SubCategoryDetail, null=True,verbose_name="SubCategoryDetail", on_delete=models.CASCADE)
    company_name = models.CharField(max_length=200, verbose_name="company_name",  null=True)
    business_type = models.CharField(max_length=500, verbose_name="business_type",  null=True)
    legal_form = models.CharField(max_length=500, verbose_name="legal_form",  null=True)
    city = models.CharField(max_length=200, verbose_name="city", null=True)
    country = models.CharField(max_length=200, verbose_name="country", null=True)
    company_start_date = models.CharField(max_length=200, verbose_name="company_start_date", null=True)
    office_address = models.CharField(max_length=500, verbose_name="office_address", null=True)
    total_employee = models.CharField(max_length=200, verbose_name="total_employee", null=True)
    production_capacity = models.CharField(max_length=200, verbose_name="production_capacity", null=True)
    vendor_name = models.CharField(max_length=200, verbose_name="vendor_name", null=True)
    phone_number = models.CharField(max_length=200, verbose_name="phone_number", null=True)
    email = models.CharField(max_length=200, verbose_name="email", null=True)
    document_type = models.CharField(max_length=500, verbose_name="document_type", null=True)
    document = models.FileField(upload_to='image/vendorDetails/documents', verbose_name='Image image', null=True, blank=True,
                        validators=[validators.validate_file_extension_pdf])
    
    website = models.CharField(max_length=500, verbose_name="website", null=True)
    lastLoginDate  = models.CharField(max_length=100, verbose_name='Last Login Date', null=True)
    OTP = models.CharField(max_length=500, blank=True, null=True, verbose_name='OTP')
    password = models.CharField(max_length=500, blank=True, null=True, verbose_name='password')
    is_verify = models.CharField(max_length=10, verbose_name="is_verify", default='pending', null= True)
    reject_reason = models.CharField(max_length=500, verbose_name="reject_reason", null= True)
    status = models.CharField(max_length=10, verbose_name="is User Active", default='Active', null= True)
    created_at = models.CharField(max_length=100, verbose_name="created at", null= True)
    created_at_datetime = models.DateTimeField(verbose_name="created at", null= True)
    
    def __str__(self):
        return "%s" % str(self.email)+'--ID-->'+str(self.id)

class VendorAddress(models.Model):
    vendor = models.ForeignKey(VendorDetail, null=True,verbose_name="VendorDetail", on_delete=models.CASCADE)

    location_type = models.CharField(max_length=200, verbose_name="location_type",  null=True)
    description = models.CharField(max_length=500, verbose_name="description",  null=True)
    office_address = models.CharField(max_length=500, verbose_name="office_address", null=True)
    created_at = models.CharField(max_length=100, verbose_name="created at", null= True)
    
    def __str__(self):
        return "%s" % self.id

class VendorLoginHistory(models.Model):
    email = models.CharField(max_length=100, verbose_name="Email",  null=True)
    login_time = models.CharField(max_length=100, verbose_name="Login Time",  null=True)

    def __str__(self):
        return "%s" % self.id

class VendorProductPrice(models.Model):
    product = models.ForeignKey(
        "diabaApp.ProductDetail",
        null=True,
        on_delete=models.CASCADE
    )

    model = models.ForeignKey(
        "diabaApp.ProductModel",
        null=True,
        on_delete=models.CASCADE
    )

    variant = models.ForeignKey(
        "diabaApp.ProductModelVariant",
        null=True,
        on_delete=models.CASCADE
    )
    # product = models.ForeignKey(ProductDetail, null=True,verbose_name="ProductDetail", on_delete=models.CASCADE)
    # model = models.ForeignKey(ProductModel, null=True,verbose_name="Product Model", on_delete=models.CASCADE)
    vendor = models.ForeignKey(VendorDetail, null=True,verbose_name="VendorDetail", on_delete=models.CASCADE)
    # variant = models.ForeignKey(ProductModelVariant, null=True,verbose_name="ProductModelVariant", on_delete=models.CASCADE)
    price = models.CharField(max_length=100, verbose_name="price",  null=True)
    quantity = models.CharField(max_length=100, verbose_name="quantity",  null=True)
    status = models.CharField(max_length=100, verbose_name="status",  null=True, default= 'Active')
    # is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return "%s" % self.id


class VendorTransaction(models.Model):
    vendor = models.ForeignKey(VendorDetail, verbose_name='Vendor', null=True, blank=True, on_delete=models.CASCADE)
    payment_type = models.CharField(verbose_name='Payment Type', null=True, blank=True)
    currency = models.CharField(verbose_name='Currency', null=True, blank=True)
    amount = models.DecimalField(verbose_name='Amount', null=True, blank=True, decimal_places=2, max_digits=12)
    transaction_type = models.CharField(verbose_name='Transaction Type', null=True, blank=True)
    remarks = models.CharField(verbose_name='Remarks', null=True, blank=True)

    created_at = models.DateTimeField(verbose_name='Created At', null=True, blank=True)
    status =  models.CharField(verbose_name='status', null=True, blank=True)
    
    def __str__(self):
        return "%s" % str(self.id)+"--vendor-->"+str(self.vendor)+'--transaction type-->'+str(self.transaction_type)


class VendorPaymentTracker(models.Model):
    vendor = models.ForeignKey(VendorDetail, verbose_name='Vendor', null=True, blank=True, on_delete=models.SET_NULL)
    vendor_name = models.CharField(verbose_name='vendor_name', null=True, blank=True)
    vendor_email = models.CharField(verbose_name='vendor_email', null=True, blank=True)
    vendor_mobile = models.CharField(verbose_name='vendor_mobile', null=True, blank=True)
    payment_type = models.CharField(verbose_name='Payment Type', null=True, blank=True)
    currency = models.CharField(verbose_name='Currency', null=True, blank=True)
    amount = models.DecimalField(verbose_name='Amount', null=True, blank=True, decimal_places=2, max_digits=12)
    remaining_amount = models.DecimalField(verbose_name='Remaining Amount', null=True, blank=True, decimal_places=2, max_digits=12)
    description = models.CharField(verbose_name='Description', null=True, blank=True)
    created_at = models.DateTimeField(verbose_name='Created At', null=True, blank=True)

    def __str__(self):
        return "%s" % str(self.id)+"--vendor-->"+str(self.vendor)+'--amount-->'+str(self.amount)+'--payment_type-->'+str(self.payment_type)


class VendorDelayNote(models.Model):
    vendor = models.ManyToManyField(VendorDetail, verbose_name='vendor', null=True, blank=True)
    delay_note_code = models.CharField(verbose_name='delay_note_code', null=True, blank=True)
    note = models.TextField(verbose_name="note", null=True, blank=True)
    start_at = models.DateTimeField(verbose_name='Start At', null=True, blank=True)
    end_at = models.DateTimeField(verbose_name='End At', null=True, blank=True)
    created_at = models.DateTimeField(verbose_name='Created At', null=True, blank=True)
    status = models.CharField(verbose_name='Status',null=True, blank=True, default='Active')

    def __str__(self):
        return "%s" % str(self.id)+"---->"+str(self.note)

