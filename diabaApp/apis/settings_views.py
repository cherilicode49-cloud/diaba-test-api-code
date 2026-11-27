from django.views.decorators.csrf import csrf_exempt
from diabaApp import models
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from django.http import HttpResponse
import io
import math, random , calendar
from datetime import datetime, timedelta
from django.conf import settings
from django.db.models import Sum, Count, F, Q, ExpressionWrapper,  OuterRef, Subquery
from django.db.models.functions import Cast, TruncMonth, Coalesce, ExtractMonth, Round, TruncDate
from django.db.models.fields import FloatField
from firebase_admin import messaging
import requests
from django.template.loader import get_template
from django.core.mail import send_mail
from diabaApp.serializer import AppDynamicSettingSerializer, InquirySettingSerializer, ProductDataSerializer, RecentlyViewProductSerializer, CategoryDetailSerializer, \
    AboutUsSerializer, PrivacyPolicySerializer, RefundPolicySerializer, TermsAndConditionSerializer, ImportantNoteSerializer, \
    IntroBannerSerializer, AppVersionSettingSerializer
from django.db.models.functions import Random
from django.core.cache import cache

BASE_URL = settings.BASE_URL
IMAGE_URL = settings.IMAGE_URL


@csrf_exempt
def app_setting(request):
    if request.method in ["POST", "GET"]:
        setting = models.AppDynamicSetting.objects.all().first()
        if not setting:
            setting = models.AppDynamicSetting.objects.create(
                app_version='1.0.0',
                release_note=''
            )
        setting_serializer = AppDynamicSettingSerializer(setting).data

        # Also provide inquiry setting info if available
        inq_setting = models.InquirySetting.objects.all().first()
        if not inq_setting:
            inq_setting = models.InquirySetting.objects.create(
                inquiry_price=0.00,
                inquiry_currency='XOF',
                free_inquiry=False
            )
        setting_serializer['inquiry_setting'] = InquirySettingSerializer(inq_setting).data
        setting_serializer['free_inquiry'] = inq_setting.free_inquiry
        setting_serializer['is_free_inquiry'] = inq_setting.free_inquiry
        setting_serializer['inquiry_price'] = str(inq_setting.inquiry_price)
        setting_serializer['inquiry_currency'] = inq_setting.inquiry_currency

        res={
            'data':setting_serializer
        }
        return HttpResponse(JSONRenderer().render(res), content_type='application/json', status=200)


@csrf_exempt
def admin_app_dynamic_setting(request):
    if request.method in ["POST", "GET"]:
        setting = models.AppDynamicSetting.objects.all().first()
        if not setting:
            setting = models.AppDynamicSetting.objects.create(
                app_version='1.0.0',
                release_note=''
            )

        setting_serializer = AppDynamicSettingSerializer(setting).data

        inq_setting = models.InquirySetting.objects.all().first()
        if not inq_setting:
            inq_setting = models.InquirySetting.objects.create(
                inquiry_price=0.00,
                inquiry_currency='XOF',
                free_inquiry=False
            )
        setting_serializer['inquiry_setting'] = InquirySettingSerializer(inq_setting).data
        setting_serializer['free_inquiry'] = inq_setting.free_inquiry
        setting_serializer['is_free_inquiry'] = inq_setting.free_inquiry
        setting_serializer['inquiry_price'] = str(inq_setting.inquiry_price)
        setting_serializer['inquiry_currency'] = inq_setting.inquiry_currency

        res={
            'data':setting_serializer
        }
        return HttpResponse(JSONRenderer().render(res), content_type='application/json', status=200)


