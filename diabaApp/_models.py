from django.db import models
from diabaApp import validators
from datetime import datetime

# Create your models here.

class AboutUs(models.Model): #done
    about_us = models.TextField(verbose_name='About US', null=True, blank=True)

    def __str__(self):
        return "%s" % str(self.id)+'--About Us-->'+str(self.about_us)
    
class PrivacyPolicy(models.Model): #done
    privacy_policy = models.TextField(verbose_name='Privacy Policy', null=True, blank=True)

    def __str__(self):
        return "%s" % str(self.id)+'--Privacy Policy-->'+str(self.privacy_policy)
    
class RefundPolicy(models.Model):#done
    refund_policy = models.TextField(verbose_name='Refund Policy', null=True, blank=True)

    def __str__(self):
        return "%s" % str(self.id)+'--Refund Policy-->'+str(self.refund_policy)
    
class TermsAndCondition(models.Model):#done
    terms_and_condition = models.TextField(verbose_name='Terms And Condition', null=True, blank=True)

    def __str__(self):
        return "%s" % str(self.id)+'--Terms And Condition-->'+str(self.terms_and_condition)

class AppDynamicSetting(models.Model):#done
    app_version = models.CharField(max_length=2000,verbose_name='App Version', null=True, blank=True)
    release_note = models.TextField(max_length=2000,verbose_name='Release Note', null=True, blank=True)

    def __str__(self):
        return "%s" % str(self.id)
    

class Role(models.Model):#done
    # roleID = models.BigIntegerField(verbose_name="Role id ")
    roleName = models.CharField(max_length=100, verbose_name="Role Name")

    def __str__(self):
        return "%s" % self.roleName


class Country(models.Model):#done
    country_name = models.CharField(max_length=100, verbose_name="Role Name")
    image = models.FileField(upload_to='image/country', verbose_name='Image', null=True, blank=True,
                        validators=[validators.validate_file_extension_image])
    
    def __str__(self):
        return "%s" % self.country_name
    
class CountryMoneyNetwork(models.Model):#done
    country_name = models.CharField(max_length=100, verbose_name="Role Name")
    key = models.CharField(max_length=100, verbose_name="Key",null=True)
    # image = models.FileField(upload_to='image/country/network', verbose_name='Image', null=True, blank=True,
    #                     validators=[validators.validate_file_extension_image])
    
    def __str__(self):
        return "%s" % self.country_name +"---->"+ self.key


    
class MoneyNetwork(models.Model):#done
    country = models.ForeignKey(CountryMoneyNetwork, null=True,verbose_name="User Role", on_delete=models.CASCADE)
    label = models.CharField(max_length=100, verbose_name="Label", null=True)
    value = models.CharField(max_length=100, verbose_name="value",null=True)
    icon = models.FileField(upload_to='image/network_icon', verbose_name='icon', null=True, blank=True,
                        validators=[validators.validate_file_extension_image])
    status = models.CharField(max_length=100, verbose_name="Status", null=True, default="Inactive")
    
    def __str__(self):
        return "%s" % str(self.id)+"<--id--"+str(self.country) + '-->'+ str(self.label) + ' ' + str(self.value)
  
    
class CurrencyConverter(models.Model):#done
    currency_code = models.CharField(verbose_name="Currency Code", null= True, blank=True)
    system_rate = models.DecimalField(verbose_name="System Rate", null= True, blank=True, default = 0, max_digits=6, decimal_places=2)
        
    def __str__(self):
        return "%s" % str(self.id)+'--currency_code->'+str(self.currency_code)+'-system_rate->'+str(self.system_rate)

class CountryWithCurrency(models.Model):#done
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


class CountryCashLimit(models.Model):#done
    country = models.ForeignKey(CountryWithCurrency, null=True,verbose_name="country", on_delete=models.CASCADE)
    cash_limit = models.CharField(max_length=100, verbose_name="cash_limit",null=True)
    
    def __str__(self):
        return "%s" % self.cash_limit
  
class CountryWiseBankDetail(models.Model): #done
    country = models.ForeignKey(CountryWithCurrency, null=True,verbose_name="Country", on_delete=models.CASCADE)
    holder_name = models.CharField(verbose_name="Account Holder Name", null=True, blank=True)
    bank_name = models.CharField(verbose_name="Bank Name", null=True, blank=True)
    account_number = models.CharField(verbose_name="Account Number", null=True, blank=True)
    branch_name = models.CharField(verbose_name="Branch/Agency Name", null=True, blank=True)
    branch_code = models.CharField(verbose_name="Branch/Bank Code", null=True, blank=True)

    def __str__(self):
        return "%s" % str(self.id)+"<--id--"+str(self.country) + '-->'+ str(self.bank_name)


class ModuleDetail(models.Model):#done
    module = models.CharField(max_length=100, verbose_name="module")

    def __str__(self):
        return "%s" % self.module


