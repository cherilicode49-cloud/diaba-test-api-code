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
from django.utils import timezone
from django.db.models import Max, Min

from diabaApp.serializer import ProductDetailSerializer, CustomerDetailSerializer, OrderDetailExportSerializer, VendorDetailSerializer

BASE_URL = settings.BASE_URL
IMAGE_URL = settings.IMAGE_URL





def calculate_shipping_cost(
        carton_length,
        carton_width,
        carton_height,
        carton_weight,
        quantity,
        price_by_air,
        price_by_ship,
        price_by_express
    ):

        # print("price_by_ship----->",price_by_ship)
        # Convert to float safely
        if carton_length != "-":
            L = float(carton_length or 0)
        else:
            L = 0 
        
        if carton_width != "-":
            W = float(carton_width or 0)
        else:
            W = 0 
        
        if carton_height != "-":
            H = float(carton_height or 0)
        else:
            H = 0 

        if carton_weight != "-":
            weight = float(carton_weight or 0)
        else:
            weight = 0 

        # weight = float(carton_weight or 0)
        qty = int(quantity or 0)

        #CBM per unit
        # print("L", L , "W", W, "H", H)
        cbm_per_unit = (L*W*H) / 1000000  # cm → m conversion

        # print("L=-=------>",L)
        # print("W=-=------>",W)
        # print("H=-=------>",H)
        #  Totals
        total_cbm = cbm_per_unit * qty
        # print(total_cbm, 'total_cbm')
        total_weight = weight * qty

        # print("total_cbm=-=------>",cbm_per_unit, qty )

        #Chargeable weights
        chargeable_air_weight = total_weight      # Billed per KG
        chargeable_express_weight = total_weight      # Billed per KG
        chargeable_sea_weight = total_cbm         # Billed per CBM

        # print("chargeable_sea_weight----->",chargeable_air_weight)

        #Final shipping costs
        # print(chargeable_sea_weight, 'chargeable_sea_weightchargeable_sea_weightchargeable_sea_weight')
        # print("total_cbm====>",total_cbm)
        # print("chargeable_air_weight====>",chargeable_air_weight)
        # print("chargeable_sea_weight====>",chargeable_sea_weight)

        # print("chargeable_air_weight * float(price_by_air or 0)====>",chargeable_air_weight * float(price_by_air or 0))
        # print("chargeable_sea_weight * float(price_by_ship or 0====>",chargeable_sea_weight * float(price_by_ship or 0))
        # print("chargeable_express_weight * float(price_by_express or 0====>",chargeable_express_weight * float(price_by_express or 0))

        total_air_cost = round(chargeable_air_weight * float(price_by_air or 0))
        total_sea_cost = round(chargeable_sea_weight * float(price_by_ship or 0),4)
        total_express_cost = round(chargeable_express_weight * float(price_by_express or 0),4)


        # print("total_sea_cost------->",total_air_cost)

        return {
            "cbm": math.ceil(round(total_cbm, 6)),
            "chargeable_air_weight": round(chargeable_air_weight),
            "chargeable_sea_weight": round(chargeable_sea_weight, 6),
            "total_air_cost": total_air_cost,
            "total_sea_cost": total_sea_cost,
            "total_express_cost":total_express_cost
        }


