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
from django.http import JsonResponse
from django.db import connection, transaction
import uuid
import json
import openpyxl, requests

from diabaApp.serializer import ProductInquirySerializer, VendorDelayNoteSerializer, VendorDetailExistsInDelayNote

BASE_URL = settings.BASE_URL
IMAGE_URL = settings.IMAGE_URL

@csrf_exempt
def product_inquiry_form(request):
    if request.method == "POST":        
        product_data = json.loads(request.POST.get("product_data", "[]"))
        customer_id = request.POST.get("customer_id")

        # amount: 121798
        # bictorys_transaction_id: "1b846d91-9dad-4dc4-9551-a24594805ca8"
        
        # payment_reference: "BICT-4461419D7E36"

        payment_transaction = models.ProductRequestTransaction.objects.create(
            customer_id=customer_id,
            payment_type="Bictorys",
            payment_id=request.POST.get("bictorys_transaction_id"),
            reference_id=request.POST.get("payment_reference"),
            total_amount=request.POST.get("amount"),
            currency="XOF",
            status="Success",
        )
        payment_transaction.save()

        print(request.POST, 'product_data', flush=True)
        inquiry_code = f"INQ-{uuid.uuid4().hex[:8].upper()}"

        with transaction.atomic():
            for index, product in enumerate(product_data):
                product_name=product.get("product_name")
                description=product.get("description")
                quantity=product.get("quantity")

                try: 
                    quantity = int(quantity)
                except (ValueError, TypeError):
                    res={
                        'message':'Quantity should be an integer.'
                    }
                    return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 406)
                
                product_inquiry = models.ProductInquiry.objects.create(
                    transaction_id = payment_transaction.id,
                    customer_id=customer_id,
                    inquiry_code = inquiry_code,
                    product_name=product_name,
                    description=description,
                    quantity=quantity,
                    created_at = datetime.now()
                )

                images = request.FILES.getlist(f"images_{index}")

                models.ProductInquiryImages.objects.bulk_create([
                    models.ProductInquiryImages(
                        inquiry_id=product_inquiry.id,
                        image=image
                    )
                    for image in images
                ])

        res={
            'message':'Inquiry Submitted Successfully'
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)
    else:
        print(request.method, "request.method")
        res={
            'message':'something went wrong'
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 500)



@csrf_exempt
def customer_inquiry_list(request):
    if request.method == "POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))
        customer = python_data.get('customer')
        get_inquiry = models.ProductInquiry.objects.filter(customer = customer).order_by('-id')
        serialiser = ProductInquirySerializer(get_inquiry, many=True).data
        res={
            'data':serialiser
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)


@csrf_exempt
def product_inquiry_status_update(request):
    if request.method == "POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))

        inquiry_id = python_data.get('inquiry_id')
        status = python_data.get('status')

        get_inquiry = models.ProductInquiry.objects.get(id = inquiry_id)
        get_inquiry.status = status
        get_inquiry.save()

        res={
            'message':'Inquiry Status Updated'
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)

@csrf_exempt
def export_product_inquiry_list(request):
    if request.method == "POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))

        print("Python_data-=-=-=--->",python_data)

        user_type = python_data.get('user_type')

        inquiry_list = models.ProductInquiry.objects.all().order_by('-id')
        inquiry_list_serializer = ProductInquirySerializer(inquiry_list, many=True).data

        headers = [
            "Inquiry Code",
            "Product Name",
            "Description",
            "Quantity",
            "Customer Name",
            
        ]

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Inquiry List"

        field_map = {
            'Inquiry Code':'inquiry_code',
            'Product Name':'product_name',
            'Description':'description',
            'Quantity':'quantity',
            'Customer Name':'customer_name',
        }
        if user_type == "admin":
            headers.append("Customer Country Code")
            headers.append("Customer Mobile")
            headers.append("Customer Email")
        
            field_map.update({
                'Customer Email':'customer_email',          
                'Customer Country Code':'customer_countryCode',
                'Customer Mobile':'customer_mobileNumber',
            })
      
        ws.append(headers)
      
        for row in inquiry_list_serializer:  # list_data = your queryset/serializer output
            ws.append([row.get(field_map[h], "") for h in headers])


        # Create the HTTP response
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="customer_list.xlsx"'

        wb.save(response)


        # res={
        #     'data':response
        # }
        # json_data = JSONRenderer().render(res)
        # return HttpResponse(json_data, content_type= 'application/json', status=200)

        return response

