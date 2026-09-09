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
from diabaApp.serializer import ProductReviewSerializer
BASE_URL = settings.BASE_URL
IMAGE_URL = settings.IMAGE_URL


@csrf_exempt
def review_create(request):
    if request.method == "POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))
        now = datetime.now()
        date_time = now.strftime('%Y-%m-%d')
        customer = python_data.get('customer', None)
        get_customer_name = models.CustomerDetail.objects.filter(id = customer).values_list('name', flat=True)[0]
        create_review = models.ProductReview.objects.create(
            customer_id = python_data.get('customer', None),
            product_id = python_data.get('product', None),
            customer_name = get_customer_name,
            rating = python_data.get('rating', None),
            review = python_data.get('review', None),
            created_at = date_time
        ).save()
        
        res = {
            'message':"Review added."
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)


@csrf_exempt
def review_create_admin(request):
    if request.method == "POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))
        now = datetime.now()
        date_time = now.strftime('%Y-%m-%d')

        create_review = models.ProductReview.objects.create(
            product_id = python_data.get('product', None),
            customer_name = python_data.get('customer_name', None),
            rating = python_data.get('rating', None),
            review = python_data.get('review', None),
            created_at = date_time
        ).save()
        
        res = {
            'message':"Review added."
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)


@csrf_exempt
def product_review_list_admin(request):
    if request.method == "POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))
        product = python_data.get('product')

        total_review = models.ProductReview.objects.filter(product = product).count()
        get_rating = list(models.ProductReview.objects.filter(product = product).values_list('rating', flat=True))
        if total_review > 0:
            average_review = round(sum(get_rating) / total_review, 1)
        else:
            average_review = 0

        get_1_review = models.ProductReview.objects.filter(product = product, rating = 1).count()
        get_2_review = models.ProductReview.objects.filter(product = product, rating = 2).count()
        get_3_review = models.ProductReview.objects.filter(product = product, rating = 3).count()
        get_4_review = models.ProductReview.objects.filter(product = product, rating = 4).count()
        get_5_review = models.ProductReview.objects.filter(product = product, rating = 5).count()
        
        review = models.ProductReview.objects.filter(product = product).order_by('-id')
        serializer = ProductReviewSerializer(review, many=True).data
            
        res = {
            'data':serializer,
            'total_review':total_review,
            'average_review':average_review,
            '1_review_count':get_1_review,
            '2_review_count':get_2_review,
            '3_review_count':get_3_review,
            '4_review_count':get_4_review,
            '5_review_count':get_5_review,
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)