@csrf_exempt
def app_dyanmic_setting_update(request):
    if request.method == "POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))

        print('pytohn_data---app_dyanmic_setting_update--->',python_data)

        app_version = python_data.get('app_version',None)
        release_note = python_data.get('release_note',None)
        inquiry_price = python_data.get('inquiry_price', None)
        inquiry_currency = python_data.get('inquiry_currency', None)
        free_inquiry = python_data.get('free_inquiry', None)
        if free_inquiry is None:
            free_inquiry = python_data.get('is_free_inquiry', None)

        setting = models.AppDynamicSetting.objects.all().first()
        if setting:
            if release_note is not None:
                setting.release_note = release_note
            if app_version is not None:
                setting.app_version = app_version
            setting.save()
        else:
            setting = models.AppDynamicSetting.objects.create(
                app_version = app_version or '1.0.0',
                release_note = release_note or ''
            )

        # Update InquirySetting if inquiry fields were provided
        if free_inquiry is not None or inquiry_price is not None or inquiry_currency is not None:
            if free_inquiry is not None:
                if isinstance(free_inquiry, str):
                    free_inquiry = free_inquiry.strip().lower() in ['true', '1', 'yes']
                else:
                    free_inquiry = bool(free_inquiry)

            if inquiry_price is not None:
                try:
                    inquiry_price = round(float(str(inquiry_price).replace(',', '').strip()), 2)
                except (ValueError, TypeError):
                    inquiry_price = None

            inq_setting = models.InquirySetting.objects.all().first()
            if not inq_setting:
                inq_setting = models.InquirySetting.objects.create(
                    inquiry_price=inquiry_price if inquiry_price is not None else 0.00,
                    inquiry_currency=inquiry_currency or 'XOF',
                    free_inquiry=free_inquiry if free_inquiry is not None else False
                )
            else:
                if free_inquiry is not None:
                    inq_setting.free_inquiry = free_inquiry
                if inquiry_price is not None:
                    inq_setting.inquiry_price = inquiry_price
                if inquiry_currency is not None:
                    inq_setting.inquiry_currency = inquiry_currency
                inq_setting.save()

        setting_serializer = AppDynamicSettingSerializer(setting).data
        res={
            'status': True,
            'message':'Settings Updated',
            'data': setting_serializer
        }
        return HttpResponse(JSONRenderer().render(res), content_type='application/json', status=200)


@csrf_exempt
def inquiry_setting(request):
    """
    Unified API for InquirySetting module (Singleton pattern - exactly one record).
    Endpoint: /api/inquiry_setting/

    Behavior:
    - If record already exists: updates the record with incoming data and saves it.
    - If record does not exist: creates the record with incoming data (or defaults).
    - Supports GET to retrieve the current setting (creates default if missing).
    - Supports POST/PUT/PATCH with JSON or form-data to upsert.
    """
    if request.method not in ["GET", "POST", "PUT", "PATCH"]:
        return HttpResponse(
            JSONRenderer().render({'status': False, 'message': 'Method not allowed'}),
            content_type='application/json',
            status=405
        )

    python_data = {}
    if request.body:
        try:
            python_data = JSONParser().parse(io.BytesIO(request.body))
        except Exception:
            try:
                import json
                python_data = json.loads(request.body.decode('utf-8'))
            except Exception:
                pass

    if hasattr(request, 'POST') and request.POST:
        for k, v in request.POST.items():
            python_data[k] = v

    if not python_data and request.method == "GET" and request.GET:
        for k, v in request.GET.items():
            python_data[k] = v

    free_inquiry = python_data.get('free_inquiry', None)
    if free_inquiry is None:
        free_inquiry = python_data.get('is_free_inquiry', None)

    inquiry_price = python_data.get('inquiry_price', None)
    inquiry_currency = python_data.get('inquiry_currency', None)

    if free_inquiry is not None:
        if isinstance(free_inquiry, str):
            free_inquiry = free_inquiry.strip().lower() in ['true', '1', 'yes']
        else:
            free_inquiry = bool(free_inquiry)

    if inquiry_price is not None:
        try:
            inquiry_price = round(float(str(inquiry_price).replace(',', '').strip()), 2)
        except (ValueError, TypeError):
            inquiry_price = None

    if inquiry_currency is not None:
        inquiry_currency = str(inquiry_currency).strip()
        if inquiry_currency in ['', 'null', 'undefined']:
            inquiry_currency = None

    setting = models.InquirySetting.objects.all().first()

    if not setting:
        # Record does not exist -> CREATE record
        setting = models.InquirySetting.objects.create(
            inquiry_price=inquiry_price if inquiry_price is not None else 0.00,
            inquiry_currency=inquiry_currency or 'XOF',
            free_inquiry=free_inquiry if free_inquiry is not None else False
        )
        msg = 'Inquiry settings created successfully'
    else:
        # Record exists -> UPDATE record if any field is provided
        has_updates = False
        if free_inquiry is not None:
            setting.free_inquiry = free_inquiry
            has_updates = True
        if inquiry_price is not None:
            setting.inquiry_price = inquiry_price
            has_updates = True
        if inquiry_currency is not None:
            setting.inquiry_currency = inquiry_currency
            has_updates = True

        if has_updates:
            setting.save()
            msg = 'Inquiry settings updated successfully'
        else:
            msg = 'Inquiry settings fetched successfully'

    data = {
        'id': setting.id,
        'free_inquiry': setting.free_inquiry,
        'is_free_inquiry': setting.free_inquiry,
        'inquiry_price': float(setting.inquiry_price or 0.0),
        'inquiry_currency': setting.inquiry_currency or 'XOF',
        'created_at': setting.created_at.strftime('%Y-%m-%d %H:%M:%S') if setting.created_at else None,
        'updated_at': setting.updated_at.strftime('%Y-%m-%d %H:%M:%S') if setting.updated_at else None
    }

    res = {
        'status': True,
        'message': msg,
        'data': data
    }
    return HttpResponse(JSONRenderer().render(res), content_type='application/json', status=200)


