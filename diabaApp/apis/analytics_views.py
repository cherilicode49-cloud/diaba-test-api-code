from django.views.decorators.csrf import csrf_exempt
from diabaApp import models
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from django.http import HttpResponse
import io
import math, random , calendar
from datetime import datetime, timedelta
from django.conf import settings
from django.db.models import Sum, Count, F, Q, ExpressionWrapper
from django.db.models.functions import Cast, TruncMonth, Coalesce, ExtractMonth, Round, TruncDate
from django.db.models.fields import FloatField
from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Q, F, Count, Case, Sum, When, IntegerField, Value, OuterRef, Subquery, ExpressionWrapper, CharField, FloatField



BASE_URL = settings.BASE_URL
IMAGE_URL = settings.IMAGE_URL


@csrf_exempt
def dashboard_overview(request):
    if request.method == "POST":
        total_vendors = models.VendorDetail.objects.all().count()
        total_orders = models.OrderDetail.objects.all().count()
        confirmed_orders = models.OrderDetail.objects.filter(Q(status = "completed")|Q(status = "pending", payment_type__in = ["cash","bank transfer"]), order_status="pending").count()
        total_products = models.ProductDetail.objects.all().count()
        active_customer = models.CustomerDetail.objects.filter(status = "Active").count()
        chat_agents_count = models.ChatAgentDetail.objects.all().count()
        influencers_count = models.InfluencerDetail.objects.all().count()
        warehouses_count = models.WarehouseDetail.objects.all().count()

        res={
            "total_vendors" : total_vendors,
            "total_orders" : total_orders,
            "confirmed_orders" : confirmed_orders,
            "total_products" : total_products,
            "active_customer" : active_customer,
            "chat_agents_count" : chat_agents_count,
            "influencers_count" : influencers_count,
            "warehouses_count" : warehouses_count,
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)



@csrf_exempt
def dashboard_order_status_graph(request):
    if request.method == "POST":

        try:
            json_data = request.body
            stream = io.BytesIO(json_data)
            python_data = JSONParser().parse(stream)
        except:
            res={
                "message":"Send Me atleast last_record with value None/null in Payload"
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 406)

        last_record = python_data.get('last_record',7)

        if last_record in [None,'','null']:
            last_record = 7

        last_days = datetime.now() - timedelta(days=last_record)

        print("python_data===>",python_data)
        print("last_days===>",last_days)

        order_status_data = (
            models.OrderDetail.objects
            .filter(created_at__gte=last_days)
            .annotate(day=TruncDate('created_at'))
            .values('day')
            .annotate(

                # Raw Counts
                confirmed_count=Count(
                    'id',
                    filter=Q(
                        status="completed",
                        order_status="pending"
                    )
                ),

                pending_count=Count(
                    'id',
                    filter=Q(
                        status="pending",
                        payment_type__in=["cash", "bank transfer"],
                        order_status="pending"
                    )
                ),

                in_progress_count=Count(
                    'id',
                    filter=Q(order_status="In Progress")
                ),

                failed_count=Count(
                    'id',
                    filter=Q(order_status="failed")
                ),

                inquiry_count=Count(
                    'id',
                    filter=Q(order_status="inquiry")
                ),

                completed_count=Count(
                    'id',
                    filter=Q(order_status="Completed")
                ),

                total_orders=Count('id')
            )

            # Percentages
            .annotate(

                confirmed=ExpressionWrapper(
                    (F('confirmed_count') * 100.0) / F('total_orders'),
                    output_field=FloatField()
                ),

                pending=ExpressionWrapper(
                    (F('pending_count') * 100.0) / F('total_orders'),
                    output_field=FloatField()
                ),

                in_progress=ExpressionWrapper(
                    (F('in_progress_count') * 100.0) / F('total_orders'),
                    output_field=FloatField()
                ),

                failed=ExpressionWrapper(
                    (F('failed_count') * 100.0) / F('total_orders'),
                    output_field=FloatField()
                ),

                inquiry=ExpressionWrapper(
                    (F('inquiry_count') * 100.0) / F('total_orders'),
                    output_field=FloatField()
                ),

                completed=ExpressionWrapper(
                    (F('completed_count') * 100.0) / F('total_orders'),
                    output_field=FloatField()
                ),
            )

            .values(
                'day',
                'confirmed',
                'pending',
                'in_progress',
                'failed',
                'inquiry',
                'completed',
                'total_orders'
            )

            .order_by('day')
        )
    
        res={
            "order_status_data":order_status_data
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)


