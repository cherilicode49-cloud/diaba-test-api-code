from django.views.decorators.csrf import csrf_exempt
from diabaApp import models
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from django.http import HttpResponse
import io
import math, random , calendar
from datetime import datetime, timedelta
from django.template.loader import get_template
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Sum, Count, F
import json
from django.http import JsonResponse
from django.db.models import Max, Min
from django.db.models.functions import Cast, TruncMonth, Coalesce, ExtractMonth, Round, TruncDate
from django.utils import timezone
from django.db.models import Sum, Count, F, Q

import  requests
from diabaApp.serializer import VendorDetailSerializer, ProductDetailSerializer, ProductModelSerializer, AdminProductModelVariantSerializer, \
    VendorProductPriceSerializer, AdminProductDataSerializer, AdminProductModelDataSerializer, VendorProductvariantSerializer, \
    VendorDataSerializer, VendorProductDataSerializer, ProductSearchSerializer


@csrf_exempt
def vendor_update(request):
    if request.method == 'POST':
        # python_data = JSONParser().parse(io.BytesIO(request.body))
        python_data={}
        for i,j in request.FILES.items():
            python_data.update({i:j})
        
        for i,j in request.POST.items():
            python_data.update({i:j})
        
        # print(python_data, 'python_data')
        now = datetime.now()
        date_time = now.strftime('%Y-%m-%d, %H:%M:%S')
        id = python_data.get('id')
        check_vendor = models.VendorDetail.objects.filter(id = id).count()
        if check_vendor == 1:
            get_vendor_email = models.VendorDetail.objects.get(id = id)
            get_email = get_vendor_email.email
            email = python_data.get('email')
            if get_email == email:
                vendor = models.VendorDetail.objects.get(id = id)
                vendor.email = python_data.get('email', vendor.email)
                vendor.category_id = python_data.get('category', vendor.category)
                # vendor.subcategory_id = python_data.get('subcategory', vendor.subcategory)
                vendor.company_name = python_data.get('company_name', vendor.company_name)
                vendor.business_type = python_data.get('business_type', vendor.business_type)
                vendor.legal_form = python_data.get('legal_form', vendor.legal_form)
                vendor.city = python_data.get('city', vendor.city)
                vendor.country = python_data.get('country', vendor.country)
                vendor.company_start_date = python_data.get('company_start_date', vendor.company_start_date)
                vendor.office_address = python_data.get('office_address', vendor.office_address)
                vendor.total_employee = python_data.get('total_employee', vendor.total_employee)
                vendor.production_capacity = python_data.get('production_capacity', vendor.production_capacity)
                vendor.vendor_name = python_data.get('vendor_name', vendor.vendor_name)
                vendor.document_type = python_data.get('document_type', vendor.document_type)
                if type(python_data.get('document')) != str:
                    vendor.document = python_data.get('document', vendor.document)

                vendor.is_verify = python_data.get('is_verify', vendor.is_verify)
                vendor.website = python_data.get('website', vendor.website)
                vendor.save()
            else:
                check_email = models.VendorDetail.objects.filter(email = email).count()
                if check_email == 1:
                    res = {
                        'message':'This email is already registerd.'        
                        }
                    json_data = JSONRenderer().render(res)
                    return HttpResponse(json_data, content_type= 'application/json', status=406)
                else:
                    digits = "abcdefghjiklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
                    password = ""
                    for i in range(8) :
                        password += digits[math.floor(random.random() * 52)]

                    vendor = models.VendorDetail.objects.get(id = id)
                    vendor.email = python_data.get('email', vendor.email)
                    vendor.category_id = python_data.get('category', vendor.category)
                    # vendor.subcategory_id = python_data.get('subcategory', vendor.subcategory)
                    vendor.company_name = python_data.get('company_name', vendor.company_name)
                    vendor.business_type = python_data.get('business_type', vendor.business_type)
                    vendor.legal_form = python_data.get('legal_form', vendor.legal_form)
                    vendor.city = python_data.get('city', vendor.city)
                    vendor.country = python_data.get('country', vendor.country)
                    vendor.company_start_date = python_data.get('company_start_date', vendor.company_start_date)
                    vendor.office_address = python_data.get('office_address', vendor.office_address)
                    vendor.total_employee = python_data.get('total_employee', vendor.total_employee)
                    vendor.production_capacity = python_data.get('production_capacity', vendor.production_capacity)
                    vendor.vendor_name = python_data.get('vendor_name', vendor.vendor_name)
                    vendor.document_type = python_data.get('document_type', vendor.document_type)
                    if type(python_data.get('document')) != str:
                        vendor.document = python_data.get('document', vendor.document)

                    vendor.is_verify = python_data.get('is_verify', vendor.is_verify)
                    vendor.website = python_data.get('website', vendor.website)
                    vendor.password = password
                    vendor.save()
                    email = vendor.email
                    try:
                        context = {
                            'email':email,
                            'password': password
                        }
                        htmlgen = get_template("vendor_confirm_mail.html").render(context)

                        send_mail(
                            subject='Your Updated Login Credentials for Diaba Marketplace',
                            message='password',
                            from_email=settings.EMAIL_HOST_USER,
                            recipient_list=[email],
                            fail_silently=False,
                            html_message=htmlgen
                        )
                        
                        # print("MAIL SENT SUCCESSFULLY-=-=-=-=-=-=-=-")
                    except Exception as e:
                        print("print------>",e)


            res = {
                'message':"vendor Update Successfully.",
                
                }
            json_data = JSONRenderer().render(res)
            return HttpResponse(json_data, content_type= 'application/json', status=200)
        else: 
            res = {
                'message':'Something went wrong.'        
                }
            json_data = JSONRenderer().render(res)
            return HttpResponse(json_data, content_type= 'application/json', status=406)