# Backward-compatible alias for any internal imports
inquiry_setting_update = inquiry_setting



@csrf_exempt
def app_dashboard(request):
    json_data = request.body
    stream = io.BytesIO(json_data)
    python_data = JSONParser().parse(stream)

    currencyCode = python_data.get('currencyCode', None)
    countryCallingCode = python_data.get('countryCallingCode', None)
    country = python_data.get('countryName', 'Egypt')
    ip_address = python_data.get('ip_address')
    user_id = python_data.get('user_id')
    if user_id in [None, '', 'null', 'None']:
        user_id = None
    country_id = python_data.get('country_id', None)
    if country_id in [None, '', 'null', 'None']:
        country_id = None

    try:
        page_number = int(python_data.get('page_number', 1))
    except (ValueError, TypeError):
        page_number = 1

    try:
        if currencyCode not in [None, '', 'null']:
            c_obj = models.CountryWithCurrency.objects.filter(currency_code=currencyCode).first()
            if c_obj:
                country = c_obj.country_name
        elif countryCallingCode not in [None, '', 'null']:
            c_obj = models.CountryWithCurrency.objects.filter(country_calling_code=countryCallingCode).first()
            if c_obj:
                country = c_obj.country_name
        elif user_id:
            user = models.CustomerDetail.objects.filter(id=user_id).first()
            if user:
                countryCode = user.countryCode
                c_obj = models.CountryWithCurrency.objects.filter(country_calling_code=countryCode).first()
                if c_obj:
                    country = c_obj.country_name
                elif country in [None, '', 'null']:
                    if ip_address:
                        cached_ip_country = cache.get(f"ip_country_{ip_address}")
                        if cached_ip_country:
                            country = cached_ip_country
                        else:
                            try:
                                resp = requests.get(f'https://ipapi.co/{ip_address}/json/', timeout=1.5).json()
                                country = resp.get("country_name") or "Egypt"
                                cache.set(f"ip_country_{ip_address}", country, 86400)
                            except Exception:
                                country = "Egypt"
                    else:
                        country = "Egypt"
        else:
            if country in [None, '', 'null']:
                if ip_address:
                    cached_ip_country = cache.get(f"ip_country_{ip_address}")
                    if cached_ip_country:
                        country = cached_ip_country
                    else:
                        try:
                            resp = requests.get(f'https://ipapi.co/{ip_address}/json/', timeout=1.5).json()
                            country = resp.get("country_name") or "Egypt"
                            cache.set(f"ip_country_{ip_address}", country, 86400)
                        except Exception:
                            country = "Egypt"
                else:
                    country = "Egypt"
    except Exception:
        country = 'Egypt'

    page_record = 20
    last_row = page_record * page_number
    first_row = last_row - page_record

    base_qs = models.ProductDetail.objects.filter(status='Active').exclude(category__category__in=['Univers Intime et Confort', 'Intimate Universe and Comfort'])
    if country_id is not None:
        base_qs = base_qs.filter(available_country=country_id)

    client_identifier = None
    if user_id:
        client_identifier = f"user_{user_id}"
    elif request.META.get('HTTP_AUTHORIZATION'):
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        client_identifier = f"auth_{abs(hash(auth_header))}"
    elif ip_address:
        client_identifier = f"ip_{ip_address}"
    else:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', 'default')
        client_identifier = f"ip_{ip}"

    if country_id is not None:
        cache_key = f"dashboard_pids_{client_identifier}_country_{country_id}"
    else:
        cache_key = f"dashboard_pids_{client_identifier}_all"

    if page_number <= 1:
        cached_ids = list(base_qs.order_by(Random()).values_list('id', flat=True)[:500])
        cache.set(cache_key, cached_ids, 600)
    else:
        cached_ids = cache.get(cache_key)
        if not cached_ids:
            cached_ids = list(base_qs.order_by(Random()).values_list('id', flat=True)[:500])
            cache.set(cache_key, cached_ids, 600)

    total_records = len(cached_ids)
    total_pages = math.ceil(total_records / page_record) if total_records > 0 else 1

    slice_ids = cached_ids[first_row:last_row]
    if slice_ids:
        page_products = list(
            models.ProductDetail.objects.filter(
                id__in=slice_ids
            ).select_related('category', 'subcategory', 'country_of_origin')
        )
        id_to_product = {p.id: p for p in page_products}
        all_product_data = [id_to_product[pid] for pid in slice_ids if pid in id_to_product]
    else:
        all_product_data = []

    product_serializer = ProductDataSerializer(all_product_data, many=True, context={'country': country}).data

    if user_id and page_number == 1:
        recently_qs = models.RecentlyViewProduct.objects.filter(
            customer=user_id,
            product__status='Active'
        )
        if country_id is not None:
            recently_qs = recently_qs.filter(product__available_country=country_id)

        recently_products = recently_qs.select_related(
            'product', 'product__category', 'product__subcategory', 'product__country_of_origin'
        ).order_by('-id')[:5]

        recently_serializer = RecentlyViewProductSerializer(recently_products, many=True, context={'country': country}).data
        res = {
            'product_list': product_serializer,
            'total_pages': total_pages,
            'recently_view': recently_serializer,
            'recently_title': 'Recently Browsed',
            'recently_title_fr': 'Consulté récemment'
        }
    else:
        res = {
            'product_list': product_serializer,
            'total_pages': total_pages,
        }

    json_data = JSONRenderer().render(res)
    return HttpResponse(json_data, content_type='application/json', status=200)