@csrf_exempt
def export_product_list(request):
    if request.method == "POST":
        try:
            python_data = JSONParser().parse(io.BytesIO(request.body))
        except:
            python_data = {}
    
        # print("python_data--all_product_list--->", python_data)

        today = timezone.now()

        page_number = int(python_data.get('page_number', 1))
        row_size = int(python_data.get('row_data', 10))
        last_row = row_size * page_number
        first_row = last_row - row_size

        category_name = python_data.get('category_name',None)
        search_key = python_data.get('search_key',None)
        subcategory_name = python_data.get('subcategory_name',None)
        status = python_data.get('status',None)

        filter_condition = Q()

        if category_name not in [None,'','null']:
            filter_condition &= Q(category__category = category_name)
        if subcategory_name not in [None,'','null']:
            filter_condition &= Q(subcategory__subcategory = subcategory_name)
        if search_key not in [None,'','null']:
            filter_condition &= Q(product_name__icontains = search_key)|Q(refpro__icontains = search_key)
        if status not in [None,'','null']:
            filter_condition &= Q(status = status)

        
        total_records = models.ProductDetail.objects.filter(filter_condition).count()
        # all_product = models.ProductDetail.objects.filter(filter_condition).order_by('-id')[first_row:last_row]
        # serializer = ProductDetailSerializer(all_product, many=True).data
        
        list_data = []
        all_product = models.ProductDetail.objects.filter(filter_condition).order_by('-id')
        for product in all_product:
            product = models.ProductDetail.objects.get(id = product.id)
            price_data = models.ProductModelVariant.objects.filter(product=product).aggregate(
                max_price=Max('price'),
                min_price=Min('price')
            )

            category = product.category.category
            subcategory = product.subcategory.subcategory
            max_price = price_data['max_price']
            min_price = price_data['min_price']
            serializer = ProductDetailSerializer(product).data

            get_data = models.CountryWithCurrency.objects.get(country_calling_code = '+221')
            print(product.carton_length,product.carton_width,product.carton_height,product.carton_weight, 'product.carton_length,product.carton_width,product.carton_height,product.carton_weight', product.id)
            shipping_cost_per_product = calculate_shipping_cost(product.carton_length,product.carton_width,product.carton_height,product.carton_weight,1,get_data.price_by_air,get_data.price_by_ship, get_data.express_shipping)

            serializer.update({'max_price': max_price, 'min_price':min_price, 'category':category, 'subcategory':subcategory, 'total_air_cost':shipping_cost_per_product.get('total_air_cost'), \
                            'total_sea_cost':shipping_cost_per_product.get('total_sea_cost'),'total_express_cost':shipping_cost_per_product.get('total_express_cost')})
            list_data.append(serializer)

        headers = [
            'Product Name', 'Product Code', 'Subcategory', 'Category', 'Min Price', 'Max Price',
            'Min Quantity', 'Max Quantity', 'Weight', 'Width', 'Height','Length','Total Air Cost', 'Total Sea Cost', 
            'Total Express Cost', 'Image', 'Status'
        ]
        

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Product"

        ws.append(headers) 
        field_map = {
            'Product Name':'product_name',
            'Product Code':'product_code',
            'Subcategory':'subcategory_name',
            'Category':'category_name',
            'Min Price':'max_price',
            'Max Price':'min_price',
            'Min Quantity':'min_order_quantity',
            'Max Quantity':'max_order_quantity',
            'Weight':'weight',
            'Width':'width',
            'Height':'height',
            'Length':'length',
            'Total Air Cost' : 'total_air_cost', 
            'Total Sea Cost' :'total_sea_cost' , 
            'Total Express Cost':'total_express_cost',
            'Image':'product_image_1',
            'Status':'status',
        }

        # if list_data:
        #     headers = list(list_data[0].keys())
        #     ws.append(headers)  # write headers

        for row in list_data:  # list_data = your queryset/serializer output
            ws.append([row.get(field_map[h], "") for h in headers])



       
        # Convert QuerySet to a DataFrame
        # df = pd.DataFrame(list_data)

        # # Rename columns to match headers
        # df.columns = headers

        # Handle datetime fields by ensuring they are timezone-unaware (if any datetime field has timezone)
        # for col in df.select_dtypes(include=['datetime']):
        #     df[col] = df[col].dt.tz_localize(None)

        # Create the HTTP response
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="customer_list.xlsx"'

        # Write the DataFrame to the Excel file using the openpyxl engine
        # df.to_excel(response, index=False, engine='openpyxl')
        wb.save(response)

        return response


