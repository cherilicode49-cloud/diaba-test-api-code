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
from diabaApp.serializer import ContainerRequestSerializer, ContainerTermsSerializer
import numpy as np

BASE_URL = settings.BASE_URL
IMAGE_URL = settings.IMAGE_URL

@csrf_exempt
def container_request_create(request):
    if request.method == "POST":
        try:
            python_data = JSONParser().parse(io.BytesIO(request.body))
            customer = python_data.get('customer')
            departure_city = python_data.get('departure_city')
            customer_shipping_mark = python_data.get('customer_shipping_mark')
            quantity_cbm = python_data.get('quantity_cbm')
            weight_kg = python_data.get('weight_kg')
            destination_country = python_data.get('destination_country')
            # product_type = python_data.get('product_type')
            product_type = python_data.get('product_type', [])
            sponsor = python_data.get('sponsor', None)
            customer_note = python_data.get('customer_note', None)
            print(python_data, 'python_data')
            transport_type =  python_data.get('transport_type')
            volume =  python_data.get('volume')

            is_fragile = python_data.get('is_fragile')
            is_battery = python_data.get('is_battery')
            is_flammable = python_data.get('is_flammable')
            is_liquid = python_data.get('is_liquid')
            
            create_request = models.ContainerRequest.objects.create(
                customer_id=customer,
                departure_city=departure_city,
                customer_shipping_mark=customer_shipping_mark,
                quantity_cbm=quantity_cbm,
                weight_kg=weight_kg,
                destination_country_id=destination_country,
                sponsor=sponsor,
                customer_note=customer_note,
                volume = volume,
                status='Pending',
                transport_type = transport_type,
                is_fragile = is_fragile,
                is_battery = is_battery,
                is_flammable = is_flammable,
                is_liquid = is_liquid,
            )
            if product_type:
                create_request.product_type.set(product_type)

            res = {'message': 'Container Request Added Successfully.'}
            json_data = JSONRenderer().render(res)
            return HttpResponse(json_data,content_type='application/json',status=200)
        except Exception as e:

            print(
                "Customer create error:",
                str(e),
                flush=True
            )

            return HttpResponse({

                'status': 'Failed',

                'statuscode': 500,

                'message': str(e)

            }, status=500)


@csrf_exempt
def container_request_status_update(request):
    if request.method == "POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))
        id = python_data.get('id')
        update = models.ContainerRequest.objects.get(id=id)
        update.status = python_data.get('status',update.status)
        update.save()
        res = {'message': 'Status updated successfully.'}
        json_data = JSONRenderer().render(res)
        return HttpResponse(json_data,content_type='application/json',status=200)


@csrf_exempt
def all_container_request_list(request):
    python_data = JSONParser().parse(io.BytesIO(request.body))

    print("python_data--all_container_request_list--->", python_data)

    page_number = max(int(python_data.get('page_number', 1)), 1)
    row_size = max(int(python_data.get('row_data', 10)), 1)

    last_row = row_size * page_number
    first_row = last_row - row_size

    status = python_data.get('status', None)

    filter_condition = Q()

    if status not in [None, '', 'null']:
        filter_condition &= Q(status=status)

    total_records = models.ContainerRequest.objects.filter(filter_condition).count()

    all_requests = models.ContainerRequest.objects.filter(
        filter_condition
    ).select_related('customer','destination_country').order_by('-id')[first_row:last_row]

    serializer = ContainerRequestSerializer(all_requests,many=True).data

    res = {
        'data': serializer,
        'total_records': total_records,
        'current_page': page_number,
        'total_pages': int(np.ceil(total_records / row_size))
    }

    json_data = JSONRenderer().render(res)

    return HttpResponse(
        json_data,
        content_type='application/json',
        status=200
    )

@csrf_exempt
def customer_container_request_list(request):
    python_data = JSONParser().parse(io.BytesIO(request.body))

    print(
        "python_data--customer_container_request_list--->",
        python_data
    )

    customer = python_data.get('customer')

    page_number = max(int(python_data.get('page_number', 1)), 1)
    row_size = max(int(python_data.get('row_data', 10)), 1)

    last_row = row_size * page_number
    first_row = last_row - row_size

    status = python_data.get('status', None)

    filter_condition = Q(
        customer_id=customer
    )

    if status not in [None, '', 'null']:
        filter_condition &= Q(status=status)

    total_records = models.ContainerRequest.objects.filter(
        filter_condition
    ).count()

    all_requests = models.ContainerRequest.objects.filter(
        filter_condition
    ).select_related(
        'customer',
        'destination_country'
    ).order_by('-id')[first_row:last_row]

    serializer = ContainerRequestSerializer(
        all_requests,
        many=True
    ).data

    res = {
        'data': serializer,
        'total_records': total_records,
        'current_page': page_number,
        'total_pages': int(np.ceil(total_records / row_size))
    }

    json_data = JSONRenderer().render(res)

    return HttpResponse(
        json_data,
        content_type='application/json',
        status=200
    )

@csrf_exempt
def container_create_update(request):

    if request.method == "POST":

        terms_en = request.POST.get("terms_en")
        terms_fr = request.POST.get("terms_fr")
        status_value = request.POST.get("status", "active")

        container_terms = models.ContainerTerms.objects.first()

        if container_terms is None:

            container_terms = models.ContainerTerms.objects.create(
                terms_en=terms_en,
                terms_fr=terms_fr,
                status=status_value
            )

            res = {
                "message": "Container terms added successfully."
            }

        else:

            if terms_en is not None:
                container_terms.terms_en = terms_en

            if terms_fr is not None:
                container_terms.terms_fr = terms_fr

            if status_value is not None:
                container_terms.status = status_value

            container_terms.save()

            res = {
                "message": "Container terms updated successfully."
            }

        json_data = JSONRenderer().render(res)

        return HttpResponse(
            json_data,
            content_type="application/json",
            status=200
        )

    res = {
        "message": "Invalid request method."
    }

    return HttpResponse(
        JSONRenderer().render(res),
        content_type="application/json",
        status=405
    )

@csrf_exempt
def container_terms_list_admin(request):

    if request.method == "POST":

        terms = models.ContainerTerms.objects.all()

        serializer = ContainerTermsSerializer(
            terms,
            many=True
        ).data

        res = {
            "data": serializer
        }

        return HttpResponse(
            JSONRenderer().render(res),
            content_type="application/json",
            status=200
        )

    res = {
        "message": "Invalid request method."
    }

    return HttpResponse(
        JSONRenderer().render(res),
        content_type="application/json",
        status=405
    )

@csrf_exempt
def container_terms_list_app(request):

    if request.method == "POST":

        terms = models.ContainerTerms.objects.filter(
            status="Active"
        )

        print(terms, 'http://103.205.216.39:2308/apihttp://103.205.216.39:2308/api')

        serializer = ContainerTermsSerializer(
            terms,
            many=True
        ).data

        res = {
            "data": serializer
        }

        return HttpResponse(
            JSONRenderer().render(res),
            content_type="application/json",
            status=200
        )

    res = {
        "message": "Invalid request method."
    }

    return HttpResponse(
        JSONRenderer().render(res),
        content_type="application/json",
        status=405
    )