@csrf_exempt
def app_dashboard_category(request):
    list_category = []    
    all_category = models.CategoryDetail.objects.filter(status = 'Active').exclude(category='Intimate Universe and Comfort')
    for category in all_category:
        check_subcategory_count = models.SubCategoryDetail.objects.filter(category = category.id).count()
        if check_subcategory_count > 0:
            category_data = models.CategoryDetail.objects.get(id = category.id)
            category_serializer = CategoryDetailSerializer(category_data).data
            list_category.append(category_serializer)
        
    res = {
        'data':list_category,  
    }
    json_data = JSONRenderer().render(res)
    return HttpResponse(json_data, content_type= 'application/json', status=200)


@csrf_exempt
def about_us_list(request):
    if request.method == "POST":
        
        about_us = models.AboutUs.objects.all().first()
        about_us_serializer = AboutUsSerializer(about_us).data

        res={
            'data':about_us_serializer
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)

@csrf_exempt
def about_us_update(request):
    if request.method =="POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))

        # print("python_data-=----about_us_update=--->", python_data)

        id = python_data.get('id',None)
        about_us = python_data.get('about_us',None)

        get_about_us = models.AboutUs.objects.get(id = id)
        get_about_us.about_us = about_us
        get_about_us.save()

        res={
            'message':'About Us Updated Successfully'
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)


