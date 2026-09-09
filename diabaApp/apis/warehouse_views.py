from django.views.decorators.csrf import csrf_exempt
from diabaApp import models
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from django.http import HttpResponse
import io
from datetime import datetime, timedelta
from django.template.loader import get_template
from django.core.mail import send_mail
from django.conf import settings


BASE_URL = settings.BASE_URL
IMAGE_URL = settings.IMAGE_URL
from diabaApp.serializer import WarehouseDetailSerializer


@csrf_exempt
def warehouse_create(request):
    if request.method =="POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))

        print(python_data, 'python_data')
        name = python_data.get('name')
        contact_person = python_data.get('contact_person')
        phone = python_data.get('phone')
        alternate_phone = python_data.get('alternate_phone')
        province = python_data.get('province')
        city = python_data.get('city')
        district = python_data.get('district')
        street = python_data.get('street')
        building = python_data.get('building')
        unit = python_data.get('unit')
        room = python_data.get('room')
        postal_code = python_data.get('postal_code')
        country = python_data.get('country')
        location_link = python_data.get('location_link')
        
        status = "Active"
        
        
     
        warehouse_create = models.WarehouseDetail.objects.create(
            name = name,
            contact_person = contact_person,
            phone = phone,
            alternate_phone = alternate_phone,
            province = province,
            city = city,
            district = district,
            street = street,
            building = building,
            unit = unit,
            room = room,
            postal_code = postal_code,
            country = country,
            location_link = location_link,
            status = status
        ).save()

        
        res={
            'message': "Warehouse registered successfully."
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)


@csrf_exempt
def warehouse_update(request):
    if request.method =="POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))
        id = python_data.get('id')

        warehouse = models.WarehouseDetail.objects.get(id = id)
        warehouse.name = python_data.get('name', warehouse.name)
        warehouse.contact_person = python_data.get('contact_person', warehouse.contact_person)
        warehouse.phone = python_data.get('phone', warehouse.phone)
        warehouse.alternate_phone = python_data.get('alternate_phone', warehouse.alternate_phone)
        warehouse.province = python_data.get('province', warehouse.province)
        warehouse.city = python_data.get('city', warehouse.city)
        warehouse.district = python_data.get('district', warehouse.district)
        warehouse.street = python_data.get('street', warehouse.street)
        warehouse.building = python_data.get('building', warehouse.building)
        warehouse.unit = python_data.get('unit', warehouse.unit)
        warehouse.room = python_data.get('room', warehouse.room)
        warehouse.postal_code = python_data.get('postal_code', warehouse.postal_code)
        warehouse.country = python_data.get('country', warehouse.country)
        warehouse.location_link = python_data.get('location_link', warehouse.location_link)
        warehouse.save()
     
        
        res={
            'message': "Warehouse updated successfully."
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)


@csrf_exempt
def warehouse_list(request):
    if request.method =="POST":        
        warehouse = models.WarehouseDetail.objects.all().order_by('-id')
        serializer = WarehouseDetailSerializer(warehouse, many=True).data
        res={
            'data': serializer
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)


@csrf_exempt
def warehouse_status_update(request):
    if request.method =="POST":   
        python_data = JSONParser().parse(io.BytesIO(request.body))
        id = python_data.get('id')

        warehouse = models.WarehouseDetail.objects.get(id = id)
        warehouse.status = python_data.get('status', warehouse.status)
        warehouse.save()

        res={
            'message':"Status update successfully."
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)