class AdminDetail(models.Model):#done
    email = models.CharField(max_length=200, verbose_name="User Email",  null=True)
    countryCode = models.CharField(max_length=15, verbose_name="Country Code",  null=True)
    mobileNumber = models.CharField(max_length=35, verbose_name="Mobile Number",  null=True)
    userType = models.ForeignKey(Role, related_name="role", null=True,verbose_name="User Role", on_delete=models.CASCADE, default="2")
    name = models.CharField(max_length=200, verbose_name="Name", null=True)
    lastLoginDate  = models.CharField(max_length=100, verbose_name='Last Login Date', null=True)
    OTP = models.CharField(max_length=50, blank=True, null=True, verbose_name='OTP')
    password = models.CharField(max_length=50, blank=True, null=True, verbose_name='password')
    status = models.CharField(max_length=10, verbose_name="is User Active", default='Active', null= True)
    created_at = models.CharField(max_length=100, verbose_name="created at", null= True)
     
    def __str__(self):
        return "%s" % self.email


class AdminModuleRightsDetail(models.Model):#done
    admin = models.ForeignKey(AdminDetail, null=True,verbose_name="admin", on_delete=models.CASCADE, blank=True)
    module_name = models.CharField(max_length=100, verbose_name="module_name")
    view = models.BooleanField(verbose_name='view', null=True, blank=True, default=False)
    create = models.BooleanField(verbose_name='create', null=True, blank=True, default=False)
    update = models.BooleanField(verbose_name='update', null=True, blank=True, default=False)
    delete = models.BooleanField(verbose_name='delete', null=True, blank=True, default=False)
    last_update = models.CharField(max_length=100, verbose_name="last_update", null= True)

    def __str__(self):
        return "%s" % self.id


class ChatAgentDetail(models.Model):#done
    email = models.CharField(max_length=200, verbose_name="User Email",  null=True, blank=True)
    countryCode = models.CharField(max_length=15, verbose_name="Country Code",  null=True, blank=True)
    mobileNumber = models.CharField(max_length=35, verbose_name="Mobile Number",  null=True, blank=True)
    userType = models.ForeignKey(Role, null=True,verbose_name="User Role", on_delete=models.CASCADE, blank=True)
    agent_type = models.CharField(verbose_name="Agent Type", null=True, blank=True, default = "junior")
    name = models.CharField(max_length=200, verbose_name="Name", null=True, blank=True)
    is_verified = models.BooleanField(verbose_name='Is Verified', null=True, blank=True, default=False)
    lastLoginDate  = models.DateTimeField(max_length=100, verbose_name='Last Login Date', null=True, blank=True)
    OTP = models.CharField(max_length=50, blank=True, null=True, verbose_name='OTP')
    password = models.CharField(max_length=50, blank=True, null=True, verbose_name='password')
    status = models.CharField(max_length=10, verbose_name="is User Active", default='Active', null= True, blank=True)
    created_at = models.DateTimeField(max_length=100, verbose_name="created at", null= True, blank=True)
     
    def __str__(self):
        return "%s" % str(self.email)+"--ID--->"+str(self.id)


class CategoryDetail(models.Model):#done
    category = models.CharField(max_length=100, verbose_name="category",  null=True)
    category_french = models.CharField(max_length=100, verbose_name="category_french",  null=True)
    image = models.FileField(upload_to='image/category', verbose_name='Image', null=True, blank=True,
                        validators=[validators.validate_file_extension_image])
    status = models.CharField(max_length=100, verbose_name="status",  null=True)

    def __str__(self):
        return "%s" % self.category

class SubCategoryDetail(models.Model):#done
    category = models.ForeignKey(CategoryDetail, null=True,verbose_name="category", on_delete=models.CASCADE)
    subcategory = models.CharField(max_length=100, verbose_name="subcategory",  null=True)
    subcategory_french = models.CharField(max_length=100, verbose_name="subcategory_french",  null=True)
    image = models.FileField(upload_to='image/subCategory', verbose_name='Image', null=True, blank=True,
                        validators=[validators.validate_file_extension_image])
    status = models.CharField(max_length=100, verbose_name="status",  null=True)

    def __str__(self):
        return "%s" % self.id


class SuperSubCategoryDetail(models.Model):#done
    category = models.ForeignKey(CategoryDetail, null=True,verbose_name="CategoryDetail", on_delete=models.CASCADE)
    subcategory = models.ForeignKey(SubCategoryDetail, null=True,verbose_name="SubCategoryDetail", on_delete=models.CASCADE)
    super_subcategory = models.CharField(max_length=100, verbose_name="subcategory",  null=True)
    image = models.FileField(upload_to='image/superSubCategory', verbose_name='Image', null=True, blank=True,
                        validators=[validators.validate_file_extension_image])
    status = models.CharField(max_length=100, verbose_name="status",  null=True)

    def __str__(self):
        return "%s" % self.id


class VendorDetail(models.Model):#done
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

