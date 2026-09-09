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
from googletrans import Translator
from django.core.files.base import ContentFile, File

from diabaApp.serializer import DailyPriceSerializer

BASE_URL = settings.BASE_URL
IMAGE_URL = settings.IMAGE_URL
LOGIN = "toubasi"
API_KEY = "5893b5f784a5e13fb525df276cbcbb49"
TOKEN = "f4043c2be69d324bafbe1ea0ac00898c"
SUBJECT = "test_API"
SIGNATURE = "DIABA"



def custom_404(request, exception):
    return JsonResponse({
        "status": False,
        "message": "Page not found"
    }, status=404)



@csrf_exempt
def translator_check(request):
    if request.method == 'POST':
        python_data = JSONParser().parse(io.BytesIO(request.body))
        text = python_data.get('text')
        dest_lang = "fr" 

        translator = Translator()
        translation = translator.translate(text, dest=dest_lang)

        
        res={
            'data':translation.text
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)


@csrf_exempt
def convert_product_french(request):
    if request.method == 'POST':
        # json_data = request.body
        # stream = io.BytesIO(json_data)
        # python_data = JSONParser().parse(stream)
        # id = python_data.get('id')
        dest_lang = "fr" 

        # product_data = models.ProductDetail.objects.get(id = id)
        # all_field_serializer = ProductDetailTransalteSerializer(product_data).data
        # list_data = []
        # print(all_field_serializer, 'all_field_serializer')
        # for key, value in all_field_serializer.items():
        #     # print(key, value, 'fieldfield')
        #     try_dict = {}
        #     if key != 'id':
        #         parameter = key + '_french'

        #         if value != '' and value != None and value != 'Approved' and value != 'Active' and type(value) != int:
        #             translator = Translator()
        #             translation = translator.translate(value, dest=dest_lang)
        #             value = translation.text
        #             print(value, 'value')
                
        #         try_dict.update({parameter:value})
        #         list_data.append(try_dict)
        # print(list_data)
        
        all_product_data = models.ProductDetail.objects.all()
        for product in all_product_data:
            product_id = product.id
            product_name = product.product_name
            
            translator = Translator()
            translation = translator.translate(product_name, dest=dest_lang)
            value = translation.text
            # print(value, 'value')

            data = models.ProductDetail.objects.get(id = product_id)
            data.product_name_french = value
            data.save()

        res={
            'data':'list_data'
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)



@csrf_exempt
def download_image(img_url):
    if img_url not in [None,'','null']:  
        img_url = img_url.strip()
        if img_url.startswith("http"):
            response = requests.get(img_url)
            if response.status_code == 200:
                image_content = ContentFile(response.content)

                print("image_content=-===-=-=--->",image_content)
                return image_content
            return None
        return None
    return None