@csrf_exempt
def export_customer_list(request):
    # if request.method == "POST":
        try:
            python_data = JSONParser().parse(io.BytesIO(request.body))
        except:
            python_data = {}
    
        # print("python_data--all_product_list--->", python_data)
        country = python_data.get('country',None)
        filter_condition = Q()

        if country not in [None,'','null']:
            filter_condition &= Q(country = country)

        today = timezone.now()

        list_data = []
        all_customers = models.CustomerDetail.objects.filter(filter_condition)
        for customer in all_customers:
            get_customer = models.CustomerDetail.objects.get(id = customer.id)
            get_customer_serializer = CustomerDetailSerializer(get_customer).data

            list_data.append(get_customer_serializer)

        headers = [
            'Email', 'Country Code', 'Mobile Number', 'Name', 'Gender', 'IP Address',
            'Country', 'Status'
        ]
    
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Customer"

        ws.append(headers) 
        field_map = {
            'Email':'email',
            'Country Code':'countryCode',
            'Mobile Number':'mobileNumber',
            'Name':'name',
            'Gender':'gender',
            'IP Address':'ip_address',
            'Country':'country',
            'Status':'status',
        }

        # if list_data:
        #     headers = list(list_data[0].keys())
        #     ws.append(headers)  # write headers

        for row in list_data:  # list_data = your queryset/serializer output
            ws.append([row.get(field_map[h], "") for h in headers])



       
        # Convert QuerySet to a DataFrame
        # df = pd.DataFrame(list_data)

        # # Rename columns to match headers
        # df.columns = headers

        # Handle datetime fields by ensuring they are timezone-unaware (if any datetime field has timezone)
        # for col in df.select_dtypes(include=['datetime']):
        #     df[col] = df[col].dt.tz_localize(None)

        # Create the HTTP response
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="customer_list.xlsx"'

        # Write the DataFrame to the Excel file using the openpyxl engine
        # df.to_excel(response, index=False, engine='openpyxl')
        wb.save(response)


        # res={
        #     'data':response
        # }
        # json_data = JSONRenderer().render(res)
        # return HttpResponse(json_data, content_type= 'application/json', status=200)

        return response
        

@csrf_exempt
def export_order_list_admin(request):
    if request.method == 'POST':
        python_data = JSONParser().parse(io.BytesIO(request.body))
        order_status = python_data.get('order_status', 'completed')


        list_data = []
        
        order_list = models.OrderDetail.objects.filter(order_status = order_status).order_by('-id')
        for order in order_list:          
            order_serializer = OrderDetailExportSerializer(order).data
            list_data.append(order_serializer)

        headers = [
            'ORDER Date',
            'ORDER ID',
            'Customer Name',
            'Email',
            'Country Code',
            'Mobile Number',
            'Payment ID',
            'Payment Type',
            'Air Shipping Price',
            'Ship Shipping Price',
            'Express Shipping Price',
            'Cargo Name',
            'Original Total Amount',
            'Total Price',
            'Order Status',
        ]
        
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Customer"

        ws.append(headers) 
        field_map = {
            'ORDER Date':'created_at',
            'ORDER ID':'order_id',
            'Customer Name':'customer_name',
            'Email':'email',
            'Country Code':'countryCode',
            'Mobile Number':'mobileNumber',
            'Payment ID':'payment_id',
            'Payment Type':'payment_type',
            'Air Shipping Price':'air_shipping_price',
            'Ship Shipping Price':'ship_shipping_price',
            'Express Shipping Price':'express_shipping_price',
            'Cargo Name':'cargo_name',
            'Original Total Amount':'original_total_amount',
            'Total Price':'total_price',
            'Order Status':'order_status',
        }

        for row in list_data:  # list_data = your queryset/serializer output
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
def export_vendor_list(request):
    if request.method == "POST":        
        list_data = []
        
        vendor_list = models.VendorDetail.objects.all().order_by('-id')
        for vendor in vendor_list:          
            vendor_serializer = VendorDetailSerializer(vendor).data
            list_data.append(vendor_serializer)

        headers = [
            'Company Name',
            'Vendor Name',
            'Phone Number',
            'Email',
            'Category Name',
            'City',
            'Country',
            'Status',
        ]
        
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Vendor"

        ws.append(headers) 
        field_map = {
            'Company Name':'company_name',
            'Vendor Name':'vendor_name',
            'Phone Number':'phone_number',
            'Email':'email',
            'Category Name':'category_name',
            'City':'city',
            'Country':'country',
            'Status':'status',
          
        }
      
        for row in list_data:  # list_data = your queryset/serializer output
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