class VendorAddress(models.Model):#done
    vendor = models.ForeignKey(VendorDetail, null=True,verbose_name="VendorDetail", on_delete=models.CASCADE)

    location_type = models.CharField(max_length=200, verbose_name="location_type",  null=True)
    description = models.CharField(max_length=500, verbose_name="description",  null=True)
    office_address = models.CharField(max_length=500, verbose_name="office_address", null=True)
    created_at = models.CharField(max_length=100, verbose_name="created at", null= True)
    
    def __str__(self):
        return "%s" % self.id

class VendorLoginHistory(models.Model):#done
    email = models.CharField(max_length=100, verbose_name="Email",  null=True)
    login_time = models.CharField(max_length=100, verbose_name="Login Time",  null=True)

    def __str__(self):
        return "%s" % self.id


class ProductCountry(models.Model):#done
    name = models.CharField(max_length=100, verbose_name="name",  null=True)
    name_french = models.CharField(max_length=100, verbose_name="name_french",  null=True)
    countryCode = models.CharField(max_length=100, verbose_name="country_code",  null=True)

    def __str__(self):
        return "%s" % str(self.id)+'---->'+str(self.name)

class ProductTag(models.Model):#done
    category = models.ForeignKey(CategoryDetail, null=True,verbose_name="category", on_delete=models.CASCADE)
    tag = models.CharField(max_length=100, verbose_name="tag",  null=True)
    
    def __str__(self):
        return "%s" % str(self.id)+"======>"+str(self.tag)

class ProductType(models.Model):#done
    product_type = models.CharField(max_length=100, verbose_name="product_type",  null=True)
    def __str__(self):
        return "%s" % str(self.id)+"======>"+str(self.product_type)


class ProductPackagingBy(models.Model):#done
    product_packaging = models.CharField(max_length=100, verbose_name="product_packaging",  null=True)
    def __str__(self):
        return "%s" % str(self.id)+"======>"+str(self.product_packaging)