@csrf_exempt
def bulk_import(request):
    if request.method == "POST":
        python_data={}
        for i,j in request.FILES.items():
            python_data.update({i:j})
        
        for i,j in request.POST.items():
            python_data.update({i:j})

        # print("python_data-=-=--bulk_import---->",python_data)

        bulk_import_excel = python_data.get("bulk_import_excel", None)

        if bulk_import_excel not in [None,'','null']:
            
            workbook = openpyxl.load_workbook(bulk_import_excel)

            product_sheet = workbook["product"]
            model_sheet = workbook["model"]
            variant_sheet = workbook["variant"]
            # vendor_sheet = workbook["vendor"]
            otherspecification_sheet = workbook["otherspecification"]


            for row in product_sheet.iter_rows(min_row=2, values_only=True):
                (
                    unique_product_id,
                    product_name, 
                    product_name_french,
                    category, 
                    subcategory, 
                    super_subcategory, 
                    country_of_origin,
                    description, 
                    description_french, 
                    unit_of_measure, 
                    material,
                    length, 
                    height, 
                    width, 
                    weight,
                    color, 
                    carton_length, 
                    carton_width, 
                    carton_height,
                    carton_weight, 
                    available_quantity, 
                    quantity, 
                    min_order_quantity,
                    max_order_quantity, 
                    product_image_1,
                    product_image_2, 
                    product_image_3, 
                    product_image_4,
                    price, 
                    discount, 
                    final_price, 
                    shipping_via,
                    refpro, 
                    reuser,
                    product_images,
                ) = row


                digits = "123456789"
                random_number = ""
                for i in range(3) :
                    random_number += digits[math.floor(random.random() * 9)]

                category_name = ""
                subcategory_name = ""
                category_id = None
                subcategory_id = None
                country_of_origin = None


                if models.CategoryDetail.objects.filter(category = category).exists():
                    category_name = models.CategoryDetail.objects.filter(category = category).values_list('category', flat=True)[0][:3].upper()
                    category_id = models.CategoryDetail.objects.filter(category = category).values_list('id', flat=True)[0]
                if models.SubCategoryDetail.objects.filter(subcategory = subcategory).exists():
                    subcategory_name = models.SubCategoryDetail.objects.filter(subcategory = subcategory).values_list('subcategory', flat=True)[0][:3].upper()
                    subcategory_id = models.SubCategoryDetail.objects.filter(subcategory = subcategory).values_list('id', flat=True)[0]
                if models.SuperSubCategoryDetail.objects.filter(super_subcategory = super_subcategory).exists():
                    super_subcategory_id = models.SuperSubCategoryDetail.objects.filter(super_subcategory = super_subcategory).values_list('id', flat=True)[0]
                if models.Country.objects.filter(country_name = country_of_origin).exists():
                    country_of_origin = models.SubCategoryDetail.objects.filter(country_name = country_of_origin).values_list('id', flat=True)[0]
                
                product_name_data = (product_name)[:3].upper()
                product_code =  category_name+'_'+subcategory_name+ '_'+ product_name_data + '_' + random_number
                # print(product_code, 'product_codeproduct_code')

                product_create = models.ProductDetail.objects.create(
                    product_name = product_name,
                    product_name_french = product_name_french,
                    product_code = product_code,
                    category_id = category_id,
                    subcategory_id = subcategory_id,
                    super_subcategory_id = super_subcategory_id,
                    country_of_origin_id = country_of_origin,
                    description = description,
                    description_french = description_french,
                    unit_of_measure = unit_of_measure,
                    material = material,
                    length = length,
                    height = height,
                    width = width,
                    weight = weight,
                    carton_length = carton_length,
                    carton_width = carton_width,
                    carton_height = carton_height,
                    carton_weight = carton_weight,
                    available_quantity = available_quantity,
                    quantity = quantity,
                    color = color,
                    min_order_quantity = min_order_quantity,
                    max_order_quantity = max_order_quantity,
                    product_image_1 = download_image(product_image_1),
                    product_image_2 = download_image(product_image_2),
                    product_image_3 = download_image(product_image_3),
                    product_image_4 = download_image(product_image_4),
                    # price = price,
                    discount = discount,
                    final_price = final_price,
                    status = 'Inactive',
                    product_verification = 'Approved',
                    shipping_via = shipping_via,
                    refpro = refpro,
                    reuser = reuser,
                )
                product_create.save()

                if product_images:
                    image_urls = product_images.split(",")
                    for img_url in image_urls:
                        img_url = img_url.strip()
                        if img_url.startswith("http"):
                            response = requests.get(img_url)
                            if response.status_code == 200:
                                image_content = ContentFile(response.content)
                                
                                models.ProductImage.objects.create(
                                    product_id=product_create.id,
                                    image=image_content,
                                )


                for specification_row in otherspecification_sheet.iter_rows(min_row=2, values_only=True):
                    (
                        unique_product_id_for_specification,
                        key,
                        key_french, 
                        value,
                        value_french, 
                    ) = specification_row


                    if unique_product_id == unique_product_id_for_specification:

                        product_specification = models.ProductOtherSpecification.objects.create(
                            product_id = product_create.id,
                            key = key,
                            key_french = key_french,
                            value = value,
                            value_french = value_french,
                        ).save()

                
                for model_row in model_sheet.iter_rows(min_row=2, values_only=True):
                    (
                        unique_product_id_for_model,
                        unique_model_id,
                        model_name,
                        model_name_french, 
                        model_image,
                        status,
                    ) = model_row

                    if unique_product_id == unique_product_id_for_model:
                        product_model = models.ProductModel.objects.create(
                            product_id = product_create.id,
                            model_name = model_name,
                            model_name_french = model_name_french,
                            model_image = download_image(model_image),
                            status = status,
                        )
                        product_model.save()


                        for model_row in variant_sheet.iter_rows(min_row=2, values_only=True):
                            (
                                unique_model_id_for_variant,
                                name,
                                name_french,
                                image,
                                price,
                            ) = model_row

                            if unique_model_id_for_variant == unique_model_id:

                                model_variant = models.ProductModelVariant.objects.create(
                                    product_id = product_create.id,
                                    model_id = product_model.id,
                                    name = name,
                                    name_french = name_french,
                                    image = download_image(image),
                                    price = price,
                                    variant_verification = 'Approved',
                                    status = 'Active'
                                ).save()


            res = {
                'message':'Bulk Import Successfull'
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)
        else:
            res={
                'message':'No Excel File Found or The File May be Corrupted'
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 406)


