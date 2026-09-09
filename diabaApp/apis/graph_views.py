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
def graph_product_verification_data(request):
    if request.method == "POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))
        vendor = python_data.get('vendor')

        vendor_products_for_approval = models.ProductDetail.objects.filter(vendor=vendor)

        # Order Status List Graph

        statusList = [("Pending","#34D399"), ("Approved","#FBBF24"), ("Rejected","#F87171")]
        
        productVerificationData = []
        for status, color in statusList:
            order = vendor_products_for_approval.filter(product_verification = status).count()
            productVerificationData.append({"name": status, "value": order, "color": color})
        
        res = {
            "productVerificationData": productVerificationData,
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)

@csrf_exempt
def graph_order_status(request):
    if request.method == "POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))
        vendor = python_data.get('vendor')

        vendor_products_for_order = models.VendorOrderDetail.objects.filter(vendor=vendor)

        # Order Status List Graph

        statusList = [("pending","#FBBF24"), ("Processing","#60A5FA"), ("Shipping","#A78BFA"), ("Delivered","#34D399"), ("Cancelled","#F87171")]
        
        orderStatusData = []
        for status, color in statusList:
            order = vendor_products_for_order.filter(variant__vendor_status = status).count()
            orderStatusData.append({"name": status, "value": order, "color": color})
        
        res = {
            "orderStatusData": orderStatusData,
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)

@csrf_exempt
def graph_top_products(request):
    if request.method == "POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))
        vendor = python_data.get('vendor')

        vendor_products_for_order = models.VendorOrderDetail.objects.filter(vendor=vendor)

        # TOP Product Data Graph

        product_price_subquery = models.VendorProductPrice.objects.filter(
            product=OuterRef('variant__product'),
            variant=OuterRef('variant__variant'),
            status='Active'
        ).order_by('-id').values('price')[:1]
                
        topProductsData = (
            vendor_products_for_order
            .annotate(
                product_price=Cast(Subquery(product_price_subquery), FloatField())
            )
            .values(
                product_id=F('variant__product'),
                name=F('variant__product__product_name_french')
            )
            .annotate(
                sales=Count('id'),
                revenue=Sum(ExpressionWrapper(
                    F('variant__quantity') * Coalesce(
                        Cast(F('variant__variant__vendorproductprice__price'), FloatField()),
                        0.0
                    ),
                    output_field=FloatField()
            )
            )
            )
            .order_by('-sales')[:5]
        )

        res = {
            "topProductsData": topProductsData
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)

@csrf_exempt
def graph_top_variants(request):
    if request.method == "POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))
        vendor = python_data.get('vendor')

        vendor_products_for_order = models.VendorOrderDetail.objects.filter(vendor=vendor)

        # TOP Variant Data Graph

        variant_price_subquery = models.VendorProductPrice.objects.filter(
            variant=OuterRef('variant__variant')
        ).values('price')[:1]

        # print(list(variant_price_subquery.query))

        variantPerformanceData = (
            vendor_products_for_order
            .annotate(
                variant_price=Cast(Subquery(variant_price_subquery), FloatField())
            )
            .values(
                variant_name=F('variant__variant'),
                name=F('variant__variant__name_french')
            )
            .annotate(
                orders=Count('id'),
                revenue=Sum(ExpressionWrapper(
                    F('variant__quantity') * Coalesce(
                        Cast(F('variant__variant__vendorproductprice__price'), FloatField()),
                        0.0
                    ),
                    output_field=FloatField()
            )
            )   
            )
            .order_by('-orders')[:5]
        )

        res = {
            "variantPerformanceData": variantPerformanceData
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)

@csrf_exempt
def graph_recent_orders(request):
    if request.method == "POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))
        vendor = python_data.get('vendor')

        vendor_products_for_order = models.VendorOrderDetail.objects.filter(vendor=vendor)

        # RECENT ORDER Data Graph

        variant_price_subquery = models.VendorProductPrice.objects.filter(
            variant = OuterRef('variant__variant')
        ).values('price')[:1]

        recentOrders = (
            vendor_products_for_order
            .annotate(
            price=Cast(Subquery(variant_price_subquery), FloatField())
        ).values(
            orderId=F('order__order_id'),
            product_name = F('variant__product__product_name_french'),
            variant_name=F('variant__variant__name_french'),
            quantity=F('variant__quantity'),
            status=F('variant__vendor_status'),
            customer_name=F('variant__order__customer__name'),
            date =F('variant__created_at'),
            price=F('price')
        ).order_by('-id')[:5])

        res = {
            "recentOrders": recentOrders
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)

@csrf_exempt
def graph_last_twelve_months_performance(request):
    if request.method == "POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))
        vendor = python_data.get('vendor')

        vendor_products_for_order = models.VendorOrderDetail.objects.filter(vendor=vendor)

        # Monthly Sales Data Graph

        last_12_months = datetime.now() - timedelta(days=365)

        queryset = (
            vendor_products_for_order
            .filter(
                variant__created_at__gte=last_12_months,
                variant__variant__vendorproductprice__vendor=vendor,
                variant__variant__vendorproductprice__status="Active"
            )

            # optimized single annotate
            .annotate(
                month=TruncMonth('variant__created_at'),

                price=Cast(
                    F('variant__variant__vendorproductprice__price'),
                    FloatField()
                ),

                revenue_per_item=ExpressionWrapper(
                    F('variant__quantity') * Coalesce(
                        Cast(F('variant__variant__vendorproductprice__price'), FloatField()),
                        0.0
                    ),
                    output_field=FloatField()
                )
            )

            .values('month')

            .annotate(
                revenue=Coalesce(Sum('revenue_per_item'), 0.0),
                orders=Count('order_id', distinct=True)
            )

            .order_by('month')
        )

        #  EXECUTE QUERY
        raw_data = list(queryset)

        #  FORMAT DATA (THIS IS YOUR MISSING PART)
        previous_tweleve_months_data = []
        for row in raw_data:
            previous_tweleve_months_data.append({
                "month": row["month"].strftime("%b"),   # Jan, Feb, Mar
                "revenue": float(row["revenue"]),
                "orders": row["orders"]
            })

        res = {
            "previous_tweleve_months_data": previous_tweleve_months_data
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)