class ProductDetail(models.Model): #done
    product_name = models.CharField( verbose_name="product_name",  null=True)
    product_name_french = models.CharField( verbose_name="product_name_french",  null=True)
    product_code = models.CharField( verbose_name="product_code",  null=True)
    vendor = models.ForeignKey(VendorDetail, null=True,verbose_name="VendorDetail", on_delete=models.CASCADE, blank=True)
    category = models.ForeignKey(CategoryDetail, null=True,verbose_name="CategoryDetail", on_delete=models.CASCADE)
    subcategory = models.ForeignKey(SubCategoryDetail, null=True,verbose_name="SubCategoryDetail", on_delete=models.CASCADE)
    product_type = models.ForeignKey(ProductType, null=True,verbose_name="ProductType", on_delete=models.SET_NULL)
    product_packaging = models.ForeignKey(ProductPackagingBy, null=True,verbose_name="ProductPackagingBy", on_delete=models.SET_NULL)
    product_packaging_value = models.CharField( verbose_name="width",  null=True, blank=True)
    # super_subcategory = models.ForeignKey(SuperSubCategoryDetail, null=True,verbose_name="SubCategoryDetail", on_delete=models.CASCADE)
    country_of_origin = models.ForeignKey(Country, null=True,verbose_name="SubCategoryDetail", on_delete=models.CASCADE, default= 2)
    available_country = models.ManyToManyField(ProductCountry, null=True,verbose_name="available_country", blank=True)
    tag = models.ManyToManyField(ProductTag, null=True,verbose_name="tag", blank=True)
    description = models.TextField(verbose_name="description", null=True,blank=True) 
    description_french = models.TextField(verbose_name="description", null=True,blank=True) 
    unit_of_measure = models.CharField( verbose_name="unit_of_measure",  null=True)
    material = models.CharField( verbose_name="material",  null=True, blank=True)
    length = models.CharField( verbose_name="length",  null=True, blank=True)
    height = models.CharField( verbose_name="height",  null=True, blank=True)
    width = models.CharField( verbose_name="width",  null=True, blank=True)
    weight = models.CharField( verbose_name="weight",  null=True, blank=True)
    color = models.CharField( verbose_name="color",  null=True, blank=True)
    
    # syncWithDimensions = models.CharField( verbose_name="syncWithDimensions",  null=True)
    carton_length = models.CharField( verbose_name="carton_length",  null=True)
    carton_width = models.CharField( verbose_name="carton_width",  null=True)
    carton_height = models.CharField( verbose_name="carton_height",  null=True)
    carton_weight = models.CharField( verbose_name="carton_weight",  null=True)
    # syncWithModelOrVariant = models.CharField( verbose_name="syncWithModelOrVariant",  null=True)

    available_quantity = models.CharField( verbose_name="available_quantity",  null=True)
    quantity = models.CharField( verbose_name="quantity",  null=True)
    min_order_quantity = models.CharField( verbose_name="min_order_quantity",  null=True, blank=True)
    max_order_quantity = models.CharField( verbose_name="max_order_quantity",  null=True, blank=True)
    product_image_1 = models.FileField(upload_to='image/product/image', verbose_name='product_image_1', null=True, blank=True,
                        validators=[validators.validate_file_extension_image])
    product_image_2 = models.FileField(upload_to='image/product/image', verbose_name='product_image_2', null=True, blank=True,
                        validators=[validators.validate_file_extension_image])
    product_image_3 = models.FileField(upload_to='image/product/image', verbose_name='product_image_3', null=True, blank=True,
                        validators=[validators.validate_file_extension_image])
    product_image_4 = models.FileField(upload_to='image/product/image', verbose_name='product_image_4', null=True, blank=True,
                        validators=[validators.validate_file_extension_image])
    product_image_5 = models.FileField(upload_to='image/product/image', verbose_name='product_image_5', null=True, blank=True,
                        validators=[validators.validate_file_extension_image])
    product_image_6 = models.FileField(upload_to='image/product/image', verbose_name='product_image_6', null=True, blank=True,
                        validators=[validators.validate_file_extension_image])
    product_image_7 = models.FileField(upload_to='image/product/image', verbose_name='product_image_7', null=True, blank=True,
                        validators=[validators.validate_file_extension_image])
    product_image_8 = models.FileField(upload_to='image/product/image', verbose_name='product_image_8', null=True, blank=True,
                        validators=[validators.validate_file_extension_image])
    product_video = models.FileField(upload_to='image/product/video', verbose_name='product_video', null=True, blank=True,
                        validators=[validators.validate_file_extension_video])
    product_image_1_vector = models.JSONField(blank=True, null=True, verbose_name="product_image_1_vector")
    product_image_2_vector = models.JSONField(blank=True, null=True, verbose_name="product_image_2_vector")
    product_image_3_vector = models.JSONField(blank=True, null=True, verbose_name="product_image_3_vector")
    product_image_4_vector = models.JSONField(blank=True, null=True, verbose_name="product_image_4_vector")
    product_image_5_vector = models.JSONField(blank=True, null=True, verbose_name="product_image_5_vector")
    product_image_6_vector = models.JSONField(blank=True, null=True, verbose_name="product_image_6_vector")
    product_image_7_vector = models.JSONField(blank=True, null=True, verbose_name="product_image_7_vector")
    product_image_8_vector = models.JSONField(blank=True, null=True, verbose_name="product_image_8_vector")
    
    price = models.FloatField( verbose_name="price",  null=True)
    discount = models.CharField( verbose_name="discount",  null=True , blank=True)
    final_price = models.CharField( verbose_name="final_price",  null=True, blank=True)
    product_verification = models.CharField( verbose_name="product_verification",  null=True)
    shipping_via = models.CharField( verbose_name="shipping_via",  null=True, default='By Air')
    refpro = models.CharField( verbose_name="refpro",  null=True)
    reuser = models.CharField( verbose_name="reuser",  null=True)
    
    status = models.CharField( verbose_name="status",  null=True)
    created_at = models.DateTimeField(verbose_name="created_at",  null=True, default=datetime.now())

    product_added_from = models.CharField( verbose_name="product_added_from",  null=True, default="manual")

    delay_days_air = models.IntegerField( verbose_name="Delay Days Air",  null=True, blank=True)
    delay_days_ship = models.IntegerField( verbose_name="Delay Days Ship",  null=True, blank=True)
    delay_days_express = models.IntegerField( verbose_name="Delay Days Express",  null=True, blank=True)

    def __str__(self):
        return "%s" % str(self.id)+'--product--->'+str(self.product_name)+'---productcode--->'+str(self.product_code)

class ProductImage(models.Model):#done
    product = models.ForeignKey(ProductDetail, null=True,verbose_name="ProductDetail", on_delete=models.CASCADE)
    image = models.FileField(upload_to='image/product/other/image', verbose_name='Model Image', null=True, blank=True,
                        validators=[validators.validate_file_extension_image])

    def __str__(self):
        return "%s" % self.id

class ProductOtherSpecification(models.Model):#done
    product = models.ForeignKey(ProductDetail, null=True,verbose_name="ProductDetail", on_delete=models.CASCADE)
    key = models.CharField( verbose_name="key Name",  null=True)
    key_french = models.CharField( verbose_name="key French",  null=True)
    value = models.CharField( verbose_name="value Name",  null=True)
    value_french = models.CharField( verbose_name="value French",  null=True)
    
    def __str__(self):
        return "%s" % self.id

class ProductModel(models.Model): #done
    product = models.ForeignKey(ProductDetail, null=True,verbose_name="ProductDetail", on_delete=models.CASCADE)
    model_name = models.CharField(verbose_name="Model Name",  null=True)
    model_name_french = models.CharField(verbose_name="model_name_french",  null=True)
    model_image = models.FileField(upload_to='image/model/image', verbose_name='Model Image', null=True, blank=True,
                        validators=[validators.validate_file_extension_image])
    status = models.CharField( verbose_name="status",  null=True, default='Active')

    def __str__(self):
        return "%s" % str(self.id)+'--->productDEtail----->'+str(self.product)
    