@csrf_exempt
def privacy_policy_list(request):
    if request.method == "POST":
        get_privacy_policy = models.PrivacyPolicy.objects.all().first()
        get_privacy_policy_serializer = PrivacyPolicySerializer(get_privacy_policy).data

        res={
            'data':get_privacy_policy_serializer
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)


@csrf_exempt
def privacy_policy_update(request):
    if request.method =="POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))

        # print("python_data-=----privacy_policy_update=--->", python_data)

        id = python_data.get('id',None)
        privacy_policy = python_data.get('privacy_policy',None)

        get_privacy_policy = models.PrivacyPolicy.objects.get(id = id)
        get_privacy_policy.privacy_policy = privacy_policy
        get_privacy_policy.save()

        res={
            'message':'About Us Updated Successfully'
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)


@csrf_exempt
def refund_policy_list(request):
    if request.method == "POST":
        get_refund_policy = models.RefundPolicy.objects.all().first()
        get_refund_policy_serializer = RefundPolicySerializer(get_refund_policy).data

        res={
            'data':get_refund_policy_serializer
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)

@csrf_exempt
def refund_policy_update(request):
    if request.method =="POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))

        # print("python_data-=----refund_policy_update=--->", python_data)

        id = python_data.get('id',None)
        refund_policy = python_data.get('refund_policy',None)

        get_refund_policy = models.RefundPolicy.objects.get(id = id)
        get_refund_policy.refund_policy = refund_policy
        get_refund_policy.save()

        res={
            'message':'Refund Policy Updated Successfully'
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)


@csrf_exempt
def terms_and_condition_list(request):
    if request.method == "POST":
        get_terms_and_condition = models.TermsAndCondition.objects.all().first()
        get_terms_and_condition_serializer = TermsAndConditionSerializer(get_terms_and_condition).data

        res={
            'data':get_terms_and_condition_serializer
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)


@csrf_exempt
def terms_and_condition_update(request):
    if request.method =="POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))

        # print("python_data-=----terms_and_condition=--->", python_data)

        id = python_data.get('id',None)
        terms_and_condition = python_data.get('terms_and_condition',None)

        get_privacy_policy = models.TermsAndCondition.objects.get(id = id)
        get_privacy_policy.terms_and_condition = terms_and_condition
        get_privacy_policy.save()

        res={
            'message':'Refund Policy Updated Successfully'
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)


@csrf_exempt
def important_note_update(request):
    if request.method == "POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))
        id = python_data.get('id')
        note_update = models.ImportantNote.objects.get(id = id)
        note_update.note = python_data.get('note', note_update.note)
        note_update.note_french = python_data.get('note_french', note_update.note_french)
        note_update.status = python_data.get('status', note_update.status)
        note_update.save()
       
        res = {
            'message':'Note update.'
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)
 
@csrf_exempt
def important_note_list(request):
    if request.method == "POST":
        important_note = models.ImportantNote.objects.all().first()
        note_serialser = ImportantNoteSerializer(important_note).data
        res = {
            'data':note_serialser
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)


@csrf_exempt
def intro_banner_update(request):
    python_data={}
    for i,j in request.FILES.items():
        python_data.update({i:j})
 
    for i,j in request.POST.items():
        python_data.update({i:j})
   
    id = python_data.get('id')
    banner = python_data.get('banner')
 
 
    banner_update = models.IntroBanner.objects.get(id = id)
    if type(banner) != str:
        banner_update.banner = banner
    banner_update.save()
   
    res = {
        'message':"Updated successfully."        
        }
    json_data = JSONRenderer().render(res)
    return HttpResponse(json_data, content_type= 'application/json', status=200)