@csrf_exempt
def vendor_detail(request):
    json_data = request.body
    stream = io.BytesIO(json_data)
    python_data = JSONParser().parse(stream)
    vendor = python_data.get('vendor')
    check_vendor = models.VendorDetail.objects.filter(id = vendor).count()
    if check_vendor == 1:
        list_data = []
        vendor_data = models.VendorDetail.objects.get(id = vendor)
        vendor_seraliser = VendorDetailSerializer(vendor_data).data
        
        get_all_product = models.VendorProductPrice.objects.filter(vendor = vendor).values_list('product', flat=True)
        get_all_product = list(set(get_all_product))
        get_all_product = [item for item in get_all_product if item is not None]
        
        list_data = []
        for product in get_all_product:
            product = models.ProductDetail.objects.get(id = product)
            get_all_product_serializer = ProductDetailSerializer(product).data
            get_all_model = models.ProductModel.objects.filter(product = product)
            
            list_model = []
            for model in get_all_model:
                model = models.ProductModel.objects.get(id = model.id)
                model_serializer = ProductModelSerializer(model).data
                get_all_variant = models.ProductModelVariant.objects.filter(model = model)

                list_variant = []
                for variant in get_all_variant:
                    variant = models.ProductModelVariant.objects.get(id = variant.id)
                    variant_serialiser = AdminProductModelVariantSerializer(variant).data
                    
                    check_varint = models.VendorProductPrice.objects.filter(variant = variant.id, vendor = vendor).count()
                    if check_varint == 1:
                        # print(variant, 'avriant')
                        varint = models.VendorProductPrice.objects.get(variant = variant, vendor = vendor)
                        price_serialiser = VendorProductPriceSerializer(varint).data
                    
                        variant_serialiser.update({'vendor_data':price_serialiser})
                    
                        list_variant.append(variant_serialiser)

                model_serializer.update({'variant_data':list_variant})
            
                list_model.append(model_serializer)

            get_all_product_serializer.update({'model':list_model})
            list_data.append(get_all_product_serializer)

        res = {
            'data':vendor_seraliser,
            'product_data': list_data
        }
        json_data = JSONRenderer().render(res)
        return HttpResponse(json_data, content_type= 'application/json', status=200)

    res = {
        'meassage': "Something went wrong."
    }
    json_data = JSONRenderer().render(res)
    return HttpResponse(json_data, content_type= 'application/json', status=200)