class ProductModelVariant(models.Model):#done
    product = models.ForeignKey(ProductDetail, null=True,verbose_name="ProductDetail", on_delete=models.CASCADE)
    model = models.ForeignKey(ProductModel, null=True,verbose_name="Product Model", on_delete=models.CASCADE)
    name = models.CharField( verbose_name="Variant Name",  null=True)
    name_french = models.CharField( verbose_name="Variant_french",  null=True)
    image = models.FileField(upload_to='image/variant/image', verbose_name='Variant Image', null=True, blank=True,
                        validators=[validators.validate_file_extension_image])
    price = models.CharField( verbose_name="Variant Price",  null=True, blank=True)
    variant_verification = models.CharField( verbose_name="variant_verification",  null=True, default='Approved')
    status = models.CharField( verbose_name="status",  null=True, default='Active')

    def __str__(self):
        return "%s" % str(self.id)+'--->MOdel detail----->'+str(self.model)
    
# class ProductModelVariantCountryWisePrice(models.Model):
#     variant = models.ForeignKey(ProductModelVariant, null=True, blank=True, verbose_name="Variant", on_delete=models.CASCADE)
#     country = models.ForeignKey(CountryWithCurrency, verbose_name="Country", null=True, blank=True, on_delete=models.CASCADE)
#     price = models.CharField(verbose_name="Variant Price",  null=True, blank=True)

#     def __str__(self):
#         return "%s" % str(self.id)+'--->variant----->'+str(self.variant)+'--->currency----->'+str(self.currency)

class VendorProductPrice(models.Model):#done
    product = models.ForeignKey(ProductDetail, null=True,verbose_name="ProductDetail", on_delete=models.CASCADE)
    model = models.ForeignKey(ProductModel, null=True,verbose_name="Product Model", on_delete=models.CASCADE)
    vendor = models.ForeignKey(VendorDetail, null=True,verbose_name="VendorDetail", on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductModelVariant, null=True,verbose_name="ProductModelVariant", on_delete=models.CASCADE)
    price = models.CharField(max_length=100, verbose_name="price",  null=True)
    quantity = models.CharField(max_length=100, verbose_name="quantity",  null=True)
    status = models.CharField(max_length=100, verbose_name="status",  null=True, default= 'Active')

    def __str__(self):
        return "%s" % self.id


class ProductRequest(models.Model): #done
    vendor = models.ForeignKey(VendorDetail, null=True,verbose_name="vendor", on_delete=models.CASCADE)
    product_name = models.CharField(max_length=100, verbose_name="product_name",  null=True)
    category = models.CharField(max_length=100, verbose_name="category",  null=True)
    subcategory = models.CharField(max_length=100, verbose_name="subcategory",  null=True)
    category_description = models.TextField(verbose_name="category_description", null=True,blank=True) 
    description = models.TextField(verbose_name="description", null=True,blank=True) 
    product_image_1 = models.FileField(upload_to='image/productRequest/image', verbose_name='product_image_1', null=True, blank=True,
                        validators=[validators.validate_file_extension_image])
    product_image_2 = models.FileField(upload_to='image/productRequest/image', verbose_name='product_image_2', null=True, blank=True,
                        validators=[validators.validate_file_extension_image]) 
    status = models.CharField(max_length=100, verbose_name="status",  null=True)
    
    def __str__(self):
        return "%s" % self.id



class CustomerDetail(models.Model): #done
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


class CustomerLogin(models.Model): #done
    customer = models.ForeignKey(CustomerDetail, null=True,verbose_name="User Role", on_delete=models.SET_NULL)
    login_time = models.CharField(max_length=100, verbose_name="Login Time",  null=True)

    def __str__(self):
        return "%s" % self.id


class CustomerLoginHistory(models.Model): #done
    email = models.CharField(max_length=100, verbose_name="Email",  null=True)
    login_time = models.CharField(max_length=100, verbose_name="Login Time",  null=True)

    def __str__(self):
        return "%s" % self.id

class CustomerAddressDetail(models.Model): #done
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


class WishlistDetail(models.Model):  #done
    customer = models.ForeignKey(CustomerDetail, null=True,verbose_name="User Role", on_delete=models.SET_NULL)
    product = models.ForeignKey(ProductDetail, null=True,verbose_name="ProductDetail", on_delete=models.SET_NULL)
    created_at = models.CharField(max_length=100, verbose_name="created at", null= True)

    def __str__(self):
        return "%s" % str(self.id)+'----product--->'+str(self.product)


class CartDetail(models.Model): #done
    customer = models.ForeignKey(CustomerDetail, null=True,verbose_name="User Role", on_delete=models.SET_NULL)
    product = models.ForeignKey(ProductDetail, null=True,verbose_name="ProductDetail", on_delete=models.SET_NULL)
    variant = models.ForeignKey(ProductModelVariant, null=True,verbose_name="ProductModelVariant", on_delete=models.SET_NULL)
    quantity = models.CharField(max_length=100, verbose_name="quantity ")
    shipping_via = models.CharField(max_length=100, verbose_name="shipping_via " , null= True)
    created_at = models.CharField(max_length=100, verbose_name="created at", null= True)

    def __str__(self):
        return "%s" % self.id

