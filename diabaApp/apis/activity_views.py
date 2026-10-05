from django.views.decorators.csrf import csrf_exempt
from diabaApp import models
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from django.http import HttpResponse
import io
import json
from datetime import datetime, timedelta
from django.db.models import Count, Q
from diabaApp.serializer import UserActivitySerializer
from diabaApp.utils import track_user_activity

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@csrf_exempt
def log_user_activity(request):
    """
    API for client (web/mobile) to record user activity actions:
    e.g. PRODUCT_VIEW, PAYMENT_METHOD_SELECT, ADD_TO_CART, SEARCH, etc.
    """
    if request.method == 'POST':
        try:
            python_data = JSONParser().parse(io.BytesIO(request.body))
        except Exception:
            res = {'status': False, 'message': 'Invalid JSON body'}
            return HttpResponse(JSONRenderer().render(res), content_type='application/json', status=400)

        action_type = python_data.get('action_type')
        if not action_type:
            res = {'status': False, 'message': 'action_type is required'}
            return HttpResponse(JSONRenderer().render(res), content_type='application/json', status=400)

        customer_id = python_data.get('customer') or python_data.get('customer_id')
        product_id = python_data.get('product_id') or python_data.get('product')
        product_name = python_data.get('product_name')
        payment_method = python_data.get('payment_method') or python_data.get('payment_type')
        search_keyword = python_data.get('search_keyword') or python_data.get('search')
        category_name = python_data.get('category_name')
        metadata = python_data.get('metadata', {})
        device_id = python_data.get('device_id')
        device_type = python_data.get('device_type')
        country = python_data.get('country')
        ip_address = python_data.get('ip_address') or get_client_ip(request)

        activity = track_user_activity(
            action_type=action_type,
            customer_id=customer_id,
            product_id=product_id,
            product_name=product_name,
            payment_method=payment_method,
            search_keyword=search_keyword,
            category_name=category_name,
            metadata=metadata,
            device_id=device_id,
            device_type=device_type,
            ip_address=ip_address,
            country=country
        )

        if activity:
            res = {
                'status': True,
                'message': 'Activity recorded successfully',
                'activity_id': activity.id
            }
            return HttpResponse(JSONRenderer().render(res), content_type='application/json', status=200)
        else:
            res = {'status': False, 'message': 'Failed to record activity'}
            return HttpResponse(JSONRenderer().render(res), content_type='application/json', status=500)


@csrf_exempt
def get_user_activity_list(request):
    """
    API to fetch activity logs with filters (by customer, action_type, device_id, date range).
    """
    if request.method == 'POST':
        try:
            python_data = JSONParser().parse(io.BytesIO(request.body))
        except Exception:
            python_data = {}

        customer_id = python_data.get('customer_id') or python_data.get('customer')
        action_type = python_data.get('action_type')
        device_id = python_data.get('device_id')
        limit = int(python_data.get('limit', 50))
        offset = int(python_data.get('offset', 0))

        queryset = models.UserActivity.objects.all().order_by('-id')

        if customer_id:
            queryset = queryset.filter(customer_id=customer_id)
        if action_type:
            queryset = queryset.filter(action_type=action_type)
        if device_id:
            queryset = queryset.filter(device_id=device_id)

        total_count = queryset.count()
        records = queryset[offset:offset + limit]
        serializer = UserActivitySerializer(records, many=True).data

        res = {
            'status': True,
            'total_count': total_count,
            'data': serializer
        }
        return HttpResponse(JSONRenderer().render(res), content_type='application/json', status=200)


@csrf_exempt
def get_user_activity_analytics(request):
    """
    API for Admin Analytics Dashboard:
    - Most visited products
    - Most selected payment methods
    - Top search keywords
    - Activity distribution by action_type
    """
    if request.method == 'POST':
        try:
            python_data = JSONParser().parse(io.BytesIO(request.body))
        except Exception:
            python_data = {}

        days = int(python_data.get('days', 30))
        start_date = datetime.now() - timedelta(days=days)

        base_qs = models.UserActivity.objects.filter(created_at__gte=start_date)

        # 1. Most Visited Products
        top_products = list(
            base_qs.filter(action_type='PRODUCT_VIEW')
            .exclude(product_name__isnull=True)
            .exclude(product_name='')
            .values('product_id', 'product_name')
            .annotate(visit_count=Count('id'))
            .order_by('-visit_count')[:10]
        )

        # 2. Most Selected Payment Methods
        top_payments = list(
            base_qs.filter(action_type='PAYMENT_METHOD_SELECT')
            .exclude(payment_method__isnull=True)
            .exclude(payment_method='')
            .values('payment_method')
            .annotate(select_count=Count('id'))
            .order_by('-select_count')
        )

        # 3. Top Searches
        top_searches = list(
            base_qs.filter(action_type='SEARCH')
            .exclude(search_keyword__isnull=True)
            .exclude(search_keyword='')
            .values('search_keyword')
            .annotate(search_count=Count('id'))
            .order_by('-search_count')[:10]
        )

        # 4. Action Type Breakdown
        action_breakdown = list(
            base_qs.values('action_type')
            .annotate(total=Count('id'))
            .order_by('-total')
        )

        res = {
            'status': True,
            'days': days,
            'data': {
                'top_products': top_products,
                'top_payments': top_payments,
                'top_searches': top_searches,
                'action_breakdown': action_breakdown
            }
        }
        return HttpResponse(JSONRenderer().render(res), content_type='application/json', status=200)
