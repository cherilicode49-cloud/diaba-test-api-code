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


class AppVersionSetting(models.Model):
    PLATFORM_CHOICES = (
        ('android', 'Android'),
        ('ios', 'iOS'),
    )

    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES, unique=True, verbose_name='Target Platform')
    latest_version = models.CharField(max_length=20, default='1.0.0', verbose_name='Latest Version')
    min_supported_version = models.CharField(max_length=20, default='1.0.0', verbose_name='Minimum Supported Version')
    is_force_update = models.BooleanField(default=False, verbose_name='Is Force Update')
    update_title = models.CharField(max_length=150, default='New Version Available', verbose_name='Update Title')
    release_notes = models.TextField(null=True, blank=True, verbose_name='Release Notes')
    store_url = models.CharField(max_length=255, default='', verbose_name='Store URL')
    is_maintenance_mode = models.BooleanField(default=False, verbose_name='Is Maintenance Mode')
    maintenance_message = models.TextField(null=True, blank=True, verbose_name='Maintenance Message')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True, verbose_name='Created At')

    class Meta:
        verbose_name = 'App Version Setting'
        verbose_name_plural = 'App Version Settings'
        db_table = 'diabaApp_appversionsetting'

    def __str__(self):
        return f"{self.platform} - {self.latest_version}"