class WarehouseDetail(models.Model): #done
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


class InfluencerDetail(models.Model): #done
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

class PromocodeDetail(models.Model): #done
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

class CargoDetail(models.Model): #done
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


class OrderDetail(models.Model): #done
    customer = models.ForeignKey(CustomerDetail, null=True,verbose_name="customer", on_delete=models.SET_NULL)
    promocode = models.ForeignKey(PromocodeDetail, null=True, on_delete=models.SET_NULL)
    customer_address = models.ForeignKey(CustomerAddressDetail, null=True,verbose_name="CustomerAddressDetail", on_delete=models.SET_NULL)
    cargo = models.ForeignKey(CargoDetail, null=True,verbose_name="CargoDetail", on_delete=models.SET_NULL)
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
    
    created_at = models.DateTimeField(verbose_name="created at",auto_now_add=True, null= True)
    expire_at = models.DateTimeField(verbose_name='Expire At', null=True, blank=True)

    def __str__(self):
        return "%s" % self.id +"-->--> "+ str(self.customer )

class OrderPaymentReceivingBankDetail(models.Model): #done
    order = models.ForeignKey(OrderDetail, null=True,verbose_name="OrderDetail", on_delete=models.CASCADE)
    holder_name = models.CharField(verbose_name="Account Holder Name", null=True, blank=True)
    bank_name = models.CharField(verbose_name="Bank Name", null=True, blank=True)
    account_number = models.CharField(verbose_name="Account Number", null=True, blank=True)
    branch_name = models.CharField(verbose_name="Branch/Agency Name", null=True, blank=True)
    branch_code = models.CharField(verbose_name="Branch/Bank Code", null=True, blank=True)

    def __str__(self):
        return "%s" % str(self.id)+"<--id--"+"--ORDER ID-->"+str(self.order)+ '-->'+ str(self.bank_name)



class ProductOrderDetail(models.Model): #done
    order = models.ForeignKey(OrderDetail, null=True,verbose_name="OrderDetail", on_delete=models.CASCADE)
    product = models.ForeignKey(ProductDetail, null=True,verbose_name="ProductDetail", on_delete=models.SET_NULL)
    variant = models.ForeignKey(ProductModelVariant, null=True,verbose_name="ProductModelVariant", on_delete=models.SET_NULL)
    warehouse = models.ForeignKey(WarehouseDetail, null=True,verbose_name="WarehouseDetail", on_delete=models.SET_NULL)
    quantity = models.IntegerField(verbose_name="quantity ")
    price = models.CharField(max_length=100, verbose_name="price", null=True)
    total_price = models.CharField(max_length=100, verbose_name="total_price")
    vendor_price = models.IntegerField(verbose_name="vendor price", null=True)
    total_vendor_price = models.IntegerField(verbose_name="total vendor price", null=True, blank=True)
    currency = models.CharField(max_length=100, verbose_name="payment currency", null=True)
    currency_name = models.CharField(max_length=100, verbose_name="payment currency name", null=True)
    product_shipping_price = models.CharField(max_length=100, verbose_name="product_shipping_price", null=True)
    shipping_via = models.CharField(max_length=100, verbose_name="shipping_via", null=True)
    status = models.CharField(max_length=100, verbose_name="status", null=True)
    vendor_status = models.CharField(max_length=100, verbose_name="vendor_status", null=True)
    created_at = models.DateTimeField(max_length=100, verbose_name="created at",auto_now_add=True, null= True)

    def __str__(self):
        return "%s" % str(self.id)+"---->"+str(self.shipping_via)+"---order_status-->"+str(self.order.order_status)+"---order_id-->"+str(self.order.order_id)


class VendorOrderDetail(models.Model):  #done
    order = models.ForeignKey(OrderDetail, null=True,verbose_name="OrderDetail", on_delete=models.SET_NULL, blank=True)
    variant = models.ForeignKey(ProductOrderDetail, null=True,verbose_name="variant", on_delete=models.CASCADE, blank=True)
    vendor = models.ForeignKey(VendorDetail, null=True,verbose_name="vendor", on_delete=models.SET_NULL, blank=True)
    created_at = models.DateTimeField(max_length=100, verbose_name="created at", auto_now_add=True, null= True, blank=True)

    def __str__(self):
        return "%s" % self.id

class VendorOrderTracking(models.Model): #done
    order = models.ForeignKey(OrderDetail, null=True,verbose_name="OrderDetail", on_delete=models.SET_NULL)
    variant = models.ForeignKey(ProductOrderDetail, null=True,verbose_name="variant", on_delete=models.CASCADE)
    status = models.CharField(max_length=100, verbose_name="quantity ")
    created_at = models.CharField(max_length=100, verbose_name="created at", null= True)

    def __str__(self):
        return "%s" % self.id