@csrf_exempt
def product_inquiry_list(request):
    if request.method == "POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))

        print("python_data=====>",python_data)

        page_number = int(python_data.get('page_number', 1))
        row_size = int(python_data.get('row_data', 10))
        last_row = row_size * page_number
        first_row = last_row - row_size
        
        search_key = python_data.get('search_key')
        status = python_data.get('status')
        filter_condition = Q()

        if status not in [None,'','null']:
            filter_condition &= Q(status = status)

        if search_key not in [None,'','null']:
            filter_condition &= Q(customer__name__icontains = search_key)| Q(inquiry_code__icontains = search_key) | Q(product_name__icontains = search_key) | Q(customer__mobileNumber__icontains = search_key)

        total_inquiry_count = models.ProductInquiry.objects.filter(filter_condition).order_by('-id').count()
        inquiry_list = models.ProductInquiry.objects.filter(filter_condition).order_by('-id')[first_row:last_row]
        inquiry_list_serializer = ProductInquirySerializer(inquiry_list, many=True).data


        res={
            'data':inquiry_list_serializer,
            'total_inquiry_count':total_inquiry_count,
            'total_count':total_inquiry_count
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)


@csrf_exempt
def delay_note_create(request):
    if request.method == "POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))
        
        vendor_ids = python_data.get('vendor_ids')
        note = python_data.get('note')
        start_at = python_data.get('start_at')
        end_at = python_data.get('end_at')
        
        created_at = datetime.now()

        delay_note_code = f"DN-{uuid.uuid4().hex[:8].upper()}"

        # try:
        #     vendor_list = [int(x) for x in vendor_ids.split(',')]
        # except Exception as e:

        #     vendor_list = json.loads(vendor_ids)

        delay_note_exists = models.VendorDelayNote.objects.filter(
            start_at__gte = start_at,
            end_at__lte = end_at,
            vendor__id__in = vendor_ids
        ).exists()

        if delay_note_exists:
            res={
                "message":"A delay note already exists among selected vandors during this time period."
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 406)

        delay_note = models.VendorDelayNote.objects.create(
            delay_note_code = delay_note_code,
            note = note,
            start_at = start_at,
            end_at = end_at,
            created_at = created_at,
        )
        delay_note.vendor.set(vendor_ids)
        delay_note.save()

        res={
            'message':'Delay Note Added'
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)

        
@csrf_exempt
def delay_note_list(request):
    if request.method == "POST":
        delay_notes = models.VendorDelayNote.objects.all().order_by('-id')
        delay_notes_serializer = VendorDelayNoteSerializer(delay_notes, many=True).data

        res={
            'data':delay_notes_serializer
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)


@csrf_exempt
def delay_note_update(request):
    if request.method == "POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))

        id = python_data.get('id')
        vendor_ids = python_data.get('vendor_ids')
        note = python_data.get('note')
        start_at = python_data.get('start_at')
        end_at = python_data.get('end_at')

        delay_note_exists = models.VendorDelayNote.objects.filter(
            start_at__gte = start_at,
            end_at__lte = end_at,
            vendor__id__in = vendor_ids
        ).exclude(id=id).exists()

        if delay_note_exists:
            res={
                "message":"A delay note already exists among selected vandors during this time period."
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 406)
        
        delay_note = models.VendorDelayNote.objects.get(id = id)
        delay_note.note = note
        delay_note.start_at = start_at
        delay_note.end_at = end_at
        delay_note.vendor.set(vendor_ids)
        delay_note.save()

        res={
            'message':'Delay Note Updated'
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)


@csrf_exempt
def delay_note_status_update(request):
    if request.method == "POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))
        id = python_data.get('id')
        status = python_data.get('status')

        delay_note = models.VendorDelayNote.objects.get(id=id)
        delay_note.status = status
        delay_note.save()

        res={
            'message':'Delay Note Status Updated'
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)


@csrf_exempt
def vendor_list_with_delay_note(request):
    if request.method == "POST":
        vendor_list = models.VendorDetail.objects.all().order_by('vendor_name')
        vendor_list_serializer = VendorDetailExistsInDelayNote(vendor_list, many=True).data

        res={
            'data':vendor_list_serializer
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)