@csrf_exempt
def monthly_dashboard_revenue_graph(request):
    if request.method == "POST":
        try:
            python_data = JSONParser().parse(io.BytesIO(request.body))

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
        revenue_data = (
            models.OrderDetail.objects.filter(
                Q(status = "completed")|Q(status = "pending", payment_type__in = ["cash","bank transfer"], ordertransaction__cash_status = "True"),
                created_at__gt = start, 
                created_at__lt = end,
            )
            .annotate(month = ExtractMonth('created_at'))
            .values('month')
            .annotate(total_revenue=Sum('total_price'))
            .order_by('month')
        )
        result = {calendar.month_abbr[i].upper(): 0 for i in range(1, 13)}
        
        for item in revenue_data:
            month_abbr = calendar.month_abbr[item['month']].upper()
            result[month_abbr] = item['total_revenue'] or 0
        
        res = {
            "year": year,
            "revenue_data": result,
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)


@csrf_exempt
def dashboard_platform_module_count(request):
    if request.method == "POST":
        modules_list = []

        agent_count = models.ChatAgentDetail.objects.filter(status="Active").count()
        currency_converter_count = models.CurrencyConverter.objects.filter(status="Active").count() + 1
        total_bank_details_count = models.CountryWiseBankDetail.objects.filter(status="Active").count()
        category_count = models.CategoryDetail.objects.filter(status="Active").count()
        subcategory_count = models.SubCategoryDetail.objects.filter(status="Active").count()
        super_subcategory_count = models.SuperSubCategoryDetail.objects.filter(status="Active").count()
        vendor_count = models.VendorDetail.objects.filter(status="Active").count()
        cargo_count = models.CargoDetail.objects.filter(status="Active").count()
        chat_room_count = models.ChatRoom.objects.filter(status="Active").count()

        
        modules_list.append(
            {
                "module_name":"Chat Agent",
                "count":agent_count
            },
            {
                "module_name":"Currency Converter",
                "count":currency_converter_count
            },
            {
                "module_name":"Total Bank Details",
                "count":total_bank_details_count
            },
            {
                "module_name":"Category",
                "count":category_count
            },
            {
                "module_name":"Subcategory",
                "count":subcategory_count
            },
            {
                "module_name":"Super Subcategory",
                "count":super_subcategory_count
            },
            {
                "module_name":"Vendor",
                "count":vendor_count
            },
            {
                "module_name":"Cargo",
                "count":cargo_count
            },
            {
                "module_name":"Chat Room",
                "count":chat_room_count
            },
        )

        res={
            "modules_list":modules_list
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)


@csrf_exempt
def dashboard_currencry_exchange_rate_base(request):
    if request.method == "POST":
        try:
            python_data = JSONParser().parse(io.BytesIO(request.body))

        except:
            res={
                "message":"Send Me atleast base_currency with value None/null in Payload"
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 406)
        
        base_currency = python_data.get('base_currency')
        if base_currency in [None,'','null']:
            base_currency = 'XOF'

        all_currency = models.CurrencyConverter.objects.all().exclude(currency_code=base_currency).values('currency_code', 'system_rate')

        get_base_rate = 0
        try:
            get_base_rate = models.CurrencyConverter.objects.filter(currency_code=base_currency).values_list('system_rate', flat=True).first()
        except:
            res={
                "message":"Base currency not found"
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 406)

        for currency in all_currency:
            currency['system_rate'] = round(currency['system_rate'] / get_base_rate if currency['system_rate'] else 0, 2)

        res={
            "base_currency":base_currency,
            "all_currency":all_currency,
            "get_base_rate":get_base_rate,
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)


@csrf_exempt
def app_admin_counts(request):
    if request.method == "POST":
        total_vendors = models.VendorDetail.objects.all().count()
        total_orders = models.OrderDetail.objects.all().count()
        total_customer = models.CustomerDetail.objects.all().count()
        
        res={
            "total_vendors":total_vendors,
            "total_orders":total_orders,
            "total_customer":total_customer,
            "total_revenue":0,
        }
        return HttpResponse(JSONRenderer().render(res), content_type="application/json", status=200)

        