@csrf_exempt
def vendor_detail_admin(request):
    if request.method == 'POST':
        python_data = JSONParser().parse(io.BytesIO(request.body))
        vendor = python_data.get('vendor')
        
        get_vendor_data = models.VendorDetail.objects.get(id = vendor)
        data = VendorDetailSerializer(get_vendor_data).data
        
        res={
            'data':data
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)



@csrf_exempt
def vendor_product_admin(request):
    if request.method == 'POST':
        python_data = JSONParser().parse(io.BytesIO(request.body))
        vendor = python_data.get('vendor')
        
        datadata = models.VendorProductPrice.objects.filter(vendor = vendor).values_list('product', 'model').distinct()
        get_all_product = models.VendorProductPrice.objects.filter(vendor = vendor).values_list('product', flat=True).distinct('product_id').order_by('product')
        print(get_all_product, 'get_all_product')
        list_data = []
        for product in get_all_product:
           
            get_product_data = models.ProductDetail.objects.get(id = product)
            product_data = AdminProductDataSerializer(get_product_data).data

            get_all_model = models.VendorProductPrice.objects.filter(product = product, vendor = vendor).values_list('model', flat=True).distinct()
            list_model = []
            for model in get_all_model:
                get_model_data = models.ProductModel.objects.get(id = model)
                model_data = AdminProductModelDataSerializer(get_model_data).data

                get_all_variant = models.VendorProductPrice.objects.filter(product = product, vendor = vendor, model = model).values_list('variant', flat=True).distinct()
                list_variant = []
                for variant in get_all_variant:
                    
                    get_variant_data = models.ProductModelVariant.objects.get(id = variant)
                    variant_data = AdminProductModelVariantSerializer(get_variant_data).data
                    
                    price_data = models.ProductModelVariant.objects.filter(product=product).aggregate(
                        max_price=Max('price'),
                        min_price=Min('price')
                    )
                    max_price = price_data['max_price']
                    min_price = price_data['min_price']

                    get_all_vendor = models.VendorProductPrice.objects.get(product = product, vendor = vendor, model = model, variant = variant)
                    vendor_data = VendorProductvariantSerializer(get_all_vendor).data
                    variant_data.update({'vendor_data':vendor_data})
                    list_variant.append(variant_data)
                model_data.update({'variant_data':list_variant})
                list_model.append(model_data)
            product_data.update({'model_data':list_model,  'max_price':max_price, 'min_price':min_price})
            list_data.append(product_data)
        
        # print(list_data, 'list_datalist_data')
        
        res={
            'data':list_data
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)

@csrf_exempt
def vendor_name_list(request):
    if request.method == "POST":    
        vendor_list = models.VendorDetail.objects.all()
        serializer = VendorDataSerializer(vendor_list, many=True).data
        res={
            'data':serializer
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)

      
@csrf_exempt
def vendor_list_category_subcategory(request):
    if request.method == "POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))

        # print(python_data, 'python_data')
        category = int(python_data.get('category'))
        subcategory = int(python_data.get('subcategory'))

        
        vendor_list = models.VendorDetail.objects.filter(category=category, subcategory = subcategory)
        serializer = VendorDataSerializer(vendor_list, many=True).data
        res={
            'data':serializer
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)


@csrf_exempt
def variant_vendor_list(request):
    if request.method == 'POST':
        python_data = JSONParser().parse(io.BytesIO(request.body))
        variant = python_data.get('variant')

        list_vendor = models.VendorProductPrice.objects.filter(variant = variant)
        vendor_data = VendorProductDataSerializer(list_vendor, many=True).data
        
        res={
    
            'data':vendor_data
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)