def send_sms(login, api_key, token, subject, signature, recipient, content,base_url="https://api.orangesmspro.sn:8443/api", verify_ssl=False):
    """
    Send SMS using Orange SMS Pro API
    """
    # Step 1: Generate timestamp and key
    timestamp = int(time.time())
    msg_to_encrypt = f"{token}{subject}{signature}{recipient}{content}{timestamp}"
    key = hmac.new(api_key.encode("utf-8"), msg_to_encrypt.encode("utf-8"), hashlib.sha1).hexdigest()

    # Step 2: Build query params
    params = {
        "token": token,
        "subject": subject,
        "signature": signature,
        "recipient": recipient,
        "content": content,
        "timestamp": timestamp,
        "key": key,
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
    }

    try:
        response = requests.get(
            base_url,
            params=params,
            headers=headers,
            auth=HTTPBasicAuth(login, token),
            verify=verify_ssl
        )
        data = {
            "status_code": response.status_code,
            "body": response.json() if response.headers.get("Content-Type") == "application/json" else response.text,
        }

        # print(True, data)
        return {
            "status_code": response.status_code,
            "body": response.json() if response.headers.get("Content-Type") == "application/json" else response.text,
        }

    except requests.RequestException as e:
        # print(False, str(e)) 
        return {"status_code": 500, "error": str(e)}

@csrf_exempt
def send_sms_api(request):
    if request.method == "POST":
        recipient = '221774115164'
        # recipient = '919265096459'
        digits = '123456789' 
        OTP = ""
        for i in range(4):
            OTP += digits[math.floor(random.random() * 9)]

        content = f'Your Diaba verification code is {OTP}. It will expire in 5 minutes. Do not share this code with anyone.'
        result = send_sms(
            LOGIN, API_KEY, TOKEN, SUBJECT, SIGNATURE, recipient, content
        )
    
        res={
            'message':'Chat Room not found'
        }
        json_data = JSONRenderer().render(res)
        return HttpResponse(json_data, content_type= 'application/json', status=200)

@csrf_exempt
def convert_string_date_to_datetime(request):
    if request.method == "POST":
        all_records = models.CustomerDetail.objects.all()

        updated_count = 0
        failed_records = []

        for record in all_records:

            if record.created_at not in [None, '', 'null']:

                try:

                    # convert string -> datetime
                    dt = datetime.strptime(
                        record.created_at,
                        "%Y-%m-%d, %H:%M:%S"
                    )

                    # make timezone aware (recommended)
                    dt = timezone.make_aware(dt)

                    # save into DateTimeField
                    record.created_at_datetime = dt

                    record.save(update_fields=["created_at_datetime"])

                    updated_count += 1

                except Exception as e:

                    failed_records.append({
                        "id": record.id,
                        "date": record.created_at,
                        "error": str(e)
                    })

        return JsonResponse({
            "status": "success",
            "updated_count": updated_count,
            "failed_records": failed_records
        })

    return JsonResponse({
        "status": "failed",
        "message": "POST method required"
    })