@csrf_exempt
def product_analytics_count(request):
    if request.method == "POST":
        active_products = models.ProductDetail.objects.filter(status = 'Active').count()
        inactive_products = models.ProductDetail.objects.filter(status = 'Inactive').count()
        total_products = models.ProductDetail.objects.all().count()
        check_total_products = active_products + inactive_products

        total_product_inquiries = models.ProductInquiry.objects.all().count()
        pending_inquiries = models.ProductInquiry.objects.filter(status = 'Pending').count()

        res={
            'active_products':active_products,
            'inactive_products':inactive_products,
            'total_products':total_products,
            'check_total_products':check_total_products,
            'total_product_inquiries':total_product_inquiries,
            'pending_inquiries':pending_inquiries,
        }
        return HttpResponse(JSONRenderer().render(res), content_type="application/json", status=200)

    
@csrf_exempt
def product_monthly_addition_graph(request):
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

        product_qs = models.ProductDetail.objects.filter(
            created_at__gt = start, 
            created_at__lt = end
        )
        monthly_data = (
            product_qs.annotate(month = ExtractMonth('created_at')).values('month').annotate(count=Count('id')).order_by('month')
        )
        total_product_count = product_qs.count()

        result = {calendar.month_abbr[i].upper(): 0 for i in range(1, 13)}

        result.update({
            calendar.month_abbr[item['month']].upper(): item['count']
            for item in monthly_data
        })

        res = {
            "year": year,
            "data": result,
            "total_product_count":total_product_count
        }

        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)

@csrf_exempt
def product_category_based_analysis(request):
    if request.method == "POST":
        total_products = models.ProductDetail.objects.count()
        category_data = (
            models.ProductDetail.objects
            .values(
                category_name=F('category__category')
            )
            .annotate(
                total_product=Count('id')
            )
            .annotate(
                percentage=Cast(
                    (F('total_product') * 100.0) / total_products,
                    output_field=FloatField()
                )
            ).order_by('-total_product')
        )

        res={
            "category_data":category_data,
            "total_products":total_products
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)

@csrf_exempt
def product_top_selling_variants(request):
    if request.method == "POST":
        top_variants = (
            models.ProductOrderDetail.objects.values(
                variantId=F('variant__id'),
                product_name=F('variant__product__product_name'),
                orderId=F('order__order_id'),
            )
            .annotate(
                total_sold=Sum('quantity')
            )
            .order_by('-total_sold')[:10]
        )
        res={
            "top_variants":top_variants
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)


@csrf_exempt
def product_top_add_to_cart_analysis(request):
    if request.method == "POST":
        top_carted_products = (
            models.CartDetail.objects.values(
                product_name=F('product__product_name'),
                productId=F('product__id'),
            )
            .annotate(
                total_carted=Count('id')
            )
            .order_by('-total_carted')[:10]
        )
        res={
            "top_carted_products":top_carted_products
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)


@csrf_exempt
def product_wishlist_analysis(request):
    if request.method == "POST":
        top_wishlisted_products = (
            models.WishlistDetail.objects.values(
                product_name=F('product__product_name'),
                productId=F('product__id'),
            )
            .annotate(
                total_wishlisted=Count('id')
            )
            .order_by('-total_wishlisted')[:10]
        )
        res={
            "top_wishlisted_products":top_wishlisted_products
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)
    

@csrf_exempt
def product_recent_inquiry_list_analysis(request):
    if request.method == "POST":
        recent_inquired_products = (
            models.ProductInquiry.objects.values(
                'id',
                'status',
                'created_at',
                'product_name',
                customer_name=F('customer__name'),
            ).order_by('-created_at')[:10])

        res={
            "recent_inquired_products":recent_inquired_products
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)

@csrf_exempt
def order_status_analytics_count(request): 
    if request.method == "POST":
        order_qs = models.OrderDetail.objects
        
        confirmed_orders = order_qs.filter(Q(status = "completed")|Q(status = "pending", payment_type__in = ["cash","bank transfer"]), order_status="pending").count()
        in_progress_orders = order_qs.filter(order_status = "In Progress").count()
        completed_orders = order_qs.filter(order_status = "Completed").count()
        failed_orders = order_qs.filter(order_status = "failed").count()
        inquiry_orders = order_qs.filter(order_status = "inquiry").count()

        res={
            "confirmed_orders":confirmed_orders,
            "in_progress_orders":in_progress_orders,
            "completed_orders":completed_orders,
            "failed_orders":failed_orders,
            "inquiry_orders":inquiry_orders,
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)