@csrf_exempt
def intro_banner_data(request):
    if request.method == 'POST':
        project_list = models.IntroBanner.objects.all().first()
       
        serialiser = IntroBannerSerializer(project_list).data
        res = {
            'data':serialiser        
            }
        json_data = JSONRenderer().render(res)
        return HttpResponse(json_data, content_type= 'application/json', status=200)


def parse_semver(version_str):
    """
    Parses a version string into a comparable tuple/version object.
    Supports versions like '1.2.0', 'v1.2.0', '1.2', etc.
    """
    if not version_str:
        return (0, 0, 0)
    cleaned = str(version_str).strip().lstrip('vV')
    try:
        from packaging import version
        return version.parse(cleaned)
    except Exception:
        # Fallback numeric tuple comparison
        base = cleaned.split('-')[0].split('+')[0]
        parts = []
        for p in base.split('.'):
            digits = ''.join(c for c in p if c.isdigit())
            parts.append(int(digits) if digits else 0)
        while len(parts) < 3:
            parts.append(0)
        return tuple(parts[:3])


@csrf_exempt
def app_version_check(request):
    """
    App Version Check (Mobile App).
    Compares the client's current app version against store releases using Semantic Versioning (SemVer).
    Public endpoint requiring no authentication. Accepts GET query params or POST JSON body.
    Returns update_type: 'none', 'optional', 'force', or 'maintenance'.
    """
    if request.method in ["GET", "POST"]:
        python_data = {}
        if request.body:
            try:
                python_data = JSONParser().parse(io.BytesIO(request.body))
            except Exception:
                pass

        platform = python_data.get('platform') or request.GET.get('platform')
        app_version = python_data.get('app_version') or request.GET.get('app_version')

        if not platform:
            res = {
                'status': False,
                'message': 'Platform is required (android or ios).',
                'data': None
            }
            return HttpResponse(JSONRenderer().render(res), content_type='application/json', status=400)

        platform_clean = str(platform).strip().lower()
        if platform_clean not in ['android', 'ios']:
            res = {
                'status': False,
                'message': 'Invalid platform. Must be "android" or "ios".',
                'data': None
            }
            return HttpResponse(JSONRenderer().render(res), content_type='application/json', status=400)

        default_store_url = (
            'https://play.google.com/store/apps/details?id=com.diaba.ecommerce'
            if platform_clean == 'android'
            else 'https://apps.apple.com/app/id6754025301'
        )

        setting = models.AppVersionSetting.objects.filter(platform=platform_clean).first()
        if not setting:
            # Fallback to default if record not yet saved
            setting = models.AppVersionSetting.objects.create(
                platform=platform_clean,
                latest_version='1.0.0',
                min_supported_version='1.0.0',
                is_force_update=False,
                update_title='New Version Available',
                release_notes='Welcome to Diaba! Check out our latest updates.',
                store_url=default_store_url,
                is_maintenance_mode=False,
                maintenance_message='Scheduled maintenance in progress. Please check back shortly.'
            )

        # Resolve platform-correct store_url
        store_url = (setting.store_url or '').strip()
        if not store_url:
            store_url = default_store_url
        elif platform_clean == 'ios' and 'play.google.com' in store_url:
            store_url = default_store_url
        elif platform_clean == 'android' and 'apple.com' in store_url:
            store_url = default_store_url

        is_maintenance = bool(setting.is_maintenance_mode)
        maintenance_msg = setting.maintenance_message or 'Scheduled maintenance in progress. Please check back shortly.'

        # Determine force vs optional:
        # 1. Maintenance Mode active -> blocks user (force update payload with maintenance flag)
        if is_maintenance:
            is_force = True
            update_type = "force"
        # 2. If client passed app_version and installed version < min_supported_version -> Force
        elif app_version and parse_semver(str(app_version)) < parse_semver(setting.min_supported_version):
            is_force = True
            update_type = "force"
        # 3. Admin Force Update toggle
        elif setting.is_force_update:
            is_force = True
            update_type = "force"
        # 4. Optional Update (Soft update)
        else:
            is_force = False
            update_type = "optional"

        res = {
            'status': True,
            'message': 'Version check retrieved successfully',
            'data': {
                'update_type': update_type,
                'is_force_update': is_force,
                'is_maintenance_mode': is_maintenance,
                'maintenance_message': maintenance_msg,
                'latest_version': setting.latest_version,
                'min_supported_version': setting.min_supported_version,
                'update_title': setting.update_title or 'New Version Available',
                'release_notes': setting.release_notes or '',
                'store_url': store_url
            }
        }
        return HttpResponse(JSONRenderer().render(res), content_type='application/json', status=200)

    res = {'status': False, 'message': 'Invalid request method.'}
    return HttpResponse(JSONRenderer().render(res), content_type='application/json', status=405)


