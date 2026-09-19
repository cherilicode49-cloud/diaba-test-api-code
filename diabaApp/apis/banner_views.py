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
from diabaApp.serializer import BannerContentSerializer

BASE_URL = settings.BASE_URL
IMAGE_URL = settings.IMAGE_URL

@csrf_exempt
def banner_create_update(request):
    if request.method == "POST":

        banner_type = request.POST.get('banner_type')
        title = request.POST.get('title')
        status = request.POST.get('status', 'active')
        image = request.FILES.get('image')

        banner = models.BannerContent.objects.filter(banner_type=banner_type).first()

        if banner is None:

            banner = models.BannerContent.objects.create(
                banner_type=banner_type,
                title=title,
                image=image,
                status=status
            )

            res = {'message': 'Banner Added Successfully.'}

        else:

            if title is not None:
                banner.title = title

            if status is not None:
                banner.status = status

            if image:
                banner.image = image

            banner.save()

            res = {'message': 'Banner data updated successfully.'}

        json_data = JSONRenderer().render(res)
        return HttpResponse(json_data,content_type='application/json',status=200)

    res = {'message': 'Invalid request method.'}
    json_data = JSONRenderer().render(res)
    return HttpResponse(json_data,content_type='application/json',status=405)

@csrf_exempt
def banner_list_admin(request):

    if request.method == "POST":
        banners = models.BannerContent.objects.all()
        serializer = BannerContentSerializer(banners,many=True).data

        res = {'data': serializer}
        json_data = JSONRenderer().render(res)
        return HttpResponse(json_data,content_type='application/json',status=200)

    res = {'message': 'Invalid request method.'}
    json_data = JSONRenderer().render(res)
    return HttpResponse(json_data,content_type='application/json',status=405)

@csrf_exempt
def banner_list_app(request):

    if request.method == "POST":
        banners = models.BannerContent.objects.filter(status = "active")
        serializer = BannerContentSerializer(banners,many=True).data

        res = {'data': serializer}
        json_data = JSONRenderer().render(res)
        return HttpResponse(json_data,content_type='application/json',status=200)

    res = {'message': 'Invalid request method.'}
    json_data = JSONRenderer().render(res)
    return HttpResponse(json_data,content_type='application/json',status=405)