@csrf_exempt
def order_monthly_analysis(request):
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
        
        if python_data.get('year') in [None,'','null']:
            year = datetime.now().year
        else:
            year = int(python_data.get('year'))

        start = datetime(year, 1, 1)
        end = datetime(year+1, 1, 1)

        order_qs = models.OrderDetail.objects.filter(
            Q(status = "completed")|Q(status = "pending", payment_type__in = ["cash","bank transfer"]),
            created_at__gt = start, 
            created_at__lt = end,
        )

        total_revenue = (
            order_qs.aggregate(
                total_revenue=Sum('total_price')
            )['total_revenue'] or 0
        )
        total_order_count = order_qs.count()

        avearage_order_value = total_revenue / total_order_count if total_order_count > 0 else 0

        monthly_data = (
            order_qs.annotate(month = ExtractMonth('created_at')).values('month').annotate(count=Count('id')).order_by('month')
        )

        result = {calendar.month_abbr[i].upper(): 0 for i in range(1, 13)}
        for item in monthly_data:
            month_abbr = calendar.month_abbr[item['month']].upper()
            result[month_abbr] = item['count']
            
        res = {
            "year": year,
            "data": result,
            "total_order_count":total_order_count,
            "total_revenue":total_revenue,
            "avearage_order_value":avearage_order_value,
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)

@csrf_exempt
def top_orders_analysis(request):
    if request.method == "POST":
        top_orders = (
            models.OrderDetail.objects.filter(Q(status = "completed")|Q(status = "pending", payment_type__in = ["cash","bank transfer"])).values(
                'order_id',
                'total_price',
                'created_at',
                customer_name = F('customer__name'),
            ).order_by('-total_price')[:10]
        )
        res={
            "top_orders":top_orders
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)

@csrf_exempt
def order_source_and_ship_by(request):
    if request.method == "POST":
        order_qs = models.OrderDetail.objects.filter(Q(status = "completed")|Q(status = "pending", payment_type__in = ["cash","bank transfer"]))

        total_order = order_qs.count()

        source_data =(
            order_qs.values(
                'order_from',
        ).annotate(
            ratio=Round(
                (Count('id') * 100.0) / total_order,
                precision=2
            )
        )
        )

        res={
            "source_data":source_data
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)

@csrf_exempt
def top_order_category_based_analysis(request):
    if request.method == "POST":
        top_categories = (
            models.ProductOrderDetail.objects.filter(Q(order__status = "completed")|Q(order__status = "pending", order__payment_type__in = ["cash","bank transfer"])).values(
                category_name=F('product__category__category'),
                category_name_french=F('product__category__category_french'),
            ).annotate(
                total_order=Count('order',distinct=True)
            ).order_by('-total_order')[:10]
        )
        res={
            "top_categories":top_categories
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)


@csrf_exempt
def order_recent_list_analysis(request):
    if request.method == "POST":
        recent_orders = (
            models.OrderDetail.objects
            .filter(
                Q(status="completed") |
                Q(status="pending", payment_type__in=["cash", "bank transfer"])
            )
            .annotate(
                customer_name=F('customer__name'),

                ship_by=ArrayAgg(
                    'productorderdetail__shipping_via',
                    distinct=True
                )
            )
            .values(
                'order_id',
                'total_price',
                'created_at',
                'status',
                'order_status',
                'customer_name',
                'ship_by',
            )
            .order_by('-created_at')[:10]
        )

        res={
            "recent_orders":recent_orders
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)


@csrf_exempt
def customer_analytics_count(request):
    if request.method == "POST":

        all_customers = models.CustomerDetail.objects.all()
        total_customers = all_customers.count()
        new_last_thirty_days = all_customers.filter(created_at_datetime__gt = datetime.now()-timedelta(days=30)).count()
        customer_used_promocode = models.OrderDetail.objects.filter(promocode__isnull=False).distinct('customer').count()

        res={
            "total_customers": total_customers,
            "new_last_thirty_days": new_last_thirty_days,
            "customer_used_promocode": customer_used_promocode
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)