class OrderTracking(models.Model): #done
    order = models.ForeignKey(OrderDetail, null=True,verbose_name="OrderDetail", on_delete=models.SET_NULL)
    variant = models.ForeignKey(ProductOrderDetail, null=True,verbose_name="variant", on_delete=models.CASCADE)
    status = models.CharField(max_length=100, verbose_name="quantity ")
    created_at = models.CharField(max_length=100, verbose_name="created at", null= True)

    def __str__(self):
        return "%s" % self.id

class OrderTransaction(models.Model): #done
    order = models.ForeignKey(OrderDetail, null=True,verbose_name="OrderDetail", on_delete=models.CASCADE)
    customer = models.ForeignKey(CustomerDetail, null=True,verbose_name="customer", on_delete=models.SET_NULL)
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


class PromocodeTracking(models.Model): #done
    order = models.ForeignKey(OrderDetail, null=True,verbose_name="OrderDetail", on_delete=models.SET_NULL)
    promocode = models.ForeignKey(PromocodeDetail, null=True,verbose_name="variant", on_delete=models.CASCADE)
    customer = models.ForeignKey(CustomerDetail, null=True,verbose_name="customer", on_delete=models.SET_NULL)
    created_at = models.CharField(max_length=100, verbose_name="created at", null= True)

    def __str__(self):
        return "%s" % self.id


class PromocodeCommissionDetail(models.Model): #done
    order = models.ForeignKey(OrderDetail, null=True,verbose_name="OrderDetail", on_delete=models.SET_NULL)
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



class ChatRoom(models.Model): #done
    user = models.ForeignKey(CustomerDetail,verbose_name = 'User', null=True, blank = True, on_delete=models.CASCADE)
    admin = models.ForeignKey(AdminDetail, verbose_name = 'Admin', null=True, blank = True, on_delete=models.SET_NULL)
    chat_agent = models.ForeignKey(ChatAgentDetail, verbose_name = 'Chat Agent', null=True, blank = True, on_delete=models.CASCADE)
    room = models.CharField(verbose_name='Room ID', null=True, blank=True)
    note = models.CharField(verbose_name='Note', null=True, blank=True)
    priority = models.CharField(verbose_name='Priority', null=True, blank=True, default="Normal")
    is_resolved = models.CharField(verbose_name='Is Resolved', null=True, blank=True, default = False)
    created_at = models.DateTimeField(verbose_name='Created At', null=True, blank=True)
    updated_at = models.DateTimeField(verbose_name="updated at", null= True)

    status = models.CharField(verbose_name='Status', null=True, blank=True, default="Active")

    def __str__(self):
        return "%s" % str(self.id) +"--ROOM ID-->"+str(self.room)
    
class ChatConversion(models.Model): #done
    user = models.ForeignKey(CustomerDetail,verbose_name = 'User', null=True, blank = True, on_delete=models.CASCADE)
    admin = models.ForeignKey(AdminDetail, verbose_name = 'Admin', null=True, blank = True, on_delete=models.SET_NULL)
    chat_agent = models.ForeignKey(ChatAgentDetail, verbose_name = 'Agent', null=True, blank = True, on_delete=models.CASCADE)
    room = models.ForeignKey(ChatRoom ,verbose_name='Room ID', null=True, blank=True, on_delete=models.CASCADE)
    message = models.CharField(verbose_name='Message', null=True, blank=True)
    message_french = models.CharField(verbose_name='Message French', null=True, blank=True)
    message_type = models.CharField(verbose_name='Message Type', null=True, blank=True)
    send_by = models.CharField(verbose_name='Send By', null=True, blank=True)
    product_id = models.IntegerField(null=True, blank=True)

    file = models.FileField(upload_to='chat/files', verbose_name='File', null=True, blank=True,
                        validators=[validators.validate_file_extension_image])
    file_type = models.CharField(verbose_name='File Type', null=True, blank=True)

    create_at = models.DateTimeField(verbose_name="Created At", null=True, blank=True)
    status = models.CharField(verbose_name='Status', null=True, blank=True, default='Unseen')

    def __str__(self):
        return "%s" % str(self.id) +"--ROOM ID-->"+str(self.room)
    


class DailyPrice(models.Model): #done
    country = models.ForeignKey(CountryWithCurrency, verbose_name='Country With Currency', null=True, blank = True, on_delete=models.CASCADE)
    price_by_air = models.CharField(verbose_name='price_by_air', null=True, blank=True)
    price_by_ship = models.CharField(verbose_name='price_by_ship', null=True, blank=True)

    def __str__(self):
        return "%s" % str(self.id) +"--country with currency-->"+str(self.country)


