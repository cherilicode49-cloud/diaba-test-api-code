from django.db import models
from diabaApp import validators
from datetime import datetime

class AboutUs(models.Model):
    about_us = models.TextField(verbose_name='About US', null=True, blank=True)

    def __str__(self):
        return "%s" % str(self.id)+'--About Us-->'+str(self.about_us)
    
class PrivacyPolicy(models.Model):
    privacy_policy = models.TextField(verbose_name='Privacy Policy', null=True, blank=True)

    def __str__(self):
        return "%s" % str(self.id)+'--Privacy Policy-->'+str(self.privacy_policy)
    
class RefundPolicy(models.Model):
    refund_policy = models.TextField(verbose_name='Refund Policy', null=True, blank=True)

    def __str__(self):
        return "%s" % str(self.id)+'--Refund Policy-->'+str(self.refund_policy)
    
class TermsAndCondition(models.Model):
    terms_and_condition = models.TextField(verbose_name='Terms And Condition', null=True, blank=True)

    def __str__(self):
        return "%s" % str(self.id)+'--Terms And Condition-->'+str(self.terms_and_condition)

class AppDynamicSetting(models.Model):
    app_version = models.CharField(max_length=2000,verbose_name='App Version', null=True, blank=True)
    release_note = models.TextField(max_length=2000,verbose_name='Release Note', null=True, blank=True)

    def __str__(self):
        return "%s" % str(self.id)
    

class Role(models.Model):
    # roleID = models.BigIntegerField(verbose_name="Role id ")
    roleName = models.CharField(max_length=100, verbose_name="Role Name")

    def __str__(self):
        return "%s" % self.roleName

class IntroBanner(models.Model):
    banner = models.FileField(upload_to='image/IntroBanner/image', verbose_name='banner', null=True, blank=True,
                        validators=[validators.validate_file_extension_image_and_video])
 
    def __str__(self):
        return "%s" % self.banner
    

class ImportantNote(models.Model):
    note = models.CharField(verbose_name='note', null=True, blank=True)
    note_french = models.CharField(verbose_name='note_french', null=True, blank=True)
    status = models.CharField(verbose_name='status', null=True, blank=True)
    created_at = models.CharField(verbose_name='Created At', null=True, blank=True)
 
    def __str__(self):
        return "%s" % self.id