@csrf_exempt
def vendor_search_product(request):
    json_data = request.body
    stream = io.BytesIO(json_data)
    python_data = JSONParser().parse(stream)

    category = python_data.get('category')
    subcategory = python_data.get('subcategory')
    super_subcategory = python_data.get('super_subcategory')
    product_name = python_data.get('product_name')
    # print(python_data, 'python_data')
    filter_condition = {}
        
    
    if category and category != None and category != "null" and category != "":
        filter_condition['category'] = category

    if subcategory and subcategory != None and subcategory != "null" and subcategory != "":
        filter_condition['subcategory'] = subcategory

    if super_subcategory and super_subcategory != None and super_subcategory != "null" and super_subcategory != "":
        filter_condition['super_subcategory'] = super_subcategory     

    if product_name and product_name != None and product_name != "null" and product_name != "":
        filter_condition['product_name__icontains'] = product_name     

    # print(filter_condition, 'filter_condition')
    if filter_condition != {}:
        get_product_list = models.ProductDetail.objects.filter(**filter_condition).order_by('-id')
        serializer = ProductSearchSerializer(get_product_list, many=True).data
    else:
        serializer = []

    res = {
        'data': serializer 
    }
    json_data = JSONRenderer().render(res)
    return HttpResponse(json_data, content_type= 'application/json', status=200)

@csrf_exempt
def vendor_product_search(request):
    json_data = request.body
    stream = io.BytesIO(json_data)
    python_data = JSONParser().parse(stream)
    product_name = python_data.get('product_name')

    seach_product = models.ProductDetail.objects.filter(product_name__icontains = product_name)
    serializer = ProductSearchSerializer(seach_product, many=True).data
    
    res = {
        'data': serializer
    }
    json_data = JSONRenderer().render(res)
    return HttpResponse(json_data, content_type= 'application/json', status=200)

            
@csrf_exempt
def vendor_approve_reject(request):
    if request.method == "POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))

        id = python_data.get('id')
        is_verify = python_data.get('is_verify')

        check_vendor = models.VendorDetail.objects.filter(id = id).count()
        if check_vendor == 1:
            vendor = models.VendorDetail.objects.get(id = id)
            vendor.is_verify = python_data.get('is_verify', vendor.is_verify)
            if is_verify == "rejected":
                vendor.reject_reason = python_data.get('reject_reason', vendor.reject_reason)
            vendor.save()        
            res={
                'message':'Vendor Status Update Successfully'
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)
        else:
            res = {
                'message':'Enter Valid id.'        
                }
            json_data = JSONRenderer().render(res)
            return HttpResponse(json_data, content_type= 'application/json', status=406)

@csrf_exempt
def pending_order_vendor_count(request):
    if request.method =="POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))
        vendor = python_data.get('vendor')

        product_count = models.VendorOrderDetail.objects.filter(vendor = vendor, variant__status = "pending").count()
        
        res={
            'total_count': product_count
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)


@csrf_exempt
def vendor_credentials_resend(request):
    if request.method == 'POST':
        python_data = JSONParser().parse(io.BytesIO(request.body))
        id = python_data.get('id')
        if models.VendorDetail.objects.filter(id = id).exists():
            vendor = models.VendorDetail.objects.get(id = id)
            try:
                context = {
                    'vendor_email':vendor.email,
                    'vendor_password': vendor.password, 
                    'vendor_name':vendor.company_name,
                    'current_year':datetime.now().year
                }

                htmlgen = get_template("resend_vendor_creds.html").render(context)
                # send_mail('Diaba - Team Onboarding',"password",'settings.EMAIL_HOST_USER',[email], fail_silently=False, html_message=htmlgen)

                send_mail(
                    subject='Diaba - Login Credentials',
                    message='password',
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[vendor.email],
                    fail_silently=False,
                    html_message=htmlgen
                )
            except Exception as e:
                print("print------>",e)
            res={
                'message':"Vendor credentials resent successfully."
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)
        else:
            res = {
                'message':'Vendor Not Found'
            }
            json_data = JSONRenderer().render(res)
            return HttpResponse(json_data, content_type= 'application/json', status=406)     


