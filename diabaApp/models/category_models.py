from django.db import models
from diabaApp import validators
from datetime import datetime

class CategoryDetail(models.Model):
    category = models.CharField(max_length=100, verbose_name="category",  null=True)
    category_french = models.CharField(max_length=100, verbose_name="category_french",  null=True)
    image = models.FileField(upload_to='image/category', verbose_name='Image', null=True, blank=True,
                        validators=[validators.validate_file_extension_image])
    status = models.CharField(max_length=100, verbose_name="status",  null=True)

    def __str__(self):
        return "%s" % self.category

class SubCategoryDetail(models.Model):
    category = models.ForeignKey(CategoryDetail, null=True,verbose_name="category", on_delete=models.CASCADE)
    subcategory = models.CharField(max_length=100, verbose_name="subcategory",  null=True)
    subcategory_french = models.CharField(max_length=100, verbose_name="subcategory_french",  null=True)
    image = models.FileField(upload_to='image/subCategory', verbose_name='Image', null=True, blank=True,
                        validators=[validators.validate_file_extension_image])
    status = models.CharField(max_length=100, verbose_name="status",  null=True)

    def __str__(self):
        return "%s" % self.id


class SuperSubCategoryDetail(models.Model):
    category = models.ForeignKey(CategoryDetail, null=True,verbose_name="CategoryDetail", on_delete=models.CASCADE)
    subcategory = models.ForeignKey(SubCategoryDetail, null=True,verbose_name="SubCategoryDetail", on_delete=models.CASCADE)
    super_subcategory = models.CharField(max_length=100, verbose_name="subcategory",  null=True)
    image = models.FileField(upload_to='image/superSubCategory', verbose_name='Image', null=True, blank=True,
                        validators=[validators.validate_file_extension_image])
    status = models.CharField(max_length=100, verbose_name="status",  null=True)

    def __str__(self):
        return "%s" % self.id
