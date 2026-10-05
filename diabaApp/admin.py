from django.contrib import admin
from diabaApp import models

from datetime import datetime

class SoftDeleteAdmin(admin.ModelAdmin):
    """
    Prevents permanent deletion from Django Admin Panel.
    Intercepts delete actions and performs a soft-delete instead.
    """
    actions = ['soft_delete_selected', 'restore_selected']

    def soft_delete_selected(self, request, queryset):
        queryset.update(is_deleted=True, deleted_at=datetime.now())
        self.message_user(request, "Selected items marked as soft-deleted.")
    soft_delete_selected.short_description = "Soft delete selected records"

    def restore_selected(self, request, queryset):
        queryset.update(is_deleted=False, deleted_at=None)
        self.message_user(request, "Selected items restored.")
    restore_selected.short_description = "Restore selected soft-deleted records"

    def delete_model(self, request, obj):
        # Soft delete instead of SQL DELETE
        obj.is_deleted = True
        obj.deleted_at = datetime.now()
        if hasattr(obj, 'status'):
            obj.status = 'Inactive'
        obj.save()

    def delete_queryset(self, request, queryset):
        # Soft delete in bulk action
        queryset.update(is_deleted=True, deleted_at=datetime.now())


class ProtectedNoDeleteAdmin(admin.ModelAdmin):
    """
    Completely disables delete buttons/actions in Django Admin Panel.
    """
    def has_delete_permission(self, request, obj=None):
        return False


# Register your models here.
admin.site.register(models.Role)
admin.site.register(models.AdminDetail)
admin.site.register(models.VendorDetail)
admin.site.register(models.VendorAddress)
admin.site.register(models.VendorLoginHistory)
admin.site.register(models.CategoryDetail)
admin.site.register(models.SubCategoryDetail)
admin.site.register(models.SuperSubCategoryDetail)
admin.site.register(models.ProductDetail, SoftDeleteAdmin)
admin.site.register(models.ProductModel)
admin.site.register(models.ProductModelVariant)
admin.site.register(models.VendorProductPrice)
admin.site.register(models.ProductRequest)
admin.site.register(models.CustomerDetail, SoftDeleteAdmin)
admin.site.register(models.CustomerLogin)
admin.site.register(models.CustomerLoginHistory)
admin.site.register(models.CustomerAddressDetail)
admin.site.register(models.ProductOtherSpecification)
admin.site.register(models.ProductImage)
admin.site.register(models.WishlistDetail)
admin.site.register(models.CartDetail)
admin.site.register(models.OrderDetail, SoftDeleteAdmin)

admin.site.register(models.ProductOrderDetail)
admin.site.register(models.Country)
admin.site.register(models.VendorOrderDetail)
admin.site.register(models.OrderTracking)
admin.site.register(models.ChatRoom)
admin.site.register(models.ChatConversion)
admin.site.register(models.DailyPrice)
admin.site.register(models.ChatAgentDetail)
admin.site.register(models.AgentInChatRoomHistory)

admin.site.register(models.AboutUs)
admin.site.register(models.PrivacyPolicy)
admin.site.register(models.RefundPolicy)
admin.site.register(models.TermsAndCondition)
admin.site.register(models.VendorTransaction)
admin.site.register(models.RecentlyViewProduct)
admin.site.register(models.ModuleDetail)
admin.site.register(models.AdminModuleRightsDetail)
admin.site.register(models.OrderTransaction)
admin.site.register(models.WarehouseDetail)
admin.site.register(models.VendorOrderTracking)

admin.site.register(models.CountryWithCurrency)
admin.site.register(models.CurrencyConverter)

admin.site.register(models.IntroBanner)

admin.site.register(models.InfluencerDetail)
admin.site.register(models.PromocodeDetail)
admin.site.register(models.PromocodeTracking)
admin.site.register(models.CountryMoneyNetwork)
admin.site.register(models.MoneyNetwork)
admin.site.register(models.PromocodeCommissionDetail)
admin.site.register(models.CargoDetail)
admin.site.register(models.ProductReview)
admin.site.register(models.AppDynamicSetting)
admin.site.register(models.ProductCountry)
admin.site.register(models.PaymentCargoSlider)
admin.site.register(models.ImportantNote)
admin.site.register(models.CountryCashLimit)
admin.site.register(models.ProductTag)
admin.site.register(models.DeliveryDayDetail)
admin.site.register(models.VendorPaymentTracker)

admin.site.register(models.ProductInquiry)
admin.site.register(models.ProductInquiryImages)
admin.site.register(models.VendorDelayNote)
admin.site.register(models.CountryWiseBankDetail)
admin.site.register(models.OrderPaymentReceivingBankDetail)
admin.site.register(models.ProductType)
admin.site.register(models.ProductPackagingBy)
admin.site.register(models.ProductRequestTransaction)
admin.site.register(models.BannerContent)
admin.site.register(models.ContainerTerms)
admin.site.register(models.ContainerBookingFee)
admin.site.register(models.UserActivity)