@csrf_exempt
def vendor_revenue(request):
    if request.method == "POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))
        vendor = python_data.get('vendor')

        today = datetime.today()
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)

        start_of_month = today.replace(day=1)

        if today.month == 12:
            next_month = today.replace(year=today.year + 1, month=1, day=1)
        else:
            next_month = today.replace(month=today.month + 1, day=1)

        end_of_month = next_month - timedelta(days=1)
        
        # today_data = list(models.VendorPaymentTracker.objects.filter(vendor = vendor, created_at__date = today.date()).values_list('amount', flat=True))
        # today_revenue = int(sum(today_data))

        active_products = models.ProductDetail.objects.filter(vendor = vendor, status = "Active").count()

        total_orders_count = models.VendorOrderDetail.objects.filter(vendor = vendor).count()
        total_order_data = models.VendorOrderDetail.objects.filter(vendor = vendor)
        total_variants = models.VendorProductPrice.objects.filter(vendor = vendor).count()

        total_revenue = 0
        for order in total_order_data:
            get_vendor_variant = models.VendorProductPrice.objects.filter(variant = order.variant.variant.id, vendor = vendor).first()
            total_revenue += int(int(get_vendor_variant.price) * int(order.variant.quantity))
        
        amount_data = list(models.VendorPaymentTracker.objects.filter(vendor = vendor, payment_type="Pay").values_list('amount', flat=True))
        # total_order_data = models.VendorPaymentTracker.objects.filter(vendor = vendor, payment_type="Pay").count()
        # total_revenue = int(sum(amount_data))

        average_order_value = round(total_revenue / total_orders_count) if total_orders_count > 0 else 0

        pending_order_count =  models.VendorOrderDetail.objects.filter(vendor = vendor, variant__vendor_status = "pending").count()

        pending_products = models.ProductDetail.objects.filter(vendor = vendor, product_verification = "Pending").count()

        res = {
            'active_products' : active_products,
            'total_orders_count' : total_orders_count,
            'total_variants' : total_variants,

            # 'total_order_data' : total_order_data,
            'total_revenue':total_revenue,
            'average_order_value':average_order_value,

            'pending_order_count':pending_order_count,
            'pending_products':pending_products,

        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)

@csrf_exempt
def vendor_total_income(request):
    if request.method == "POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))
        vendor = python_data.get('vendor')
        total_income = models.VendorPaymentTracker.objects.filter(vendor = vendor, payment_type = 'Pay').aggregate(total_income = Sum('amount'))['total_income'] or 0
        res = {
            'total_income': total_income
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)


@csrf_exempt
def vendor_total_payout(request):
    if request.method == "POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))
        vendor = python_data.get('vendor')
        total_payout = models.VendorPaymentTracker.objects.filter(vendor = vendor, payment_type = 'Paid').aggregate(total_payout = Sum('amount'))['total_payout'] or 0
        res = {
            'total_payout': total_payout
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)

@csrf_exempt
def vendor_pending_payment(request):
    if request.method == "POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))
        vendor = python_data.get('vendor')
        pending_payment = models.VendorPaymentTracker.objects.filter(vendor = vendor).order_by('-id').values_list('remaining_amount', flat=True).first() or 0
        res = {
            'pending_payment': pending_payment
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)


@csrf_exempt
def vendor_analytics_count(request):
    if request.method == "POST":
        current_dt = datetime.now()

        last_30_days = current_dt - timedelta(days=30)

        total_vendor = models.VendorDetail.objects.all().count()
        new_vendor = models.VendorDetail.objects.filter(created_at_datetime__gt = last_30_days).count()

        all_vendor_profit = list(models.VendorOrderDetail.objects.annotate(
            total_profit = Sum('variant__total_vendor_price')
        ).values_list('total_profit', flat=True))
        print("all_vendor_profit===>",all_vendor_profit)

        total_vendor_profit = sum(profit for profit in all_vendor_profit if isinstance(profit,int))

        res={
            "total_vendor":total_vendor,
            "new_vendor":new_vendor,
            "total_vendor_profit":total_vendor_profit,
        }
        return HttpResponse(JSONRenderer().render(res), content_type="application/json", status=200)