@csrf_exempt
def monthly_customer_analysis(request):
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
        
        if python_data.get('year') in [None,'','null']:
            year = datetime.now().year
        else:
            year = int(python_data.get('year'))

        start = datetime(year, 1, 1)
        end = datetime(year+1, 1, 1)

        customer_qs = models.CustomerDetail.objects.filter(
            created_at_datetime__gt = start, 
            created_at_datetime__lt = end,
        )

        total_customer_qs_count = customer_qs.count()

        monthly_data = (
            customer_qs.annotate(month = ExtractMonth('created_at_datetime')).values('month').annotate(count=Count('id')).order_by('month')
        )

        result = {calendar.month_abbr[i].upper(): 0 for i in range(1, 13)}
        for item in monthly_data:
            month_abbr = calendar.month_abbr[item['month']].upper()
            result[month_abbr] = item['count']
            
        res = {
            "year": year,
            "data": result,
            "total_customer_qs_count":total_customer_qs_count,
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)

@csrf_exempt
def customer_by_country_analysis(request):
    if request.method == "POST":
        country_data = (
            models.CustomerDetail.objects
            .exclude(
                country__isnull=True
            )
            .exclude(
                country__in=["", "null"]
            )
            .values('country')
            .annotate(
                count=Count('id')
            )
            .order_by('-count')
        )
        res={
            "country_data":country_data
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)

@csrf_exempt
def customer_top_spenders_analysis(request):
    if request.method == "POST":
        top_spenders = (
            models.OrderDetail.objects.filter(Q(status = "completed")|Q(status = "pending", payment_type__in = ["cash","bank transfer"])).values(
                customer_name=F('customer__name'),
                customerId=F('customer__id'),
            ).annotate(
                total_spent=Sum('total_price')
            ).order_by('-total_spent')[:10]
        )
        res={
            "top_spenders":top_spenders
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)

@csrf_exempt
def customer_order_frequency_distribution_analysis(request):
    if request.method == "POST":
        order_qs = models.OrderDetail.objects.filter(
            Q(status="completed") |
            Q(status="pending", payment_type__in=["cash", "bank transfer"])
        )

      
        customer_orders = (
            order_qs
            .values('customer_id')
            .annotate(
                total_orders=Count('id')
            )
        )


        total_customers = customer_orders.count()

        frequency_rate = (
            customer_orders
            .annotate(
                frequency_rate=Case(
                    When(total_orders=1, then=Value('1 order')),
                    When(total_orders__gte=2, total_orders__lte=5, then=Value('2-5 orders')),
                    When(total_orders__gte=6, total_orders__lte=10, then=Value('6-10 orders')),
                    When(total_orders__gt=10, then=Value('10+ orders')),
                    output_field=CharField()
                )
            )
            .values('frequency_rate')
            .annotate(
                customer_count=Count('customer_id')
            )
            .annotate(
                percentage=Round(
                    (F('customer_count') * 100.0) / total_customers,
                    precision=2
                )
)
            .order_by('frequency_rate')
        )
        res={
            "frequency_rate":frequency_rate
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)

@csrf_exempt
def customer_recent_registered_list_analysis(request):
    if request.method == "POST":
        recent_customers = (
            models.CustomerDetail.objects
            .annotate(
                total_orders=Count(
                    'orderdetail',
                    filter=(
                        Q(orderdetail__status="completed") |
                        Q(
                            orderdetail__status="pending",
                            orderdetail__payment_type__in=[
                                "cash",
                                "bank transfer"
                            ]
                        )
                    ),
                    distinct=True
                ),

                total_spent=Coalesce(
                    Sum(
                        'orderdetail__total_price',
                        filter=(
                            Q(orderdetail__status="completed") |
                            Q(
                                orderdetail__status="pending",
                                orderdetail__payment_type__in=[
                                    "cash",
                                    "bank transfer"
                                ]
                            )
                        )
                    ),
                    0
                ),

                promo_used=ArrayAgg(
                    'orderdetail__promocode__promocode',
                    distinct=True,
                    filter=Q(
                        orderdetail__promocode__promocode__isnull=False
                    )
                ),
            )
            .values(
                'id',
                'name',
                'email',
                'created_at_datetime',
                'country',
                'total_orders',
                'total_spent',
                'promo_used',
                'status',
            )
            .order_by('-created_at_datetime')
        )

        res = {
            "recent_customers": list(recent_customers)
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)
