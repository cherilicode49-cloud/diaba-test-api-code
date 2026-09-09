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
from diabaApp.serializer import VendorTransactionSerializer, OrderTransactionSerializer, VendorPaymentTrackerSerializer

BASE_URL = settings.BASE_URL
IMAGE_URL = settings.IMAGE_URL

      
@csrf_exempt
def vendor_transaction_create(request):
    if request.method == 'POST':
        python_data = JSONParser().parse(io.BytesIO(request.body))

        # print("python_data---vendor_transaction_create---->", python_data)

        vendor = python_data.get('vendor')
        payment_type = python_data.get('payment_type')
        currency = python_data.get('currency')
        amount = python_data.get('amount')
        remarks = python_data.get('remarks')
        transaction_type = python_data.get('transaction_type')
        status = python_data.get('status',None)

        if models.VendorDetail.objects.filter(id = vendor).exists():
            transaction_create = models.VendorTransaction.objects.create(
                vendor_id = vendor,
                payment_type = payment_type,
                currency = currency,
                amount = amount,
                transaction_type = transaction_type,
                remarks = remarks,
                status = status
            )

            res={
                'message':'Transaction Created Successfully'
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)



@csrf_exempt
def vendor_transaction_list(request):
    if request.method == 'POST':
        python_data = JSONParser().parse(io.BytesIO(request.body))
        vendor = python_data.get('vendor')

        transaction = models.VendorTransaction.objects.filter(vendor = vendor)
        transaction_data = VendorTransactionSerializer(transaction, many=True).data
        res={
            'data':transaction_data
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)


@csrf_exempt
def vendor_transaction_list_admin(request):
    if request.method == "POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))

        # print("python_data-==-vendor_transaction_list--->", python_data)

        vendor = python_data.get('vendor')

        if models.VendorTransaction.objects.filter(vendor = vendor).exists():
            vendor_transaction_list = models.VendorTransaction.objects.filter(vendor = vendor)
            vendor_transaction_list_serializer = VendorTransactionSerializer(vendor_transaction_list, many=True).data

            res = {
                'data':vendor_transaction_list_serializer
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)



@csrf_exempt
def all_vendor_transaction_list(request):
    if request.method == 'POST':
        transaction = models.VendorTransaction.objects.all()
        transaction_data = VendorTransactionSerializer(transaction, many=True).data
        res={
            'data':transaction_data
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)

@csrf_exempt
def all_transaction_list_admin(request):
    if request.method =="POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))

        status = python_data.get('status', 'completed')
        page_number = int(python_data.get('page_number', 1))
        row_size = int(python_data.get('row_data', 10))
        last_row = row_size * page_number
        first_row = last_row - row_size

        transaction_count = models.OrderTransaction.objects.filter(status = status).count()
        all_transaction_list = models.OrderTransaction.objects.filter(status = status).order_by('-id')[first_row:last_row]
        transaction_serialiser = OrderTransactionSerializer(all_transaction_list, many=True).data

        
        res={
            'data': transaction_serialiser,
            'transaction_count':transaction_count
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)

 
@csrf_exempt
def vendor_payment_track_create(request):
    if request.method == "POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))
        created_at = datetime.now()

        vendor = python_data.get('vendor')
        
        payment_type = python_data.get('payment_type')
        currency = python_data.get('currency')
        amount = int(python_data.get('amount'))
        description = python_data.get('description')

        get_vendor = models.VendorDetail.objects.get(id = vendor)

        vendor_name = get_vendor.vendor_name
        vendor_email = get_vendor.email
        vendor_mobile = get_vendor.phone_number

        getRecentPament = models.VendorPaymentTracker.objects.filter(vendor = vendor).order_by('-id').first()
        if getRecentPament:
            if getRecentPament.remaining_amount != 0 and amount > getRecentPament.remaining_amount:
                res = {
                    'message':'Amount should be less than or equal to remaining amount.'
                }
                return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 406)
        
        previous_remaining_amount = models.VendorPaymentTracker.objects.filter(vendor = vendor).order_by('-id').values_list('remaining_amount', flat=True).first()

        if payment_type == 'Pay':
            remaining_amount = amount if previous_remaining_amount is None else previous_remaining_amount + amount
        else:
            remaining_amount = 0 if previous_remaining_amount is None else previous_remaining_amount - amount

        create_payment = models.VendorPaymentTracker.objects.create(
            vendor_id = vendor,
            vendor_name = vendor_name,
            vendor_email = vendor_email,
            vendor_mobile = vendor_mobile,
            payment_type = payment_type,
            currency = currency,
            amount = amount,
            remaining_amount = remaining_amount,
            description = description,
            created_at = created_at,
        ).save()


        res = {
            'message':'Entry Added Successfully.'
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)


@csrf_exempt
def vendor_payment_track_list(request):
    if request.method == "POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))
        vendor = python_data.get('vendor')
        page_number = int(python_data.get('page_number', 1))
        row_size = int(python_data.get('row_size', 10))
        last_row = row_size * page_number
        first_row = last_row - row_size

        vendor_data = models.VendorPaymentTracker.objects.filter(vendor = vendor).order_by('-id')

        total_data = vendor_data.count()
        payment_history = vendor_data[first_row:last_row]

        serialser = VendorPaymentTrackerSerializer(payment_history, many=True).data

        res = {
            'data':serialser,
            'total_data':total_data
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)


@csrf_exempt
def vendor_payment_track_delete(request):
    if request.method == "POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))
        id = python_data.get('id')
        check_data = models.VendorPaymentTracker.objects.filter(id = id)
        if check_data.exists():
            check_data.delete()
            res = {
                'message':'Entry Deleted Successfully.'
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)
        else:
            res = {
                'message':'Something went wrong.'
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 406)