@csrf_exempt
def vendor_monthly_user(request):
    if request.method == "POST":
        try:
            json_data = request.body
            stream = io.BytesIO(json_data)
            python_data = JSONParser().parse(stream)
        except:
            res={
                "message":"Send Me atleast Year with value None/null in Payload"
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 406)
        
        year = python_data.get('year')

        if year in [None,'','null']:
            year = datetime.now().year

        year = int(year)

        start = datetime(year, 1, 1)
        end = datetime(year+1, 1, 1)

        customer_qs = models.VendorDetail.objects.filter(
            created_at_datetime__gt = start, 
            created_at_datetime__lt = end
        )

        monthly_data = (
            customer_qs.annotate(month = ExtractMonth('created_at_datetime')).values('month').annotate(count=Count('id')).order_by('month')
        )
        total_customer_count = customer_qs.count()

        result = {calendar.month_abbr[i].upper(): 0 for i in range(1, 13)}

        result.update({
            calendar.month_abbr[item['month']].upper(): item['count']
            for item in monthly_data
        })

        res = {
            "year": year,
            "data": result,
            "total_customer_count":total_customer_count
        }

        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200) 

     
@csrf_exempt
def top_vendor_net_profit(request):
    if request.method == "POST":
        vendor_order_detail = models.VendorOrderDetail.objects.values(
            'vendor',
            company_name = F('vendor__company_name'),
            ).annotate(
            total_profit = Sum('variant__total_vendor_price')
        ).filter(total_profit__isnull = False).order_by('-total_profit')[:5]

        res = {
            'vendor_order_detail':vendor_order_detail
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)

@csrf_exempt
def categories_wise_vendor(request):
    if request.method == "POST":
        vendor_order_detail = models.VendorOrderDetail.objects.values(
            category_french = F('variant__product__category__category_french'),
        ).annotate(vendor_count = Count('vendor',distinct=True))

        res = {
            'vendor_order_detail':vendor_order_detail
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)



@csrf_exempt
def vendor_list_analyse(request):
    if request.method == "POST":
        vendor_order_detail = models.VendorOrderDetail.objects.values(
            'vendor',
            company_name = F('vendor__company_name'),
            status = F('vendor__status'),
            category_name = F('variant__product__category__category'),
            ).annotate(
            total_profit = Sum('variant__total_vendor_price'),
            total_order = Count('vendor'),
        ).filter(total_profit__isnull = False).order_by('-total_profit')[:5]

        res = {
            'vendor_order_detail':vendor_order_detail
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)


@csrf_exempt
def all_vendor_list(request):
    if request.method == 'POST':
        python_data = JSONParser().parse(io.BytesIO(request.body))
            
        # print("python_data--all_product_list--->", python_data)

        today = timezone.now()
        
        search_key = python_data.get('search_key',None)

        page_number = int(python_data.get('page_number', 1))
        row_size = int(python_data.get('row_data', 10))
        last_row = row_size * page_number
        first_row = last_row - row_size

        search_query = Q()
        if search_key:
            search_query = Q(company_name__icontains=search_key) | Q(vendor_name__icontains=search_key) | Q(phone_number__icontains=search_key) | Q(email__icontains=search_key)

        vendorData = models.VendorDetail.objects.filter(search_query).distinct('id')
        vendor_count = vendorData.count()
        vendor_list = vendorData.order_by('-id')[first_row:last_row]
        serializer = VendorDetailSerializer(vendor_list, many=True).data

        res = {
            'data': serializer, 
            'vendor_count': vendor_count 
        }
        json_data = JSONRenderer().render(res)
        return HttpResponse(json_data, content_type= 'application/json', status=200)