def fix_created_at_format(request):
    if request.GET.get("key") != "dateUpdate@icode49":
        return JsonResponse({"error": "Unauthorized"}, status=403)
    
    try:
        updated_count = 0
        failed_count = 0

        with transaction.atomic():
            records = models.OrderDetail.objects.exclude(created_at__isnull=True)

            for obj in records:
                if obj.created_at and "," in obj.created_at:
                    try:
                        # Convert: "2026-03-23, 07:19:46" -> datetime
                        parsed_date = datetime.strptime(obj.created_at, "%Y-%m-%d, %H:%M:%S")

                        # Save back in clean format (string for now)
                        obj.created_at = parsed_date.strftime("%Y-%m-%d %H:%M:%S")
                        obj.save(update_fields=["created_at"])

                        updated_count += 1
                    except Exception:
                        failed_count += 1

        return JsonResponse({
            "status": "success",
            "updated": updated_count,
            "failed": failed_count
        })

            # orders = models.OrderDetail.objects.filter(created_at__isnull=True)

            # updated_count = 0
            # failed_count = 0

            # for order in orders:
            #     if not order.created_at:
            #         continue

            #     try:
            #         # convert string → datetime
            #         created_dt = datetime.strptime(
            #             order.created_at,
            #             "%Y-%m-%d, %H:%M:%S"
            #         )

            #         # add 15 minutes expiry
            #         expire_dt = created_dt + timedelta(minutes=15)

            #         order.expire_at = expire_dt
            #         order.save(update_fields=['created_at'])

            #         updated_count += 1

            #     except Exception as e:
            #         failed_count += 1
            #         print(f"Error for order {order.id}: {e}")
        # return JsonResponse({
        #     "status": "success",
        #     "updated": updated_count,
        #     "failed": failed_count
        # })

    except Exception as e:
        return JsonResponse({
            "status": "error",
            "error": str(e)
        }, status=500)
      

@csrf_exempt
def daily_price(request):
    price_update = models.DailyPrice.objects.last()
    price = DailyPriceSerializer(price_update).data
    res={
        'data':price
    }
    return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)


@csrf_exempt
def daily_price_update(request):
    json_data = request.body
    stream = io.BytesIO(json_data)
    python_data = JSONParser().parse(stream)
    
    id = python_data.get('id')
    price_by_air = python_data.get('price_by_air')
    price_by_ship = python_data.get('price_by_ship')

    price_update = models.DailyPrice.objects.get(id = id)
    price_update.price_by_air = price_by_air
    price_update.price_by_ship = price_by_ship
    price_update.save()

    res={
        'message':'Price Update successfully.',

    }
    return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)


@csrf_exempt
def check_user(request):
    title = 'Trye'
    token = 'crfwj79jS8SzZSp7DR1bnu:APA91bFT2XqK-5KSyTgNWS06LkelLrDB_LP1OoB2Glk5aw9uXXEGA7VZgKqruVp4EtZmtM2S0pITTNqoycCKjfmZGnJulVkOYU8FXRyACeaKEbTpO8wZAus'
    try:
        message = messaging.Message(
        notification=messaging.Notification(
                title=title,
                body="Renew Now!",
            ),
            data={
                'notification_type' : "order"
            },
            token=token
            # tokens=token_chunk,
        )
        try:
            response = messaging.send(message)

            print("Notification Sent Successfully")

            # Process the response
            # print(f'{response.success_count} messages were sent successfully')
            # print(f'{response.failure_count} messages failed')

            # if response.failed_tokens:
            #     print("------5------")
            #     print('List of failed tokens and their errors:')
            #     for error in response.failed_tokens:
            #         print(f'  Token: {error.token}, Error: {error.exception}')

            # print("------6------")
        except Exception as e:
            print(f"An error occurred while sending multicast message: {e}")
    except Exception as e:
        print('Error---->',e)
    
    res = {
        'data': 'list_data' 
    }
    json_data = JSONRenderer().render(res)
    return HttpResponse(json_data, content_type= 'application/json', status=200)


@csrf_exempt
def need_to_change(request):
    if request.method == "POST":
        
        all_product = models.ProductDetail.objects.all()
        for product in all_product:
            print(product, 'product')
            all_product = models.ProductDetail.objects.get(id = product.id)

            product.available_country.set([1])
            
        res={
            "message":"Done"
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)

from googletrans import Translator

@csrf_exempt
def google_transalate(request):
    json_data = request.body
    stream = io.BytesIO(json_data)
    python_data = JSONParser().parse(stream)

    text = python_data.get('text')
    translator = Translator()

    result = translator.translate(text, src='en', dest='fr')
    res = {
        'data': result.text
    }
    json_data = JSONRenderer().render(res)
    return HttpResponse(json_data, content_type= 'application/json', status=200)

    