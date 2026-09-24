from django.db import models
from diabaApp import validators
from datetime import datetime
from .category_models import CategoryDetail, SubCategoryDetail
from .country_models import Country
from .vendor_models import VendorDetail

class ProductCountry(models.Model):
    name = models.CharField(max_length=100, verbose_name="name",  null=True)
    name_french = models.CharField(max_length=100, verbose_name="name_french",  null=True)
    countryCode = models.CharField(max_length=100, verbose_name="country_code",  null=True)

    def __str__(self):
        return "%s" % str(self.id)+'---->'+str(self.name)

class ProductTag(models.Model):
    category = models.ForeignKey(CategoryDetail, null=True,verbose_name="category", on_delete=models.CASCADE)
    tag = models.CharField(max_length=100, verbose_name="tag",  null=True)
    
    def __str__(self):
        return "%s" % str(self.id)+"======>"+str(self.tag)

class ProductType(models.Model):
    product_type = models.CharField(max_length=100, verbose_name="product_type",  null=True)
    def __str__(self):
        return "%s" % str(self.id)+"======>"+str(self.product_type)


class ProductPackagingBy(models.Model):
    product_packaging = models.CharField(max_length=100, verbose_name="product_packaging",  null=True)
    def __str__(self):
        return "%s" % str(self.id)+"======>"+str(self.product_packaging)


class ProductDetail(models.Model):
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
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return "%s" % str(self.id)+'--product--->'+str(self.product_name)+'---productcode--->'+str(self.product_code)

class ProductImage(models.Model):
    product = models.ForeignKey(ProductDetail, null=True,verbose_name="ProductDetail", on_delete=models.CASCADE)
    image = models.FileField(upload_to='image/product/other/image', verbose_name='Model Image', null=True, blank=True,
                        validators=[validators.validate_file_extension_image])

    def __str__(self):
        return "%s" % self.id

class ProductOtherSpecification(models.Model):
    product = models.ForeignKey(ProductDetail, null=True,verbose_name="ProductDetail", on_delete=models.CASCADE)
    key = models.CharField( verbose_name="key Name",  null=True)
    key_french = models.CharField( verbose_name="key French",  null=True)
    value = models.CharField( verbose_name="value Name",  null=True)
    value_french = models.CharField( verbose_name="value French",  null=True)
    
    def __str__(self):
        return "%s" % self.id
    
    
class ProductModel(models.Model):
    product = models.ForeignKey(ProductDetail, null=True,verbose_name="ProductDetail", on_delete=models.CASCADE)
    model_name = models.CharField(verbose_name="Model Name",  null=True)
    model_name_french = models.CharField(verbose_name="model_name_french",  null=True)
    model_image = models.FileField(upload_to='image/model/image', verbose_name='Model Image', null=True, blank=True,
                        validators=[validators.validate_file_extension_image])
    status = models.CharField( verbose_name="status",  null=True, default='Active')
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return "%s" % str(self.id)+'--->productDEtail----->'+str(self.product)
    
class ProductModelVariant(models.Model):
    product = models.ForeignKey(ProductDetail, null=True,verbose_name="ProductDetail", on_delete=models.CASCADE)
    model = models.ForeignKey(ProductModel, null=True,verbose_name="Product Model", on_delete=models.CASCADE)
    name = models.CharField( verbose_name="Variant Name",  null=True)
    name_french = models.CharField( verbose_name="Variant_french",  null=True)
    image = models.FileField(upload_to='image/variant/image', verbose_name='Variant Image', null=True, blank=True,
                        validators=[validators.validate_file_extension_image])
    price = models.CharField( verbose_name="Variant Price",  null=True, blank=True)
    variant_verification = models.CharField( verbose_name="variant_verification",  null=True, default='Approved')
    status = models.CharField( verbose_name="status",  null=True, default='Active')
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return "%s" % str(self.id)+'--->MOdel detail----->'+str(self.model)


class ProductRequest(models.Model):
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