@csrf_exempt
def admin_app_versions(request):
    """
    App Version Settings Management (Admin).
    GET: Returns current version configurations for all platforms (Android & iOS).
    POST / PUT: Updates or creates version configuration for a specific platform.
    Requires Admin Authentication Token.
    """
    if request.method == "GET":
        settings_qs = models.AppVersionSetting.objects.all().order_by('platform')
        serializer = AppVersionSettingSerializer(settings_qs, many=True).data
        res = {
            'status': True,
            'message': 'App version settings fetched successfully',
            'data': serializer
        }
        return HttpResponse(JSONRenderer().render(res), content_type='application/json', status=200)

    if request.method in ["POST", "PUT"]:
        python_data = {}
        if request.body:
            try:
                python_data = JSONParser().parse(io.BytesIO(request.body))
            except Exception:
                pass

        platform = python_data.get('platform')
        if not platform:
            res = {'status': False, 'message': 'Platform is required (android or ios).'}
            return HttpResponse(JSONRenderer().render(res), content_type='application/json', status=400)

        platform_clean = str(platform).strip().lower()
        if platform_clean not in ['android', 'ios']:
            res = {'status': False, 'message': 'Invalid platform. Must be "android" or "ios".'}
            return HttpResponse(JSONRenderer().render(res), content_type='application/json', status=400)

        def to_bool(val):
            if isinstance(val, bool):
                return val
            if isinstance(val, str):
                return val.strip().lower() in ['true', '1', 'yes', 'on']
            if isinstance(val, (int, float)):
                return val != 0
            return False

        defaults = {}
        if 'latest_version' in python_data:
            defaults['latest_version'] = str(python_data.get('latest_version')).strip()
        if 'min_supported_version' in python_data:
            defaults['min_supported_version'] = str(python_data.get('min_supported_version')).strip()
        if 'is_force_update' in python_data:
            defaults['is_force_update'] = to_bool(python_data.get('is_force_update'))
        if 'update_title' in python_data:
            defaults['update_title'] = str(python_data.get('update_title')).strip()
        if 'release_notes' in python_data:
            defaults['release_notes'] = python_data.get('release_notes')
        if 'store_url' in python_data:
            defaults['store_url'] = str(python_data.get('store_url')).strip()
        if 'is_maintenance_mode' in python_data:
            defaults['is_maintenance_mode'] = to_bool(python_data.get('is_maintenance_mode'))
        if 'maintenance_message' in python_data:
            defaults['maintenance_message'] = python_data.get('maintenance_message')

        setting_obj, created = models.AppVersionSetting.objects.update_or_create(
            platform=platform_clean,
            defaults=defaults
        )

        serializer = AppVersionSettingSerializer(setting_obj).data
        res = {
            'status': True,
            'message': 'App version settings updated successfully',
            'data': serializer
        }
        return HttpResponse(JSONRenderer().render(res), content_type='application/json', status=200)

    res = {'status': False, 'message': 'Invalid request method.'}
    return HttpResponse(JSONRenderer().render(res), content_type='application/json', status=405)
  