class AgentInChatRoomHistory(models.Model): #done
    room = models.ForeignKey(ChatRoom, verbose_name='Room ID', blank=True, null=True, on_delete=models.CASCADE)
    agent = models.ForeignKey(ChatAgentDetail, verbose_name='Agent ID', blank=True, null=True, on_delete=models.CASCADE)
    assigned_date = models.DateTimeField(verbose_name='Assigned Date', null=True, blank=True)
    unassigned_date = models.DateTimeField(verbose_name='Unassigned Date', null=True, blank=True)

    def __str__(self):
        return "%s" % str(self.id)+"--room-->"+str(self.agent)
    
class VendorTransaction(models.Model):#done
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
    
class RecentlyViewProduct(models.Model): #done
    customer = models.ForeignKey(CustomerDetail, verbose_name='CustomerDetail', blank=True, null=True, on_delete=models.CASCADE)
    product = models.ForeignKey(ProductDetail, verbose_name='Product', blank=True, null=True, on_delete=models.CASCADE)
    created_at = models.CharField(verbose_name='Created At', null=True, blank=True)

    def __str__(self):
        return "%s" % self.id


class IntroBanner(models.Model): #done
    banner = models.FileField(upload_to='image/IntroBanner/image', verbose_name='banner', null=True, blank=True,
                        validators=[validators.validate_file_extension_image_and_video])
 
    def __str__(self):
        return "%s" % self.banner


class ProductReview(models.Model): #done
    customer = models.ForeignKey(CustomerDetail, verbose_name='CustomerDetail', blank=True, null=True, on_delete=models.CASCADE)
    product = models.ForeignKey(ProductDetail, verbose_name='Product', blank=True, null=True, on_delete=models.CASCADE)
    customer_name = models.CharField(verbose_name='customer_name', null=True, blank=True)
    rating = models.IntegerField(verbose_name='rating', null=True, blank=True)
    review = models.TextField(verbose_name='review', null=True, blank=True)
    
    created_at = models.CharField(verbose_name='Created At', null=True, blank=True)
 
    def __str__(self):
        return "%s" % self.id


class PaymentCargoSlider(models.Model): #done
    banner = models.FileField(upload_to='image/PaymentCargo/image', verbose_name='banner', null=True, blank=True,
                        validators=[validators.validate_file_extension_image_and_video])
    status = models.CharField(verbose_name='status', null=True, blank=True)
    created_at = models.CharField(verbose_name='Created At', null=True, blank=True)

    def __str__(self):
        return "%s" % str(self.id)

class ImportantNote(models.Model): #done
    note = models.CharField(verbose_name='note', null=True, blank=True)
    note_french = models.CharField(verbose_name='note_french', null=True, blank=True)
    status = models.CharField(verbose_name='status', null=True, blank=True)
    created_at = models.CharField(verbose_name='Created At', null=True, blank=True)
 
    def __str__(self):
        return "%s" % self.id

class DeliveryDayDetail(models.Model): #done
    express_delivery = models.IntegerField(verbose_name='express_delivery', null=True, blank=True)
    air_delivery = models.IntegerField(verbose_name='express_delivery', null=True, blank=True)
    ship_delivery = models.IntegerField(verbose_name='note_french', null=True, blank=True)

    def __str__(self):
        return "%s" % self.id


class VendorPaymentTracker(models.Model): #done
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




class ProductInquiry(models.Model): #done
    customer = models.ForeignKey(CustomerDetail, verbose_name='CustomerDetail', blank=True, null=True, on_delete=models.CASCADE)
    inquiry_code = models.CharField(verbose_name='inquiry_code', null=True, blank=True)

    product_name = models.CharField(verbose_name='product_name', null=True, blank=True)
    description = models.TextField(verbose_name='description', null=True, blank=True)
    quantity = models.IntegerField(verbose_name='quantity', null=True, blank=True)
    created_at = models.DateTimeField(verbose_name='Created At', null=True, blank=True)

    status = models.CharField(verbose_name='Status', null=True, blank=True, default='Pending')

    def __str__(self):
        return "%s" % self.id
    
class ProductInquiryImages(models.Model): #done
    inquiry = models.ForeignKey(ProductInquiry, verbose_name='Product Inquiry', null=True, blank=True, on_delete=models.CASCADE)
    image = models.FileField(upload_to='image/productInquiry/image', verbose_name='Product Inquiry Image', null=True, blank=True,
                        validators=[validators.validate_file_extension_image])

    def __str__(self):
        return "%s" % self.id
    

class VendorDelayNote(models.Model):#done
    vendor = models.ManyToManyField(VendorDetail, verbose_name='vendor', null=True, blank=True)
    delay_note_code = models.CharField(verbose_name='delay_note_code', null=True, blank=True)
    note = models.TextField(verbose_name="note", null=True, blank=True)
    start_at = models.DateTimeField(verbose_name='Start At', null=True, blank=True)
    end_at = models.DateTimeField(verbose_name='End At', null=True, blank=True)
    created_at = models.DateTimeField(verbose_name='Created At', null=True, blank=True)
    status = models.CharField(verbose_name='Status',null=True, blank=True, default='Active')

    def __str__(self):
        return "%s" % str(self.id)+"---->"+str(self.note)



