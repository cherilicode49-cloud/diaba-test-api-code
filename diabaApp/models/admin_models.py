from django.db import models
from diabaApp import validators
from datetime import datetime
from .common_models import Role


class ModuleDetail(models.Model):
    module = models.CharField(max_length=100, verbose_name="module")

    def __str__(self):
        return "%s" % self.module


class AdminDetail(models.Model):
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


class AdminModuleRightsDetail(models.Model):
    admin = models.ForeignKey(AdminDetail, null=True,verbose_name="admin", on_delete=models.CASCADE, blank=True)
    module_name = models.CharField(max_length=100, verbose_name="module_name")
    view = models.BooleanField(verbose_name='view', null=True, blank=True, default=False)
    create = models.BooleanField(verbose_name='create', null=True, blank=True, default=False)
    update = models.BooleanField(verbose_name='update', null=True, blank=True, default=False)
    delete = models.BooleanField(verbose_name='delete', null=True, blank=True, default=False)
    last_update = models.CharField(max_length=100, verbose_name="last_update", null= True)

    def __str__(self):
        return "%s" % self.id


class ChatAgentDetail(models.Model):
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
