from re import search
from turtle import title

from django.db.models.fields import FloatField
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import JSONRenderer
from django.http import HttpResponse, FileResponse
from datetime import datetime, timedelta
from rest_framework.parsers import JSONParser
import io, os
from diabaApp import models
import math, random 
import json
import calendar
from googletrans import Translator
from django.db.models import Q, F, Count, Case, Sum, When, IntegerField, Value, OuterRef, Subquery, ExpressionWrapper, CharField, FloatField
from django.db.models.functions import Cast, TruncMonth, Coalesce, ExtractMonth, Round, TruncDate
from django.contrib.postgres.aggregates import ArrayAgg

from decimal import Decimal
import re

import openpyxl, requests
from django.core.files.base import ContentFile, File

import time
import hmac
import hashlib
import requests
from requests.auth import HTTPBasicAuth

from django.template.loader import get_template
from django.core.mail import send_mail
from django.conf import settings

from django.utils import timezone
from django.db.models import Max, Min

import firebase_config
from firebase_admin import messaging

import uuid

import numpy as np
import torch
import torchvision.models as torchmodels
import torchvision.transforms as transforms
from PIL import Image
import requests
from io import BytesIO
from sklearn.metrics.pairwise import cosine_similarity
import faiss
import clip
from collections import Counter

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
# from .models import Product


device = "cuda" if torch.cuda.is_available() else "cpu"

import pillow_avif

from django.template.loader import render_to_string
from weasyprint import HTML
from django.core.files.base import ContentFile


from django.core.files.storage import FileSystemStorage

from openpyxl import load_workbook
from openpyxl.styles import PatternFill
# SITE_MEDIA_BASE_URL = settings.SITE_MEDIA_BASE_URL ## BASE URLs for media which is defind in setting.py
# SITE_MEDIA_BASE_URL = 'http://122.167.187.175:8002/media/'
SITE_MEDIA_BASE_URL = 'https://diaba-live.s3.amazonaws.com/'


from django.db.models.functions import Trim
from django.core.files.storage import default_storage as fs




from django.contrib.postgres.search import TrigramSimilarity
from django.db.models.functions import Replace, Lower
from django.db.models import Value
from django.db.models import Q, Value, FloatField
from django.db.models.functions import Replace, Lower, Greatest
from django.db.models.expressions import Value as V
from django.contrib.postgres.search import TrigramWordSimilarity
    

BASE_URL = settings.BASE_URL
IMAGE_URL = settings.IMAGE_URL


from django.db.models.functions import Random

from .payment_gateway import APIDTSClient

from .serializer import AdminDetailSerializer, VendorDetailSerializer, CategoryDetailSerializer, SubCategoryDetailSerializer, \
    SuperSubCategoryDetailSerializer, ProductDetailSerializer, ProductRequestSerializer, ProductSearchSerializer, VendorProductPriceSerializer,\
    AdminProductDetailSerializer, VendorDataSerializer, AdminProductModelSerializer, ProductImageSerializer, ProductOtherSpecificationSerializer, \
    ProductModelVariantSerializer, ProductModelSerializer, CustomerDetailSerializer, CustomerAddressDetailSerializer, AdminProductModelVariantSerializer, \
    SubCategoryListSerializer, WishlistDetailSerializer, CartDetailSerializer, ProductDetailAppSerializer, OrderDetailSerializer, ProductOrderDetailSerializer, \
    ProductOrderDetailDataSerializer, VendorProductDataSerializer, ProductDataSerializer, VendorOrderDetailSerializer, VendorOrderDataSerializer, \
    OrderTrackingSerializer, ProductDetailTransalteSerializer, VendorProductvariantSerializer, AdminProductDataSerializer, AdminProductModelDataSerializer, \
    OrderDetailDataSerializer, ChatConversionSerializer, ChatRoomSerializer, DailyPriceSerializer, ChatAgentDetailSerializer,\
    AdminChatAgentDetailSerializer, ChatCustomerDetailSerializer, AgentInChatRoomHistorySerializer,AboutUsSerializer,PrivacyPolicySerializer,\
    RefundPolicySerializer,TermsAndConditionSerializer,VendorTransactionSerializer, ProductDetailCheckSerializer, RecentlyViewProductSerializer, \
    ProductNameSerializer, AdminModuleRightsDetailSerializer, OrderTransactionSerializer, WarehouseDetailSerializer, VendorOrderTrackingSerializer,\
    AdminCountryWithCurrencyListSerializer,AdminCurrencyConverterSerializer, ProductModelVariantSerializerAdmin, IntroBannerSerializer,\
    AppDynamicSettingSerializer, InfluencerDetailSerializer, PromocodeDetailSerializer, MoneyNetworkSerializer, ProductOrderDetailOrderSerializer, \
    CargoDetailSerializer, AdminCountrySerializer, ProductReviewSerializer, PaymentCargoSliderSerializer, ImportantNoteSerializer, ProductCountrySerializer, \
    ProductTagSerializer, DeliveryDayDetailSerializer,OrderDetailExportSerializer,VendorPaymentTrackerSerializer, ProductInquirySerializer, VendorDelayNoteSerializer,\
    VendorDetailExistsInDelayNote, ProductTagSearchSerializer, DummyTagProductNameEnglishSerializer,DummyTagProductNameFrenchSerializer,\
    CountryWiseBankDetailSerializer, ProductTypeSerializer, ProductPackagingBySerializer, OrderInquiryDataSerializer,\
    ChatAgentProductDetailSerializer



from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.core.cache import cache
import io

LOGIN = "toubasi"
API_KEY = "5893b5f784a5e13fb525df276cbcbb49"
TOKEN = "f4043c2be69d324bafbe1ea0ac00898c"
SUBJECT = "test_API"
SIGNATURE = "DIABA"


def custom_404(request, exception=None):
    return render(request, "404_page.html", status=404)


# efficientnet model


transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225])
])

# efficientnet model
model = torchmodels.efficientnet_b0(weights=torchmodels.EfficientNet_B0_Weights.DEFAULT)
model.eval()
model = model.to(device)
feature_extractor = torch.nn.Sequential(*list(model.children())[:-1]).to(device)


transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225])
])


device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess = clip.load("ViT-B/32", device=device)

FAISS_INDEX = None
FAISS_IDS = None

CACHE_CATEGORIES = []
TEXT_FEATURES = None

from .faiss_store import get_faiss_index, preload_clip_categories

# Extract vector from uploaded file -> convert file to vector
def extract_features_from_file(file):
    image = Image.open(file).convert("RGB")
    image = preprocess(image).unsqueeze(0).to(device)
    with torch.no_grad():
        features = model.encode_image(image)
    features = features / features.norm(dim=-1, keepdim=True)
    return features.cpu().numpy().astype("float32")

# Extract vector from image URL -> convert db image to vector
def extract_features_from_url(url):
    try:
        response = requests.get(url, timeout=10)
        image = Image.open(BytesIO(response.content)).convert("RGB")
        image = preprocess(image).unsqueeze(0).to(device)
        with torch.no_grad():
            features = model.encode_image(image)
        features = features / features.norm(dim=-1, keepdim=True)
        return features.cpu().numpy().astype("float32")
    except Exception as e:
        print(f"Failed to process {url}: {e}")
        return None


# vectors for DB products -> which don't have vectors yet
def ensure_product_vectors():
    products = models.ProductDetail.objects.filter(product_image_1_vector__isnull=True, product_image_1__isnull=False)
    for prod in products:
        feat = extract_features_from_url(prod.product_image_1)
        if feat is not None:
            prod.product_image_1_vector = feat.tolist()
            prod.save()
            print(f"Vector created for {prod.product_title} ({prod.id})")



# faiss: Facebook AI Research for efficient similarity search and clustering of high-dimensional vectors
def build_faiss_index(products):
    vectors, ids = [], []
    EXPECTED_DIM = 512

    for p in products:
        if p.product_image_1_vector:
            # print("p.product_image_1_vector=======>",p.product_image_1_vector)
            # print("type-p.product_image_1_vector=======>",type(p.product_image_1_vector))
            vec = np.array(p.product_image_1_vector, dtype="float32").flatten()
            # print("Product ID:", p.id)
            # print("Shape:", vec.shape)
            # print("Type-Shape:", type(vec.shape))
            # print("Size:", vec.size)
            # print("First type:", type(vec[0]))

            if vec.size > 0:
                if vec.size != EXPECTED_DIM:
                    continue
                vectors.append(vec)
                ids.append(p.id)
    if not vectors:
        return None, None
    
    # for p in products:
    #     try:
    #         # Assume `image_urls` field stores multiple URLs as JSON or comma-separated string
    #         image_urls = []
    #         if hasattr(p, "image_urls") and p.image_urls:
    #             try:
    #                 image_urls = json.loads(p.image_urls)  # JSON list
    #             except Exception:
    #                 image_urls = [u.strip() for u in str(p.image_urls).split(",") if u.strip()]
    #         else:
    #             # fallback to single image
    #             image_urls = [p.image_url] if p.image_url else []
    # 
    #         # Extract vector for each image
    #         for url in image_urls:
    #             feat = extract_features_from_url(url)
    #             if feat is not None and feat.size > 0:
    #                 vectors.append(feat.flatten())
    #                 ids.append(p.product_id)
    # 
    #     except Exception as e:
    #         print(f"[WARN] Skipping product {p.product_id}: {e}")
    #         continue

    vectors = np.stack(vectors)
    faiss.normalize_L2(vectors)
    index = faiss.IndexFlatIP(vectors.shape[1])
    index.add(vectors)
    return index, ids


def preload_faiss():

    global FAISS_INDEX
    global FAISS_IDS

    print("Loading FAISS index...")

    products = list(
        models.ProductDetail.objects.filter(
            Q(product_image_1_vector__isnull=False) |
            Q(product_image_2_vector__isnull=False) |
            Q(product_image_3_vector__isnull=False) |
            Q(product_image_4_vector__isnull=False) |
            Q(product_image_5_vector__isnull=False) |
            Q(product_image_6_vector__isnull=False) |
            Q(product_image_7_vector__isnull=False) |
            Q(product_image_8_vector__isnull=False)
        ).only(
            "id",
            "product_image_1_vector"
        )
    )

    FAISS_INDEX, FAISS_IDS = build_faiss_index(products)

    print("FAISS loaded")



def search_similar_products(query_vector, index, ids, top_k=10):
    faiss.normalize_L2(query_vector)
    D, I = index.search(query_vector, top_k)
    results = []
    for sim, idx in zip(D[0], I[0]):
        if idx < len(ids) and sim >= 0.75:
            results.append({"id": ids[idx], "similarity": float(sim)})
    return results






# # Normalize vectors
# def _safe_normalize(vec):
#     arr = np.array(vec, dtype=float)
#     if arr.size == 0 or np.any(np.isnan(arr)):
#         return None
#     norm = np.linalg.norm(arr)
#     if norm == 0:
#         return None
#     return arr / norm


# # check similarity and return results
# def compute_similarities(query_vector, products):
#     q = _safe_normalize(query_vector)
#     if q is None:
#         return []

#     valid_products = []
#     vecs = []
#     for p in products:
#         pv = (getattr(p, "product_image_1_vector", None)
#             or getattr(p, "product_image_2_vector", None)
#             or getattr(p, "product_image_3_vector", None)
#             or getattr(p, "product_image_4_vector", None))
#         pv_norm = _safe_normalize(pv)
#         print(pv_norm, 'pv')
#         if pv_norm is None:
#             # print(True)
#             continue
#         # print(False)
#         valid_products.append(p)
#         vecs.append(pv_norm)

#     if not vecs:
#         return []

#     db_mat = np.vstack(vecs)
#     sims = np.dot(db_mat, q).reshape(-1) 

#     results = []
#     for i, p in enumerate(valid_products):
#         results.append({
#             "product_id": getattr(p, "product_id", getattr(p, "id", None)),
#             "product_name": getattr(p, "product_name", ""),
#             "category": getattr(p, "category", None),
#             "subcategory": getattr(p, "subcategory", None),
#             # "colour": getattr(p, "colour", None),
#             "product_image_1": getattr(p, "product_image_1", None),
#             "product_image_2": getattr(p, "product_image_2", None),
#             "product_image_3": getattr(p, "product_image_3", None),
#             "product_image_4": getattr(p, "product_image_4", None),
#             "similarity": float(sims[i])
#         })


#     return sorted(results, key=lambda x: x['similarity'], reverse=True)

def compute_similarities(query_vector, products):
    q = _safe_normalize(query_vector)
    if q is None:
        return []

    results = []

    for p in products:
        best_sim = -1
        best_image_index = None
        best_image_url = None

        for i in range(1, 9):
            pv = getattr(p, f"product_image_{i}_vector", None)
            pv_norm = _safe_normalize(pv)
            if pv_norm is None:
                continue

            sim = float(np.dot(pv_norm, q))
            # print(sim, 'adfaf')
            if sim > best_sim:
                best_sim = sim
                best_image_index = i
                best_image_url = getattr(p, f"product_image_{i}", None)

        if best_sim >= 0:
            results.append({
                "product_id": getattr(p, "product_id", getattr(p, "id", None)),
                "product_name": getattr(p, "product_name", ""),
                "category": getattr(p, "category", None),
                "subcategory": getattr(p, "subcategory", None),
                "best_image": best_image_url,
                "image_index": best_image_index,
                "similarity": best_sim,
            })
            # print(results, 'CHeck check result')
    return sorted(results, key=lambda x: x['similarity'], reverse=True)


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
        


####################################################################################


@csrf_exempt
def app_dyanmic_setting_update(request):
    if request.method == "POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))

        print('pytohn_data---app_dyanmic_setting_update--->',python_data)

        # login_page = python_data.get('login_page',None)
        # otp_page = python_data.get('otp_page',None)
        # subscription_page = python_data.get('subscription_page',None)
        # ios_free_content = python_data.get('ios_free_content',None)
        app_version = python_data.get('app_version',None)
        release_note = python_data.get('release_note',None)

        if models.AppDynamicSetting.objects.all().count() > 0:
            setting = models.AppDynamicSetting.objects.all().first()

            # if not isinstance(login_page, str):
            #     setting.login_page = login_page
            # if not isinstance(otp_page, str):
            #     setting.otp_page = otp_page
            # if not isinstance(subscription_page, str):
            #     setting.subscription_page = subscription_page
                
            # setting.ios_free_content = python_data.get('ios_free_content',setting.ios_free_content)
            setting.release_note = python_data.get('release_note',setting.release_note)
            setting.app_version = python_data.get('app_version',setting.app_version)

            setting.save()

        else:
            models.AppDynamicSetting.objects.create(
                # login_page = login_page,
                # otp_page = otp_page,
                # subscription_page = subscription_page,
                # ios_free_content = ios_free_content,
                app_version = app_version,
                release_note = release_note,
            )

        res={
            'message':'Settings Updated'
        }
        return HttpResponse(JSONRenderer().render(res), content_type='application/json', status=200)
    

@csrf_exempt
def app_setting(request):
    if request.method == "POST":
        setting = models.AppDynamicSetting.objects.all().first()
        setting_serializer = AppDynamicSettingSerializer(setting).data
    

        res={
            'data':setting_serializer
        }
        return HttpResponse(JSONRenderer().render(res), content_type='application/json', status=200)


@csrf_exempt
def admin_app_dynamic_setting(request):
    if request.method == "POST":
        setting = models.AppDynamicSetting.objects.all().first()

        setting_serializer = AppDynamicSettingSerializer(setting).data

        res={
            'data':setting_serializer
        }
        return HttpResponse(JSONRenderer().render(res), content_type='application/json', status=200)





####################################################################################






@csrf_exempt
def admin_login(request):
    if request.method == 'POST':
        python_data = JSONParser().parse(io.BytesIO(request.body))
        
        now = datetime.now()
        date_time = now.strftime('%Y-%m-%d, %H:%M:%S')

        email = python_data.get('email')
        password = python_data.get('password') 
        check_email = models.AdminDetail.objects.filter(email = email, status='Active').count()

        if check_email == 1:
            check_password = models.AdminDetail.objects.filter(email = email, password = password).count()
            if check_password == 1:
                get_user = models.AdminDetail.objects.get(email = email)
                get_user.lastLoginDate = date_time
                get_user.save()
                user_serialiser = AdminDetailSerializer(get_user).data

                admin_rights = models.AdminModuleRightsDetail.objects.filter(admin = get_user.id)
                rights_serialiser = AdminModuleRightsDetailSerializer(admin_rights, many=True).data


                res = {
                    'data':user_serialiser,
                    'rights':rights_serialiser      
                    }
                json_data = JSONRenderer().render(res)
                return HttpResponse(json_data, content_type= 'application/json', status=200)
            else:
                res = {
                    'message':'Enter Valid Password'        
                    }
                json_data = JSONRenderer().render(res)
                return HttpResponse(json_data, content_type= 'application/json', status=406)
        else:
            res = {
                    'message':'Enter Valid email or your account is inactive.'
                }
            json_data = JSONRenderer().render(res)
            return HttpResponse(json_data, content_type= 'application/json', status=406)



@csrf_exempt
def vendor_register(request):
    if request.method == 'POST':
        python_data={}
        for i,j in request.FILES.items():
            python_data.update({i:j})
        
        for i,j in request.POST.items():
            python_data.update({i:j})
        
        # print(python_data, 'python_datapython_data')
        now = datetime.now()
        date_time = now.strftime('%Y-%m-%d, %H:%M:%S')
        
        digits = "abcdefghjiklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
        password = ""
        for i in range(8) :
            password += digits[math.floor(random.random() * 52)]
        

        email = python_data.get('email')
        address = python_data.get('address', None)
        address = json.loads(address)
        phone_number = python_data.get('phone_number', None)
        
        check_email = models.VendorDetail.objects.filter(email = email).count()

        if check_email == 0:
            check_phone_number = models.VendorDetail.objects.filter(phone_number = phone_number).count()
            if check_phone_number == 0:
                vendor = models.VendorDetail.objects.create(
                    category_id = python_data.get('category'),
                    subcategory_id = python_data.get('subcategory'),
                    company_name = python_data.get('company_name'),
                    business_type = python_data.get('business_type'),
                    legal_form = python_data.get('legal_form'),
                    city = python_data.get('city'),
                    country = python_data.get('country'),
                    company_start_date = python_data.get('company_start_date'),
                    office_address = python_data.get('office_address'),
                    total_employee = python_data.get('total_employee'),
                    production_capacity = python_data.get('production_capacity'),
                    vendor_name = python_data.get('vendor_name'),
                    phone_number = python_data.get('phone_number'),
                    email = python_data.get('email'),
                    document_type = python_data.get('document_type', None),
                    document = python_data.get('document', None),
                    website = python_data.get('website'),
                    password = password,
                    status = 'Active',
                    is_verify = 'pending',
                    created_at = date_time
                )
                vendor.save()
 
                if address != None and address != []:
                    for single in address:
                        # print(single, 'single')
                        create = models.VendorAddress.objects.create(
                            vendor_id = vendor.id,
                            location_type = single.get('location_type'),
                            description = single.get('description'),
                            office_address = single.get('office_address'),
                            created_at = date_time
                        ).save()

                try:
                    context = {
                        'vendor_email':email,
                        'vendor_password': password, 
                        'vendor_name':python_data.get('vendor_name'),
                        'current_year':datetime.now().year
                        }
                    htmlgen = get_template("new_vendor_register.html").render(context)
                    # send_mail('Diaba - Team Onboarding',"password",'settings.EMAIL_HOST_USER',[email], fail_silently=False, html_message=htmlgen)

                    send_mail(
                        subject='Diaba - Team Onboarding',
                        message='password',
                        from_email=settings.EMAIL_HOST_USER,
                        recipient_list=[email],
                        fail_silently=False,
                        html_message=htmlgen
                    )
                    
                    # print("MAIL SENT SUCCESSFULLY-=-=-=-=-=-=-=-")
                except Exception as e:
                    print("print------>",e)

                res = {
                    'message':"Registerd successfully."        
                    }
                json_data = JSONRenderer().render(res)
                return HttpResponse(json_data, content_type= 'application/json', status=200)
            else:
                res = {
                    'message':'Enter Mobile number is already registerd.'        
                    }
                json_data = JSONRenderer().render(res)
                return HttpResponse(json_data, content_type= 'application/json', status=406)
        else:
            res = {
                    'message':'Enter Email is already registerd.'        
                }
            json_data = JSONRenderer().render(res)
            return HttpResponse(json_data, content_type= 'application/json', status=406)



@csrf_exempt
def vendor_credentials_resend(request):
    if request.method == 'POST':
        python_data = JSONParser().parse(io.BytesIO(request.body))
        id = python_data.get('id')
        if models.VendorDetail.objects.filter(id = id).exists():
            vendor = models.VendorDetail.objects.get(id = id)
            try:
                context = {
                    'vendor_email':vendor.email,
                    'vendor_password': vendor.password, 
                    'vendor_name':vendor.company_name,
                    'current_year':datetime.now().year
                }

                htmlgen = get_template("resend_vendor_creds.html").render(context)
                # send_mail('Diaba - Team Onboarding',"password",'settings.EMAIL_HOST_USER',[email], fail_silently=False, html_message=htmlgen)

                send_mail(
                    subject='Diaba - Login Credentials',
                    message='password',
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[vendor.email],
                    fail_silently=False,
                    html_message=htmlgen
                )
            except Exception as e:
                print("print------>",e)
            res={
                'message':"Vendor credentials resent successfully."
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)
        else:
            res = {
                'message':'Vendor Not Found'
            }
            json_data = JSONRenderer().render(res)
            return HttpResponse(json_data, content_type= 'application/json', status=406)     


@csrf_exempt
def vendor_login(request):
    if request.method == 'POST':
        python_data = JSONParser().parse(io.BytesIO(request.body))
        
        now = datetime.now()
        date_time = now.strftime('%Y-%m-%d, %H:%M:%S')

        email = python_data.get('email')
        password = python_data.get('password') 
        check_email = models.VendorDetail.objects.filter(email = email).count()

        if check_email == 1:
            check_activation = models.VendorDetail.objects.filter(email = email, status = 'Active').count()
            if check_activation == 1:
                check_password = models.VendorDetail.objects.filter(email = email, password = password).count()
                if check_password == 1:
                    get_user = models.VendorDetail.objects.get(email = email)
                    get_user.lastLoginDate = date_time
                    get_user.save()
                    user_serialiser = VendorDetailSerializer(get_user).data

                    check_login_data = models.VendorLoginHistory.objects.filter(email = email).count()
                    if check_login_data == 0:
                        first_time_login = True
                        login = models.VendorLoginHistory.objects.create(
                            email = email,
                            login_time = date_time
                        ).save()
                    else:
                        first_time_login = False
                        login = models.VendorLoginHistory.objects.create(
                            email = email,
                            login_time = date_time
                        ).save()

                    res = {
                        'data':user_serialiser,
                        "first_time_login":first_time_login,
                        'role':'vendor'        
                        }
                    json_data = JSONRenderer().render(res)
                    return HttpResponse(json_data, content_type= 'application/json', status=200)
                res = {
                    'message':'Enter Valid Password'        
                    }
                json_data = JSONRenderer().render(res)
                return HttpResponse(json_data, content_type= 'application/json', status=406)
            res = {
                'message':'Enter account is inactive'        
                }
            json_data = JSONRenderer().render(res)
            return HttpResponse(json_data, content_type= 'application/json', status=406)

        res = {
                'message':'Enter Valid email'        
            }
        json_data = JSONRenderer().render(res)
        return HttpResponse(json_data, content_type= 'application/json', status=406)

@csrf_exempt
def vendor_update(request):
    if request.method == 'POST':
        # python_data = JSONParser().parse(io.BytesIO(request.body))
        python_data={}
        for i,j in request.FILES.items():
            python_data.update({i:j})
        
        for i,j in request.POST.items():
            python_data.update({i:j})
        
        # print(python_data, 'python_data')
        now = datetime.now()
        date_time = now.strftime('%Y-%m-%d, %H:%M:%S')
        id = python_data.get('id')
        check_vendor = models.VendorDetail.objects.filter(id = id).count()
        if check_vendor == 1:
            get_vendor_email = models.VendorDetail.objects.get(id = id)
            get_email = get_vendor_email.email
            email = python_data.get('email')
            if get_email == email:
                vendor = models.VendorDetail.objects.get(id = id)
                vendor.email = python_data.get('email', vendor.email)
                vendor.category_id = python_data.get('category', vendor.category)
                # vendor.subcategory_id = python_data.get('subcategory', vendor.subcategory)
                vendor.company_name = python_data.get('company_name', vendor.company_name)
                vendor.business_type = python_data.get('business_type', vendor.business_type)
                vendor.legal_form = python_data.get('legal_form', vendor.legal_form)
                vendor.city = python_data.get('city', vendor.city)
                vendor.country = python_data.get('country', vendor.country)
                vendor.company_start_date = python_data.get('company_start_date', vendor.company_start_date)
                vendor.office_address = python_data.get('office_address', vendor.office_address)
                vendor.total_employee = python_data.get('total_employee', vendor.total_employee)
                vendor.production_capacity = python_data.get('production_capacity', vendor.production_capacity)
                vendor.vendor_name = python_data.get('vendor_name', vendor.vendor_name)
                vendor.document_type = python_data.get('document_type', vendor.document_type)
                if type(python_data.get('document')) != str:
                    vendor.document = python_data.get('document', vendor.document)

                vendor.is_verify = python_data.get('is_verify', vendor.is_verify)
                vendor.website = python_data.get('website', vendor.website)
                vendor.save()
            else:
                check_email = models.VendorDetail.objects.filter(email = email).count()
                if check_email == 1:
                    res = {
                        'message':'This email is already registerd.'        
                        }
                    json_data = JSONRenderer().render(res)
                    return HttpResponse(json_data, content_type= 'application/json', status=406)
                else:
                    digits = "abcdefghjiklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
                    password = ""
                    for i in range(8) :
                        password += digits[math.floor(random.random() * 52)]

                    vendor = models.VendorDetail.objects.get(id = id)
                    vendor.email = python_data.get('email', vendor.email)
                    vendor.category_id = python_data.get('category', vendor.category)
                    # vendor.subcategory_id = python_data.get('subcategory', vendor.subcategory)
                    vendor.company_name = python_data.get('company_name', vendor.company_name)
                    vendor.business_type = python_data.get('business_type', vendor.business_type)
                    vendor.legal_form = python_data.get('legal_form', vendor.legal_form)
                    vendor.city = python_data.get('city', vendor.city)
                    vendor.country = python_data.get('country', vendor.country)
                    vendor.company_start_date = python_data.get('company_start_date', vendor.company_start_date)
                    vendor.office_address = python_data.get('office_address', vendor.office_address)
                    vendor.total_employee = python_data.get('total_employee', vendor.total_employee)
                    vendor.production_capacity = python_data.get('production_capacity', vendor.production_capacity)
                    vendor.vendor_name = python_data.get('vendor_name', vendor.vendor_name)
                    vendor.document_type = python_data.get('document_type', vendor.document_type)
                    if type(python_data.get('document')) != str:
                        vendor.document = python_data.get('document', vendor.document)

                    vendor.is_verify = python_data.get('is_verify', vendor.is_verify)
                    vendor.website = python_data.get('website', vendor.website)
                    vendor.password = password
                    vendor.save()
                    email = vendor.email
                    try:
                        context = {
                            'email':email,
                            'password': password
                        }
                        htmlgen = get_template("vendor_confirm_mail.html").render(context)

                        send_mail(
                            subject='Your Updated Login Credentials for Diaba Marketplace',
                            message='password',
                            from_email=settings.EMAIL_HOST_USER,
                            recipient_list=[email],
                            fail_silently=False,
                            html_message=htmlgen
                        )
                        
                        # print("MAIL SENT SUCCESSFULLY-=-=-=-=-=-=-=-")
                    except Exception as e:
                        print("print------>",e)


            res = {
                'message':"vendor Update Successfully.",
                
                }
            json_data = JSONRenderer().render(res)
            return HttpResponse(json_data, content_type= 'application/json', status=200)
        else: 
            res = {
                'message':'Something went wrong.'        
                }
            json_data = JSONRenderer().render(res)
            return HttpResponse(json_data, content_type= 'application/json', status=406)

@csrf_exempt
def vendor_verification(request):
    if request.method == 'POST':
        python_data = JSONParser().parse(io.BytesIO(request.body))
        
        now = datetime.now()
        date_time = now.strftime('%Y-%m-%d, %H:%M:%S')

        email = python_data.get('email')
        
        check_email = models.VendorDetail.objects.filter(email = email).count()
        if check_email == 1:
            update = models.VendorDetail.objects.get(email = email)
            update.is_verify = 'true'
            update.save()

            res = {
                'message':'Vendor is verified now.'        
            }
            json_data = JSONRenderer().render(res)
            return HttpResponse(json_data, content_type= 'application/json', status=200)

@csrf_exempt
def category_create(request):
    python_data={}
    for i,j in request.FILES.items():
        python_data.update({i:j})
    
    for i,j in request.POST.items():
        python_data.update({i:j})

    category = python_data.get('category')
    category_french = python_data.get('category_french')
    image = python_data.get('image', None)
    check_category = models.CategoryDetail.objects.filter(category = category).count()
    if check_category == 0:
        category_create = models.CategoryDetail.objects.create(
            category = category,
            category_french = category_french,
            image = image,
            status = 'Active'
            ).save()
        res = {
            'message':'Category create successfully.'        
        }
        json_data = JSONRenderer().render(res)
        return HttpResponse(json_data, content_type= 'application/json', status=200)
    else:
        res = {
            'message':'Category already registerd.'        
        }
        json_data = JSONRenderer().render(res)
        return HttpResponse(json_data, content_type= 'application/json', status=406)


@csrf_exempt
def category_update(request):
    python_data={}
    for i,j in request.FILES.items():
        python_data.update({i:j})
    
    for i,j in request.POST.items():
        python_data.update({i:j})

    id = python_data.get('id')
    category = python_data.get('category')
    category_french = python_data.get('category_french')
    image = python_data.get('image', None)
    status = python_data.get('status', None)

    check_category = models.CategoryDetail.objects.filter(id = id, category = category,category_french = category_french ).count()
    if check_category == 1:
        category_update = models.CategoryDetail.objects.get(id = id)
        category_update.category = python_data.get('category', category_update.category)
        category_update.category_french = python_data.get('category_french', category_update.category_french)
        if type(python_data.get('image')) != str:
            category_update.image = image
        category_update.status = python_data.get('status', category_update.status)
        category_update.save()
        res = {
            'message':'Category Update successfully.'        
        }
        json_data = JSONRenderer().render(res)
        return HttpResponse(json_data, content_type= 'application/json', status=200)
    else:
        check_category = models.CategoryDetail.objects.filter(category = category,category_french = category_french ).count()
        if check_category == 0:
            category_update = models.CategoryDetail.objects.get(id = id)
            category_update.category = python_data.get('category', category_update.category)
            category_update.category_french = python_data.get('category_french', category_update.category_french)
            if type(python_data.get('image')) != str:
                category_update.image = image
            category_update.status = python_data.get('status', category_update.status)
            category_update.save()
            res = {
                'message':'Category Update successfully.'        
            }
            json_data = JSONRenderer().render(res)
            return HttpResponse(json_data, content_type= 'application/json', status=200)
        else:
            res = {
                'message':'Category already registerd.'        
            }
            json_data = JSONRenderer().render(res)
            return HttpResponse(json_data, content_type= 'application/json', status=406)



@csrf_exempt
def all_category_list(request):
    all_category = models.CategoryDetail.objects.all().order_by('-id')
    serializer = CategoryDetailSerializer(all_category, many=True).data

    res = {
        'data': serializer 
    }
    json_data = JSONRenderer().render(res)
    return HttpResponse(json_data, content_type= 'application/json', status=200)


@csrf_exempt
def subcategory_create(request):
    python_data={}
    for i,j in request.FILES.items():
        python_data.update({i:j})
    
    for i,j in request.POST.items():
        python_data.update({i:j})

    category = python_data.get('category_id')
    subcategory = python_data.get('subcategory')
    subcategory_french = python_data.get('subcategory_french')
    image = python_data.get('image', None)
    check_category = models.SubCategoryDetail.objects.filter(category = category, subcategory= subcategory).count()
    # print(check_category, 'check_category', python_data)
    if check_category == 0:
        category_create = models.SubCategoryDetail.objects.create(
            category_id = category,
            subcategory = subcategory,
            subcategory_french = subcategory_french,
            image = image,
            status = 'Active'
            ).save()
        res = {
            'message':'Sub Category create successfully.'        
        }
        json_data = JSONRenderer().render(res)
        return HttpResponse(json_data, content_type= 'application/json', status=200)
    else:
        res = {
            'message':'Sub Category already registerd.'        
        }
        json_data = JSONRenderer().render(res)
        return HttpResponse(json_data, content_type= 'application/json', status=406)

@csrf_exempt
def subcategory_update(request):
    python_data={}
    for i,j in request.FILES.items():
        python_data.update({i:j})
    
    for i,j in request.POST.items():
        python_data.update({i:j})

    id = python_data.get('id')
    category = python_data.get('category')
    subcategory = python_data.get('subcategory')
    subcategory_french = python_data.get('subcategory_french')
    image = python_data.get('image', None)
    status = python_data.get('status', None)

    check_subcategory = models.SubCategoryDetail.objects.filter(id = id, category = category, subcategory = subcategory, subcategory_french = subcategory_french ).count()
    if check_subcategory == 1:
        subcategory_update = models.SubCategoryDetail.objects.get(id = id)
        subcategory_update.category_id = python_data.get('category', subcategory_update.category)
        subcategory_update.subcategory = python_data.get('subcategory', subcategory_update.subcategory)
        subcategory_update.subcategory_french = python_data.get('subcategory_french', subcategory_update.subcategory_french)
        if type(python_data.get('image')) != str:
            subcategory_update.image = image
        subcategory_update.status = python_data.get('status', subcategory_update.status)
        subcategory_update.save()
        res = {
            'message':'Subcategory Update successfully.'        
        }
        json_data = JSONRenderer().render(res)
        return HttpResponse(json_data, content_type= 'application/json', status=200)
    else:
        check_subcategory = models.SubCategoryDetail.objects.filter(category = category, subcategory = subcategory, subcategory_french = subcategory_french).count()
        if check_subcategory == 0:
            subcategory_update = models.SubCategoryDetail.objects.get(id = id)
            subcategory_update.category_id = python_data.get('category', subcategory_update.category)
            subcategory_update.subcategory = python_data.get('subcategory', subcategory_update.subcategory)
            subcategory_update.subcategory_french = python_data.get('subcategory_french', subcategory_update.subcategory_french)
            if type(python_data.get('image')) != str:
                subcategory_update.image = image
            subcategory_update.status = python_data.get('status', subcategory_update.status)
            subcategory_update.save()
            res = {
                'message':'Subcategory Update successfully.'        
            }
            json_data = JSONRenderer().render(res)
            return HttpResponse(json_data, content_type= 'application/json', status=200)
        else:
            res = {
                'message':'Subcategory already registerd.'        
            }
            json_data = JSONRenderer().render(res)
            return HttpResponse(json_data, content_type= 'application/json', status=406)


@csrf_exempt
def all_subcategory_list(request):
    all_category = models.SubCategoryDetail.objects.all().order_by('-id')
    serializer = SubCategoryDetailSerializer(all_category, many=True).data

    res = {
        'data': serializer 
    }
    json_data = JSONRenderer().render(res)
    return HttpResponse(json_data, content_type= 'application/json', status=200)



@csrf_exempt
def super_subcategory_create(request):
    python_data={}
    for i,j in request.FILES.items():
        python_data.update({i:j})
    
    for i,j in request.POST.items():
        python_data.update({i:j})

    category = python_data.get('category_id')
    subcategory = python_data.get('subcategory_id')
    super_subcategory = python_data.get('super_subcategory')
    image = python_data.get('image', None)
    check_category = models.SuperSubCategoryDetail.objects.filter(category = category, subcategory= subcategory, super_subcategory= super_subcategory).count()
    if check_category == 0:
        category_create = models.SuperSubCategoryDetail.objects.create(
            category_id = category,
            subcategory_id = subcategory,
            super_subcategory = super_subcategory,
            image = image,
            status = 'Active'
            ).save()
        res = {
            'message':'Super Sub Category create successfully.'        
        }
        json_data = JSONRenderer().render(res)
        return HttpResponse(json_data, content_type= 'application/json', status=200)
    else:
        res = {
            'message':'Super Sub Category already registerd.'        
        }
        json_data = JSONRenderer().render(res)
        return HttpResponse(json_data, content_type= 'application/json', status=406)


@csrf_exempt
def all_super_subcategory_list(request):
    all_super_category = models.SuperSubCategoryDetail.objects.all()
    serializer = SuperSubCategoryDetailSerializer(all_super_category, many=True).data

    res = {
        'data': serializer 
    }
    json_data = JSONRenderer().render(res)
    return HttpResponse(json_data, content_type= 'application/json', status=200)



# @csrf_exempt
# def product_create(request):
#     python_data={}
#     for i,j in request.FILES.items():
#         python_data.update({i:j})
    
#     for i,j in request.POST.items():
#         python_data.update({i:j})

#     print(python_data, 'python_data')
#     product_name = python_data.get('product_name')
#     # product_code = python_data.get('product_code', None)
#     category = python_data.get('category')
#     subcategory = python_data.get('subcategory')
#     super_subcategory = python_data.get('super_subcategory')
#     description = python_data.get('description')
#     unit_of_measure = python_data.get('unit_of_measure')
#     material = python_data.get('material')
#     length = python_data.get('length')
#     height = python_data.get('height')
#     width = python_data.get('width')
#     weight = python_data.get('weight')
#     color = python_data.get('color')
#     min_order_quantity = python_data.get('min_order_quantity')
#     max_order_quantity = python_data.get('max_order_quantity')
#     quantity = python_data.get('quantity')
#     product_image_1 = python_data.get('product_image_1')
#     product_image_2 = python_data.get('product_image_2')
#     product_image_3 = python_data.get('product_image_3')
#     product_image_4 = python_data.get('product_image_4')
#     price = python_data.get('price')
#     discount = python_data.get('discount')
#     final_price = python_data.get('final_price')
#     vendor = python_data.get('vendor')
#     product_verification = python_data.get('product_verification')
#     # syncWithDimensions = python_data.get('syncWithDimensions')
#     carton_length = python_data.get('carton_length')
#     carton_width = python_data.get('carton_width')
#     carton_height = python_data.get('carton_height')
#     carton_weight = python_data.get('carton_weight')
#     syncWithModelOrVariant = python_data.get('syncWithModelOrVariant')
#     available_quantity = python_data.get('available_quantity')
#     quantity = python_data.get('quantity')

#     digits = "123456789"
#     random_number = ""
#     for i in range(3) :
#         random_number += digits[math.floor(random.random() * 9)]

#     category_name = models.CategoryDetail.objects.filter(id = category).values_list('category', flat=True)[0][:3].upper()
#     subcategory_name = models.SubCategoryDetail.objects.filter(id = subcategory).values_list('subcategory', flat=True)[0][:3].upper()
#     product_name_data = (product_name)[:3].upper()
#     product_code =  category_name+'_'+subcategory_name+ '_'+ product_name_data + '_' + random_number
#     print(product_code, 'product_codeproduct_code')
#     product = models.ProductDetail.objects.create(
#         product_name = product_name,
#         product_code = product_code,
#         vendor_id = vendor,
#         category_id = category,
#         subcategory_id = subcategory,
#         super_subcategory_id = super_subcategory,
#         description = description,
#         unit_of_measure = unit_of_measure,
#         material = material,
#         length = length,
#         height = height,
#         width = width,
#         weight = weight,
#         # syncWithDimensions = syncWithDimensions,
#         carton_length = carton_length,
#         carton_width = carton_width,
#         carton_height = carton_height,
#         carton_weight = carton_weight,
#         syncWithModelOrVariant = syncWithModelOrVariant,
#         available_quantity = available_quantity,
#         quantity = quantity,
#         color = color,
#         min_order_quantity = min_order_quantity,
#         max_order_quantity = max_order_quantity,
#         product_image_1 = product_image_1,
#         product_image_2 = product_image_2,
#         product_image_3 = product_image_3,
#         product_image_4 = product_image_4,
#         price = price,
#         discount = discount,
#         final_price = final_price,
#         status = 'pending',
#         product_verification = 'pending'
#     )
#     product.save()
#     product_id = product.id 

#     price = models.VendorProductPrice.objects.create(
#         vendor_id = vendor,
#         product_id = product_id,
#         price = price,
#         quantity = quantity,
#         status = "pending",
#     ).save()

#     res = {
#         'message':'Project create successfully.'        
#     }
#     json_data = JSONRenderer().render(res)
#     return HttpResponse(json_data, content_type= 'application/json', status=200)


@csrf_exempt
def pending_product_verification_list_admin(request):
    json_data = request.body
    stream = io.BytesIO(json_data)
    python_data = JSONParser().parse(stream)
    
    page_number = int(python_data.get('page_number', 1))
    row_size = int(python_data.get('row_data', 10))
    last_row = row_size * page_number
    first_row = last_row - row_size

    total_pending_count = models.ProductDetail.objects.filter(product_verification = 'Pending').count()
    all_product = models.ProductDetail.objects.filter(product_verification = 'Pending')[first_row:last_row]
    serializer = ProductDetailSerializer(all_product, many=True).data

    res = {
        'data': serializer,
        'total_pending_product_count':total_pending_count
    }
    json_data = JSONRenderer().render(res)
    return HttpResponse(json_data, content_type= 'application/json', status=200)


@csrf_exempt
def product_verification_update(request):
    json_data = request.body
    stream = io.BytesIO(json_data)
    python_data = JSONParser().parse(stream)
    id = python_data.get('id')

    request_form = models.ProductDetail.objects.get(id = id)
    request_form.product_verification = python_data.get('product_verification', request_form.product_verification)
    request_form.save()

    res = {
        'message':'Product verification update successfully.'        
    }
    json_data = JSONRenderer().render(res)
    return HttpResponse(json_data, content_type= 'application/json', status=200)

# @csrf_exempt
# def all_product_list(request):
#     python_data = JSONParser().parse(io.BytesIO(request.body))
    
#     print("python_data--all_product_list--->", python_data)

#     today = timezone.now()

#     page_number = int(python_data.get('page_number', 1))
#     row_size = int(python_data.get('row_data', 10))
#     last_row = row_size * page_number
#     first_row = last_row - row_size

#     category_name = python_data.get('category_name',None)
#     search_key = python_data.get('search_key',None)
#     subcategory_name = python_data.get('subcategory_name',None)
#     status = python_data.get('status',None)
#     product_added_from = python_data.get('product_added_from',None)

#     filter_condition = Q()

#     if category_name not in [None,'','null']:
#         filter_condition &= Q(category__category = category_name)
#     if subcategory_name not in [None,'','null']:
#         filter_condition &= Q(subcategory__subcategory = subcategory_name)
#     if search_key not in [None,'','null']:
#         filter_condition &= Q(product_name__icontains = search_key)|Q(refpro__icontains = search_key | Q(product_code__icontains = search_key) | Q(product_name_french__icontains = search_key))
#     if status not in [None,'','null']:
#         filter_condition &= Q(status = status)
#     if product_added_from not in [None,'','null']:
#         filter_condition &= Q(product_added_from = product_added_from)

#     total_bulk_records = models.ProductDetail.objects.filter(filter_condition, status= 'bulk').count()

    
#     total_records = models.ProductDetail.objects.filter(filter_condition, product_verification= 'Approved').exclude(status = 'bulk').count()
#     # all_product = models.ProductDetail.objects.filter(filter_condition).order_by('-id')[first_row:last_row]
#     # serializer = ProductDetailSerializer(all_product, many=True).data
#     total_pending_records = models.ProductDetail.objects.filter(product_verification= 'Pending').count()
    
#     list_data = []
#     all_product = models.ProductDetail.objects.filter(filter_condition, product_verification= 'Approved').exclude(status = 'bulk').order_by('-id')[first_row:last_row]
#     for product in all_product:
#         product = models.ProductDetail.objects.get(id = product.id)
#         price_data = models.ProductModelVariant.objects.filter(product=product).aggregate(
#             max_price=Max('price'),
#             min_price=Min('price')
#         )

#         max_price = price_data['max_price']
#         min_price = price_data['min_price']
#         serializer = ProductDetailSerializer(product).data
#         serializer.update({'max_price': max_price, 'min_price':min_price})
#         list_data.append(serializer)

#     pending_inquiry_count = models.ProductInquiry.objects.filter(status = "Pending").count()

#     res = {
#         'data': list_data ,
#         'total_records':total_records,
#         'current_page':page_number,
#         'total_pages': int(np.ceil(total_records/row_size)),
#         'total_pending_records': total_pending_records,
#         'pending_inquiry_count':pending_inquiry_count,
#         'total_bulk_records':total_bulk_records
#     }
#     json_data = JSONRenderer().render(res)
#     return HttpResponse(json_data, content_type= 'application/json', status=200)


@csrf_exempt
def all_product_list(request):
    python_data = JSONParser().parse(io.BytesIO(request.body))

    print("python_data--all_product_list--->", python_data)

    today = timezone.now()

    page_number = int(python_data.get('page_number', 1))
    row_size = int(python_data.get('row_data', 10))

    last_row = row_size * page_number
    first_row = last_row - row_size

    category_name = python_data.get('category_name', None)
    search_key = python_data.get('search_key', None)
    subcategory_name = python_data.get('subcategory_name', None)
    status = python_data.get('status', None)
    product_added_from = python_data.get('product_added_from', None)

    filter_condition = Q()

    # Category Filter
    if category_name not in [None, '', 'null']:
        filter_condition &= Q(category__category=category_name)

    # Subcategory Filter
    if subcategory_name not in [None, '', 'null']:
        filter_condition &= Q(subcategory__subcategory=subcategory_name)

    # Search Filter
    # if search_key not in [None, '', 'null']:
    #     filter_condition &= (
    #         Q(product_name__icontains=search_key) |
    #         Q(refpro__icontains=search_key) |
    #         Q(product_code__icontains=search_key) |
    #         Q(product_name_french__icontains=search_key)
    #     )
    
    # Search Filter
    if search_key not in [None, '', 'null']:

        search_words = search_key.strip().split()

        search_query = Q()

        for word in search_words:

            search_query &= (
                Q(product_name__unaccent__icontains=word) |
                Q(refpro__unaccent__icontains=word) |
                Q(product_code__unaccent__icontains=word) |
                Q(product_name_french__unaccent__icontains=word)
            )

        filter_condition &= search_query


    # Status Filter
    if status not in [None, '', 'null']:
        filter_condition &= Q(status=status)

    # Product Added From Filter
    if product_added_from not in [None, '', 'null']:
        filter_condition &= Q(product_added_from=product_added_from)

    # Counts
    total_bulk_records = models.ProductDetail.objects.filter(
        filter_condition,
        status='bulk'
    ).count()

    total_records = models.ProductDetail.objects.filter(
        filter_condition,
        product_verification='Approved'
    ).exclude(status='bulk').count()

    total_pending_records = models.ProductDetail.objects.filter(
        product_verification='Pending'
    ).count()

    pending_inquiry_count = models.ProductInquiry.objects.filter(
        status="Pending"
    ).count()

    # Product List
    all_product = models.ProductDetail.objects.filter(
        filter_condition,
        product_verification='Approved'
    ).exclude(
        status='bulk'
    ).order_by('-id')[first_row:last_row]

    list_data = []

    for product in all_product:

        # Aggregate Min/Max Price
        price_data = models.ProductModelVariant.objects.filter(
            product=product
        ).aggregate(
            max_price=Max('price'),
            min_price=Min('price')
        )

        serializer = ProductDetailSerializer(product).data

        serializer.update({
            'max_price': price_data['max_price'],
            'min_price': price_data['min_price']
        })

        list_data.append(serializer)

    # Response
    res = {
        'data': list_data,
        'total_records': total_records,
        'current_page': page_number,
        'total_pages': int(np.ceil(total_records / row_size)),
        'total_pending_records': total_pending_records,
        'pending_inquiry_count': pending_inquiry_count,
        'total_bulk_records': total_bulk_records
    }

    json_data = JSONRenderer().render(res)

    return HttpResponse(
        json_data,
        content_type='application/json',
        status=200
    )


# @csrf_exempt
# def chat_agent_product_list(request):
#     python_data = JSONParser().parse(io.BytesIO(request.body))
    
#     print("python_data--chat_agent_product_list--->", python_data)

#     today = timezone.now()

#     page_number = int(python_data.get('page_number', 1))
#     row_size = int(python_data.get('row_data', 10))
#     last_row = row_size * page_number
#     first_row = last_row - row_size

#     category_name = python_data.get('category_name',None)
#     search_key = python_data.get('search_key',None)
#     subcategory_name = python_data.get('subcategory_name',None)
#     status = python_data.get('status',None)

#     filter_condition = Q()

#     if category_name not in [None,'','null']:
#         filter_condition &= Q(category__category = category_name)
#     if subcategory_name not in [None,'','null']:
#         filter_condition &= Q(subcategory__subcategory = subcategory_name)
#     if search_key not in [None,'','null']:
#         filter_condition &= Q(product_name__icontains = search_key)|Q(refpro__icontains = search_key) | Q(product_code__icontains = search_key)
#     if status not in [None,'','null']:
#         filter_condition &= Q(status = status)

#     # total_bulk_records = models.ProductDetail.objects.filter(filter_condition, status= 'bulk').count()

    
#     total_records = models.ProductDetail.objects.filter(filter_condition, product_verification= 'Approved').exclude(status = 'bulk').count()
#     # all_product = models.ProductDetail.objects.filter(filter_condition).order_by('-id')[first_row:last_row]
#     # serializer = ProductDetailSerializer(all_product, many=True).data
#     total_pending_records = models.ProductDetail.objects.filter(product_verification= 'Pending').count()
    
#     list_data = []
#     all_product = models.ProductDetail.objects.filter(filter_condition, product_verification= 'Approved').exclude(status = 'bulk').order_by('-id')[first_row:last_row]
#     for product in all_product:
#         product = models.ProductDetail.objects.get(id = product.id)
#         price_data = models.ProductModelVariant.objects.filter(product=product).aggregate(
#             max_price=Max('price'),
#             min_price=Min('price')
#         )

#         max_price = price_data['max_price']
#         min_price = price_data['min_price']
#         serializer = ChatAgentProductDetailSerializer(product).data
#         serializer.update({'max_price': max_price, 'min_price':min_price})
#         list_data.append(serializer)

#     # pending_inquiry_count = models.ProductInquiry.objects.filter(status = "Pending").count()

#     res = {
#         'data': list_data ,
#         'total_records':total_records,
#         'current_page':page_number,
#         'total_pages': int(np.ceil(total_records/row_size)),
#     }
#     json_data = JSONRenderer().render(res)
#     return HttpResponse(json_data, content_type= 'application/json', status=200)



@csrf_exempt
def chat_agent_product_list(request):
    python_data = JSONParser().parse(io.BytesIO(request.body))
    
    print("python_data--chat_agent_product_list--->", python_data)

    today = timezone.now()

    page_number = int(python_data.get('page_number', 1))
    row_size = int(python_data.get('row_data', 10))
    last_row = row_size * page_number
    first_row = last_row - row_size

    


    category_name = python_data.get('category_name', None)
    search_key = python_data.get('search_key', None)
    subcategory_name = python_data.get('subcategory_name', None)
    status = python_data.get('status', None)

    filter_condition = Q()

    if search_key == '':
        res = {
            'data': []
        }
        json_data = JSONRenderer().render(res)
        return HttpResponse(json_data, content_type= 'application/json', status=200)
    else:

        if category_name not in [None, '', 'null']:

            filter_condition &= Q(
                category__category=category_name
            )

        if subcategory_name not in [None, '', 'null']:

            filter_condition &= Q(
                subcategory__subcategory=subcategory_name
            )

        if status not in [None, '', 'null']:

            filter_condition &= Q(
                status=status
            )

        products = models.ProductDetail.objects.annotate(

            clean_product_name=Lower(
                Replace(
                    'product_name',
                    Value(' '),
                    Value('')
                )
            ),

            clean_product_name_french=Lower(
                Replace(
                    'product_name_french',
                    Value(' '),
                    Value('')
                )
            ),

            clean_refpro=Lower(
                Replace(
                    'refpro',
                    Value(' '),
                    Value('')
                )
            ),

            clean_product_code=Lower(
                Replace(
                    'product_code',
                    Value(' '),
                    Value('')
                )
            ),
        )

        # -----------------------------------
        # SMART SEARCH
        # -----------------------------------
        search_clean = ""

        if search_key not in [None, '', 'null']:

            search_clean = search_key.strip().replace(" ", "").lower()

            products = products.annotate(

                similarity=Greatest(

                    TrigramSimilarity(
                        'clean_product_name',
                        search_clean
                    ),

                    TrigramSimilarity(
                        'clean_product_name_french',
                        search_clean
                    ),

                    TrigramSimilarity(
                        'clean_refpro',
                        search_clean
                    ),

                    TrigramSimilarity(
                        'clean_product_code',
                        search_clean
                    ),
                )

            ).filter(
                similarity__gt=0.1
            )

        # -----------------------------------
        # TOTAL RECORDS
        # -----------------------------------
        total_records = (
            products
            .filter(
                filter_condition,
                product_verification='Approved'
            )
            .exclude(status='bulk')
            .count()
        )

        # -----------------------------------
        # TOTAL PENDING
        # -----------------------------------
        total_pending_records = models.ProductDetail.objects.filter(
            product_verification='Pending'
        ).count()

        # -----------------------------------
        # FINAL PRODUCT QUERY
        # -----------------------------------
        all_product = (
            products
            .filter(
                filter_condition,
                product_verification='Approved'
            )
            .exclude(status='bulk')
            .distinct()
        )

        # -----------------------------------
        # ORDERING
        # -----------------------------------
        if search_clean:

            all_product = all_product.order_by(
                '-similarity',
                '-id'
            )

        else:

            all_product = all_product.order_by(
                '-id'
            )

        # -----------------------------------
        # PAGINATION
        # -----------------------------------
        all_product = all_product[first_row:last_row]

        # -----------------------------------
        # SERIALIZER DATA
        # -----------------------------------
        list_data = []

        for product in all_product:

            price_data = models.ProductModelVariant.objects.filter(
                product=product
            ).aggregate(
                max_price=Max('price'),
                min_price=Min('price')
            )

            serializer = ChatAgentProductDetailSerializer(
                product
            ).data

            serializer.update({
                'max_price': price_data['max_price'],
                'min_price': price_data['min_price']
            })

            list_data.append(serializer)
        print(filter_condition, 'filter_conditionfilter_condition')
        res = {
            'data': list_data ,
            'total_records':total_records,
            'current_page':page_number,
            'total_pages': int(np.ceil(total_records/row_size)),
        }
        json_data = JSONRenderer().render(res)
        return HttpResponse(json_data, content_type= 'application/json', status=200)








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
def product_request_create(request):
    python_data={}
    for i,j in request.FILES.items():
        python_data.update({i:j})
    
    for i,j in request.POST.items():
        python_data.update({i:j})

    vendor = python_data.get('vendor')
    product_name = python_data.get('product_name')
    category = python_data.get('category')
    subcategory = python_data.get('subcategory')
    category_description = python_data.get('category_description')
    description = python_data.get('description')
    product_image_1 = python_data.get('product_image_1')
    product_image_2 = python_data.get('product_image_2')
    
    product = models.ProductRequest.objects.create(
        vendor_id = vendor,
        product_name = product_name,
        category = category,
        subcategory = subcategory,
        category_description = category_description,
        description = description,
        product_image_1 = product_image_1,
        product_image_2 = product_image_2,
        status = 'pending'
    ).save()

    res = {
        'message':'Product Request Submite successfully.'        
    }
    json_data = JSONRenderer().render(res)
    return HttpResponse(json_data, content_type= 'application/json', status=200)

@csrf_exempt
def product_request_status_update(request):
    json_data = request.body
    stream = io.BytesIO(json_data)
    python_data = JSONParser().parse(stream)
    product = python_data.get('product')

    request_form = models.ProductRequest.objects.get(id = product)
    request_form.status = python_data.get('status', request_form.status)
    request_form.save()

    res = {
        'message':'Product Request status update successfully.'        
    }
    json_data = JSONRenderer().render(res)
    return HttpResponse(json_data, content_type= 'application/json', status=200)



@csrf_exempt
def vendor_product_request_list(request):
    json_data = request.body
    stream = io.BytesIO(json_data)
    python_data = JSONParser().parse(stream)
    vendor = python_data.get('vendor')

    product_list = models.ProductRequest.objects.filter(vendor =vendor)
    serializer = ProductRequestSerializer(product_list, many=True).data

    res = {
        'data': serializer 
    }
    json_data = JSONRenderer().render(res)
    return HttpResponse(json_data, content_type= 'application/json', status=200)

@csrf_exempt
def all_vendor_list(request):
    if request.method == 'POST':
        python_data = JSONParser().parse(io.BytesIO(request.body))
            
        # print("python_data--all_product_list--->", python_data)

        today = timezone.now()
        
        search_key = python_data.get('search_key',None)

        page_number = int(python_data.get('page_number', 1))
        row_size = int(python_data.get('row_data', 10))
        last_row = row_size * page_number
        first_row = last_row - row_size

        search_query = Q()
        if search_key:
            search_query = Q(company_name__icontains=search_key) | Q(vendor_name__icontains=search_key) | Q(phone_number__icontains=search_key) | Q(email__icontains=search_key)

        vendorData = models.VendorDetail.objects.filter(search_query).distinct('id')
        vendor_count = vendorData.count()
        vendor_list = vendorData.order_by('-id')[first_row:last_row]
        serializer = VendorDetailSerializer(vendor_list, many=True).data

        res = {
            'data': serializer, 
            'vendor_count': vendor_count 
        }
        json_data = JSONRenderer().render(res)
        return HttpResponse(json_data, content_type= 'application/json', status=200)


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



@csrf_exempt
def all_product_request_list(request):
    
    product_list = models.ProductRequest.objects.all()
    serializer = ProductRequestSerializer(product_list, many=True).data

    res = {
        'data': serializer 
    }
    json_data = JSONRenderer().render(res)
    return HttpResponse(json_data, content_type= 'application/json', status=200)



@csrf_exempt
def vendor_search_product(request):
    json_data = request.body
    stream = io.BytesIO(json_data)
    python_data = JSONParser().parse(stream)

    category = python_data.get('category')
    subcategory = python_data.get('subcategory')
    super_subcategory = python_data.get('super_subcategory')
    product_name = python_data.get('product_name')
    # print(python_data, 'python_data')
    filter_condition = {}
        
    
    if category and category != None and category != "null" and category != "":
        filter_condition['category'] = category

    if subcategory and subcategory != None and subcategory != "null" and subcategory != "":
        filter_condition['subcategory'] = subcategory

    if super_subcategory and super_subcategory != None and super_subcategory != "null" and super_subcategory != "":
        filter_condition['super_subcategory'] = super_subcategory     

    if product_name and product_name != None and product_name != "null" and product_name != "":
        filter_condition['product_name__icontains'] = product_name     

    # print(filter_condition, 'filter_condition')
    if filter_condition != {}:
        get_product_list = models.ProductDetail.objects.filter(**filter_condition).order_by('-id')
        serializer = ProductSearchSerializer(get_product_list, many=True).data
    else:
        serializer = []

    res = {
        'data': serializer 
    }
    json_data = JSONRenderer().render(res)
    return HttpResponse(json_data, content_type= 'application/json', status=200)

@csrf_exempt
def product_detail_admin(request):
    if request.method == 'POST':
        python_data = JSONParser().parse(io.BytesIO(request.body))
        id = python_data.get('id')
        
        product_check = models.ProductDetail.objects.filter(id = id).count()
        if product_check == 1:
            product = models.ProductDetail.objects.get(id = id)
            data = ProductDetailSerializer(product).data

            get_image = models.ProductImage.objects.filter(product = id)
            image_serializer = ProductImageSerializer(get_image, many=True).data

            get_other_specification = models.ProductOtherSpecification.objects.filter(product = id)
            other_serializer = ProductOtherSpecificationSerializer(get_other_specification, many=True).data

            list_model = []

            all_model = models.ProductModel.objects.filter(product = id).order_by('-id')
            for model in all_model:
                model = models.ProductModel.objects.get(id = model.id)
                model_serializer = ProductModelSerializer(model).data
                get_variants = models.ProductModelVariant.objects.filter(model = model.id).order_by('-id')
                list_variant = []
                for variant in get_variants:
                    variants_data = models.ProductModelVariant.objects.get(id = variant.id)
                    variant_serilizer = ProductModelVariantSerializerAdmin(variants_data).data

                    vendor_data = models.VendorProductPrice.objects.filter(variant= variant.id).order_by('-id')
                    price_serializer = VendorProductPriceSerializer(vendor_data, many=True).data
                    
                    variant_serilizer.update({'vendor_list':price_serializer})
                    list_variant.append(variant_serilizer)

                model_serializer.update({'variants':list_variant})    
                
                list_model.append(model_serializer)
            
            data.update({'image':image_serializer, 'other_data':other_serializer})

        res={
            'data':data,
            'models':list_model
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)



@csrf_exempt
def product_detail_vendor(request):
    if request.method == 'POST':
        python_data = JSONParser().parse(io.BytesIO(request.body))
        id = python_data.get('id')
        vendor = python_data.get('vendor')
        
        product_check = models.ProductDetail.objects.filter(id = id).count()
        if product_check == 1:
            product = models.ProductDetail.objects.get(id = id)
            data = ProductDetailSerializer(product).data

            get_image = models.ProductImage.objects.filter(product = id)
            image_serializer = ProductImageSerializer(get_image, many=True).data

            get_other_specification = models.ProductOtherSpecification.objects.filter(product = id)
            other_serializer = ProductOtherSpecificationSerializer(get_other_specification, many=True).data

            list_model = []

            all_model = models.ProductModel.objects.filter(product = id).order_by('-id')
            for model in all_model:
                model = models.ProductModel.objects.get(id = model.id)
                model_serializer = ProductModelSerializer(model).data
                get_variants = models.ProductModelVariant.objects.filter(model = model.id).order_by('-id')
                list_variant = []
                for variant in get_variants:
                    variants_data = models.ProductModelVariant.objects.get(id = variant.id)
                    variant_serilizer = ProductModelVariantSerializer(variants_data).data

                    # print(variant.id,'<-----variant.id, vendor---->', vendor)

                    vendor_data = models.VendorProductPrice.objects.get(variant= variant.id, vendor = vendor)
                    
                    variant_serilizer.update({'vendor_price':vendor_data.price})
                    list_variant.append(variant_serilizer)

                model_serializer.update({'variants':list_variant})    
                
                list_model.append(model_serializer)
            
            data.update({'image':image_serializer, 'other_data':other_serializer})

        res={
            'data':data,
            'models':list_model
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)



@csrf_exempt
def product_list_admin(request):
    product= models.ProductDetail.objects.all()
    serializer = ProductDetailSerializer(product, many=True).data
    
    res = {
        'data': serializer
    }
    json_data = JSONRenderer().render(res)
    return HttpResponse(json_data, content_type= 'application/json', status=200)


@csrf_exempt
def vendor_detail(request):
    json_data = request.body
    stream = io.BytesIO(json_data)
    python_data = JSONParser().parse(stream)
    vendor = python_data.get('vendor')
    check_vendor = models.VendorDetail.objects.filter(id = vendor).count()
    if check_vendor == 1:
        list_data = []
        vendor_data = models.VendorDetail.objects.get(id = vendor)
        vendor_seraliser = VendorDetailSerializer(vendor_data).data
        
        get_all_product = models.VendorProductPrice.objects.filter(vendor = vendor).values_list('product', flat=True)
        get_all_product = list(set(get_all_product))
        get_all_product = [item for item in get_all_product if item is not None]
        
        list_data = []
        for product in get_all_product:
            product = models.ProductDetail.objects.get(id = product)
            get_all_product_serializer = ProductDetailSerializer(product).data
            get_all_model = models.ProductModel.objects.filter(product = product)
            
            list_model = []
            for model in get_all_model:
                model = models.ProductModel.objects.get(id = model.id)
                model_serializer = ProductModelSerializer(model).data
                get_all_variant = models.ProductModelVariant.objects.filter(model = model)

                list_variant = []
                for variant in get_all_variant:
                    variant = models.ProductModelVariant.objects.get(id = variant.id)
                    variant_serialiser = AdminProductModelVariantSerializer(variant).data
                    
                    check_varint = models.VendorProductPrice.objects.filter(variant = variant.id, vendor = vendor).count()
                    if check_varint == 1:
                        # print(variant, 'avriant')
                        varint = models.VendorProductPrice.objects.get(variant = variant, vendor = vendor)
                        price_serialiser = VendorProductPriceSerializer(varint).data
                    
                        variant_serialiser.update({'vendor_data':price_serialiser})
                    
                        list_variant.append(variant_serialiser)

                model_serializer.update({'variant_data':list_variant})
            
                list_model.append(model_serializer)

            get_all_product_serializer.update({'model':list_model})
            list_data.append(get_all_product_serializer)

        res = {
            'data':vendor_seraliser,
            'product_data': list_data
        }
        json_data = JSONRenderer().render(res)
        return HttpResponse(json_data, content_type= 'application/json', status=200)

    res = {
        'meassage': "Something went wrong."
    }
    json_data = JSONRenderer().render(res)
    return HttpResponse(json_data, content_type= 'application/json', status=200)

@csrf_exempt
def vendor_product_search(request):
    json_data = request.body
    stream = io.BytesIO(json_data)
    python_data = JSONParser().parse(stream)
    product_name = python_data.get('product_name')

    seach_product = models.ProductDetail.objects.filter(product_name__icontains = product_name)
    serializer = ProductSearchSerializer(seach_product, many=True).data
    
    res = {
        'data': serializer
    }
    json_data = JSONRenderer().render(res)
    return HttpResponse(json_data, content_type= 'application/json', status=200)


# @csrf_exempt
# def product_detail_vendor(request):
#     json_data = request.body
#     stream = io.BytesIO(json_data)
#     python_data = JSONParser().parse(stream)
#     product = python_data.get('product')
#     vendor = python_data.get('vendor')
    
#     product_data = models.ProductDetail.objects.get(id = product)
#     serializer = ProductDetailSerializer(product_data).data

#     price_data = None
#     check_price = models.VendorProductPrice.objects.filter(vendor = vendor, product = product).count()
#     if check_price == 1:
#         price = models.VendorProductPrice.objects.get(vendor = vendor, product = product)
#         price_data = VendorProductPriceSerializer(price).data

#     res = {
#         'data': serializer, 
#         "price_data":price_data
#     }
#     json_data = JSONRenderer().render(res)
#     return HttpResponse(json_data, content_type= 'application/json', status=200)


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

    



@csrf_exempt
def product_model_variant_create(request):
    python_data={}
    for i,j in request.FILES.items():
        python_data.update({i:j})
    
    for i,j in request.POST.items():
        python_data.update({i:j})

    # print("python_data--=-=-model_name_french-=-=-=>",python_data)


    product_name = (python_data.get('product_name')).strip()
    product_name_french = (python_data.get('product_name_french')).strip()
    category = python_data.get('category')
    subcategory = python_data.get('subcategory')
    # super_subcategory = python_data.get('super_subcategory')
    description = python_data.get('description')
    description_french = python_data.get('description_french')
    unit_of_measure = python_data.get('unit_of_measure')
    material = python_data.get('material')
    length = python_data.get('length')
    height = python_data.get('height')
    width = python_data.get('width')
    weight = python_data.get('weight')
    color = python_data.get('color')
    min_order_quantity = python_data.get('min_order_quantity')
    max_order_quantity = python_data.get('max_order_quantity')
    quantity = python_data.get('quantity')
    product_image_1 = python_data.get('product_image_1')
    product_image_2 = python_data.get('product_image_2')
    product_image_3 = python_data.get('product_image_3')
    product_image_4 = python_data.get('product_image_4')
    product_image_5 = python_data.get('product_image_5')
    product_image_6 = python_data.get('product_image_6')
    product_image_7 = python_data.get('product_image_7')
    product_image_8 = python_data.get('product_image_8')
    
    delay_days_air = python_data.get('delay_days_air',None)
    delay_days_ship = python_data.get('delay_days_ship',None)
    delay_days_express = python_data.get('delay_days_express',None)
    product_type = python_data.get('product_type',None)
    product_packaging = python_data.get('product_packaging',None)
    product_packaging_value = python_data.get('product_packaging_value',None)

    if delay_days_air in [None,'','null']:
        delay_days_air = None

    if delay_days_ship in [None,'','null']:
        delay_days_ship = None

    if delay_days_express in [None,'','null']:
        delay_days_express = None
    
    
    if product_image_1 != None and product_image_1 != 'null' and product_image_1 != '':
        img = Image.open(product_image_1)
        if img.format == "AVIF":        
            if img.mode in ("RGBA", "LA"):
                img = img.convert("RGB")

            buffer = BytesIO()
            img.save(buffer, format="JPEG", quality=90)
            buffer.seek(0)
            base_name, ext = os.path.splitext(product_image_1.name)
            jpg_name = base_name + ".jpg"
            product_image_1 = ContentFile(buffer.read(), name=jpg_name)

    if product_image_2 != None and product_image_2 != 'null' and product_image_2 != '':
        img = Image.open(product_image_2)
        if img.format == "AVIF":        
            if img.mode in ("RGBA", "LA"):
                img = img.convert("RGB")
                
            buffer = BytesIO()
            img.save(buffer, format="JPEG", quality=90)
            buffer.seek(0)
            base_name, ext = os.path.splitext(product_image_2.name)
            jpg_name = base_name + ".jpg"
            product_image_2 = ContentFile(buffer.read(), name=jpg_name)

    if product_image_3 != None and product_image_3 != 'null' and product_image_3 != '':
        img = Image.open(product_image_3)
        if img.format == "AVIF":        
            if img.mode in ("RGBA", "LA"):
                img = img.convert("RGB")
                
            buffer = BytesIO()
            img.save(buffer, format="JPEG", quality=90)
            buffer.seek(0)
            base_name, ext = os.path.splitext(product_image_3.name)
            jpg_name = base_name + ".jpg"
            product_image_3 = ContentFile(buffer.read(), name=jpg_name)

    if product_image_4 != None and product_image_4 != 'null' and product_image_4 != '':
        img = Image.open(product_image_4)
        if img.format == "AVIF":        
            if img.mode in ("RGBA", "LA"):
                img = img.convert("RGB")
                
            buffer = BytesIO()
            img.save(buffer, format="JPEG", quality=90)
            buffer.seek(0)
            base_name, ext = os.path.splitext(product_image_4.name)
            jpg_name = base_name + ".jpg"
            product_image_4 = ContentFile(buffer.read(), name=jpg_name)

    if product_image_5 != None and product_image_5 != 'null' and product_image_5 != '':
        img = Image.open(product_image_5)
        if img.format == "AVIF":        
            if img.mode in ("RGBA", "LA"):
                img = img.convert("RGB")
                
            buffer = BytesIO()
            img.save(buffer, format="JPEG", quality=90)
            buffer.seek(0)
            base_name, ext = os.path.splitext(product_image_5.name)
            jpg_name = base_name + ".jpg"
            product_image_5 = ContentFile(buffer.read(), name=jpg_name)

    if product_image_6 != None and product_image_6 != 'null' and product_image_6 != '':
        img = Image.open(product_image_6)
        if img.format == "AVIF":        
            if img.mode in ("RGBA", "LA"):
                img = img.convert("RGB")
                
            buffer = BytesIO()
            img.save(buffer, format="JPEG", quality=90)
            buffer.seek(0)
            base_name, ext = os.path.splitext(product_image_6.name)
            jpg_name = base_name + ".jpg"
            product_image_6 = ContentFile(buffer.read(), name=jpg_name)

    if product_image_7 != None and product_image_7 != 'null' and product_image_7 != '':
        img = Image.open(product_image_7)
        if img.format == "AVIF":        
            if img.mode in ("RGBA", "LA"):
                img = img.convert("RGB")
                
            buffer = BytesIO()
            img.save(buffer, format="JPEG", quality=90)
            buffer.seek(0)
            base_name, ext = os.path.splitext(product_image_7.name)
            jpg_name = base_name + ".jpg"
            product_image_7 = ContentFile(buffer.read(), name=jpg_name)

    if product_image_8 != None and product_image_8 != 'null' and product_image_8 != '':
        img = Image.open(product_image_8)
        if img.format == "AVIF":        
            if img.mode in ("RGBA", "LA"):
                img = img.convert("RGB")
                
            buffer = BytesIO()
            img.save(buffer, format="JPEG", quality=90)
            buffer.seek(0)
            base_name, ext = os.path.splitext(product_image_8.name)
            jpg_name = base_name + ".jpg"
            product_image_8 = ContentFile(buffer.read(), name=jpg_name)


    price = python_data.get('price')
    discount = python_data.get('discount')
    final_price = python_data.get('final_price')
    vendor = python_data.get('vendor')
    product_verification = python_data.get('product_verification')
    # syncWithDimensions = python_data.get('syncWithDimensions')
    carton_length = python_data.get('carton_length')
    carton_width = python_data.get('carton_width')
    carton_height = python_data.get('carton_height')
    carton_weight = python_data.get('carton_weight')
    # syncWithModelOrVariant = python_data.get('syncWithModelOrVariant')
    available_quantity = python_data.get('available_quantity')
    quantity = python_data.get('quantity')
    refpro = python_data.get('refpro', None)
    reuser = python_data.get('reuser', None)
    shipping_via = python_data.get('shipping_via', None)
    country_of_origin = python_data.get('country_of_origin', None)
    product_video = python_data.get('product_video', None)
    available_country = python_data.get('available_country', None)
    tag = python_data.get('tag', None)
    
    

    other_specification = json.loads(python_data.get('other_specification'))
    
    
    login_flag = python_data.get('login_flag')
    if login_flag == 'Admin':
        status = "Approved"
        product_verification = 'Approved'
        
    else:
        status = "Pending"
        product_verification = 'Pending'

    digits = "123456789"
    random_number = ""
    for i in range(3) :
        random_number += digits[math.floor(random.random() * 9)]

    category_name = models.CategoryDetail.objects.filter(id = category).values_list('category', flat=True)[0][:3].upper()
    subcategory_name = models.SubCategoryDetail.objects.filter(id = subcategory).values_list('subcategory', flat=True)[0][:3].upper()
    product_name_data = (product_name)[:3].upper()
    product_code =  category_name+'_'+subcategory_name+ '_'+ product_name_data + '_' + random_number
    # print(product_code, 'product_codeproduct_code')
    
    if available_country not in [None,"","null"]:
        try:
            available_country = [int(x) for x in available_country.split(',')]
        except Exception as e:

            available_country = json.loads(available_country)

    if tag not in [None,"","null"]:
        try:
            tag = [int(x) for x in tag.split(',')]
        except Exception as e:

            tag = json.loads(tag)


    product = models.ProductDetail.objects.create(
        product_name = product_name,
        product_name_french = product_name_french,
        product_code = product_code,
        vendor_id = vendor,
        category_id = category,
        subcategory_id = subcategory,
        # super_subcategory_id = super_subcategory,
        description = description,
        description_french = description_french,
        unit_of_measure = unit_of_measure,
        material = material,
        length = length,
        height = height,
        width = width,
        weight = weight,
        country_of_origin_id = country_of_origin,
        carton_length = length,
        carton_width = width,
        carton_height = height,
        carton_weight = weight,
        # syncWithModelOrVariant = syncWithModelOrVariant,
        available_quantity = available_quantity,
        quantity = quantity,
        color = color,
        min_order_quantity = min_order_quantity,
        max_order_quantity = max_order_quantity,
        product_image_1 = product_image_1,
        product_image_2 = product_image_2,
        product_image_3 = product_image_3,
        product_image_4 = product_image_4,
        product_image_5 = product_image_5,
        product_image_6 = product_image_6,
        product_image_7 = product_image_7,
        product_image_8 = product_image_8,
        product_video = product_video,
        # price = price,
        discount = discount,
        final_price = final_price,
        status = 'Inactive',
        product_verification = product_verification,
        refpro = refpro,
        reuser = reuser,
        shipping_via = shipping_via,
        delay_days_air = delay_days_air,
        delay_days_ship = delay_days_ship,
        delay_days_express = delay_days_express,
        product_type_id = product_type,
        product_packaging_id = product_packaging,
        product_packaging_value = product_packaging_value,
        
    )
    product.save()
    try: 
        product.available_country.set(available_country)
    except:
        product.available_country.clear()

    try: 
        product.tag.set(tag)
    except:
        product.tag.clear()


    product_id = product.id 


    get_product_image_1 = product.product_image_1
    get_product_image_2 = product.product_image_2
    get_product_image_3 = product.product_image_3
    get_product_image_4 = product.product_image_4
    get_product_image_5 = product.product_image_5
    get_product_image_6 = product.product_image_6
    get_product_image_7 = product.product_image_7
    get_product_image_8 = product.product_image_8

    domain_path = ""


    if get_product_image_1 != None and get_product_image_1 != 'null' and get_product_image_1 != '':
        feat = extract_features_from_url(domain_path+get_product_image_1.url)
        try:
            if feat.size > 0:
                product.product_image_1_vector = feat.tolist()
                product.save()
        except:
            pass
    
    if get_product_image_2 != None and get_product_image_2 != 'null' and get_product_image_2 != '':
        feat = extract_features_from_url(domain_path+get_product_image_2.url)
        try:
            if feat.size > 0:
                product.product_image_2_vector = feat.tolist()
                product.save()
        except:
            pass

    if get_product_image_3 != None and get_product_image_3 != 'null' and get_product_image_3 != '':
        feat = extract_features_from_url(domain_path+get_product_image_3.url)
        try:
            if feat.size > 0:
                product.product_image_3_vector = feat.tolist()
                product.save()
        except:
            pass

    if get_product_image_4 != None and get_product_image_4 != 'null' and get_product_image_4 != '':
        feat = extract_features_from_url(domain_path+get_product_image_4.url)
        try:
            if feat.size > 0:
                product.product_image_4_vector = feat.tolist()
                product.save()
        
        except:
            pass


    if get_product_image_5 != None and get_product_image_5 != 'null' and get_product_image_5 != '':
        feat = extract_features_from_url(domain_path+get_product_image_5.url)
        try:
            if feat.size > 0:
                product.product_image_5_vector = feat.tolist()
                product.save()
        except:
            pass

    if get_product_image_6 != None and get_product_image_6 != 'null' and get_product_image_6 != '':
        feat = extract_features_from_url(domain_path+get_product_image_6.url)
        try:
            if feat.size > 0:
                product.product_image_6_vector = feat.tolist()
                product.save()
        except:
            pass

    if get_product_image_7 != None and get_product_image_7 != 'null' and get_product_image_7 != '':
        feat = extract_features_from_url(domain_path+get_product_image_7.url)
        try:
            if feat.size > 0:
                product.product_image_7_vector = feat.tolist()
                product.save()
        except:
            pass

    if get_product_image_8 != None and get_product_image_8 != 'null' and get_product_image_8 != '':
        feat = extract_features_from_url(domain_path+get_product_image_8.url)
        try:
            if feat.size > 0:
                product.product_image_8_vector = feat.tolist()
                product.save()
        except:
            pass


    for specification in other_specification:
        key = specification['key']
        key_french = specification['key_french']
        value = specification['value']
        value_french = specification['value_french']

        create_specification = models.ProductOtherSpecification.objects.create(
            product_id = product_id,
            key = key,
            key_french = key_french,
            value = value,
            value_french = value_french,
        ).save()


    for i in range(500):
        model_name = f'models[{i}][name]'
        model_name_french = f'models[{i}][model_name_french]'
        if python_data.get(model_name):
            model_name = (python_data.get(model_name)).strip()
            model_name_french = (python_data.get(model_name_french)).strip()
            model_image = python_data.get(f'models[{i}][image]')
            
            if model_image != None and model_image != 'null' and model_image != '':
                img = Image.open(model_image)
                if img.format == "AVIF":        
                    if img.mode in ("RGBA", "LA"):
                        img = img.convert("RGB")
                        
                    buffer = BytesIO()
                    img.save(buffer, format="JPEG", quality=90)
                    buffer.seek(0)
                    base_name, ext = os.path.splitext(model_image.name)
                    jpg_name = base_name + ".jpg"
                    model_image = ContentFile(buffer.read(), name=jpg_name)

            create_model = models.ProductModel.objects.create(
                product_id = product_id,
                model_name = model_name,
                model_name_french = model_name_french,
                model_image = model_image,
                status = 'Active'
            )
            create_model.save()
            list_price = []
            for j in range(500):
                variant_name = f'models[{i}][variants][{j}][name]'
                variant_name_french = f'models[{i}][variants][{j}][variant_name_french]'
                if python_data.get(variant_name):
                    variant_name = (python_data.get(variant_name)).strip()
                    variant_name_french = (python_data.get(variant_name_french)).strip()
                    variant_image = python_data.get(f'models[{i}][variants][{j}][image]')
                    variant_price = python_data.get(f'models[{i}][variants][{j}][price]')
                    list_price.append(variant_price)

                    if variant_image != None and model_image != 'null' and variant_image != '':
                        img = Image.open(variant_image)
                        if img.format == "AVIF":        
                            if img.mode in ("RGBA", "LA"):
                                img = img.convert("RGB")
                                
                            buffer = BytesIO()
                            img.save(buffer, format="JPEG", quality=90)
                            buffer.seek(0)
                            base_name, ext = os.path.splitext(variant_image.name)
                            jpg_name = base_name + ".jpg"
                            variant_image = ContentFile(buffer.read(), name=jpg_name)

                    create_variant = models.ProductModelVariant.objects.create(
                        product_id = product_id,
                        model_id = create_model.id,
                        name = variant_name,
                        name_french = variant_name_french,
                        image = variant_image,
                        price = variant_price,
                        variant_verification = 'Approved',
                        status = 'Active'

                    )
                    create_variant.save()
                    variant_id = create_variant.id

                    get_vendor_data = f'models[{i}][variants][{j}][vendor]'
                    get_vendor_price = f'models[{i}][variants][{j}][vendor_price]'
                    vendor = python_data.get(get_vendor_data)
                    vendor_price = python_data.get(get_vendor_price)
                   
                    price = models.VendorProductPrice.objects.create(
                        product_id = product_id,
                        model_id = create_model.id,
                        vendor_id = vendor,
                        variant_id = variant_id,
                        price = vendor_price,
                        # quantity = quantity,
                        status = 'Active'
                    ).save()


             
                else:
                    break
        else:
            break    


    smallest_price = min(list_price)
    product_update = models.ProductDetail.objects.get(id = product_id)
    product_update.price = smallest_price
    product_update.save()

    res = {
        'message':'Project create successfully.'        
    }
    json_data = JSONRenderer().render(res)
    return HttpResponse(json_data, content_type= 'application/json', status=200)

@csrf_exempt
def all_product_model_variant_list_admin(request):
    if request.method == "POST":
        product_model_variant_list = models.ProductDetail.objects.all().order_by('-id')
        product_model_variant_list_serializer = AdminProductDetailSerializer(product_model_variant_list, many=True).data

        res={
            'data':product_model_variant_list_serializer
        }
        return HttpResponse(JSONRenderer().render(res), content_type='application/json', status=200)


@csrf_exempt
def product_model_variant_update(request):
    if request.method == 'POST':
        python_data={}
        for i,j in request.FILES.items():
            python_data.update({i:j})
        
        for i,j in request.POST.items():
            python_data.update({i:j})

        id = python_data.get('id')
        product_name = (python_data.get('product_name')).strip()
        product_name_french = (python_data.get('product_name_french')).strip()
        description_french = python_data.get('description_french')
        product_code = python_data.get('product_code', None)
        category = python_data.get('category')
        subcategory = python_data.get('subcategory')
        # super_subcategory = python_data.get('super_subcategory')
        description = python_data.get('description')
        unit_of_measure = python_data.get('unit_of_measure')
        material = python_data.get('material')
        length = python_data.get('length')
        height = python_data.get('height')
        width = python_data.get('width')
        weight = python_data.get('weight')
        color = python_data.get('color')
        min_order_quantity = python_data.get('min_order_quantity')
        max_order_quantity = python_data.get('max_order_quantity')
        quantity = python_data.get('quantity')
        product_image_1 = python_data.get('product_image_1')
        product_image_2 = python_data.get('product_image_2')
        product_image_3 = python_data.get('product_image_3')
        product_image_4 = python_data.get('product_image_4')
        product_image_5 = python_data.get('product_image_5')
        product_image_6 = python_data.get('product_image_6')
        product_image_7 = python_data.get('product_image_7')
        product_image_8 = python_data.get('product_image_8')
        product_video = python_data.get('product_video')
        
        delay_days_air = python_data.get('delay_days_air')
        delay_days_ship = python_data.get('delay_days_ship')
        delay_days_express = python_data.get('delay_days_express')

        if delay_days_air in [None,'','null']:
            delay_days_air = None

        if delay_days_ship in [None,'','null']:
            delay_days_ship = None

        if delay_days_express in [None,'','null']:
            delay_days_express = None

        available_country = python_data.get('available_country')
        tag = python_data.get('tag')
        
        if available_country not in [None,"","null"]:
            try:
                available_country = [int(x) for x in available_country.split(',')]
            except Exception as e:

                available_country = json.loads(available_country)

        if tag not in [None,"","null"]:
            try:
                tag = [int(x) for x in tag.split(',')]
            except Exception as e:

                tag = json.loads(tag)

        if product_image_1 != None and product_image_1 != 'null' and product_image_1 != '':
            try:
                img = Image.open(product_image_1)
                if img.format == "AVIF":        
                    if img.mode in ("RGBA", "LA"):
                        img = img.convert("RGB")

                    buffer = BytesIO()
                    img.save(buffer, format="JPEG", quality=90)
                    buffer.seek(0)
                    base_name, ext = os.path.splitext(product_image_1.name)
                    jpg_name = base_name + ".jpg"
                    product_image_1 = ContentFile(buffer.read(), name=jpg_name)
            except:
                pass
            
        if product_image_2 != None and product_image_2 != 'null' and product_image_2 != '':
            try:
                img = Image.open(product_image_2)
                if img.format == "AVIF":        
                    if img.mode in ("RGBA", "LA"):
                        img = img.convert("RGB")
                        
                    buffer = BytesIO()
                    img.save(buffer, format="JPEG", quality=90)
                    buffer.seek(0)
                    base_name, ext = os.path.splitext(product_image_2.name)
                    jpg_name = base_name + ".jpg"
                    product_image_2 = ContentFile(buffer.read(), name=jpg_name)
            except:
                pass
            
        if product_image_3 != None and product_image_3 != 'null' and product_image_3 != '':
            try:
                img = Image.open(product_image_3)
                if img.format == "AVIF":        
                    if img.mode in ("RGBA", "LA"):
                        img = img.convert("RGB")
                        
                    buffer = BytesIO()
                    img.save(buffer, format="JPEG", quality=90)
                    buffer.seek(0)
                    base_name, ext = os.path.splitext(product_image_3.name)
                    jpg_name = base_name + ".jpg"
                    product_image_3 = ContentFile(buffer.read(), name=jpg_name)
            except:
                pass
            
        if product_image_4 != None and product_image_4 != 'null' and product_image_4 != '':
            try:
                img = Image.open(product_image_4)
                if img.format == "AVIF":        
                    if img.mode in ("RGBA", "LA"):
                        img = img.convert("RGB")
                        
                    buffer = BytesIO()
                    img.save(buffer, format="JPEG", quality=90)
                    buffer.seek(0)
                    base_name, ext = os.path.splitext(product_image_4.name)
                    jpg_name = base_name + ".jpg"
                    product_image_4 = ContentFile(buffer.read(), name=jpg_name)
            except:
                pass
            
        if product_image_5 != None and product_image_5 != 'null' and product_image_5 != '':
            try:
                img = Image.open(product_image_5)
                if img.format == "AVIF":        
                    if img.mode in ("RGBA", "LA"):
                        img = img.convert("RGB")
                        
                    buffer = BytesIO()
                    img.save(buffer, format="JPEG", quality=90)
                    buffer.seek(0)
                    base_name, ext = os.path.splitext(product_image_5.name)
                    jpg_name = base_name + ".jpg"
                    product_image_5 = ContentFile(buffer.read(), name=jpg_name)
            except:
                pass
            
        if product_image_6 != None and product_image_6 != 'null' and product_image_6 != '':
            try:
                img = Image.open(product_image_6)
                if img.format == "AVIF":        
                    if img.mode in ("RGBA", "LA"):
                        img = img.convert("RGB")
                        
                    buffer = BytesIO()
                    img.save(buffer, format="JPEG", quality=90)
                    buffer.seek(0)
                    base_name, ext = os.path.splitext(product_image_6.name)
                    jpg_name = base_name + ".jpg"
                    product_image_6 = ContentFile(buffer.read(), name=jpg_name)
            except:
                pass
            
        if product_image_7 != None and product_image_7 != 'null' and product_image_7 != '':
            try:
                img = Image.open(product_image_7)
                if img.format == "AVIF":        
                    if img.mode in ("RGBA", "LA"):
                        img = img.convert("RGB")
                        
                    buffer = BytesIO()
                    img.save(buffer, format="JPEG", quality=90)
                    buffer.seek(0)
                    base_name, ext = os.path.splitext(product_image_7.name)
                    jpg_name = base_name + ".jpg"
                    product_image_7 = ContentFile(buffer.read(), name=jpg_name)
            except:
                pass
            
        if product_image_8 != None and product_image_8 != 'null' and product_image_8 != '':
            try:
                img = Image.open(product_image_8)
                if img.format == "AVIF":        
                    if img.mode in ("RGBA", "LA"):
                        img = img.convert("RGB")
                        
                    buffer = BytesIO()
                    img.save(buffer, format="JPEG", quality=90)
                    buffer.seek(0)
                    base_name, ext = os.path.splitext(product_image_8.name)
                    jpg_name = base_name + ".jpg"
                    product_image_8 = ContentFile(buffer.read(), name=jpg_name)
            except:
                pass

 
        country_of_origin = python_data.get('country_of_origin')
        
        price = python_data.get('price')
        discount = python_data.get('discount')
        final_price = python_data.get('final_price')
        vendor = python_data.get('vendor')
        product_verification = python_data.get('product_verification')
        refpro = python_data.get('refpro')
        reuser = python_data.get('reuser')

        carton_length = python_data.get('carton_length')
        carton_width = python_data.get('carton_width')
        carton_height = python_data.get('carton_height')
        carton_weight = python_data.get('carton_weight')
        shipping_via = python_data.get('shipping_via')
        status = python_data.get('status')
        product_type = python_data.get('product_type')
        product_packaging = python_data.get('product_packaging')
        product_packaging_value = python_data.get('product_packaging_value')
        
        
        
        
        other_specification = json.loads(python_data.get('other_specification'))

        if vendor in [None,'','null']:
            vendor = None
        # if super_subcategory in [None,'','null']:
        #     super_subcategory = None

        if models.ProductDetail.objects.filter(id = id).exists():
            get_product = models.ProductDetail.objects.get(id = id)
            get_product.product_name = product_name
            get_product.product_name_french = product_name_french
            
            get_product.product_code = product_code
            # get_product.vendor_id = vendor
            get_product.category_id = category
            get_product.subcategory_id = subcategory
            # get_product.super_subcategory_id = super_subcategory
            get_product.description = description
            get_product.description_french = description_french
            get_product.unit_of_measure = unit_of_measure
            get_product.material = material
            get_product.length = length
            get_product.height = height
            get_product.width = width
            get_product.weight = weight
            get_product.color = color
            get_product.min_order_quantity = min_order_quantity
            get_product.max_order_quantity = max_order_quantity
            get_product.quantity = quantity
            get_product.refpro = refpro
            get_product.reuser = reuser
            get_product.country_of_origin_id = country_of_origin

            get_product.carton_length = length
            get_product.carton_width = width
            get_product.carton_height = height
            get_product.carton_weight = weight
            
            if not isinstance(product_image_1, str):
                get_product.product_image_1 = product_image_1
            if not isinstance(product_image_2, str):
                get_product.product_image_2 = product_image_2
            if not isinstance(product_image_3, str):
                get_product.product_image_3 = product_image_3
            if not isinstance(product_image_4, str):
                get_product.product_image_4 = product_image_4
            if not isinstance(product_image_5, str):
                get_product.product_image_5 = product_image_5
            if not isinstance(product_image_6, str):
                get_product.product_image_6 = product_image_6
            if not isinstance(product_image_7, str):
                get_product.product_image_7 = product_image_7
            if not isinstance(product_image_8, str):
                get_product.product_image_8 = product_image_8
            if not isinstance(product_video, str):
                get_product.product_video = product_video


            get_product.price = price
            get_product.discount = discount
            get_product.final_price = final_price
            get_product.product_verification = product_verification
            get_product.shipping_via = shipping_via

            get_product.delay_days_air = delay_days_air
            get_product.delay_days_ship = delay_days_ship
            get_product.delay_days_express = delay_days_express
            get_product.product_type_id = product_type
            get_product.product_packaging_id = product_packaging
            get_product.product_packaging_value = product_packaging_value
            get_product.status = python_data.get('status', get_product.status)


            

            get_product.save()
            try: 
                get_product.available_country.set(available_country)
            except:
                get_product.available_country.clear()
            
            try: 
                get_product.tag.set(tag)
            except:
                get_product.tag.clear()
            
            get_product_image_1 = get_product.product_image_1
            get_product_image_2 = get_product.product_image_2
            get_product_image_3 = get_product.product_image_3
            get_product_image_4 = get_product.product_image_4
            get_product_image_5 = get_product.product_image_5
            get_product_image_6 = get_product.product_image_6
            get_product_image_7 = get_product.product_image_7
            get_product_image_8 = get_product.product_image_8

            domain_path = ""


            if get_product_image_1 != None and get_product_image_1 != 'null' and get_product_image_1 != '':
                feat = extract_features_from_url(domain_path+get_product_image_1.url)
                try:
                    if feat.size > 0:
                        get_product.product_image_1_vector = feat.tolist()
                        get_product.save()
                except:
                    pass
            
            if get_product_image_2 != None and get_product_image_2 != 'null' and get_product_image_2 != '':
                feat = extract_features_from_url(domain_path+get_product_image_2.url)
                try:
                    if feat.size > 0:
                        get_product.product_image_2_vector = feat.tolist()
                        get_product.save()
                except:
                    pass

            if get_product_image_3 != None and get_product_image_3 != 'null' and get_product_image_3 != '':
                feat = extract_features_from_url(domain_path+get_product_image_3.url)
                try:
                    if feat.size > 0:
                        get_product.product_image_3_vector = feat.tolist()
                        get_product.save()
                except:
                    pass

            if get_product_image_4 != None and get_product_image_4 != 'null' and get_product_image_4 != '':
                feat = extract_features_from_url(domain_path+get_product_image_4.url)
                try:
                    if feat.size > 0:
                        get_product.product_image_4_vector = feat.tolist()
                        get_product.save()
                
                except:
                    pass


            if get_product_image_5 != None and get_product_image_5 != 'null' and get_product_image_5 != '':
                feat = extract_features_from_url(domain_path+get_product_image_5.url)
                try:
                    if feat.size > 0:
                        get_product.product_image_5_vector = feat.tolist()
                        get_product.save()
                except:
                    pass

            if get_product_image_6 != None and get_product_image_6 != 'null' and get_product_image_6 != '':
                feat = extract_features_from_url(domain_path+get_product_image_6.url)
                try:
                    if feat.size > 0:
                        get_product.product_image_6_vector = feat.tolist()
                        get_product.save()
                except:
                    pass

            if get_product_image_7 != None and get_product_image_7 != 'null' and get_product_image_7 != '':
                feat = extract_features_from_url(domain_path+get_product_image_7.url)
                try:
                    if feat.size > 0:
                        get_product.product_image_7_vector = feat.tolist()
                        get_product.save()
                except:
                    pass

            if get_product_image_8 != None and get_product_image_8 != 'null' and get_product_image_8 != '':
                feat = extract_features_from_url(domain_path+get_product_image_8.url)
                try:
                    if feat.size > 0:
                        get_product.product_image_8_vector = feat.tolist()
                        get_product.save()
                except:
                    pass


            get_ids = []
            for specification in other_specification:
                key = specification['key']
                key_french = specification['key_french']
                value = specification['value']
                value_french = specification['value_french']
                if specification.get('id'):
                    id = specification['id']
                
                    if models.ProductOtherSpecification.objects.filter(id = id).exists() and id not in [None,'','null']:
                        update_data = models.ProductOtherSpecification.objects.get(id = id)
                        update_data.key = key
                        update_data.key_french = key_french
                        update_data.value = value
                        update_data.value_french = value_french
                        update_data.save()
                        get_ids.append(update_data.id)
                    else:
                        pass
                else:
                    create_specification = models.ProductOtherSpecification.objects.create(
                        product_id = get_product.id,
                        key = key,
                        value = value,
                    )
                    create_specification.save()
                    get_ids.append(create_specification.id)
                                
            delete_specification = models.ProductOtherSpecification.objects.filter(product = get_product.id).exclude(id__in = get_ids)
            delete_specification.delete()

            not_deleted_models_id = []
            for i in range(500):
                model_name = f'models[{i}][name]'
                model_name_french = f'models[{i}][model_name_french]'


                if python_data.get(model_name):
                    model_name = (python_data.get(model_name)).strip()
                    model_name_french = (python_data.get(model_name_french)).strip()
                    model_image = python_data.get(f'models[{i}][image]')
                    model_id = python_data.get(f'models[{i}][id]',None)


                    if models.ProductModel.objects.filter(id = model_id).exists() and model_id not in [None,'','null']:
                        update_model = models.ProductModel.objects.get(id = model_id)
                        update_model.model_name = model_name
                        update_model.model_name_french = model_name_french
                        if not isinstance(model_image, str):
                            # print("MODEL IS HERE")
                            update_model.model_image = model_image

                        update_model.save()
                        not_deleted_models_id.append(update_model.id)

                    else:
                        if model_image != None and model_image != 'null' and model_image != '':
                            img = Image.open(model_image)
                            if img.format == "AVIF":        
                                if img.mode in ("RGBA", "LA"):
                                    img = img.convert("RGB")
                                    
                                buffer = BytesIO()
                                img.save(buffer, format="JPEG", quality=90)
                                buffer.seek(0)
                                base_name, ext = os.path.splitext(model_image.name)
                                jpg_name = base_name + ".jpg"
                                model_image = ContentFile(buffer.read(), name=jpg_name)
                        create_model = models.ProductModel.objects.create(
                            product_id = get_product.id,
                            model_name = model_name,
                            model_name_french = model_name_french,
                            model_image = model_image,
                            status = 'Active'       
                        )
                        create_model.save()
                        model_id = create_model.id
                        not_deleted_models_id.append(model_id)

                    not_deleted_variant_id = []
                    list_price = []
                    # print(True)
                    for j in range(500):
                        variant_name = f'models[{i}][variants][{j}][name]'
                        variant_name_french = f'models[{i}][variants][{j}][variant_name_french]'


                        if python_data.get(variant_name):
                            variant_name = (python_data.get(variant_name)).strip()
                            variant_name_french = (python_data.get(variant_name_french)).strip()
                            variant_image = python_data.get(f'models[{i}][variants][{j}][image]')
                            variant_price = python_data.get(f'models[{i}][variants][{j}][price]')
                            variant_id = python_data.get(f'models[{i}][variants][{j}][id]',None)
                            list_price.append(variant_price)

                            

                            if variant_id not in [None,'','null'] and models.ProductModelVariant.objects.filter(id = variant_id).exists():
                                update_variant = models.ProductModelVariant.objects.get(id = variant_id)
                                update_variant.name = variant_name
                                update_variant.name_french = variant_name_french
                                
                                update_variant.price = variant_price

                                if not isinstance(variant_image, str):
                                    # print("VARIANT IS HERE")
                                    update_variant.image = variant_image
                                
                                update_variant.save()
                                not_deleted_variant_id.append(update_variant.id)

                            else:
                                if variant_image != None and variant_image != 'null' and variant_image != '':
                                    img = Image.open(variant_image)
                                    if img.format == "AVIF":        
                                        if img.mode in ("RGBA", "LA"):
                                            img = img.convert("RGB")
                                            
                                        buffer = BytesIO()
                                        img.save(buffer, format="JPEG", quality=90)
                                        buffer.seek(0)
                                        base_name, ext = os.path.splitext(variant_image.name)
                                        jpg_name = base_name + ".jpg"
                                        variant_image = ContentFile(buffer.read(), name=jpg_name)


                                create_variant = models.ProductModelVariant.objects.create(
                                    product_id = get_product.id,
                                    model_id = model_id,
                                    name = variant_name,
                                    name_french = variant_name_french,
                                    
                                    image = variant_image,
                                    price = variant_price,
                                    variant_verification = 'Approved'

                                )
                                create_variant.save()
                                
                                not_deleted_variant_id.append(create_variant.id)
                        
                        else:
                            break
                    
                    delete_variant = models.ProductModelVariant.objects.filter(model = model_id).exclude(id__in = not_deleted_variant_id)
                    delete_variant.delete()

                else:
                    break
            
            delete_model = models.ProductModel.objects.filter(product_id = get_product.id).exclude(id__in = not_deleted_models_id)
            delete_model.delete()

            # print(list_price)
            smallest_price = min(list_price)
            # print(smallest_price, 'smallest_pricesmallest_pricesmallest_price')
            get_product = models.ProductDetail.objects.get(id = id)
            get_product.price = smallest_price
            get_product.save()

            res={
                'message':'Product Updated Successfully'
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)


@csrf_exempt
def product_delete(request):
    if request.method == "POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))

        id = python_data.get('id')

        get_product = models.ProductDetail.objects.get(id=id)
        get_product.delete()

        res={
            'message':'Product Deleted Successfully'
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)


            
@csrf_exempt
def vendor_approve_reject(request):
    if request.method == "POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))

        id = python_data.get('id')
        is_verify = python_data.get('is_verify')

        check_vendor = models.VendorDetail.objects.filter(id = id).count()
        if check_vendor == 1:
            vendor = models.VendorDetail.objects.get(id = id)
            vendor.is_verify = python_data.get('is_verify', vendor.is_verify)
            if is_verify == "rejected":
                vendor.reject_reason = python_data.get('reject_reason', vendor.reject_reason)
            vendor.save()        
            res={
                'message':'Vendor Status Update Successfully'
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)
        else:
            res = {
                'message':'Enter Valid id.'        
                }
            json_data = JSONRenderer().render(res)
            return HttpResponse(json_data, content_type= 'application/json', status=406)

          
@csrf_exempt
def vendor_list_category_subcategory(request):
    if request.method == "POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))

        # print(python_data, 'python_data')
        category = int(python_data.get('category'))
        subcategory = int(python_data.get('subcategory'))

        
        vendor_list = models.VendorDetail.objects.filter(category=category, subcategory = subcategory)
        serializer = VendorDataSerializer(vendor_list, many=True).data
        res={
            'data':serializer
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)
    
@csrf_exempt
def vendor_name_list(request):
    if request.method == "POST":    
        vendor_list = models.VendorDetail.objects.all()
        serializer = VendorDataSerializer(vendor_list, many=True).data
        res={
            'data':serializer
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)


@csrf_exempt
def model_update(request):
    if request.method == "POST":
        python_data={}
        for i,j in request.FILES.items():
            python_data.update({i:j})
        
        for i,j in request.POST.items():
            python_data.update({i:j})

        id = python_data.get('id')
        model_name = python_data.get('model_name')
        model_name_french = python_data.get('model_name_french')
        model_image = python_data.get('model_image',None)

        if models.ProductModel.objects.filter(id = id):
            get_model = models.ProductModel.objects.get(id = id)
            get_model.model_name = model_name
            get_model.model_name_french = model_name_french
            
            if not isinstance(model_image, str) and model_image not in [None,'','null']:
                get_model.model_image = model_image

            get_model.save()
            res = {
                'message':'Model Updated Successfully'        
            }
            return HttpResponse(JSONRenderer().render(res), content_type= 'application/json', status=200)

        else:
            res = {
                'message':'Enter Valid id.'        
            }
            return HttpResponse(JSONRenderer().render(res), content_type= 'application/json', status=406)


@csrf_exempt
def variant_update(request):
    if request.method == "POST":
        python_data={}
        for i,j in request.FILES.items():
            python_data.update({i:j})
        
        for i,j in request.POST.items():
            python_data.update({i:j})

        id = python_data.get('id')
        name = python_data.get('name')
        name_french = python_data.get('variant_name_french')
        image = python_data.get('image')
        price = python_data.get('price')

        if models.ProductModelVariant.objects.filter(id = id):
            get_variant = models.ProductModelVariant.objects.get(id = id)
            get_variant.name = name
            get_variant.name_french = name_french
            get_variant.price = price
            if not isinstance(image, str) and image not in [None,'','null']:
                get_variant.image = image

            get_variant.save()
            print(get_variant.product)
            try:
                list_price = list(models.ProductModelVariant.objects.filter(product = get_variant.product.id).values_list('price', flat = True))
                smallest_price = min(list_price)
                # print(smallest_price, 'smallest_pricesmallest_pricesmallest_price')
                get_product = models.ProductDetail.objects.get(id = get_variant.product.id)
                get_product.price = smallest_price
                get_product.save()
            except:
                pass

            res = {
                'message':'Variant Updated Successfully'        
            }
            return HttpResponse(JSONRenderer().render(res), content_type= 'application/json', status=200)

        else:
            res = {
                'message':'Enter Valid id.'        
            }
            return HttpResponse(JSONRenderer().render(res), content_type= 'application/json', status=406)


@csrf_exempt
def vendor_variant_update(request):
    if request.method == "POST":
        python_data={}
        for i,j in request.FILES.items():
            python_data.update({i:j})
        
        for i,j in request.POST.items():
            python_data.update({i:j})

        id = python_data.get('id')
        price = python_data.get('price')
        

        if models.VendorProductPrice.objects.filter(id = id):
            get_vendor_variant = models.VendorProductPrice.objects.get(id = id)
            get_vendor_variant.price = price

            get_vendor_variant.save()
            res = {
                'message':'Variant Price Updated Successfully'        
            }
            return HttpResponse(JSONRenderer().render(res), content_type= 'application/json', status=200)

        else:
            res = {
                'message':'Enter Valid id.'        
            }
            return HttpResponse(JSONRenderer().render(res), content_type= 'application/json', status=406)






    

@csrf_exempt
def customer_register(request):
    if request.method == 'POST':
        python_data = JSONParser().parse(io.BytesIO(request.body))
        mobileNumber = python_data.get('mobileNumber')
        countryCode = python_data.get('countryCode')
        
        name = python_data.get('name')
        FCMToken = python_data.get('FCMToken')
        deviceId = python_data.get('deviceId')
        deviceType = python_data.get('deviceType')

        ip_address = python_data.get('ip_address')
        country = python_data.get('country',None)

        if countryCode not in [None,'','null']:
            if models.CountryWithCurrency.objects.filter(country_calling_code = countryCode).exists():
                country = models.CountryWithCurrency.objects.get(country_calling_code = countryCode).country_name
            else:
                try:
                    response = requests.get(f'https://ipapi.co/{ip_address}/json/')
                    response = response.json()
                    country = response.get("country_name",None)
                    # print("response====>",response)
                except Exception as e:
                    print("Errroooorrr----->",e)
                    # country = "Egypt"
        
        now = datetime.now()
        date_time = now.strftime('%Y-%m-%d, %H:%M:%S')
        
        digits = '123456789' 
        OTP = ""
        for i in range(4):
            OTP += digits[math.floor(random.random() * 9)]
        
        check_email = models.CustomerDetail.objects.filter(countryCode = countryCode, mobileNumber = mobileNumber).count()
        print(check_email, 'check_email')
        if check_email == 0:
            create_customer = models.CustomerDetail.objects.create(
                mobileNumber = mobileNumber,
                countryCode = countryCode,
                OTP = OTP,
                FCMToken = FCMToken,
                deviceId = deviceId,
                deviceType = deviceType,
                country = country,
                name = name,
                created_at = date_time
            )
            create_customer.save()

            # try:
            #     content = f'Your Diaba verification code is {OTP}. It will expire in 5 minutes. Do not share this code with anyone.'
            #     result = send_sms(LOGIN, API_KEY, TOKEN, SUBJECT, SIGNATURE, recipient, content)
            # except:
            #     pass

            
            recipient = f'{countryCode}'+ create_customer.mobileNumber
            
            url = "https://api.verifyway.com/api/v1/"
            headers = {
                "Authorization": "Bearer 1515$iwLeuAjYrEcHnD8Rs2GymuXAefPF8M5fx7wV",
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
            payload = {
                "recipient": recipient,
                "type": "otp",
                "channel": "whatsapp",
                "fallback": "no",
                "code": OTP,
                "lang": "en",
            }
            response = requests.post(url, json=payload, headers=headers)
            # print(response, 'responseresponse')



            res={
                'message':"You're successfully registerd.",
                'OTP':OTP
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)
        else:
            res = {
                'message':"This mobile number is already linked to an existing account. Please use another one."        
                }
            json_data = JSONRenderer().render(res)
            return HttpResponse(json_data, content_type= 'application/json', status=406)



@csrf_exempt
def customer_login(request):
    if request.method == 'POST':
        python_data = JSONParser().parse(io.BytesIO(request.body))
        mobileNumber = python_data.get('mobileNumber')
        countryCode = python_data.get('countryCode')
        FCMToken = python_data.get('FCMToken')
        ip_address = python_data.get('ip_address')
        country = python_data.get('country')

        # print("0-=-=----->",python_data)
        
                
        digits = '123456789' 
        OTP = ""
        for i in range(4):
            OTP += digits[math.floor(random.random() * 9)]

        now = datetime.now()
        date_time = now.strftime('%Y-%m-%d, %H:%M:%S')
        
        


        check_email = models.CustomerDetail.objects.filter(countryCode= countryCode, mobileNumber = mobileNumber).count()
        # print(check_email, 'check_email')
        if check_email == 1:
            if mobileNumber == '777888999':
                # print('Client')
                customer = models.CustomerDetail.objects.get(countryCode=countryCode, mobileNumber = mobileNumber)
                customer.OTP = '1234'
                customer.lastLoginDate = date_time
                customer.FCMToken = FCMToken
                # customer.countryCode = countryCode
                customer.save()
                
                res={
                    'message':"OTP Send Successfully.", 
                    'OTP':OTP
                }
                return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)

            else:
                # print('else Client')

                customer = models.CustomerDetail.objects.get(mobileNumber = mobileNumber, countryCode= countryCode)
                
                if countryCode not in [None,'','null']:
                    if models.CountryWithCurrency.objects.filter(country_calling_code = countryCode).exists():
                        country = models.CountryWithCurrency.objects.get(country_calling_code = countryCode).country_name
                    else:
                        try:
                            if country in [None,'','null']:
                                response = requests.get(f'https://ipapi.co/{ip_address}/json/')
                                response = response.json()

                                if not response.get('error'):
                                    country = response.get("country_name")
                                # print("response====>",response)

                        except Exception as e:
                            print("Errroooorrr----->",e)
                            # country = "Egypt"

                if customer.country != country and country not in [None,'','null']:
                    customer.country = country

                customer.OTP = OTP
                customer.lastLoginDate = date_time
                customer.FCMToken = FCMToken
                customer.countryCode = countryCode
                customer.save()
                
                recipient = str(countryCode) + str(customer.mobileNumber)
                # content = f'Your Diaba verification code is {OTP}. It will expire in 5 minutes. Do not share this code with anyone.'
                # result = send_sms(LOGIN, API_KEY, TOKEN, SUBJECT, SIGNATURE, recipient, content)
                
                url = "https://api.verifyway.com/api/v1/"
                headers = {
                    "Authorization": "Bearer 1515$iwLeuAjYrEcHnD8Rs2GymuXAefPF8M5fx7wV",
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                }
                payload = {
                    "recipient": recipient,
                    "type": "otp",
                    "channel": "whatsapp",
                    "fallback": "no",
                    "code": OTP,
                    "lang": "en",
                }
                response = requests.post(url, json=payload, headers=headers)
                print(response, 'responseresponse')


                res={
                    'message':"Verification code sent successfully.", 
                    'OTP':OTP
                }
                return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)

        else:
            res = {
                'message':"This mobile number is not registered with us."        
                }
            json_data = JSONRenderer().render(res)
            return HttpResponse(json_data, content_type= 'application/json', status=406)

@csrf_exempt
def customer_logout(request):
    if request.method == 'POST':
        python_data = JSONParser().parse(io.BytesIO(request.body))
 
        # print("python_data----=-=->",python_data)
        customer = python_data.get('customer')
   
        
        get_login_id = models.CustomerLogin.objects.filter(customer = customer)
        get_login_id.delete()
        res={
            'message':"Logged out successfully.",
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)

@csrf_exempt
def customer_verify(request):
    if request.method == 'POST':
        python_data = JSONParser().parse(io.BytesIO(request.body))
        mobileNumber = python_data.get('mobileNumber')
        countryCode = python_data.get('countryCode')
        otp = python_data.get('otp')
        
        now = datetime.now()
        date_time = now.strftime('%Y-%m-%d, %H:%M:%S')
        
        print(python_data, 'python_data')

        check_email = models.CustomerDetail.objects.filter(countryCode = countryCode, mobileNumber = mobileNumber).count()
        print(check_email, 'check_email')
        if check_email == 1:

            check_password = models.CustomerDetail.objects.filter(countryCode= countryCode, mobileNumber = mobileNumber, OTP=otp).count()
            # print(check_password, 'check_password')
            
            if check_password == 1:
                customer = models.CustomerDetail.objects.get(countryCode= countryCode, mobileNumber = mobileNumber)
                customer.lastLoginDate = date_time
                customer.save()

                serializer = CustomerDetailSerializer(customer).data
                
                check_login = models.CustomerLogin.objects.filter(customer_id = customer.id).count()
                if check_login == 0:
                    login = models.CustomerLogin.objects.create(
                        customer_id = customer.id,
                        login_time = date_time,
                    ).save()
                
                if check_login == 1:
                    login_update = models.CustomerLogin.objects.get(customer_id = customer.id)
                    login_update.login_time = date_time
                    login_update.save()
                    

                login_history = models.CustomerLoginHistory.objects.create(
                    email = mobileNumber,
                    login_time = date_time,
                ).save()
                 
                res={
                    'message':"Verification completed successfully.", 
                    'data':serializer
                }
                return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)
            else:
                res = {
                    'message':"Invalid password. Please try again."        
                    }
                json_data = JSONRenderer().render(res)
                return HttpResponse(json_data, content_type= 'application/json', status=406)

        else:
            res = {
                'message':"Invalid email. Please try again."        
                }
            json_data = JSONRenderer().render(res)
            return HttpResponse(json_data, content_type= 'application/json', status=406)



@csrf_exempt
def customer_update_password(request):
    if request.method == 'POST':
        python_data = JSONParser().parse(io.BytesIO(request.body))
        email = python_data.get('email')
        old_password = python_data.get('old_password')
        new_password = python_data.get('new_password')
        
        now = datetime.now()
        date_time = now.strftime('%Y-%m-%d, %H:%M:%S')
        
        check_email = models.CustomerDetail.objects.filter(email = email).count()
        if check_email == 1:
            check_password = models.CustomerDetail.objects.filter(email = email, password=old_password).count()
            if check_password == 1:
                customer = models.CustomerDetail.objects.get(email = email)
                customer.password = new_password
                customer.save()
                res={
                    'message':"Your password has been updated successfully."
                }
                return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)
            else:
                res = {
                    'message':"Invalid password. Please try again."        
                    }
                json_data = JSONRenderer().render(res)
                return HttpResponse(json_data, content_type= 'application/json', status=406)

        else:
            res = {
                'message':"Invalid email. Please try again."        
                }
            json_data = JSONRenderer().render(res)
            return HttpResponse(json_data, content_type= 'application/json', status=406)



@csrf_exempt
def customer_address_create(request):
    if request.method == 'POST':
        python_data = JSONParser().parse(io.BytesIO(request.body))
        customer = python_data.get('customer')
        recipient_name = python_data.get('recipient_name')
        street_address = python_data.get('street_address')
        city = python_data.get('city')
        region = python_data.get('region')
        postal_code = python_data.get('postal_code')
        country = python_data.get('country')
        address_type = python_data.get('address_type')
        mobile_number = python_data.get('mobile_number')
        
        # print(python_data, 'python_data')
        now = datetime.now()
        date_time = now.strftime('%Y-%m-%d, %H:%M:%S')
        check_customer = models.CustomerDetail.objects.filter(id = customer).count()
        
        if check_customer == 1:
            check_total_address = models.CustomerAddressDetail.objects.filter(customer_id = customer).count()
            if check_total_address == 0:
                is_default = 'True'
            else:
                is_default = python_data.get('is_default', 'False')

            address = models.CustomerAddressDetail.objects.create(
                customer_id = customer,
                recipient_name = recipient_name,
                street_address = street_address,
                city = city,
                region = region,
                postal_code = postal_code,
                country = country,
                address_type = address_type,
                mobile_number = mobile_number,
                is_default = is_default, 
                created_at = date_time
            ).save()

            
            customer_number = models.CustomerDetail.objects.get(id = customer)
            if customer_number.mobileNumber == None:
                # print('True Data', mobile_number)
                number_update = models.CustomerDetail.objects.get(id = customer)
                number_update.mobileNumber = mobile_number
                number_update.save()

            res={
                'message':"You have successfully added a new address."
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)
        
        else:
            res = {
                'message':"Customer id not found."        
                }
            json_data = JSONRenderer().render(res)
            return HttpResponse(json_data, content_type= 'application/json', status=406)



@csrf_exempt
def customer_address_update(request):
    if request.method == 'POST':
        python_data = JSONParser().parse(io.BytesIO(request.body))
        id = python_data.get('id')
        customer = python_data.get('customer')
        recipient_name = python_data.get('recipient_name')
        street_address = python_data.get('street_address')
        city = python_data.get('city')
        region = python_data.get('region')
        postal_code = python_data.get('postal_code')
        country = python_data.get('country')
        address_type = python_data.get('address_type')
        mobile_number = python_data.get('mobile_number')
        is_default = str(python_data.get('is_default'))
        # print(python_data, 'python_data')
        now = datetime.now()
        date_time = now.strftime('%Y-%m-%d, %H:%M:%S')
        check_customer = models.CustomerAddressDetail.objects.filter(id = id).count()
        if check_customer == 1:
            if is_default == 'True':
                get_all_address = models.CustomerAddressDetail.objects.filter(customer = customer)
                for address in get_all_address:
                    update_default = models.CustomerAddressDetail.objects.get(id = address.id)
                    update_default.is_default = 'False'
                    update_default.save()
            

            address = models.CustomerAddressDetail.objects.get(id = id)
            address.recipient_name = python_data.get('recipient_name', address.recipient_name)
            address.street_address = python_data.get('street_address', address.street_address)
            address.city = python_data.get('city', address.city)
            address.region = python_data.get('region', address.region)
            address.postal_code = python_data.get('postal_code', address.postal_code)
            address.country = python_data.get('country', address.country)
            address.address_type = python_data.get('address_type', address.address_type)
            address.mobile_number = python_data.get('mobile_number', address.mobile_number)
            address.is_default = python_data.get('is_default', address.is_default)
            address.save()

            res={
                'message':"You have successfully update a address."
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)
        
        else:
            res = {
                'message':"Customer id not found."        
                }
            json_data = JSONRenderer().render(res)
            return HttpResponse(json_data, content_type= 'application/json', status=406)



@csrf_exempt
def customer_detail(request):
    if request.method == 'POST':
        python_data = JSONParser().parse(io.BytesIO(request.body))
        customer = python_data.get('customer')
        
        check_customer = models.CustomerDetail.objects.filter(id = customer).count()
        if check_customer == 1:

            customer = models.CustomerDetail.objects.get(id = customer)
            serializer = CustomerDetailSerializer(customer).data
            
            all_address = models.CustomerAddressDetail.objects.filter(customer = customer)
            address_serializer = CustomerAddressDetailSerializer(all_address, many=True).data

            res = {
                'data':serializer,
                'address': address_serializer    
            }
            json_data = JSONRenderer().render(res)
            return HttpResponse(json_data, content_type= 'application/json', status=200)
        else:
            res = {
                'message':"Customer id not found."        
                }
            json_data = JSONRenderer().render(res)
            return HttpResponse(json_data, content_type= 'application/json', status=406)


@csrf_exempt
def customer_profile_update(request):
    if request.method == 'POST':
        python_data = JSONParser().parse(io.BytesIO(request.body))
        customer = python_data.get('customer')
        
        check_customer = models.CustomerDetail.objects.filter(id = customer).count()
        if check_customer == 1:
            customer_detail = models.CustomerDetail.objects.get(id = customer)
            customer_detail.email = python_data.get('email', customer_detail.email)
            customer_detail.mobileNumber = python_data.get('mobileNumber', customer_detail.mobileNumber)
            customer_detail.name = python_data.get('name', customer_detail.name)
            customer_detail.gender = python_data.get('gender', customer_detail.gender)
            customer_detail.save()

            serializer = CustomerDetailSerializer(customer_detail).data

            res = {
                'message':" Details update successfully.",
                'data':serializer
            }
            json_data = JSONRenderer().render(res)
            return HttpResponse(json_data, content_type= 'application/json', status=200)
        else:
            res = {
                'message':"Customer id not found."        
                }
            json_data = JSONRenderer().render(res)
            return HttpResponse(json_data, content_type= 'application/json', status=406)


@csrf_exempt
def vendor_product_price_create(request):
    python_data={}
    for i,j in request.FILES.items():
        python_data.update({i:j})
    
    for i,j in request.POST.items():
        python_data.update({i:j})
        
    # print(python_data, 'python_data')

    if python_data.get('variant_id'):
        variant_id = python_data.get('variant_id')
        vendor = python_data.get('vendor_id')
        vendor_price = python_data.get('vendor_price')
        get_variant = models.ProductModelVariant.objects.get(id = variant_id)
        model_id = get_variant.model.id
        product_id = get_variant.product.id

        create = models.VendorProductPrice.objects.create(
            product_id = product_id,
            model_id = model_id,
            vendor_id = vendor,
            variant_id = variant_id,
            price = vendor_price,
            status = 'Active',
        ).save()

        res = {
            'message': "Vendor price added succesfully."
        }
        json_data = JSONRenderer().render(res)
        return HttpResponse(json_data, content_type= 'application/json', status=200)
    
    if python_data.get('model_id'):
        model_id = python_data.get('model_id')
        name = python_data.get('name')
        image = python_data.get('image')
        price = python_data.get('price')
        vendor = python_data.get('vendor_id')
        vendor_price = python_data.get('vendor_price')
        name_french = python_data.get('variant_name_french')

        create_variant = models.ProductModelVariant.objects.create(
            model_id = model_id,
            name = name,
            name_french = name_french,
            image = image,
            price = price,
        )
        create_variant.save()
        variant_id = create_variant.id
        
        get_model = models.ProductModel.objects.get(id = model_id)
        product_id = get_model.product.id

        create = models.VendorProductPrice.objects.create(
            product_id = product_id,
            model_id = model_id,
            vendor_id = vendor,
            variant_id = variant_id,
            price = vendor_price,
            status = 'Active',
        ).save()

        res = {
            'message': "Variant and Vendor price added succesfully."
        }
        json_data = JSONRenderer().render(res)
        return HttpResponse(json_data, content_type= 'application/json', status=200)
    
    if python_data.get('product_id'):

        product_id = python_data.get('product_id')
        name = python_data.get('name')
        image = python_data.get('image')
        
        variant_name = python_data.get('variant_name')
        variant_image = python_data.get('variant_image')
        variant_price = python_data.get('variant_price')
        model_name_french = python_data.get('model_name_french')
        name_french = python_data.get('variant_name_french')
        
        vendor = python_data.get('vendor_id')
        vendor_price = python_data.get('vendor_price')

        create_model = models.ProductModel.objects.create(
            product_id = product_id,
            model_name = name,
            model_name_french = model_name_french,
            model_image = image,
            status = 'Active'
        )
        create_model.save()

        model_id = create_model.id

        create_variant = models.ProductModelVariant.objects.create(
            model_id = model_id,
            name = variant_name,
            name_french = name_french,
            image = variant_image,
            price = variant_price,
        )
        create_variant.save()
        variant_id = create_variant.id
        
        create = models.VendorProductPrice.objects.create(
            product_id = product_id,
            model_id = model_id,
            vendor_id = vendor,
            variant_id = variant_id,
            price = vendor_price,
            status = 'Active',
        ).save()

        res = {
            'message': "Model, Variant and Vendor price added succesfully."
        }
        json_data = JSONRenderer().render(res)
        return HttpResponse(json_data, content_type= 'application/json', status=200)


    res = {
        'message': "Something went wrong."
    }
    json_data = JSONRenderer().render(res)
    return HttpResponse(json_data, content_type= 'application/json', status=406)



@csrf_exempt
def vendor_apply_product_price(request):
    python_data={}
    for i,j in request.FILES.items():
        python_data.update({i:j})
    
    for i,j in request.POST.items():
        python_data.update({i:j})
        
    # print(python_data, 'python_data')

    if python_data.get('variant_id'):
        variant_id = python_data.get('variant_id')
        vendor = python_data.get('vendor_id')
        vendor_price = python_data.get('vendor_price')
        get_variant = models.ProductModelVariant.objects.get(id = variant_id)
        model_id = get_variant.model.id
        product_id = get_variant.product.id

        create = models.VendorProductPrice.objects.create(
            product_id = product_id,
            model_id = model_id,
            vendor_id = vendor,
            variant_id = variant_id,
            price = vendor_price,
            status = 'Inactive',
        ).save()

        res = {
            'message': "Vendor price added succesfully."
        }
        json_data = JSONRenderer().render(res)
        return HttpResponse(json_data, content_type= 'application/json', status=200)
    
    if python_data.get('model_id'):
        model_id = python_data.get('model_id')
        name = python_data.get('name')
        image = python_data.get('image')
        price = python_data.get('price')
        vendor = python_data.get('vendor_id')
        vendor_price = python_data.get('vendor_price')
        name_french = python_data.get('variant_name_french')

        create_variant = models.ProductModelVariant.objects.create(
            model_id = model_id,
            name = name,
            name_french = name_french,
            image = image,
            price = price,
        )
        create_variant.save()
        variant_id = create_variant.id
        
        get_model = models.ProductModel.objects.get(id = model_id)
        product_id = get_model.product.id

        create = models.VendorProductPrice.objects.create(
            product_id = product_id,
            model_id = model_id,
            vendor_id = vendor,
            variant_id = variant_id,
            price = vendor_price,
            status = 'Inactive',
        ).save()

        res = {
            'message': "Variant and Vendor price added succesfully."
        }
        json_data = JSONRenderer().render(res)
        return HttpResponse(json_data, content_type= 'application/json', status=200)
    
    if python_data.get('product_id'):

        product_id = python_data.get('product_id')
        name = python_data.get('name')
        image = python_data.get('image')
        
        variant_name = python_data.get('variant_name')
        variant_image = python_data.get('variant_image')
        variant_price = python_data.get('variant_price')
        model_name_french = python_data.get('model_name_french')
        name_french = python_data.get('variant_name_french')
        
        vendor = python_data.get('vendor_id')
        vendor_price = python_data.get('vendor_price')

        create_model = models.ProductModel.objects.create(
            product_id = product_id,
            model_name = name,
            model_name_french = model_name_french,
            model_image = image,
            status = 'Inactive'
        )
        create_model.save()

        model_id = create_model.id

        create_variant = models.ProductModelVariant.objects.create(
            model_id = model_id,
            name = variant_name,
            name_french = name_french,
            image = variant_image,
            price = variant_price,
        )
        create_variant.save()
        variant_id = create_variant.id
        
        create = models.VendorProductPrice.objects.create(
            product_id = product_id,
            model_id = model_id,
            vendor_id = vendor,
            variant_id = variant_id,
            price = vendor_price,
            status = 'Inactive',
        ).save()

        res = {
            'message': "Model, Variant and Vendor price added succesfully."
        }
        json_data = JSONRenderer().render(res)
        return HttpResponse(json_data, content_type= 'application/json', status=200)


    res = {
        'message': "Something went wrong."
    }
    json_data = JSONRenderer().render(res)
    return HttpResponse(json_data, content_type= 'application/json', status=406)




@csrf_exempt
def product_model_status_update(request):
    json_data = request.body
    stream = io.BytesIO(json_data)
    python_data = JSONParser().parse(stream)
    id = python_data.get('id')

    product = models.ProductModel.objects.get(id = id)
    product.status = python_data.get('status', product.status)
    product.save()

    res = {
        'message':'Product verification update successfully.'        
    }
    json_data = JSONRenderer().render(res)
    return HttpResponse(json_data, content_type= 'application/json', status=200)


@csrf_exempt
def product_variant_status_update(request):
    json_data = request.body
    stream = io.BytesIO(json_data)
    python_data = JSONParser().parse(stream)

    # print("python_Data-=-=-->",python_data)
    id = python_data.get('id')

    product = models.ProductModelVariant.objects.get(id = id)
    product.status = python_data.get('status', product.status)
    product.save()

    res = {
        'message':'Product verification update successfully.'        
    }
    json_data = JSONRenderer().render(res)
    return HttpResponse(json_data, content_type= 'application/json', status=200)



@csrf_exempt
def product_vendor_status_update(request):
    json_data = request.body
    stream = io.BytesIO(json_data)
    python_data = JSONParser().parse(stream)
    id = python_data.get('id')

    product = models.VendorProductPrice.objects.get(id = id)
    product.status = python_data.get('status', product.status)
    product.save()

    res = {
        'message':'Product verification update successfully.'        
    }
    json_data = JSONRenderer().render(res)
    return HttpResponse(json_data, content_type= 'application/json', status=200)


@csrf_exempt
def country_list_customer_filter(request):
    if request.method == "POST":
        country_list = list(
            models.CustomerDetail.objects
            .values_list('country', flat=True)
            .exclude(country__isnull=True)
            .exclude(country__exact="")
            .distinct()
            .order_by('country')
        )
        res={
            'data':country_list
        }
        json_data = JSONRenderer().render(res)
        return HttpResponse(json_data, content_type= 'application/json', status=200)


@csrf_exempt
def customer_list_admin(request):
    if request.method == "POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))
        
        # print("python_data--all_product_list--->", python_data)

        today = timezone.now()

        page_number = int(python_data.get('page_number', 1))
        row_size = int(python_data.get('row_data', 10))
        last_row = row_size * page_number
        first_row = last_row - row_size
        
        search_key = python_data.get('search_key',None)
        country = python_data.get('country',None)

        filter_condition = Q()

        if country not in [None,'','null']:
            filter_condition &= Q(country = country)
        if search_key not in [None,'','null']:
            filter_condition &= Q(email__icontains = search_key)|Q(mobileNumber__icontains = search_key)|Q(name__icontains = search_key)

        total_records = models.CustomerDetail.objects.filter(filter_condition).count()
        all_customer = models.CustomerDetail.objects.filter(filter_condition).order_by('-id')[first_row:last_row]
        serializer = CustomerDetailSerializer(all_customer, many=True).data

        res = {
            'data':serializer,
            'total_records':total_records,
            'current_page':page_number,
            'total_pages': int(np.ceil(total_records/row_size))
        }
        json_data = JSONRenderer().render(res)
        return HttpResponse(json_data, content_type= 'application/json', status=200)

        
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
def customer_detail_admin(request):
    json_data = request.body
    stream = io.BytesIO(json_data)
    python_data = JSONParser().parse(stream)
    id = python_data.get('id')
    check_customer = models.CustomerDetail.objects.filter(id = id).count()
    if check_customer == 1:

        customer = models.CustomerDetail.objects.get(id = id)
        serializer = CustomerDetailSerializer(customer).data
        
        all_address = models.CustomerAddressDetail.objects.filter(customer = id)
        address_serializer = CustomerAddressDetailSerializer(all_address, many=True).data

        list_order = []
        all_order_list = models.OrderDetail.objects.filter(customer = id)
        for order in all_order_list:
            order_get = models.OrderDetail.objects.get(id = order.id)
            order_data = OrderDetailDataSerializer(order_get).data

            product = models.ProductOrderDetail.objects.filter(order = order.id)
            product_data = ProductOrderDetailSerializer(product, many=True).data

            order_data.update({'product_data':product_data})
            list_order.append(order_data)

        get_cart = models.CartDetail.objects.filter(customer = id)
        cart_data = CartDetailSerializer(get_cart, many=True).data

        get_wishlist = models.WishlistDetail.objects.filter(customer = id)
        wishlist_data = WishlistDetailSerializer(get_wishlist, many=True).data


        res = {
            'data':serializer,
            'address': address_serializer,
            'order_data':list_order,
            'cart_data':cart_data,
            'wishlist_data':wishlist_data
        }
        json_data = JSONRenderer().render(res)
        return HttpResponse(json_data, content_type= 'application/json', status=200)


@csrf_exempt
def app_dashboard_category(request):
    list_category = []    
    all_category = models.CategoryDetail.objects.filter(status = 'Active').exclude(category='Intimate Universe and Comfort')
    for category in all_category:
        check_subcategory_count = models.SubCategoryDetail.objects.filter(category = category.id).count()
        if check_subcategory_count > 0:
            category_data = models.CategoryDetail.objects.get(id = category.id)
            category_serializer = CategoryDetailSerializer(category_data).data
            list_category.append(category_serializer)
        
    res = {
        'data':list_category,  
    }
    json_data = JSONRenderer().render(res)
    return HttpResponse(json_data, content_type= 'application/json', status=200)

# @csrf_exempt
# def app_dashboard(request):
#     json_data = request.body
#     stream = io.BytesIO(json_data)
#     python_data = JSONParser().parse(stream)

#     page_number = python_data.get('page_number',1)

#     page_record = 5
#     last_row = page_record * page_number
#     first_row = last_row - page_record
       
#     total_pages =  math.ceil(models.CategoryDetail.objects.filter(status='Active').order_by('-id').count()/page_record)
    
#     list_data = []

#     all_random_category_data = models.CategoryDetail.objects.filter(status='Active').order_by('id')[first_row:last_row]


#     # all_random_category_data = models.CategoryDetail.objects.filter(status= 'Active')
    
#     list_data = []
#     for random_category in all_random_category_data:
#         get_product_count = models.ProductDetail.objects.filter(category = random_category.id, status='Active').count()
#         if get_product_count > 0:
#             category_data = {}
#             get_product = models.ProductDetail.objects.filter(category = random_category.id, status='Active').order_by("-id")[:10]
#             product_serializer = ProductDataSerializer(get_product, many=True).data

#             category_data.update({"name":random_category.category,"name_french":random_category.category_french, 'category_id':random_category.id,'product':product_serializer})
#             list_data.append(category_data)
    
#     res = {
#         'category_product_list': list_data,
#         'total_pages':total_pages
#     }
#     json_data = JSONRenderer().render(res)
#     return HttpResponse(json_data, content_type= 'application/json', status=200)



@csrf_exempt
def app_dashboard(request):
    json_data = request.body
    stream = io.BytesIO(json_data)
    python_data = JSONParser().parse(stream)

    currencyCode = python_data.get('currencyCode',None)
    countryCallingCode = python_data.get('countryCallingCode',None)
    country = python_data.get('countryName','Egypt')
    ip_address = python_data.get('ip_address')
    user_id = python_data.get('user_id')
    country_id = python_data.get('country_id', None)

    page_number = python_data.get('page_number',1)

    # f("python_data--app_dashboard_dummy-->",python_data)
    
    try:
        if currencyCode not in [None,'','null']:
            country = models.CountryWithCurrency.objects.filter(currency_code = currencyCode).first().country_name
        elif countryCallingCode not in [None,'','null']:
            country = models.CountryWithCurrency.objects.filter(country_calling_code = countryCallingCode).first().country_name
            
        elif user_id:
            user = models.CustomerDetail.objects.get(id = user_id)
            countryCode = user.countryCode

            if models.CountryWithCurrency.objects.filter(country_calling_code = countryCode).exists():
                country = models.CountryWithCurrency.objects.get(country_calling_code = countryCode).country_name
            else:
                if country not in [None,'','null']:
                    country = country
                else:
                    try:
                        response = requests.get(f'https://ipapi.co/{ip_address}/json/')
                        response = response.json()
                        country = response.get("country_name")
                        # print("response====>",response)

                        if country in [None,'','null']:
                            country = "Egypt"

                    except Exception as e:
                        # print("Errroooorrr----->",e)
                        country = "Egypt"
                    

        else:
            if country in [None,'','null']:
                try:
                    response = requests.get(f'https://ipapi.co/{ip_address}/json/')
                    response = response.json()
                    country = response.get("country_name")
                    # print("response====>",response)

                    if country in [None,'','null']:
                        country = "Egypt"

                except Exception as e:
                    # print("Errroooorrr----->",e)
                    country = "Egypt"
            else:
                country = country
    except Exception as e:
        # print("Error-=-=-=--->",e)
        country = 'Egypt'

   

    page_record = 20
    last_row = page_record * page_number
    first_row = last_row - page_record

    # get_country_name = models.ProductCountry.objects.filter(id = country_id)
    # available_country_name = get_country_name.name

    if country_id != None:
        total_pages =  math.ceil(models.ProductDetail.objects.filter(status='Active',available_country = country_id).order_by('-id').count()/page_record)
        
        list_data = []

        all_product_data = models.ProductDetail.objects.filter(status='Active', available_country = country_id).exclude(category__category='Intimate Universe and Comfort').order_by(Random())[first_row:last_row]
        product_serializer = ProductDataSerializer(all_product_data, many=True, context = {'country':country}).data
        

        if user_id and page_number == 1:
            product = models.RecentlyViewProduct.objects.filter(customer = user_id, product__status = 'Active', product__available_country = country_id).order_by('-id')[:5]
            recently_serializer = RecentlyViewProductSerializer(product, many=True, context = {'country':country}).data
            res = {
                'product_list': product_serializer,
                'total_pages':total_pages,
                'recently_view':recently_serializer,
                'recently_title':'Recently Browsed',
                'recently_title_fr':'Consulté récemment'
            }
            json_data = JSONRenderer().render(res)
            return HttpResponse(json_data, content_type= 'application/json', status=200)
        else:
            res = {
                'product_list': product_serializer,
                'total_pages':total_pages,
            }
            json_data = JSONRenderer().render(res)
            return HttpResponse(json_data, content_type= 'application/json', status=200)
    else:
        total_pages =  math.ceil(models.ProductDetail.objects.filter(status='Active').order_by('-id').count()/page_record)
        
        list_data = []

        all_product_data = models.ProductDetail.objects.filter(status='Active').exclude(category__category='Intimate Universe and Comfort').order_by(Random())[first_row:last_row]
        product_serializer = ProductDataSerializer(all_product_data, many=True, context = {'country':country}).data
        

        if user_id and page_number == 1:
            product = models.RecentlyViewProduct.objects.filter(customer = user_id, product__status = 'Active').order_by('-id')[:5]
            recently_serializer = RecentlyViewProductSerializer(product, many=True, context = {'country':country}).data
            res = {
                'product_list': product_serializer,
                'total_pages':total_pages,
                'recently_view':recently_serializer,
                'recently_title':'Recently Browsed',
                'recently_title_fr':'Consulté récemment'
            }
            json_data = JSONRenderer().render(res)
            return HttpResponse(json_data, content_type= 'application/json', status=200)
        else:
            res = {
                'product_list': product_serializer,
                'total_pages':total_pages,
            }
            json_data = JSONRenderer().render(res)
            return HttpResponse(json_data, content_type= 'application/json', status=200)



@csrf_exempt
def product_detail_app(request):
    if request.method == 'POST':
        python_data = JSONParser().parse(io.BytesIO(request.body))
        # print(python_data, 'python_data customer ')
        id = python_data.get('id')
        customer = python_data.get('customer')

        currencyCode = python_data.get('currencyCode',None)
        country = python_data.get('countryName','Egypt')
        ip_address = python_data.get('ip_address')
        
        price_update = models.DailyPrice.objects.last()
        # daily_price = DailyPriceSerializer(price_update).data

        get_delivery_data = models.DeliveryDayDetail.objects.first()
    
        now = datetime.now()
        date_time = now.strftime('%Y-%m-%d, %H:%M:%S')

        product = models.ProductDetail.objects.get(id = id)
        
        delay_days_air = 0
        delay_days_ship = 0
        delay_days_express = 0
        if product.delay_days_air not in [None,'','null']:
            delay_days_air = product.delay_days_air
        if product.delay_days_ship not in [None,'','null']:
            delay_days_ship = product.delay_days_ship
        if product.delay_days_express not in [None,'','null']:
            delay_days_express = product.delay_days_express

     

        express_date_now = now + timedelta(days=get_delivery_data.express_delivery + delay_days_express )
        express_date = express_date_now.strftime('%d').lower()
        express_month = express_date_now.strftime('%B').lower()
        
        air_date_now = now + timedelta(days=get_delivery_data.air_delivery + delay_days_air)
        air_date = air_date_now.strftime('%d').lower()
        air_month = air_date_now.strftime('%B').lower()
        
        ship_date_now = now + timedelta(days=get_delivery_data.ship_delivery + delay_days_ship)
        ship_date = ship_date_now.strftime('%d').lower()
        ship_month = ship_date_now.strftime('%B').lower()

        month_map = {
            "january": "janvier",
            "february": "février",
            "march": "mars",
            "april": "avril",
            "may": "mai",
            "june": "juin",
            "july": "juillet",
            "august": "août",
            "september": "septembre",
            "october": "octobre",
            "november": "novembre",
            "december": "décembre"
        }
        express_fr_month = month_map.get(express_month)
        air_fr_month = month_map.get(air_month)
        ship_fr_month = month_map.get(ship_month)
        
        express_en = f"before {express_date} {express_month}"
        express_fr = f"avant le {express_date} {express_fr_month}"
        air_en = f"before {air_date} {air_month}"
        air_fr = f"avant le {air_date} {air_fr_month}"
        ship_en = f"before {ship_date} {ship_month}"
        ship_fr = f"avant le {ship_date} {ship_fr_month}"




        try:
            if currencyCode not in [None,'','null']:
                if customer:
                    country = models.CountryWithCurrency.objects.filter(currency_code = currencyCode).first().country_name
                    
                    user = models.CustomerDetail.objects.get(id = customer)
                    delivery_country = user.country
                else:
                    delivery_country = country
                    country = models.CountryWithCurrency.objects.filter(currency_code = currencyCode).first().country_name

            elif customer:
                user = models.CustomerDetail.objects.get(id = customer)
                countryCode = user.countryCode

                if models.CountryWithCurrency.objects.filter(country_calling_code = countryCode).exists():
                    country = models.CountryWithCurrency.objects.get(country_calling_code = countryCode).country_name
                    delivery_country = country
                else:
                    if country not in [None,'','null']:
                        delivery_country = country
                    else:
                        try:
                            response = requests.get(f'https://ipapi.co/{ip_address}/json/')
                            response = response.json()
                            country = response.get("country_name")
                            # print("response====>",response)
                            delivery_country = country
                            if country in [None,'','null']:
                                country = "Egypt"

                        except Exception as e:
                            # print("Errroooorrr----->",e)
                            country = "Egypt"
                            delivery_country = country
                        

            else:
                if country in [None,'','null']:
                    try:
                        response = requests.get(f'https://ipapi.co/{ip_address}/json/')
                        response = response.json()
                        country = response.get("country_name")
                        # print("response====>",response)

                        delivery_country = country

                        if country in [None,'','null']:
                            country = "Egypt"

                    except Exception as e:
                        # print("Errroooorrr----->",e)
                        country = "Egypt"
                else:
                    try:
                        response = requests.get(f'https://ipapi.co/{ip_address}/json/')
                        response = response.json()
                        delivery_country = response.get("country_name")
                        # print("response====>",response)

                        if delivery_country in [None,'','null']:
                            delivery_country = country

                    except Exception as e:
                        # print("Errroooorrr----->",e)
                        delivery_country = country
                        
                    country = country
        except Exception as e:
            # print("Error-=-=-=--->",e)
            country = 'Egypt'

        print(delivery_country, 'delivery_countrydelivery_country')
        product_review_data = models.ProductReview.objects.filter(product = id).order_by('-id')[:5]
        review_serialiser = ProductReviewSerializer(product_review_data, many=True).data
        
        payment_data = models.PaymentCargoSlider.objects.filter(status = 'Active')
        slider_serialser = PaymentCargoSliderSerializer(payment_data, many=True).data

        important_note = models.ImportantNote.objects.filter(status = 'Active').first()
        # print("important_note---->",important_note)
        if important_note:
            note_serialser = ImportantNoteSerializer(important_note).data
        else:
            note_serialser=None
        
        # print("note_serialser---->",note_serialser)
        

        total_review = models.ProductReview.objects.filter(product = id).count()
        average_review = 0
        if total_review > 0:
            get_rating = list(models.ProductReview.objects.filter(product = id).values_list('rating', flat=True))
            average_review = round(sum(get_rating) / total_review, 1)
            # print(get_rating, 'get_rating', average_review)   

        if customer:
            product_check = models.ProductDetail.objects.filter(id = id).count()
            if product_check == 1:
                wishlist_count = models.WishlistDetail.objects.filter(customer = customer, product = id).count()
                if wishlist_count == 1:
                    wishlist_flag = True
                else:
                    wishlist_flag = False

                product = models.ProductDetail.objects.get(id = id)
                data = ProductDetailAppSerializer(product, context = {'country':country,'delivery_country':delivery_country}).data                
                subcategory = product.subcategory.id

                get_image = models.ProductImage.objects.filter(product = id)
                image_serializer = ProductImageSerializer(get_image, many=True).data

                get_other_specification = models.ProductOtherSpecification.objects.filter(product = id)
                other_serializer = ProductOtherSpecificationSerializer(get_other_specification, many=True).data

                list_model = []
                total_quantity = 0 
                all_model = models.ProductModel.objects.filter(product = id).order_by('-id')
                for model in all_model:
                    model = models.ProductModel.objects.get(id = model.id)
                    model_serializer = ProductModelSerializer(model).data
                    get_variants = models.ProductModelVariant.objects.filter(model = model.id).order_by('-id')
                    list_variant = []
                    for variant in get_variants:
                        variants_data = models.ProductModelVariant.objects.get(id = variant.id)
                        variant_serilizer = ProductModelVariantSerializer(variants_data, context = {'country':country}).data

                        # check for delay note:

                        # vendor_qs = models.VendorProductPrice.objects.filter(
                        #     variant=variants_data
                        # ).values_list('vendor', flat=True).distinct()

                        # vendor_count = vendor_qs.count()

                        # delay_notes_qs = models.VendorDelayNote.objects.filter(
                        #     vendor__in=vendor_qs,
                        #     start_at__lte=now,
                        #     end_at__gte=now,
                        #     status="Active"
                        # )

                        # delay_note_vendor_count = delay_notes_qs.count()

                        # note = None

                        # if vendor_count > 0 and delay_note_vendor_count == vendor_count:
                        #     note = delay_notes_qs.order_by('-id').values_list('note', flat=True).first()

                        # variant_serilizer.update({'delay_note': note})                        
                        
                        check_varient = models.CartDetail.objects.filter(customer = customer, product = id, variant = variant.id).count()
                        # print(check_varient, 'check_varient')
                        if check_varient != 0:
                            cart_quantity = models.CartDetail.objects.filter(customer = customer, product = id, variant = variant.id).values_list('quantity', flat=True)[0]
                            total_quantity += int(cart_quantity)
                            variant_serilizer.update({'cart_quantity':cart_quantity})
                        else:
                            variant_serilizer.update({'cart_quantity':0})

                        # variant_serilizer.update({'vendor_list':price_serializer})
                        list_variant.append(variant_serilizer)


                    model_serializer.update({'variants':list_variant})    
                    
                    list_model.append(model_serializer)
                
                data.update({'image':image_serializer, 'other_data':other_serializer})
                # print(data, 'afasf')
                
                all_related_product = models.ProductDetail.objects.filter(subcategory = subcategory, status='Active')[:10]
                list_related_product = []
                for related_product in all_related_product:
                    current_id = related_product.id
                    if product.id != current_id:
                        current_data = models.ProductDetail.objects.get(id = current_id)
                        product_serializer = ProductDataSerializer(current_data,context = {'country':country}).data
                        list_related_product.append(product_serializer)

                # print(list_related_product, 'list_related_product')

                check_review_product = models.RecentlyViewProduct.objects.filter(customer = customer, product = id).count()
                if check_review_product == 1:
                    get_review_product = models.RecentlyViewProduct.objects.get(customer = customer, product = id)
                    get_review_product.delete()

                    get_review_product = models.RecentlyViewProduct.objects.create(
                        customer_id = customer, 
                        product_id = id,
                        created_at = date_time

                    ).save()

                elif check_review_product == 0:
                    get_review_product = models.RecentlyViewProduct.objects.create(
                        customer_id = customer, 
                        product_id = id,
                        created_at = date_time

                    ).save()


            # air_fr = f'avant le {}'
                                    
            res={
                'data':data,
                'models':list_model, 
                'wishlist_flag':wishlist_flag,
                # 'cart_detail':cart_detail_serialiser, 
                # 'daily_price':daily_price,
                'list_related_product':list_related_product,
                'express_en':express_en,
                'express_fr':express_fr,
                'air_en':air_en,
                'air_fr':air_fr,
                'ship_en':ship_en,
                'ship_fr':ship_fr,
                'total_review':total_review,
                'average_review':average_review,
                'review_data':review_serialiser,
                'payment_cargo_slider':slider_serialser,
                'important_note':note_serialser,
                'total_quantity':total_quantity
                
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)

        else:
            product_check = models.ProductDetail.objects.filter(id = id).count()
            if product_check == 1:
                
                product = models.ProductDetail.objects.get(id = id)
                data = ProductDetailAppSerializer(product,context = {'country':country,'delivery_country':delivery_country}).data

                # print('data---->',data)

                subcategory = product.subcategory.id

                get_image = models.ProductImage.objects.filter(product = id)
                image_serializer = ProductImageSerializer(get_image, many=True).data

                get_other_specification = models.ProductOtherSpecification.objects.filter(product = id)
                other_serializer = ProductOtherSpecificationSerializer(get_other_specification, many=True).data 
                

                list_model = []

                all_model = models.ProductModel.objects.filter(product = id).order_by('-id')
                for model in all_model:
                    model = models.ProductModel.objects.get(id = model.id)
                    model_serializer = ProductModelSerializer(model).data
                    get_variants = models.ProductModelVariant.objects.filter(model = model.id).order_by('-id')
                    list_variant = []
                    for variant in get_variants:
                        variants_data = models.ProductModelVariant.objects.get(id = variant.id)
                        variant_serilizer = ProductModelVariantSerializer(variants_data,context = {'country':country}).data
                        
                        # variant_serilizer.update({'vendor_list':price_serializer})
                        
                        # check for delay note:

                        # vendor_qs = models.VendorProductPrice.objects.filter(
                        #     variant=variants_data
                        # ).values_list('vendor', flat=True).distinct()

                        # vendor_count = vendor_qs.count()

                        # delay_notes_qs = models.VendorDelayNote.objects.filter(
                        #     vendor__in=vendor_qs,
                        #     start_at__lte=now,
                        #     end_at__gte=now,
                        #     status="Active"
                        # )

                        # delay_note_vendor_count = delay_notes_qs.count()

                        # note = None

                        # if vendor_count > 0 and delay_note_vendor_count == vendor_count:
                        #     note = delay_notes_qs.order_by('-id').values_list('note', flat=True).first()

                        # variant_serilizer.update({'delay_note': note})

                        list_variant.append(variant_serilizer)

                    model_serializer.update({'variants':list_variant})
                    
                    list_model.append(model_serializer)
                
                data.update({'image':image_serializer, 'other_data':other_serializer})

                all_related_product = models.ProductDetail.objects.filter(subcategory = subcategory, status='Active')[:10]
                list_related_product = []
                for related_product in all_related_product:
                    current_id = related_product.id
                    if product.id != current_id:
                        current_data = models.ProductDetail.objects.get(id = current_id)
                        product_serializer = ProductDataSerializer(current_data,context = {'country':country}).data
                        list_related_product.append(product_serializer)

               
            

            res={
                'data':data,
                'models':list_model,
                # 'daily_price':daily_price,
                'list_related_product':list_related_product,
                'express_en':express_en,
                'express_fr':express_fr,
                'air_en':air_en,
                'air_fr':air_fr,
                'ship_en':ship_en,
                'ship_fr':ship_fr,
                'total_review':total_review,
                'average_review':average_review,
                'review_data':review_serialiser,
                'payment_cargo_slider':slider_serialser,
                'important_note':note_serialser
                
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)




@csrf_exempt
def category_with_subcategory_data(request):
    if request.method == 'POST':
        
        # all_category = models.CategoryDetail.objects.filter(status = 'Active').exclude(category='Intimate Universe and Comfort')
        all_category = models.CategoryDetail.objects.filter(status = 'Active')
        # print(all_category, 'all_category')
        list_data = []
        for category in all_category:
            check_subcategory_count = models.SubCategoryDetail.objects.filter(category = category.id).count()
            if check_subcategory_count > 0:
                category_data = models.CategoryDetail.objects.get(id = category.id) 
                category_serializer = CategoryDetailSerializer(category_data).data

                subcategory_list = models.SubCategoryDetail.objects.filter(category = category.id, status = 'Active')
                subcategory_serializer = SubCategoryListSerializer(subcategory_list, many=True).data

                category_serializer.update({'items':subcategory_serializer})
                list_data.append(category_serializer)
        
        res={
            'data':list_data
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)


@csrf_exempt
def subcategory_wise_product_list(request):
    if request.method == 'POST':
        python_data = JSONParser().parse(io.BytesIO(request.body))
        # print("python_data--subcategory_wise_product_list-->",python_data)

        currencyCode = python_data.get('currencyCode',None)
        countryCallingCode = python_data.get('countryCallingCode',None)
        country = python_data.get('countryName','Egypt')
        ip_address = python_data.get('ip_address')
        user_id = python_data.get('user_id')

        try:
            if currencyCode not in [None,'','null']:
                country = models.CountryWithCurrency.objects.filter(currency_code = currencyCode).first().country_name
            elif countryCallingCode not in [None,'','null']:
                country = models.CountryWithCurrency.objects.filter(country_calling_code = countryCallingCode).first().country_name
                
            elif user_id:
                user = models.CustomerDetail.objects.get(id = user_id)
                countryCode = user.countryCode

                if models.CountryWithCurrency.objects.filter(country_calling_code = countryCode).exists():
                    country = models.CountryWithCurrency.objects.get(country_calling_code = countryCode).country_name
                else:
                    if country not in [None,'','null']:
                        country = country
                    else:
                        try:
                            response = requests.get(f'https://ipapi.co/{ip_address}/json/')
                            response = response.json()
                            country = response.get("country_name")
                            # print("response====>",response)

                            if country in [None,'','null']:
                                country = "Egypt"

                        except Exception as e:
                            # print("Errroooorrr----->",e)
                            country = "Egypt"
                        

            else:
                if country in [None,'','null']:
                    try:
                        response = requests.get(f'https://ipapi.co/{ip_address}/json/')
                        response = response.json()
                        country = response.get("country_name")
                        # print("response====>",response)

                        if country in [None,'','null']:
                            country = "Egypt"

                    except Exception as e:
                        # print("Errroooorrr----->",e)
                        country = "Egypt"
                else:
                    country = country
        except Exception as e:
            # print("Error-=-=-=--->",e)
            country = 'Egypt'

        subcategory = python_data.get('subcategory')
        subcategory_list = models.ProductDetail.objects.filter(subcategory = subcategory, status = 'Active')
        subcategory_serializer = ProductSearchSerializer(subcategory_list, many=True, context = {'country':country}).data
        res={
            'data':subcategory_serializer
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)



@csrf_exempt
def add_to_wishlist(request):
    if request.method == 'POST':
        python_data = JSONParser().parse(io.BytesIO(request.body))
        customer = python_data.get('customer')
        product = python_data.get('product')

        now = datetime.now()
        date_time = now.strftime('%Y-%m-%d, %H:%M:%S')

        check_customer = models.CustomerDetail.objects.filter(id =customer).count()
        if check_customer == 1:
            check_product = models.ProductDetail.objects.filter(id = product).count()
            if check_product == 1:
                check_wishlist = models.WishlistDetail.objects.filter(customer= customer,product=product).count()
                if check_wishlist == 0:
                    create = models.WishlistDetail.objects.create(
                        customer_id= customer,
                        product_id=product,
                        created_at = date_time
                    ).save()
                    
                    res={
                        'message':"Product successfully added to your wishlist."
                    }
                    return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)

                if check_wishlist == 1:
                    delete_data = models.WishlistDetail.objects.get(customer_id= customer,product_id=product)
                    delete_data.delete()

                    res={
                        'message':"Product removed from your wishlist."
                    }
                    return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)

                else:
                    res={
                        'message':"Something Went Wrong."
                    }
                    return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=406)
            else:
                res={
                    'message':"Please Enter Valid Product."
                }
                return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=406)
        else:
            res={
                'message':"Please Enter Valid Customer."
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=406)


@csrf_exempt
def customer_wishlist(request):
    if request.method == 'POST':
        python_data = JSONParser().parse(io.BytesIO(request.body))
        customer = python_data.get('customer')
        wishlist = models.WishlistDetail.objects.filter(customer = customer).order_by('-id')
        wishlist_serializer = WishlistDetailSerializer(wishlist, many=True).data
    
        res={
            'data':wishlist_serializer
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)


@csrf_exempt
def add_to_cart(request):
    if request.method == 'POST':
        python_data = JSONParser().parse(io.BytesIO(request.body))


        all_cart = python_data.get('cart')

        for cart in all_cart:
            customer = cart.get('customer')
            product = cart.get('product')
            variant = cart.get('variant')
            quantity = cart.get('quantity')
            shipping_via = cart.get('shipping_via')

            # print(python_data, 'python_data')
            now = datetime.now()
            date_time = now.strftime('%Y-%m-%d, %H:%M:%S')

            check_customer = models.CustomerDetail.objects.filter(id =customer).count()
            if check_customer == 1:
                check_product = models.ProductDetail.objects.filter(id = product).count()
                if check_product == 1:
                    check_cart = models.CartDetail.objects.filter(customer= customer,product=product, variant = variant).count()
                    # print(check_cart, 'check_cartcheck_cart')
                    if check_cart == 0:
                        create = models.CartDetail.objects.create(
                            customer_id= customer,
                            product_id=product,
                            variant_id =variant,
                            quantity = quantity,
                            shipping_via = shipping_via,
                            created_at = date_time
                        ).save()
                        
                        res={
                            'message':"Product successfully added to your cart."
                        }
                        # return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)

                    if check_cart == 1:
                        cart_id = models.CartDetail.objects.filter(customer= customer,product=product, variant = variant).values_list('id', flat=True)[0]
                        variant_quantity = models.CartDetail.objects.filter(id = cart_id).values_list('quantity', flat=True)[0]
                        # print(variant_quantity, 'variant_quantity')
                        add_variant = int(variant_quantity) + quantity

                        cart_update = models.CartDetail.objects.get(id = cart_id)
                        cart_update.quantity = add_variant
                        cart_update.save()
                        
                        res={
                            'message':"Product successfully added to your cart."
                        }
                        # return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)

        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)


@csrf_exempt
def product_remove_from_cart(request):
    if request.method == 'POST':
        python_data = JSONParser().parse(io.BytesIO(request.body))
        cart = python_data.get('cart')
        
        check_cart = models.CartDetail.objects.filter(id= cart).count()
        if check_cart == 1:
            cart_data = models.CartDetail.objects.get(id = cart)
            cart_data.delete()

            res={
                'message':"Product Remove From Cart."
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)
        else:
            res={
                'message':"Someting went wrong."
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=406)




@csrf_exempt
def get_shipping_cost(request):
    data = JSONParser().parse(io.BytesIO(request.body))

    # print("data--get_shipping_cost-->",data)

    result = calculate_shipping_cost(
        carton_length=data.get("carton_length"),
        carton_width=data.get("carton_width"),
        carton_height=data.get("carton_height"),
        carton_weight=data.get("carton_weight"),
        quantity=data.get("quantity"),
        price_by_air=data.get("price_by_air"),
        price_by_ship=data.get("price_by_ship"),
        price_by_express=data.get("price_by_express"),
    )

    # print("result=======>",result)

    total_air_cost_view = f"{result.get('total_air_cost'):,}".replace(',', ' ')
    total_sea_cost_view = f"{result.get('total_sea_cost'):,}".replace(',', ' ')
    total_express_cost_view = f"{result.get('total_express_cost'):,}".replace(',', ' ')

    result["total_air_cost_view"] = total_air_cost_view
    result["total_sea_cost_view"] = total_sea_cost_view
    result["total_express_cost_view"] = total_express_cost_view
    
    res={
        'data':result
    }
    # print("res-=-=---->",res)
    return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)



@csrf_exempt
def customer_wishlist_cart_list(request):
    if request.method == 'POST':
        python_data = JSONParser().parse(io.BytesIO(request.body))

        # print("python_data=-=-customer_wishlist_cart_list--->",python_data)
        customer = python_data.get('customer')
        flag = python_data.get('flag')
        check_customer = models.CustomerDetail.objects.filter(id =customer).count()

        currencyCode = python_data.get('currencyCode',None)
        country = python_data.get('country','Egypt')
        ip_address = python_data.get('ip_address')
        promocode = python_data.get('promocode')

        try:
            if currencyCode not in [None,'','null']:
                country = models.CountryWithCurrency.objects.filter(currency_code = currencyCode).first().country_name
                # print("country--->",country)

            elif customer:
                user = models.CustomerDetail.objects.get(id = customer)
                countryCode = user.countryCode

                if models.CountryWithCurrency.objects.filter(country_calling_code = countryCode).exists():
                    country = models.CountryWithCurrency.objects.get(country_calling_code = countryCode).country_name
                else:
                    if country not in [None,'','null']:
                        country = country
                    else:
                        try:
                            response = requests.get(f'https://ipapi.co/{ip_address}/json/')
                            response = response.json()
                            country = response.get("country_name")
                            # print("response====>",response)

                            if country in [None,'','null']:
                                country = "Egypt"

                        except Exception as e:
                            # print("Errroooorrr----->",e)
                            country = "Egypt"
                        

            else:
                if country in [None,'','null']:
                    try:
                        response = requests.get(f'https://ipapi.co/{ip_address}/json/')
                        response = response.json()
                        country = response.get("country_name")
                        # print("response====>",response)

                        if country in [None,'','null']:
                            country = "Egypt"

                    except Exception as e:
                        # print("Errroooorrr----->",e)
                        country = "Egypt"
                else:
                    country = country
        except Exception as e:
            # print("Error-=-=-=--->",e)
            country = 'Egypt'
            

        if check_customer == 1:
            user = models.CustomerDetail.objects.get(id = customer)
            
            if flag == 'wishlist':
                wishlist_data = models.WishlistDetail.objects.filter(customer= customer)
                wishlist_serializer = WishlistDetailSerializer(wishlist_data, many=True).data

                res={
                    'data':wishlist_serializer
                }
                return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)
            
            elif flag == 'cart':
                
                cart_data = models.CartDetail.objects.filter(customer= customer,  product__status = 'Active')
                # cart_serializer = CartDetailSerializer(cart_data, many=True).data
                cart_data_list = []

                if not models.CountryWithCurrency.objects.filter(Q(country_calling_code = user.countryCode) | Q(country_name = user.country)).exists():
                    country = "Egypt"
                    for product in cart_data:
                        price_by_air = 0
                        price_by_ship = 0

                        # print("herere0-0-00-302-30--->",product)
                        per_product_cart_serializer = CartDetailSerializer(product,context = {'country':country}).data
                        quantity=product.quantity
                        product_total = float(quantity) * float(per_product_cart_serializer.get('price'))
                        per_product_cart_serializer['product_total'] = int(round(float(product_total)))
                        
                        cart_data_list.append(per_product_cart_serializer)

                    res={
                        'data':cart_data_list,
                        # 'data':cart_serializer,
                        # 'daily_price':daily_price,
                        # 'product_total':product_total,
                        # 'price_by_air':price_by_air,
                        # 'price_by_ship':price_by_ship
                        'message_en':'Cannot Place Order Outside Africa Continent',
                        'message_fr':'Impossible de passer commande en dehors du continent africain.'
                    }                    
                    return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)
                
                # print(user.countryCode, 'user.countryCode', user.country)
                # price_by = models.CountryWithCurrency.objects.filter(Q(country_calling_code = user.countryCode) | Q(country_name = user.country))
                price_by = models.CountryWithCurrency.objects.get(country_name = user.country)
                # print(price_by)
                price_by_air_rate = price_by.price_by_air
                price_by_ship_rate = price_by.price_by_ship
                price_by_express_shipping = price_by.express_shipping
                

                total_price = 0.0
                cart_data_list = []
                list_air = []
                list_ship = []
                list_express = []
                list_product_amount = []
                # count = 0
                for product in cart_data:
                    price_by_air = 0
                    price_by_ship = 0
                    price_by_express = 0

                    # print("herere0-0-00-302-30--->",product)

                    product = models.CartDetail.objects.get(id = product.id)

                    per_product_cart_serializer = CartDetailSerializer(product,context = {'country':country}).data

                    # print("per_product_cart_serializer-=-=---->",per_product_cart_serializer)
                    total_price += float(product.variant.price)
                    # print(product.shipping_via, 'product.shipping_via')
                    if product.shipping_via == "By Air":
                        
                        # print(currencyCode, 'price_by')

                        if currencyCode not in [None,'','null']:
                            if price_by.currency_code != "USD":
                                non_usd_rate = models.CurrencyConverter.objects.get(currency_code = price_by.currency_code).system_rate
                                usd_price_by_air = float(price_by_air_rate) / float(non_usd_rate)

                                if currencyCode != "USD":
                                    user_country_currency_rate = models.CurrencyConverter.objects.get(currency_code = price_by.currency_code).system_rate
                                    price_by_air = float(usd_price_by_air) * float(user_country_currency_rate)

                                else:
                                    price_by_air = usd_price_by_air
                                    
                            else:
                                if currencyCode != "USD":
                                    selected_currency_rate = models.CurrencyConverter.objects.get(currency_code = currencyCode).system_rate

                                    price_by_air = float(price_by_air_rate) * float(selected_currency_rate)

                                else:
                                    price_by_air = price_by_air_rate
                                    # print(price_by_air, 'price_by_air')

                        else:
                            price_by_air = price_by_air_rate
                            # print(price_by_air, 'price_by_air tyu' )

                        
                        # print(price_by_air,'price_by_air_rate')
                        per_product_cart_serializer['price_by_air']= round(float(price_by_air),2)
                        # list_air.append(price_by_air)


                    if product.shipping_via == "By Ship":
                        # print("user.countryCode---->",user.countryCode)
                        # print("user.country---->",user.country)
                        price_by = models.CountryWithCurrency.objects.get(country_name = user.country)
                        price_by_ship_rate = price_by.price_by_ship
                        # print(user.countryCode, user.country, 'price_by')
                        
                        if currencyCode not in [None,'','null']:
                            if price_by.currency_code != "USD":
                                non_usd_rate = models.CurrencyConverter.objects.get(currency_code = price_by.currency_code).system_rate
                                usd_price_by_ship = float(price_by_ship_rate) / float(non_usd_rate)
                                # print(price_by_ship_rate,"----usd_price_by_ship--->",usd_price_by_ship)

                                if currencyCode != "USD":
                                    user_country_currency_rate = models.CurrencyConverter.objects.get(currency_code = price_by.currency_code).system_rate
                                    price_by_ship = float(usd_price_by_ship) * float(user_country_currency_rate)
                                    # print("DATA from here---->1")

                                else:
                                    price_by_ship = usd_price_by_ship
                                    # print("DATA from here---->2")
                                    
                            else:
                                if currencyCode != "USD":
                                    selected_currency_rate = models.CurrencyConverter.objects.get(currency_code = currencyCode).system_rate

                                    price_by_ship = float(price_by_ship_rate) * float(selected_currency_rate)
                                    # print("DATA from here---->3")

                                else:
                                    price_by_ship = price_by_ship_rate
                                    # print("DATA from here---->4")

                        else:
                            price_by_ship = price_by_ship_rate
                            # print("DATA from here---->5")

                        # print(price_by_ship, 'price_by_ship_rateprice_by_ship_rateprice_by_ship_rate')
                        per_product_cart_serializer['price_by_ship'] = round(float(price_by_ship),2)
                        # list_ship.append(price_by_ship)
                    if product.shipping_via == "By Express":
                        
                        # print(currencyCode, 'price_by')

                        if currencyCode not in [None,'','null']:
                            if price_by.currency_code != "USD":
                                non_usd_rate = models.CurrencyConverter.objects.get(currency_code = price_by.currency_code).system_rate
                                usd_price_by_express = float(price_by_express_shipping) / float(non_usd_rate)

                                if currencyCode != "USD":
                                    user_country_currency_rate = models.CurrencyConverter.objects.get(currency_code = price_by.currency_code).system_rate
                                    price_by_express = float(usd_price_by_express) * float(user_country_currency_rate)

                                else:
                                    price_by_express = usd_price_by_express
                                    
                            else:
                                if currencyCode != "USD":
                                    selected_currency_rate = models.CurrencyConverter.objects.get(currency_code = currencyCode).system_rate

                                    price_by_express = float(price_by_express_shipping) * float(selected_currency_rate)

                                else:
                                    price_by_express = price_by_express_shipping
                                    # print(price_by_air, 'price_by_air')

                        else:
                            price_by_express = price_by_express_shipping
                            # print(price_by_air, 'price_by_air tyu' )

                        
                        # print(price_by_air,'price_by_air_rate')
                        per_product_cart_serializer['price_by_express']= round(float(price_by_express),2)
                    # print(price_by_express, 'price_by_expresspricvv afaf  product', product.product.carton_length, 'carton')
                    carton_length=product.product.carton_length
                    carton_width=product.product.carton_width
                    carton_height=product.product.carton_height
                    carton_weight=product.product.carton_weight
                    quantity=product.quantity
                    # print(carton_length, 'carton_length', carton_width,'carton_width',  carton_height, 'carton_height', carton_weight,'carton_weight',  quantity, 'quantity' )
                    # print("carton_length----->",carton_length)
                    # print("carton_width----->",carton_width)
                    # print("carton_height----->",carton_height)
                    # print("carton_weight----->",carton_weight)
                    # print("quantity----->",quantity)
                    # print("price_by_air----->",price_by_air)
                    # print("price_by_ship----->",price_by_ship)
                    shipping_cost_per_product = calculate_shipping_cost(carton_length,carton_width,carton_height,carton_weight,quantity,price_by_air,price_by_ship, price_by_express)
                    # print(shipping_cost_per_product, 'shipping_cost_per_product')
                    list_air.append(shipping_cost_per_product.get('total_air_cost'))
                    list_ship.append(shipping_cost_per_product.get('total_sea_cost'))
                    list_express.append(shipping_cost_per_product.get('total_express_cost'))
                    
                    product_total = float(quantity) * float(per_product_cart_serializer.get('price'))
                    list_product_amount.append(product_total)
                    
                    per_product_cart_serializer['shipping_cost_per_product'] = shipping_cost_per_product
                    per_product_cart_serializer['product_total'] = int(round(float(product_total)))

                    cart_data_list.append(per_product_cart_serializer)
                
                total_price = math.ceil(sum(list_product_amount))
                total_air = math.ceil(sum(list_air))
                total_ship = math.ceil(sum(list_ship))
                total_express = math.ceil(sum(list_express))

                # print(total_price, total_air, total_ship)
                if promocode:
                    check_promocode = models.PromocodeDetail.objects.filter(promocode = promocode).count()
                    if check_promocode == 1:
                        get_promocode = models.PromocodeDetail.objects.get(promocode = promocode)
                        discount = get_promocode.discount
                        # print(discount, 'discount')
                        discount_price = round(int(total_price) * int(discount)/100)
                        # print(total_price, 'total_price')
                        price_after_discount = math.ceil(total_price - discount_price)


                        amount_to_paid = math.ceil(price_after_discount + total_air + total_ship + total_express)
                        amount_to_paid_with_tax = math.ceil(amount_to_paid * 1.015)
                        # print(amount_to_paid_with_tax, 'amount_to_paid_with_tax')
                        
                        res={
                            'data':cart_data_list,
                            'total_price' :f"{total_price:,}".replace(",", " "),
                            'discount_price':f"{discount_price:,}".replace(",", " "), 
                            'discount_percentage': discount, 
                            'price_after_discount': f"{price_after_discount:,}".replace(",", " "),
                            'total_air' :  f"{total_air:,}".replace(",", " "),
                            'total_ship' :  f"{total_ship:,}".replace(",", " "),
                            'total_express' :  f"{total_express:,}".replace(",", " "),
                            'amount_to_paid_view': f"{amount_to_paid:,}".replace(",", " "),
                            'amount_to_paid_with_tax_view': f"{amount_to_paid_with_tax:,}".replace(",", " "),
                            'amount_to_paid': amount_to_paid,
                            'amount_to_paid_with_tax': amount_to_paid_with_tax,
                            'coupon_verify':True
                            }
                    else:
                        res={
                            'message':'Enter valid coupon.'
                        }
                        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=406)
                else:
                    amount_to_paid = math.ceil(total_price + total_air + total_ship + total_express)
                    amount_to_paid_with_tax = math.ceil(amount_to_paid * 1.015)
                    # print(amount_to_paid_with_tax, 'amount_to_paid_with_tax')
                    
                    res={
                        'data':cart_data_list,
                        'total_price' :  f"{total_price:,}".replace(",", " "),
                        'total_air' :  f"{total_air:,}".replace(",", " "),
                        'total_ship' :  f"{total_ship:,}".replace(",", " "),
                        'total_express': f"{total_express:,}".replace(",", " "),
                        'amount_to_paid_view': f"{amount_to_paid:,}".replace(",", " "),
                        'amount_to_paid_with_tax_view': f"{amount_to_paid_with_tax:,}".replace(",", " "),
                        'amount_to_paid_with_tax': amount_to_paid_with_tax,
                        'amount_to_paid': amount_to_paid,
                        'coupon_verify':False

                        }
                
                return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)
            
            else:
                res={
                    'message':'Something Went wrong.'
                }
                return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=406)
        else:
            res={
                'message':'User not Found.'
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=406)



# @csrf_exempt
# def customer_wishlist_cart_list(request):
#     if request.method == 'POST':
#         python_data = JSONParser().parse(io.BytesIO(request.body))

#         # print("python_data=-=---->",python_data)
#         customer = python_data.get('customer')
#         flag = python_data.get('flag')
#         check_customer = models.CustomerDetail.objects.filter(id =customer).count()

#         currencyCode = python_data.get('currencyCode',None)
#         country = python_data.get('country','Egypt')
#         ip_address = python_data.get('ip_address')
#         promocode = python_data.get('promocode')

#         try:
#             if currencyCode not in [None,'','null']:
#                 country = models.CountryWithCurrency.objects.filter(currency_code = currencyCode).first().country_name
#                 # print("country--->",country)

#             elif customer:
#                 user = models.CustomerDetail.objects.get(id = customer)
#                 countryCode = user.countryCode

#                 if models.CountryWithCurrency.objects.filter(country_calling_code = countryCode).exists():
#                     country = models.CountryWithCurrency.objects.get(country_calling_code = countryCode).country_name
#                 else:
#                     if country not in [None,'','null']:
#                         country = country
#                     else:
#                         try:
#                             response = requests.get(f'https://ipapi.co/{ip_address}/json/')
#                             response = response.json()
#                             country = response.get("country_name")
#                             # print("response====>",response)

#                             if country in [None,'','null']:
#                                 country = "Egypt"

#                         except Exception as e:
#                             # print("Errroooorrr----->",e)
#                             country = "Egypt"
                        

#             else:
#                 if country in [None,'','null']:
#                     try:
#                         response = requests.get(f'https://ipapi.co/{ip_address}/json/')
#                         response = response.json()
#                         country = response.get("country_name")
#                         # print("response====>",response)

#                         if country in [None,'','null']:
#                             country = "Egypt"

#                     except Exception as e:
#                         # print("Errroooorrr----->",e)
#                         country = "Egypt"
#                 else:
#                     country = country
#         except Exception as e:
#             # print("Error-=-=-=--->",e)
#             country = 'Egypt'
            

#         if check_customer == 1:
#             user = models.CustomerDetail.objects.get(id = customer)
            
#             if flag == 'wishlist':
#                 wishlist_data = models.WishlistDetail.objects.filter(customer= customer)
#                 wishlist_serializer = WishlistDetailSerializer(wishlist_data, many=True).data

#                 res={
#                     'data':wishlist_serializer
#                 }
#                 return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)
            
#             elif flag == 'cart':
                
#                 cart_data = models.CartDetail.objects.filter(customer= customer)
#                 # cart_serializer = CartDetailSerializer(cart_data, many=True).data
#                 cart_data_list = []

#                 if not models.CountryWithCurrency.objects.filter(Q(country_calling_code = user.countryCode) | Q(country_name = user.country)).exists():
#                     country = "Egypt"
#                     for product in cart_data:
#                         price_by_air = 0
#                         price_by_ship = 0

#                         # print("herere0-0-00-302-30--->",product)
#                         per_product_cart_serializer = CartDetailSerializer(product,context = {'country':country}).data
#                         quantity=product.quantity
#                         product_total = float(quantity) * float(per_product_cart_serializer.get('price'))
#                         per_product_cart_serializer['product_total'] = int(round(float(product_total)))
                        
#                         cart_data_list.append(per_product_cart_serializer)

#                     res={
#                         'data':cart_data_list,
#                         # 'data':cart_serializer,
#                         # 'daily_price':daily_price,
#                         # 'product_total':product_total,
#                         # 'price_by_air':price_by_air,
#                         # 'price_by_ship':price_by_ship
#                         'message_en':'Cannot Place Order Outside Africa Continent',
#                         'message_fr':'Impossible de passer commande en dehors du continent africain.'
#                     }                    
#                     return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)
                
#                 price_by = models.CountryWithCurrency.objects.get(Q(country_calling_code = user.countryCode) | Q(country_name = user.country))
#                 price_by_air_rate = price_by.price_by_air
#                 price_by_ship_rate = price_by.price_by_ship

#                 print(price_by_air_rate, 'afaf', price_by_ship_rate)
               
                    


#                 total_price = 0.0
#                 cart_data_list = []
#                 list_air = []
#                 list_ship = []
#                 list_product_amount = []
#                 # count = 0
#                 for product in cart_data:
#                     price_by_air = 0
#                     price_by_ship = 0

#                     # print("herere0-0-00-302-30--->",product)
#                     per_product_cart_serializer = CartDetailSerializer(product,context = {'country':country}).data

#                     # print("per_product_cart_serializer-=-=---->",per_product_cart_serializer)
#                     total_price += float(product.variant.price)

#                     if product.shipping_via == "By Air":
#                         print(user.country, 'fasas')
#                         if user.country not in [None,'','null']:
#                             try:
#                                 country = models.CountryWithCurrency.objects.get(country_name = user.country)
#                             except:
#                                 country = models.CountryWithCurrency.objects.get(country_name = user.country)
#                             print(country.currency_code, 'country')
#                             price_by_air = country.price_by_air
#                             currency_country = models.CountryWithCurrency.objects.get(country_name = user.country)
#                             if country.currency_code != currency_country.currency_code:
#                                 if country.currency_code != "USD" and currency_country.currency_code != "USD":
#                                     print("HERE--------3")
#                                     deliver_currency_value = models.CurrencyConverter.objects.get(currency_code = country.currency_code)
#                                     if country.price_by_air not in [None,'','null'] and  deliver_currency_value.price_by_air not in [None,'','null']:
#                                         usd_price_by_air = float(country.price_by_air) / float(deliver_currency_value.system_rate)
                                        
#                                         actual_currency_value = models.CurrencyConverter.objects.get(currency_code = currency_country.currency_code)
#                                         price_by_air = float(usd_price_by_air) * float(actual_currency_value.system_rate)
                                        
#                                     else:
#                                         price_by_air = currency_country.price_by_air
                                        


#                                 elif country.currency_code == "USD" and currency_country.currency_code != "USD" :
#                                     print("HERE--------4")
#                                     actual_currency_value = models.CurrencyConverter.objects.get(currency_code = currency_country.currency_code)

#                                     if country.price_by_air not in [None,'','null']:
#                                         price_by_air = float( country.price_by_air) * float(actual_currency_value.system_rate)
#                                     else:
#                                         price_by_air = float(currency_country.price_by_air)
                                       

#                                 elif country.currency_code != "USD" and currency_country.currency_code == "USD" :
#                                     print("HERE--------5")
#                                     deliver_currency_value = models.CurrencyConverter.objects.get(currency_code = country.currency_code)

#                                     if country.price_by_air not in [None,'','null']:
#                                         price_by_air = float(country.price_by_air) / float(deliver_currency_value.system_rate)
                                        
#                                     else:
#                                         price_by_air = float(currency_country.price_by_air)
                                        

#                                 else:
#                                     print("HERE--------6")
#                                     if country.price_by_air not in [None,'','null']:
#                                         price_by_air = float(currency_country.price_by_air)
                                        
#                         per_product_cart_serializer['price_by_air']= round(float(price_by_air),2)
                            
#                     else:   
#                         print(user.country, 'user.country')
#                         if user.country not in [None,'','null']:
#                             try:
#                                 country = models.CountryWithCurrency.objects.get(country_name = user.country)
#                             except:
#                                 country = models.CountryWithCurrency.objects.get(country_name = user.country)
#                             print(country.currency_code, 'country')

#                             price_by_ship = country.price_by_ship
                            
#                             # print("models.CountryWithCurrency.objects.filter(country_name = country----->)",models.CountryWithCurrency.objects.filter(country_name = selected_country).count())
#                             currency_country = models.CountryWithCurrency.objects.get(country_name = user.country)

#                             if country.currency_code != currency_country.currency_code:

#                                 print("HERE--------2")
#                                 if country.currency_code != "USD" and currency_country.currency_code != "USD":
#                                     print("HERE--------3")
#                                     deliver_currency_value = models.CurrencyConverter.objects.get(currency_code = country.currency_code)
#                                     if country.price_by_air not in [None,'','null'] and  deliver_currency_value.price_by_air not in [None,'','null']:
#                                         usd_price_by_ship = float(country.price_by_ship) / float(deliver_currency_value.system_rate)
#                                         actual_currency_value = models.CurrencyConverter.objects.get(currency_code = currency_country.currency_code)
#                                         price_by_ship = float(usd_price_by_ship) * float(actual_currency_value.system_rate)
#                                     else:

#                                         price_by_ship = currency_country.price_by_ship


#                                 elif country.currency_code == "USD" and currency_country.currency_code != "USD" :
#                                     print("HERE--------4")
#                                     actual_currency_value = models.CurrencyConverter.objects.get(currency_code = currency_country.currency_code)

#                                     if country.price_by_ship not in [None,'','null']:
#                                         price_by_ship = float(country.price_by_ship) * float(actual_currency_value.system_rate)
#                                     else:
#                                         price_by_ship = float(currency_country.price_by_ship)


#                                 elif country.currency_code != "USD" and currency_country.currency_code == "USD" :
#                                     print("HERE--------5")
#                                     deliver_currency_value = models.CurrencyConverter.objects.get(currency_code = country.currency_code)

#                                     if country.price_by_ship not in [None,'','null']:
#                                         price_by_ship = float(country.price_by_ship) / float(deliver_currency_value.system_rate)
#                                     else:
#                                         price_by_ship = float(currency_country.price_by_ship)

#                                 else:
#                                     print("HERE--------6")
#                                     if country.price_by_ship not in [None,'','null']:
#                                         price_by_ship = float(currency_country.price_by_ship)
#                         per_product_cart_serializer['price_by_ship']= round(float(price_by_ship),2)

                            
                        

#                     # price_by_air =price_by_air
#                     # price_by_ship =price_by_ship
#                     carton_length=product.product.carton_length
#                     carton_width=product.product.carton_width
#                     carton_height=product.product.carton_height
#                     carton_weight=product.product.carton_weight
#                     quantity=product.quantity
                    
#                     print(price_by_air,price_by_ship, 'fasasf')
#                     shipping_cost_per_product = calculate_shipping_cost(carton_length,carton_width,carton_height,carton_weight,quantity,price_by_air,price_by_ship)
#                     list_air.append(shipping_cost_per_product.get('total_air_cost'))
#                     list_ship.append(shipping_cost_per_product.get('total_sea_cost'))
                    
#                     product_total = float(quantity) * float(per_product_cart_serializer.get('price'))
#                     list_product_amount.append(product_total)
                    
#                     per_product_cart_serializer['shipping_cost_per_product'] = shipping_cost_per_product
#                     per_product_cart_serializer['product_total'] = int(round(float(product_total)))

#                     cart_data_list.append(per_product_cart_serializer)
                
#                 total_price = math.ceil(sum(list_product_amount))
#                 total_air = math.ceil(sum(list_air))
#                 total_ship = math.ceil(sum(list_ship))

#                 # print(total_price, total_air, total_ship)
#                 if promocode:
#                     check_promocode = models.PromocodeDetail.objects.filter(promocode = promocode).count()
#                     if check_promocode == 1:
#                         get_promocode = models.PromocodeDetail.objects.get(promocode = promocode)
#                         discount = get_promocode.discount
#                         # print(discount, 'discount')
#                         discount_price = round(int(total_price) * int(discount)/100)
#                         # print(total_price, 'total_price')
#                         price_after_discount = math.ceil(total_price - discount_price)

#                         amount_to_paid = math.ceil(price_after_discount + total_air + total_ship)
                        
#                         res={
#                             'data':cart_data_list,
#                             'total_price' : total_price,
#                             'discount_price':discount_price, 
#                             'discount_percentage':discount, 
#                             'price_after_discount':price_after_discount,
#                             'total_air' : total_air,
#                             'total_ship' : total_ship,
#                             'amount_to_paid':amount_to_paid,
#                             'coupon_verify':True
#                             }
#                     else:
#                         res={
#                             'message':'Enter valid coupon.'
#                         }
#                         return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=406)
#                 else:
#                     amount_to_paid = math.ceil(total_price + total_air + total_ship)

#                     res={
#                         'data':cart_data_list,
#                         'total_price' : total_price,
#                         'total_air' : total_air,
#                         'total_ship' : total_ship,
#                         'amount_to_paid':amount_to_paid,
#                         'coupon_verify':False

#                         }
                
#                 return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)
            
#             else:
#                 res={
#                     'message':'Something Went wrong.'
#                 }
#                 return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=406)
#         else:
#             res={
#                 'message':'User not Found.'
#             }
#             return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=406)


@csrf_exempt
def customer_cart_check(request):
    if request.method == 'POST':
        python_data = JSONParser().parse(io.BytesIO(request.body))
        customer  = python_data.get('customer')
        
        all_product_data = list(set(models.CartDetail.objects.filter(customer= customer).values_list('product', flat=True)))
        reason_data = []
        for product in all_product_data:
            get_minimun_qnt = int(models.ProductDetail.objects.filter(id = product).values_list('min_order_quantity', flat=True)[0])
            product_name = models.ProductDetail.objects.filter(id = product).values_list('product_name', flat=True)[0]
            # print(get_minimun_qnt,product, 'get_minimun_qnt')

            quantity_get = list(models.CartDetail.objects.filter(customer= customer, product = product).values_list('quantity', flat=True))
            total_quantity = sum(list(map(int, quantity_get)))
           

            if get_minimun_qnt > total_quantity:
                add_quantity = get_minimun_qnt - total_quantity
                # print(add_quantity, product)
                product_name = product_name[:15] + '...' if len(product_name) > 15 else product_name


                reason_data.append(product_name)
        if reason_data != []:
            final_reason = ', '.join(map(str, reason_data)) 
            message = f'You need to add more quantity of “{final_reason}” products to your cart before proceeding to payment.'
            status = 406
            res={
                'message':message,
                'flag':False
            }
        else:
            status=200
            res={
                'flag':True
            }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=status)

@csrf_exempt
def order_create(request):
    if request.method == 'POST':
        python_data = JSONParser().parse(io.BytesIO(request.body))
        
        customer  = python_data.get('customer')
        customer_address = python_data.get('customer_address')
        payment_type = python_data.get('payment_type').lower()
        payment_id = python_data.get('payment_id')
        air_shipping_price = python_data.get('air_shipping_price')
        ship_shipping_price = python_data.get('ship_shipping_price')
        express_shipping_price = python_data.get('express_shipping_price')
        
        total_price = python_data.get('total_price')
        amount = python_data.get('total_price')
        products = python_data.get('products')
        network = python_data.get("network_code") 
        currency = python_data.get("currency")
        promocode = python_data.get("promocode")
        original_total_amount = python_data.get("original_total_amount")
        original_amount_paid = python_data.get("original_amount_paid")
        discount_price = python_data.get("discount_price", 0)
        cargo = python_data.get("cargo")
        

        
        print(python_data, 'python_datapython_data')


        now = datetime.now()
        date_time = now.strftime('%Y-%m-%d, %H:%M:%S')
        current_date = now.strftime('%Y%m%d')
        current_date_data = datetime.strptime(current_date, '%Y%m%d').date()

        expire_at = now + timedelta(minutes=15)

        # total_price = 20

        get_customer = models.CustomerDetail.objects.get(id = customer)
        get_email = get_customer.email
        mobileNumber = get_customer.mobileNumber
        tax_price = 0
        if payment_type not in ['cash','Cash','bank','Bank','Bank Transfer','bank transfer', 'Inquiry', 'inquiry']:
            print("payment_type----0-0-0000>",payment_type)
            check_gateway = models.MoneyNetwork.objects.get(value = network)
            if check_gateway.label.startswith(('Orange Money', 'Wave')):
                price = math.ceil(total_price * 1.015)
                tax_price = math.ceil(price - total_price) 
                total_price = math.ceil(price)
                result = APIDTSClient.cash_in(total_price, mobileNumber, network, currency)
                # print(result, 'result')
                if result.get('error'):
                    res={
                        'message':f'{result.get("details")}'
                    }
                    return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=406)
            else:
                tax_price = 0

            payment_id = result["transaction"]["id"]
            reference_id = result["transaction"]["reference_id"]
            fee_amount = result["transaction"]["fee_amount"]
            net_amount = result["transaction"]["net_amount"]
            total_amount = result["transaction"]["total_amount"]
            status = result["transaction"]["status"]
            payment_url = result["transaction"]["payment_url"]
          
        print(tax_price, 'tax_price', total_price, 'total_price')
        
        digits = "abcdefghjiklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
        random_data = ""
       
        if currency == "USD":
            currency_symbol = "$"
            currency_name = "USD"
        else:
            print("currency----->",currency)
            get_currency = models.CountryWithCurrency.objects.filter(currency_code = currency).first()
            currency_symbol = get_currency.currency_symbol 
            currency_name = currency
       
        for i in range(4) :
            random_data += digits[math.floor(random.random() * 52)]
        
        order_number = "ord-diaba-"+ current_date +'-'+ random_data

        if promocode:
            promocode = models.PromocodeDetail.objects.get(promocode = promocode)
            promocode_id = promocode.id
        else:
            promocode_id = None

        order = models.OrderDetail.objects.create(
            customer_id = customer,
            customer_address_id = customer_address,
            order_id = order_number,
            promocode_id = promocode_id,
            cargo_id = cargo,
            payment_type = payment_type,
            payment_id = payment_id,
            order_status = 'pending',
            air_shipping_price = air_shipping_price,
            ship_shipping_price = ship_shipping_price,
            express_shipping_price = express_shipping_price,
            currency = currency_symbol,
            currency_name = currency_name,
            original_total_amount = original_total_amount,
            original_amount_paid = original_amount_paid,
            discount_price = discount_price,
            total_price = total_price,
            tax_price = tax_price,
            # created_at = date_time,
            expire_at = expire_at,
            status = 'pending',
        )
        order.save()
        customer_mobile = order.customer.mobileNumber
        # print(customer_mobile, 'customer_mobile')

        order_id = order.id


        for product in products:
            print("product---->",product)
            shipping_via = product.get('shipping_via')
            variant = product.get('variant')
            quantity = int(product.get('quantity'))
            price = float(product.get('price'))
            product_shipping_price = float(product.get('product_shipping_price', None))
            if product_shipping_price != None:
                product_shipping_price = float(product_shipping_price)
            # print(variant, 'variantvariantvariant')
            total_price = quantity * price
            # check_cart = models.CartDetail.objects.filter(customer = customer, variant = variant, quantity = quantity).count()
            # if check_cart == 1:
            #     cart_data = models.CartDetail.objects.get(customer = customer, variant = variant, quantity = quantity)
            #     cart_data.delete()
                

            variant_data = models.ProductModelVariant.objects.get(id = variant)
            # print("variant_data---->",variant_data)
            # print("variant_data.product---->",variant_data.product)
            # print("variant_data.product.id---->",variant_data.product.id)
            product_id = variant_data.model.product.id

            create_order = models.ProductOrderDetail.objects.create(
                order_id = order_id,
                product_id = product_id,
                variant_id = variant_data.id,
                quantity = quantity,
                price = price,
                total_price = total_price,
                currency = currency_symbol,
                currency_name = currency_name,
                product_shipping_price = product_shipping_price,
                vendor_status = "pending",
                status = 'pending',
                # created_at = now,
                shipping_via = shipping_via
            )
            create_order.save()
            product_variant = create_order.id
            create_tracking = models.OrderTracking.objects.create(
                order_id = order_id,
                variant_id = product_variant,
                status = "pending",
                created_at  = date_time
            ).save()

            create_vendor_tracking = models.VendorOrderTracking.objects.create(
                order_id = order_id,
                variant_id = product_variant,
                status = "pending",
                created_at  = date_time
            ).save()

        
        ## for the testing purpose we take 1 XOF
        # amount = float(total_price) + float(shipping_price)
        
        ### payment Gateway
        if payment_type not in ['cash','Cash','bank','Bank','Bank Transfer','bank transfer', 'Inquiry', 'inquiry']:
            phone = customer_mobile
            network = python_data.get("network_code")  
            currency = python_data.get("currency")
           

            create_transaction = models.OrderTransaction.objects.create(
                order_id  = order_id,
                customer_id = customer,
                currency= currency_name,
                payment_type = payment_type,
                payment_id = payment_id,
                reference_id = reference_id,
                fee_amount = fee_amount,
                net_amount = net_amount,
                total_amount = total_amount,
                tax_price = tax_price,
                status = status,
                created_at = date_time,
            ).save()
            order.payment_id = payment_id
            order.save()

            
        else:
            # print('Check ', 'asfasf')
            payment_id = "cash-" + current_date +'-'+ random_data
            reference_id = None
            fee_amount = None
            net_amount = None
            total_amount = amount
            status = 'pending'
            payment_url = None
            
            if payment_type not in ['Inquiry', 'inquiry']:

                create_transaction = models.OrderTransaction.objects.create(
                    order_id  = order_id,
                    customer_id = customer,
                    currency= currency_name,
                    payment_type = payment_type,
                    payment_id = payment_id,
                    reference_id = reference_id,
                    fee_amount = fee_amount,
                    net_amount = net_amount,
                    cash_status = False,
                    tax_price = tax_price, 
                    total_amount = total_amount,
                    status = status,
                    created_at = date_time,
                )

            cart_data = models.CartDetail.objects.filter(customer = customer)
            cart_data.delete()
            
        promocode_name = None
        promocode_discount = None

        if order.promocode != None:
            promocode_data = models.PromocodeDetail.objects.get(id = order.promocode.id)
            # remaining_promocode = int(promocode_data.remaining_promocode) - 1
            # promocode_data.remaining_promocode = remaining_promocode
            # promocode_data.save()
            promocode_name = promocode_data.promocode
            promocode_discount = promocode_data.discount



            promocode_track = models.PromocodeTracking.objects.create(
                order_id = order_id,
                promocode_id = order.promocode.id,
                customer_id = order.customer.id,
                created_at = date_time
            ).save()

            promocode = order.promocode.id
            # order_id = order_id

            commission_percentage = int(order.promocode.influencer.commission)
            original_currency = currency_name
            original_total_amount = original_total_amount
            original_total_amount = int(original_total_amount.replace(' ', '').strip())
            original_amount_paid = original_amount_paid
            original_amount_paid = int(original_amount_paid.replace(' ', '').strip())
            if original_currency == "XOF":
                converted_currency = original_currency
                converted_total_amount = original_total_amount
                converted_amount_paid = int(original_amount_paid)
            else:
                get_currency_rate = models.CurrencyConverter.objects.filter(currency_code = "XOF").values_list('system_rate', flat=True)[0]
                
                converted_currency = "XOF"
                converted_total_amount = float(original_total_amount)*float(get_currency_rate)
                converted_amount_paid = int(float(original_amount_paid)*float(get_currency_rate))
            
            total_commission = round((converted_amount_paid*commission_percentage)/100)

            create_commission = models.PromocodeCommissionDetail.objects.create(
                order_id = order_id,
                promocode_id = promocode,
                original_currency = original_currency,
                original_total_amount = original_total_amount,
                original_amount_paid = original_amount_paid,
                converted_currency = converted_currency,
                converted_total_amount = converted_total_amount,
                converted_amount_paid = converted_amount_paid,
                commission_percentage = commission_percentage,
                total_commission = total_commission,
                created_at = date_time
            ).save()

        # order_list_product
        order_data = models.ProductOrderDetail.objects.filter(order_id = order_id)
        order_list_product = ProductOrderDetailOrderSerializer(order_data,many=True).data

        user = get_customer.name
        get_address = models.CustomerAddressDetail.objects.get(id = customer_address)
        street_address = get_address.street_address
        city = get_address.city
        country = get_address.country
        
        if int(discount_price.replace(' ', '').strip())== 0:
            discount_price = None
        # print("STARTING OF EMAIL.......", discount_price)
        
        context = {
            'user': user, 
            'order_id': order_number,
            'date': date_time,
            'customer_name': user,
            'street_address' : street_address,
            'city' : city,
            'country' : country,
            'order_list_product' : order_list_product,
            'subtotal': original_total_amount,
            'discount_price': discount_price,
            'promocode_name':promocode_name,
            'promocode_discount':promocode_discount,
            'ship_shipping_price': ship_shipping_price,
            'air_shipping_price': air_shipping_price,
            'express_shipping_price':express_shipping_price,
            'total_price':amount,
            'currency_name':currency_name,
            'payment_type':payment_type,
            'customer_id':get_customer.id,
            'order_id':order_id,
            'get_email':get_email
        }

        if payment_type  in ['cash','Cash','bank','Bank','Bank Transfer','bank transfer']:
        
            order_number = order.order_id
            html_string = render_to_string("order_invoice.html", context)

            pdf_bytes = HTML(string=html_string).write_pdf()
            order.invoice.save(f"{order_number}.pdf",ContentFile(pdf_bytes),save=True)

            get_email = context['get_email']
            # print(order_id, get_email)
            if get_email != None and get_email != "null" and get_email != '':
                try:
                    htmlgen = get_template("order_confirm.html").render(context)
                    # print(htmlgen, 'htmlgen')

                    send_mail(
                        subject='Order Confirmation',
                        message='Your order has been confirmed successfully.',
                        from_email=settings.DEFAULT_FROM_EMAIL,  # or EMAIL_HOST_USER
                        recipient_list=[get_email],
                        fail_silently=False,
                        html_message=htmlgen
                    )

                except Exception as e:
                    print("error:..............",e)
        
            if payment_type in ['bank','Bank','Bank Transfer','bank transfer']:
                print("BANK in hererer")
                bank_id = python_data.get('bank_id')
                print("bank_id--------->",bank_id)
                get_bank_details = models.CountryWiseBankDetail.objects.filter(id = bank_id).first()
                if get_bank_details:
                    print("get_bank_details=====>",get_bank_details)
                    holder_name = get_bank_details.holder_name
                    bank_name = get_bank_details.bank_name
                    account_number = get_bank_details.account_number
                    branch_name = get_bank_details.branch_name
                    branch_code = get_bank_details.branch_code
                    
                    models.OrderPaymentReceivingBankDetail.objects.create(
                        order_id = order.id,
                        holder_name = holder_name,
                        bank_name = bank_name,
                        account_number = account_number,
                        branch_name = branch_name,
                        branch_code = branch_code,
                    )
        if payment_type in ['Inquiry', 'inquiry']:
            payment_type = 'cash'

        res={
            'message':"Order Create Successfully.",
            'payment_type':payment_type,
            'payment_url':payment_url,
            'txn_id':reference_id,
            'context':context
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)


@csrf_exempt
def order_create_wave_orange(request):
    if request.method == 'POST':
        python_data = JSONParser().parse(io.BytesIO(request.body))
        
        customer  = python_data.get('customer')
        customer_address = python_data.get('customer_address')
        payment_type = python_data.get('payment_type').lower()
        payment_id = python_data.get('payment_id')
        air_shipping_price = python_data.get('air_shipping_price')
        ship_shipping_price = python_data.get('ship_shipping_price')
        express_shipping_price = python_data.get('express_shipping_price')
        
        total_price = python_data.get('total_price')
        amount = python_data.get('total_price')
        products = python_data.get('products')
        network = python_data.get("network_code") 
        currency = python_data.get("currency")
        promocode = python_data.get("promocode")
        original_total_amount = python_data.get("original_total_amount")
        original_amount_paid = python_data.get("original_amount_paid")
        discount_price = python_data.get("discount_price", 0)
        cargo = python_data.get("cargo")
        reference_id = python_data.get("reference_id")
        

        
        print(python_data, 'python_datapython_data')


        now = datetime.now()
        date_time = now.strftime('%Y-%m-%d, %H:%M:%S')
        current_date = now.strftime('%Y%m%d')
        current_date_data = datetime.strptime(current_date, '%Y%m%d').date()

        expire_at = now + timedelta(minutes=15)

        # total_price = 20

        get_customer = models.CustomerDetail.objects.get(id = customer)
        get_email = get_customer.email
        mobileNumber = get_customer.mobileNumber
        tax_price = 0
        # if payment_type not in ['cash','Cash','bank','Bank','Bank Transfer','bank transfer']:
        #     print("payment_type----0-0-0000>",payment_type)
        #     check_gateway = models.MoneyNetwork.objects.get(value = network)
        #     if check_gateway.label.startswith(('Orange Money', 'Wave')):
        #         price = math.ceil(total_price * 1.015)
        #         tax_price = math.ceil(price - total_price) 
        #         total_price = math.ceil(price)
        #         result = APIDTSClient.cash_in(total_price, mobileNumber, network, currency)
        #         # print(result, 'result')
        #         if result.get('error'):
        #             res={
        #                 'message':f'{result.get("details")}'
        #             }
        #             return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=406)
        #     else:
        #         tax_price = 0

        #     payment_id = result["transaction"]["id"]
        #     reference_id = result["transaction"]["reference_id"]
        #     fee_amount = result["transaction"]["fee_amount"]
        #     net_amount = result["transaction"]["net_amount"]
        #     total_amount = result["transaction"]["total_amount"]
        #     status = result["transaction"]["status"]
        #     payment_url = result["transaction"]["payment_url"]
          
        # print(tax_price, 'tax_price', total_price, 'total_price')
        fee_amount = None
        net_amount = None
        payment_url = None
        payment_id = reference_id

        digits = "abcdefghjiklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
        random_data = ""
       
        if currency == "USD":
            currency_symbol = "$"
            currency_name = "USD"
        else:
            get_currency = models.CountryWithCurrency.objects.filter(currency_code = currency).first()
            currency_symbol = get_currency.currency_symbol 
            currency_name = currency
       
        for i in range(4) :
            random_data += digits[math.floor(random.random() * 52)]
        
        order_number = "ord-diaba-"+ current_date +'-'+ random_data

        if promocode:
            promocode = models.PromocodeDetail.objects.get(promocode = promocode)
            promocode_id = promocode.id
        else:
            promocode_id = None

        order = models.OrderDetail.objects.create(
            customer_id = customer,
            customer_address_id = customer_address,
            order_id = order_number,
            promocode_id = promocode_id,
            cargo_id = cargo,
            payment_type = payment_type,
            payment_id = payment_id,
            order_status = 'pending',
            air_shipping_price = air_shipping_price,
            ship_shipping_price = ship_shipping_price,
            express_shipping_price = express_shipping_price,
            currency = currency_symbol,
            currency_name = currency_name,
            original_total_amount = original_total_amount,
            original_amount_paid = original_amount_paid,
            discount_price = discount_price,
            total_price = total_price,
            tax_price = tax_price,
            # created_at = date_time,
            expire_at = expire_at,
            status = 'completed',
        )
        order.save()
        customer_mobile = order.customer.mobileNumber
        # print(customer_mobile, 'customer_mobile')

        order_id = order.id


        for product in products:
            print("product---->",product)
            shipping_via = product.get('shipping_via')
            variant = product.get('variant')
            quantity = int(product.get('quantity'))
            price = float(product.get('price'))
            product_shipping_price = float(product.get('product_shipping_price', None))
            if product_shipping_price != None:
                product_shipping_price = float(product_shipping_price)
            total_price = quantity * price
                

            variant_data = models.ProductModelVariant.objects.get(id = variant)
            product_id = variant_data.model.product.id

            create_order = models.ProductOrderDetail.objects.create(
                order_id = order_id,
                product_id = product_id,
                variant_id = variant_data.id,
                quantity = quantity,
                price = price,
                total_price = total_price,
                currency = currency_symbol,
                currency_name = currency_name,
                product_shipping_price = product_shipping_price,
                vendor_status = "pending",
                status = 'pending',
                # created_at = now,
                shipping_via = shipping_via
            )
            create_order.save()
            product_variant = create_order.id
            create_tracking = models.OrderTracking.objects.create(
                order_id = order_id,
                variant_id = product_variant,
                status = "pending",
                created_at  = date_time
            ).save()

            create_vendor_tracking = models.VendorOrderTracking.objects.create(
                order_id = order_id,
                variant_id = product_variant,
                status = "pending",
                created_at  = date_time
            ).save()

        
        ## for the testing purpose we take 1 XOF
        # amount = float(total_price) + float(shipping_price)
        
        ### payment Gateway
       
        phone = customer_mobile
        network = python_data.get("network_code")  
        currency = python_data.get("currency")
        

        create_transaction = models.OrderTransaction.objects.create(
            order_id  = order_id,
            customer_id = customer,
            currency= currency_name,
            payment_type = payment_type,
            payment_id = payment_id,
            reference_id = reference_id,
            fee_amount = fee_amount,
            net_amount = net_amount,
            total_amount = original_total_amount,
            tax_price = tax_price,
            status = 'completed',
            created_at = date_time,
        ).save()
        order.payment_id = payment_id
        order.save()

        cart_data = models.CartDetail.objects.filter(customer = customer)
        cart_data.delete()
            
        promocode_name = None
        promocode_discount = None

        if order.promocode != None:
            promocode_data = models.PromocodeDetail.objects.get(id = order.promocode.id)
            promocode_name = promocode_data.promocode
            promocode_discount = promocode_data.discount



            promocode_track = models.PromocodeTracking.objects.create(
                order_id = order_id,
                promocode_id = order.promocode.id,
                customer_id = order.customer.id,
                created_at = date_time
            ).save()

            promocode = order.promocode.id
           
            commission_percentage = int(order.promocode.influencer.commission)
            original_currency = currency_name
            original_total_amount = original_total_amount
            original_total_amount = int(original_total_amount.replace(' ', '').strip())
            original_amount_paid = original_amount_paid
            original_amount_paid = int(original_amount_paid.replace(' ', '').strip())
            if original_currency == "XOF":
                converted_currency = original_currency
                converted_total_amount = original_total_amount
                converted_amount_paid = int(original_amount_paid)
            else:
                get_currency_rate = models.CurrencyConverter.objects.filter(currency_code = "XOF").values_list('system_rate', flat=True)[0]
                
                converted_currency = "XOF"
                converted_total_amount = float(original_total_amount)*float(get_currency_rate)
                converted_amount_paid = int(float(original_amount_paid)*float(get_currency_rate))
            
            total_commission = round((converted_amount_paid*commission_percentage)/100)

            create_commission = models.PromocodeCommissionDetail.objects.create(
                order_id = order_id,
                promocode_id = promocode,
                original_currency = original_currency,
                original_total_amount = original_total_amount,
                original_amount_paid = original_amount_paid,
                converted_currency = converted_currency,
                converted_total_amount = converted_total_amount,
                converted_amount_paid = converted_amount_paid,
                commission_percentage = commission_percentage,
                total_commission = total_commission,
                created_at = date_time
            ).save()

        # order_list_product
        order_data = models.ProductOrderDetail.objects.filter(order_id = order_id)
        order_list_product = ProductOrderDetailOrderSerializer(order_data,many=True).data

        user = get_customer.name
        get_address = models.CustomerAddressDetail.objects.get(id = customer_address)
        street_address = get_address.street_address
        city = get_address.city
        country = get_address.country
        
        if int(discount_price.replace(' ', '').strip())== 0:
            discount_price = None
        # print("STARTING OF EMAIL.......", discount_price)
        
        context = {
            'user': user, 
            'order_id': order_number,
            'date': date_time,
            'customer_name': user,
            'street_address' : street_address,
            'city' : city,
            'country' : country,
            'order_list_product' : order_list_product,
            'subtotal': original_total_amount,
            'discount_price': discount_price,
            'promocode_name':promocode_name,
            'promocode_discount':promocode_discount,
            'ship_shipping_price': ship_shipping_price,
            'air_shipping_price': air_shipping_price,
            'express_shipping_price':express_shipping_price,
            'total_price':amount,
            'currency_name':currency_name,
            'payment_type':payment_type,
            'customer_id':get_customer.id,
            'order_id':order_id,
            'get_email':get_email
        }

        if payment_type  in ['cash','Cash','bank','Bank','Bank Transfer','bank transfer']:
        
            order_number = order.order_id
            html_string = render_to_string("order_invoice.html", context)

            pdf_bytes = HTML(string=html_string).write_pdf()
            order.invoice.save(f"{order_number}.pdf",ContentFile(pdf_bytes),save=True)

            get_email = context['get_email']
            # print(order_id, get_email)
            if get_email != None and get_email != "null" and get_email != '':
                try:
                    htmlgen = get_template("order_confirm.html").render(context)
                    # print(htmlgen, 'htmlgen')

                    send_mail(
                        subject='Order Confirmation',
                        message='Your order has been confirmed successfully.',
                        from_email=settings.DEFAULT_FROM_EMAIL,  # or EMAIL_HOST_USER
                        recipient_list=[get_email],
                        fail_silently=False,
                        html_message=htmlgen
                    )

                except Exception as e:
                    print("error:..............",e)
        
            if payment_type in ['bank','Bank','Bank Transfer','bank transfer']:
                print("BANK in hererer")
                bank_id = python_data.get('bank_id')
                print("bank_id--------->",bank_id)
                get_bank_details = models.CountryWiseBankDetail.objects.filter(id = bank_id).first()
                if get_bank_details:
                    print("get_bank_details=====>",get_bank_details)
                    holder_name = get_bank_details.holder_name
                    bank_name = get_bank_details.bank_name
                    account_number = get_bank_details.account_number
                    branch_name = get_bank_details.branch_name
                    branch_code = get_bank_details.branch_code
                    
                    models.OrderPaymentReceivingBankDetail.objects.create(
                        order_id = order.id,
                        holder_name = holder_name,
                        bank_name = bank_name,
                        account_number = account_number,
                        branch_name = branch_name,
                        branch_code = branch_code,
                    )


        res={
            'message':"Order Create Successfully.",
            'payment_type':payment_type,
            # 'payment_url':payment_url,
            'txn_id':reference_id,
            'context':context
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)



@csrf_exempt
def inquiry_order_create(request):
    if request.method == 'POST':
        python_data = JSONParser().parse(io.BytesIO(request.body))

        print("python_data--->",python_data)
        
        customer  = python_data.get('customer')
        customer_address = python_data.get('customer_address')
        payment_type = 'inquiry'
        payment_id = python_data.get('payment_id')
        air_shipping_price = python_data.get('air_shipping_price')
        ship_shipping_price = python_data.get('ship_shipping_price')
        express_shipping_price = python_data.get('express_shipping_price')
        
        total_price = python_data.get('total_price')
        amount = python_data.get('total_price')
        products = python_data.get('products')
        network = python_data.get("network_code") 
        currency = python_data.get("currency")
        promocode = python_data.get("promocode")
        original_total_amount = python_data.get("original_total_amount")
        original_amount_paid = python_data.get("original_amount_paid")
        discount_price = python_data.get("discount_price", 0)
        cargo = python_data.get("cargo")

        now = datetime.now()
        date_time = now.strftime('%Y-%m-%d, %H:%M:%S')
        current_date = now.strftime('%Y%m%d')
        current_date_data = datetime.strptime(current_date, '%Y%m%d').date()

        expire_at = now + timedelta(minutes=15)

        print("customer_address--->",customer_address)
        # total_price = 20

        get_customer = models.CustomerDetail.objects.get(id = customer)
        get_email = get_customer.email
        mobileNumber = get_customer.mobileNumber
        tax_price = 0

        digits = "abcdefghjiklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
        random_data = ""
       
        if currency == "USD":
            currency_symbol = "$"
            currency_name = "USD"
        else:
            get_currency = models.CountryWithCurrency.objects.filter(currency_code = currency).first()
            currency_symbol = get_currency.currency_symbol 
            currency_name = currency
       
        for i in range(4) :
            random_data += digits[math.floor(random.random() * 52)]
        
        order_number = "inq-diaba-"+ current_date +'-'+ random_data

       
        order = models.OrderDetail.objects.create(
            customer_id = customer,
            customer_address_id = customer_address,
            order_id = order_number,
            cargo_id = cargo,
            payment_type = payment_type,
            payment_id = payment_id,
            order_status = 'inquiry',
            air_shipping_price = air_shipping_price,
            ship_shipping_price = ship_shipping_price,
            express_shipping_price = express_shipping_price,
            currency = currency_symbol,
            currency_name = currency_name,
            original_total_amount = original_total_amount,
            original_amount_paid = original_amount_paid,
            discount_price = discount_price,
            total_price = total_price,
            tax_price = tax_price,
            # created_at = now,
            expire_at = expire_at,
            status = 'inquiry',
        )
        order.save()
        customer_mobile = order.customer.mobileNumber
        # print(customer_mobile, 'customer_mobile')

        order_id = order.id


        for product in products:
            print("product---->",product)
            shipping_via = product.get('shipping_via')
            variant = product.get('variant')
            quantity = int(product.get('quantity'))
            price = float(product.get('price'))
            product_shipping_price = float(product.get('product_shipping_price', None))
            if product_shipping_price != None:
                product_shipping_price = float(product_shipping_price)
            total_price = quantity * price
            
            variant_data = models.ProductModelVariant.objects.get(id = variant)
            product_id = variant_data.model.product.id

            create_order = models.ProductOrderDetail.objects.create(
                order_id = order_id,
                product_id = product_id,
                variant_id = variant_data.id,
                quantity = quantity,
                price = price,
                total_price = total_price,
                currency = currency_symbol,
                currency_name = currency_name,
                product_shipping_price = product_shipping_price,
                vendor_status = "pending",
                status = 'inquiry',
                # created_at = now,
                shipping_via = shipping_via
            )
            create_order.save()
            product_variant = create_order.id
            
            # print('Check ', 'asfasf')
            payment_id = "cash-" + current_date +'-'+ random_data
            reference_id = None
            fee_amount = None
            net_amount = None
            total_amount = amount
            status = 'pending'
            payment_url = None    
        
            cart_data = models.CartDetail.objects.filter(customer = customer)
            cart_data.delete()
            
        promocode_name = None
        promocode_discount = None

        order_data = models.ProductOrderDetail.objects.filter(order_id = order_id)
        order_list_product = ProductOrderDetailOrderSerializer(order_data,many=True).data

        user = get_customer.name
        # get_address = models.CustomerAddressDetail.objects.get(id = customer_address)
        # street_address = get_address.street_address
        # city = get_address.city
        country = get_customer.country
        
        if int(discount_price.replace(' ', '').strip())== 0:
            discount_price = None
        # print("STARTING OF EMAIL.......", discount_price)
        
        context = {
            'user': user, 
            'order_id': order_number,
            'date': date_time,
            'customer_name': user,
            # 'street_address' : street_address,
            # 'city' : city,
            'country' : country,
            'order_list_product' : order_list_product,
            'subtotal': original_total_amount,
            'discount_price': discount_price,
            'promocode_name':promocode_name,
            'promocode_discount':promocode_discount,
            'ship_shipping_price': ship_shipping_price,
            'air_shipping_price': air_shipping_price,
            'express_shipping_price':express_shipping_price,
            'total_price':amount,
            'currency_name':currency_name,
            'payment_type':payment_type,
            'customer_id':get_customer.id,
            'order_id':order_id,
            'get_email':get_email
        }

        res={
            'message':"Order inquiry created successfully.",
            'payment_type':payment_type,
            'payment_url':payment_url,
            'txn_id':reference_id,
            'context':context
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)




@csrf_exempt
def payment_callback(request):
    python_data = JSONParser().parse(io.BytesIO(request.body))
    context = python_data.get('context')
    txn_id = python_data.get('txnId')

    # print(python_data, 'status')
    result = APIDTSClient.check_status(txn_id)
    status = result["transaction"]["status"]
    reference_id = txn_id
    now = datetime.now()
    date_time = now.strftime('%Y-%m-%d, %H:%M:%S')
    print(status, 'statusstatus')
    if status == 'completed':
        get_transaction = models.OrderTransaction.objects.get(reference_id = reference_id)
        get_transaction.status = status
        get_transaction.save()

        get_order = models.OrderDetail.objects.get(id = get_transaction.order.id)
        get_order.status = status
        get_order.save()

        order_id = get_transaction.order.id
        get_customer = get_transaction.order.customer.id
        if get_transaction.order.promocode != None:
            get_promocode = get_transaction.order.promocode.id
            create_tracking = models.PromocodeTracking.objects.create(
                order_id = order_id,
                promocode_id = get_promocode,
                customer_id = get_customer,
                created_at = date_time
            ).save()

        order_id = context['order_id']
        order = models.OrderDetail.objects.get(id = order_id)
        order_number = order.order_id
        html_string = render_to_string("order_invoice.html", context)

        pdf_bytes = HTML(string=html_string).write_pdf()
        order.invoice.save(f"{order_number}.pdf",ContentFile(pdf_bytes),save=True)

        get_email = context['get_email']
        # print(order_id, get_email)
        if get_email != None and get_email != "null" and get_email != '':
            try:
                htmlgen = get_template("order_confirm.html").render(context)
                # print(htmlgen, 'htmlgen')

                send_mail(
                    subject='Order Confirmation',
                    message='Your order has been confirmed successfully.',
                    from_email=settings.DEFAULT_FROM_EMAIL,  # or EMAIL_HOST_USER
                    recipient_list=[get_email],
                    fail_silently=False,
                    html_message=htmlgen
                )

            except Exception as e:
                print("error:..............",e)
        

        
        # print(get_transaction, 'get_transaction')
        cart_data = models.CartDetail.objects.filter(customer = get_transaction.customer.id)
        cart_data.delete()

        res={
            'status': status,
            'message':"Transaction Create Successfully.",
            
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)
    else:
        # try:
        #     get_transaction = models.OrderTransaction.objects.get(reference_id = reference_id)
        #     get_order = models.OrderDetail.objects.filter(id = get_transaction.order.id)
        #     print(get_order, 'get_order')
        #     get_order.delete()
        # except: 
        #     pass
        
        if status == "pending":
            status = "failed" 

        get_transaction = models.OrderTransaction.objects.get(reference_id = reference_id)
        get_transaction.status = status
        get_transaction.save()

        get_order = models.OrderDetail.objects.get(id = get_transaction.order.id)
        get_order.order_status = status
        get_order.status = status
        get_order.save()



        res={
            'status': status,
            'message':"Transaction failed.",
            
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 406)


@csrf_exempt
def cash_status_update(request):
    if request.method == 'POST':
        python_data = JSONParser().parse(io.BytesIO(request.body))
        transaction  = python_data.get('transaction')
        print(python_data, 'python_data')

        if python_data.get('cash_status') == 'True':

            order = models.OrderTransaction.objects.get(id = transaction)
            order.cash_status = python_data.get('cash_status', order.cash_status)
            order.status = "completed"
            order.save()
            print(123)

            get_order = models.OrderDetail.objects.get(id = order.order.id)
            get_order.status = "completed"
            get_order.save()

        res={
            'message':"Status Update successfully."
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)



# @csrf_exempt
# def all_order_list_admin(request):
#     if request.method == 'POST':
#         python_data = JSONParser().parse(io.BytesIO(request.body))
        
#         status = python_data.get('status', 'completed')
#         page_number = int(python_data.get('page_number', 1))
#         row_size = int(python_data.get('row_data', 10))
#         last_row = row_size * page_number
#         first_row = last_row - row_size

#         transaction_count = models.OrderTransaction.objects.filter(status = status).count()
#         all_transaction_list = models.OrderTransaction.objects.filter(status = status).order_by('-id')[first_row:last_row]
#         transaction_serialiser = OrderTransactionSerializer(all_transaction_list, many=True).data

#         res={
#             'data':transaction_serialiser
#         }
#         return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)



# @csrf_exempt
# def all_order_list_admin(request):
#     if request.method == 'POST':
#         order_list = models.OrderDetail.objects.all().order_by('-id')
#         order_serializer = OrderDetailSerializer(order_list, many=True).data
    
#         res={
#             'data':order_serializer
#         }
#         return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)

@csrf_exempt
def all_order_list_admin(request):
    if request.method == 'POST':
        python_data = JSONParser().parse(io.BytesIO(request.body))
        
        order_status = python_data.get('order_status', 'completed')
        search_key = python_data.get('search_key', "").strip()
        
        created_at_from = python_data.get('created_at_from')
        created_at_to = python_data.get('created_at_to')
        shipping_via = python_data.get('shipping_via')
        payment_type = python_data.get('payment_type')

        sort_by = python_data.get('sort_by')
        sort_order = python_data.get('sort_order')

        page_number = int(python_data.get('page_number', 1))
        row_size = int(python_data.get('row_data', 10))

        last_row = row_size * page_number
        first_row = last_row - row_size

        print(python_data, 'python_data')
        
        if order_status == "Confirm":
            status = "completed"
            order_status = "pending"
            queryset = models.OrderDetail.objects.filter(status = status, order_status=order_status)
        elif order_status == "pending":
            queryset = models.OrderDetail.objects.filter(status = "pending", payment_type__in = ["cash","bank transfer"], order_status=order_status)
        else:
            queryset = models.OrderDetail.objects.filter(order_status=order_status)

        query_filter = Q()

        if search_key:
            if any(char in search_key for char in ["+", " "]):
                split_search_key = search_key.split() 

                print("split_search_key----->", split_search_key)

                search_countryCode = split_search_key[0]
                search_mobileNumber = split_search_key[1]

                query_filter |= Q(customer__countryCode__icontains=search_countryCode)
                query_filter &= Q(customer__mobileNumber__icontains=search_mobileNumber)
            else:
                query_filter |= Q(customer__countryCode__icontains=search_key)
                query_filter |= Q(customer__mobileNumber__icontains=search_key)

        queryset = queryset.filter(
            Q(order_id__icontains=search_key) |
            Q(customer__name__icontains=search_key) |
            Q(customer__email__icontains=search_key) |
            query_filter
        )

        if created_at_from:
            queryset = queryset.filter(created_at__gte=created_at_from)
        if created_at_to:
            queryset = queryset.filter(created_at__lte=created_at_to)
        if shipping_via:
            if shipping_via == ['ship',"Ship","SHIP"]:
                shipping_via = "By Ship"
            elif shipping_via == ['air',"Air","AIR"]:
                shipping_via = "By Air"
            elif shipping_via == ['express',"Express","EXPRESS"]:
                shipping_via = "By Express"

            queryset = queryset.filter(productorderdetail__shipping_via__icontains=shipping_via)
        if payment_type:
            payment_options ={
                'cash': ['cash', 'Cash'],
                'bank_transfer': ['bank', 'Bank', 'Bank Transfer', 'bank transfer'],
                'wave': ['Wave', 'wave'],
                'orange_money': ['Orange Money', 'orange money'],
                'inquiry': ['inquiry'],
            }
            print("payment_options[payment_type]---->",payment_options[payment_type])
            queryset = queryset.filter(payment_type__in=payment_options[payment_type])
        
        if sort_by:
            if sort_by in ['email', "Email"]:
                sort_by = 'customer__email'
            queryset = queryset.order_by(sort_by)
        if sort_order:
            if sort_order == 'asc':
                queryset = queryset.order_by(sort_by)
            else:
                queryset = queryset.order_by('-' + sort_by)
        else:
            queryset = queryset.order_by('-id')

        queryset = queryset.distinct()

        order_count = queryset.count()

        order_list = queryset[first_row:last_row]
                
        # order_count = models.OrderDetail.objects.filter( Q(order_id__icontains=search_key) |Q(customer__name__icontains=search_key) |Q(customer__email__icontains=search_key), order_status = order_status).count()
        # order_list = models.OrderDetail.objects.filter(Q(order_id__icontains=search_key) |Q(customer__name__icontains=search_key) |Q(customer__email__icontains=search_key), order_status = order_status).order_by('-id')[first_row:last_row]
        list_data = []
        for order in order_list:
            order = models.OrderDetail.objects.get(id = order.id)
            order_serializer = OrderDetailSerializer(order).data
            payment_count = models.OrderTransaction.objects.filter(order = order.id).count()
            if payment_count == 1:
                cash_status = models.OrderTransaction.objects.filter(order = order.id).values_list('cash_status', flat=True)[0]
                transaction_id = models.OrderTransaction.objects.filter(order = order.id).values_list('id', flat=True)[0]
            else:
                cash_status = None 
                transaction_id = None
            
            order_serializer.update({'cash_status':cash_status, 'transaction_id':transaction_id})
            list_data.append(order_serializer)
        res={
            'data':list_data,
            'order_count':order_count
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)


@csrf_exempt
def all_order_list_admin_inquiry(request):
    if request.method == 'POST':
        python_data = JSONParser().parse(io.BytesIO(request.body))
        
        order_status = python_data.get('order_status', 'completed')
        search_key = python_data.get('search_key', "").strip()
        page_number = int(python_data.get('page_number', 1))
        row_size = int(python_data.get('row_data', 10))
        last_row = row_size * page_number
        first_row = last_row - row_size
        print(python_data, 'python_data')
        
        if order_status == "Confirm":
            status = "completed"
            order_status = "pending"
            queryset = models.OrderDetail.objects.filter(Q(status = status)|Q(status = "pending", payment_type = "inquiry"), order_status=order_status)
        else:
            queryset = models.OrderDetail.objects.filter(order_status=order_status)

        if search_key:
            queryset = queryset.filter(
                Q(order_id__icontains=search_key) |
                Q(customer__name__icontains=search_key) |
                Q(customer__email__icontains=search_key) |
                Q(customer__mobileNumber__icontains=search_key) 
            )

        order_count = queryset.count()

        order_list = queryset.order_by('-id')[first_row:last_row]
                
        list_data = []
        for order in order_list:
            order = models.OrderDetail.objects.get(id = order.id)
            order_serializer = OrderDetailSerializer(order).data
            
            list_data.append(order_serializer)
        res={
            'data':list_data,
            'order_count':order_count,
            'total_count':order_count
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)

@csrf_exempt
def all_order_inquiry_list_app(request):
    if request.method == 'POST':
        python_data = JSONParser().parse(io.BytesIO(request.body))
        
        customer = python_data.get('customer')

        order_list = models.OrderDetail.objects.filter(customer = customer, payment_type = "inquiry",status = "inquiry").order_by('-id')
        order_count = order_list.count()

        list_data = []
        for order in order_list:
            order_data = models.OrderDetail.objects.get(id = order.id)
            order_serializer = OrderInquiryDataSerializer(order_data).data

            list_product_data = []
            get_all_product = models.ProductOrderDetail.objects.filter(order = order.id)
            for product in get_all_product:
                product = models.ProductOrderDetail.objects.get(id = product.id)

                product_data = ProductOrderDetailSerializer(product).data

                check_review = models.ProductReview.objects.filter(product = product.product).count()
                # print(check_review, 'check_review')
                review_data = ''
                if check_review == 1:
                    review = models.ProductReview.objects.get(product = product.product)
                    review_data = ProductReviewSerializer(review).data
                product_data.update({'review':review_data})
                list_product_data.append(product_data)
            
            order_serializer.update({'product':list_product_data})
            list_data.append(order_serializer)
            
        res={
            'data':list_data,
            'order_count':order_count
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)



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
def order_detail_admin(request):
    if request.method == 'POST':
        python_data = JSONParser().parse(io.BytesIO(request.body))
        order = python_data.get('order')

        print("python_data=====>",python_data)
    
        order_data = models.OrderDetail.objects.get(id = order)
        order_serializer = OrderDetailSerializer(order_data).data
        
        get_all_product = models.ProductOrderDetail.objects.filter(order = order).order_by('-id')
        list_data = []
        for product in get_all_product:
            product = models.ProductOrderDetail.objects.get(id = product.id)
            product_data = ProductOrderDetailSerializer(product).data

            warehouse_assign = product.warehouse
            if warehouse_assign != None and warehouse_assign != 'null':
                warehouseConfirmed = True 
            else:
                warehouseConfirmed = False 


            check_vendor = models.VendorOrderDetail.objects.filter(variant = product.id).count()
            if check_vendor == 1:
                vendor = models.VendorOrderDetail.objects.get(variant = product.id)
                vendor_data = VendorOrderDataSerializer(vendor).data
                
                order_tracking = models.OrderTracking.objects.filter(variant = product.id).order_by('id')
                order_tracking_data = OrderTrackingSerializer(order_tracking, many=True).data
                vendor_order_tracking = models.VendorOrderTracking.objects.filter(variant = product.id).order_by('id')
                vendor_order_tracking_data = VendorOrderTrackingSerializer(vendor_order_tracking, many=True).data
                product_data.update({'vendorConfirmed':True, 'vendor_data':vendor_data, 'order_tracking_data':order_tracking_data, \
                'warehouseConfirmed':warehouseConfirmed, 'vendor_order_tracking_data':vendor_order_tracking_data})
            else:
                vendor_order_tracking = models.VendorOrderTracking.objects.filter(variant = product.id).order_by('id')
                vendor_order_tracking_data = VendorOrderTrackingSerializer(vendor_order_tracking, many=True).data
                order_tracking = models.OrderTracking.objects.filter(variant = product.id).order_by('id')
                order_tracking_data = OrderTrackingSerializer(order_tracking, many=True).data
                product_data.update({'vendorConfirmed':False, 'order_tracking_data':order_tracking_data, \
                'warehouseConfirmed':warehouseConfirmed, 'vendor_order_tracking_data':vendor_order_tracking_data})

            list_data.append(product_data)
        
        promocode_data = None
        if order_data.promocode != None:
            all_promocode = models.PromocodeDetail.objects.get(id = order_data.promocode.id)
            promocode_data = PromocodeDetailSerializer(all_promocode).data 

        res={
            'data':order_serializer,
            'product_data':list_data,
            'promocode_data':promocode_data
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)
            

@csrf_exempt
def customer_order_list(request):
    if request.method == 'POST':
        python_data = JSONParser().parse(io.BytesIO(request.body))
        customer = python_data.get('customer')
        check_customer = models.CustomerDetail.objects.filter(id = customer).count()
        if check_customer == 1:

            order_list = models.OrderDetail.objects.filter(customer = customer).order_by('-id')
            list_data = []
            for order in order_list:
                order_data = models.OrderDetail.objects.get(id = order.id)
                order_serializer = OrderDetailDataSerializer(order_data).data

                list_product_data = []
                get_all_product = models.ProductOrderDetail.objects.filter(order = order.id)
                for product in get_all_product:
                    product = models.ProductOrderDetail.objects.get(id = product.id)

                    product_data = ProductOrderDetailSerializer(product).data

                    check_review = models.ProductReview.objects.filter(product = product.product).count()
                    # print(check_review, 'check_review')
                    review_data = ''
                    if check_review == 1:
                        review = models.ProductReview.objects.get(product = product.product)
                        review_data = ProductReviewSerializer(review).data
                    product_data.update({'review':review_data})
                    list_product_data.append(product_data)
                
                order_serializer.update({'product':list_product_data})
                list_data.append(order_serializer)

            res={
                'data':list_data
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)
                

@csrf_exempt
def variant_vendor_list(request):
    if request.method == 'POST':
        python_data = JSONParser().parse(io.BytesIO(request.body))
        variant = python_data.get('variant')

        list_vendor = models.VendorProductPrice.objects.filter(variant = variant)
        vendor_data = VendorProductDataSerializer(list_vendor, many=True).data
        
        res={
    
            'data':vendor_data
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)


@csrf_exempt
def vendor_order_assign(request):
    if request.method == 'POST':
        python_data = JSONParser().parse(io.BytesIO(request.body))

        # print("python_data-=-=vendor_order_assign-=-->", python_data)

        order = python_data.get('order')
        variant = python_data.get('variant')
        vendor = python_data.get('vendor')
        warehouse = python_data.get('warehouse')
        
        now = datetime.now()
        date_time = now.strftime('%Y-%m-%d, %H:%M:%S')

        check_order = models.VendorOrderDetail.objects.filter(order = order, variant=variant).count()
        # print("ORDER -=-=-=-=-=-=-=-=-->", check_order)
        if check_order == 0:

            create_order = models.VendorOrderDetail.objects.create(
                order_id = order, 
                variant_id = variant,
                vendor_id = vendor,
                # created_at = datetime.now()
            )
            create_order.save()

            vendor_price = int(models.VendorProductPrice.objects.filter(vendor = vendor, variant = create_order.variant.variant).first().price)
            total_vendor_price = vendor_price * int(create_order.variant.quantity)

            get_product_order_detail = models.ProductOrderDetail.objects.get(id = variant)
            get_product_order_detail.vendor_price = vendor_price
            get_product_order_detail.total_vendor_price = total_vendor_price
            get_product_order_detail.save()

            # product_update = models.ProductOrderDetail.objects.get(id = variant)
            # product_update.warehouse_id = warehouse
            # product_update.save()

            
            # order_tracking = models.OrderTracking.objects.create(
            #     order_id = order,
            #     variant_id = variant,
            #     status = "Processing",
            #     created_at  = date_time
            # ).save()

            get_vendor_variant = models.VendorProductPrice.objects.filter(variant = create_order.variant.variant.id, vendor = vendor).first()
            remarks = str(create_order.variant.product.product_name)+" X "+str(create_order.variant.quantity)

            # transaction_create = models.VendorTransaction.objects.create(
            #     vendor_id = vendor,
            #     currency = "CFA",
            #     amount = float(get_vendor_variant.price) * int(create_order.variant.quantity),
            #     transaction_type = "pending",
            #     remarks = remarks,
            #     created_at = datetime.now(),
            #     status = "pending",
            # )


            vendor_detail = models.VendorDetail.objects.get(id = vendor)
            previous_remaining_amount = models.VendorPaymentTracker.objects.filter(vendor = vendor).order_by('-id').values_list('remaining_amount', flat=True).first()
            
            vendor_name = vendor_detail.vendor_name
            vendor_email = vendor_detail.email
            vendor_mobile = vendor_detail.phone_number
            payment_type = "Pay"
            # currency = "CFA"
            amount = Decimal(str(float(get_vendor_variant.price) * int(create_order.variant.quantity)))
            remaining_amount = amount if previous_remaining_amount is None else previous_remaining_amount + amount
            description = remarks


            create_payment = models.VendorPaymentTracker.objects.create(
                vendor_id = vendor,
                vendor_name = vendor_name,
                vendor_email = vendor_email,
                vendor_mobile = vendor_mobile,
                payment_type = payment_type,
                currency = "XOF",
                amount = amount,
                remaining_amount = remaining_amount,
                description = description,
                created_at = datetime.now(),
            ).save()
            
            
            
            res={
        
                'message':"Order send to Vendor, they'll accept soon."
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)
        else:
            res={       
                'message':"This order already send to Vendor."
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=406)



@csrf_exempt
def warehouse_order_assign(request):
    if request.method == 'POST':
        python_data = JSONParser().parse(io.BytesIO(request.body))
        variant = python_data.get('variant')
        warehouse = python_data.get('warehouse')

        product_update = models.ProductOrderDetail.objects.get(id = variant)
        product_update.warehouse_id = warehouse
        product_update.save()

        res={
        
            'message':"Warehouse Added successfully."
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
def vendor_order_list(request):
    if request.method == 'POST':
        python_data = JSONParser().parse(io.BytesIO(request.body))

        # print("pytohn_data-=-vendor_order_list-=--->",python_data)

        vendor = int(python_data.get('vendor'))

        list_data = []
        order_list = models.VendorOrderDetail.objects.filter(vendor = vendor).order_by('-id')
        for order in order_list:
            order = models.VendorOrderDetail.objects.get(id = order.id)
            order_data = VendorOrderDetailSerializer(order).data

            get_price = models.VendorProductPrice.objects.filter(variant = order.variant.variant, vendor = vendor).values_list('price', flat=True).first()
            quantity = order.variant.quantity
            order_data.update({'vendor_price':get_price, 'quantity':quantity, 'total_variant_price':float(get_price)*int(quantity)})
            
            list_data.append(order_data)

        res={
    
            'data':list_data
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)



@csrf_exempt
def vendor_order_list_vendor(request):
    if request.method == 'POST':
        python_data = JSONParser().parse(io.BytesIO(request.body))
        vendor = python_data.get('vendor')
        page_number = int(python_data.get('page_number', 1))
        row_size = int(python_data.get('row_data', 10))
        last_row = row_size * page_number
        first_row = last_row - row_size
        
        list_data = []
        total_order_count = models.VendorOrderDetail.objects.filter(vendor = vendor).count()
        order_list = models.VendorOrderDetail.objects.filter(vendor = vendor).order_by('-id')[first_row:last_row]

        for order in order_list:
            order = models.VendorOrderDetail.objects.get(id = order.id)
            order_data = VendorOrderDetailSerializer(order).data

            get_price = models.VendorProductPrice.objects.filter(variant = order.variant.variant, vendor = vendor).values_list('price', flat=True).first()
            quantity = order.variant.quantity
            order_data.update({'variant_price':get_price, 'quantity':quantity, 'total_variant_price':float(get_price)*int(quantity)})

            tracking = models.VendorOrderTracking.objects.filter(order = order.order,variant = order.variant)
            order_tracking = VendorOrderTrackingSerializer(tracking, many=True).data
            order_data.update({'order_tracking':order_tracking})

            
            if getattr(order.variant.warehouse, "id", None) and models.WarehouseDetail.objects.filter(id=order.variant.warehouse.id).exists():

                warehouse_count = models.WarehouseDetail.objects.get(id =order.variant.warehouse.id)
                warehouse_serialiser = WarehouseDetailSerializer(warehouse_count).data
                order_data.update({'warehouse_data':warehouse_serialiser})

            list_data.append(order_data)
        
        res={
    
            'data':list_data,
            'total_order_count':total_order_count
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)


@csrf_exempt
def variant_order_status_update(request):
    if request.method == 'POST':
        python_data = JSONParser().parse(io.BytesIO(request.body))
        order = python_data.get('order')
        variant = python_data.get('variant')
        status = python_data.get('status')
        # print(python_data, 'python_datapython_data')
        now = datetime.now()
        date_time = now.strftime('%Y-%m-%d, %H:%M:%S')

        status_check = models.OrderTracking.objects.filter(order = order,variant = variant,status = status).count()
        if status_check == 0:
            # get_variant_id = models.ProductOrderDetail.objects.filter(order = order,variant = variant).values_list('id', flat=True)[0]
            get_variant = models.ProductOrderDetail.objects.get(id = variant)
            get_variant.status = status
            get_variant.save()

            status_create = models.OrderTracking.objects.create(
                order_id = order,
                variant_id = variant,
                status = status,
                created_at = date_time
            )
            status_create.save()

            token = status_create.order.customer.FCMToken
            product_name = status_create.variant.product.product_name
            product_image = IMAGE_URL + str(status_create.variant.product.product_image_1)
            # print(product_image, 'product_image')
            # product_name = full_name[:15] + "..." if len(full_name) > 15 else full_name
            title = 'Order Status Updated'
            body = f'Your {product_name} order is now {status}.'
            
            try:
                # print('Test')
                message = messaging.Message(
                notification=messaging.Notification(
                        title=title,
                        body=body,
                        image = product_image
                    ),
                    data={
                        'notification_type':'order',
                    },
                    token=token
                    # tokens=token_chunk,
                )
                try:
                    response = messaging.send(message)

                    print("Notification Sent Successfully")

                   
                except Exception as e:
                    print(f"An error occurred while sending multicast message: {e}")
            except Exception as e:
                print('Error---->',e)


            res={
                'message':"Status update successfully."
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)
        else:
            res={
                'message':"This status already used."
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=406)

@csrf_exempt
def vendor_variant_order_status_update(request):
    if request.method == 'POST':
        python_data = JSONParser().parse(io.BytesIO(request.body))
        order = python_data.get('order')
        variant = python_data.get('variant')
        vendor_status = python_data.get('vendor_status')
        # print(python_data, 'python_datapython_data')
        now = datetime.now()
        date_time = now.strftime('%Y-%m-%d, %H:%M:%S')

        status_check = models.VendorOrderTracking.objects.filter(order = order,variant = variant,status = vendor_status).count()
        if status_check == 0:
            # get_variant_id = models.ProductOrderDetail.objects.filter(order = order,variant = variant).values_list('id', flat=True)[0]
            get_variant = models.ProductOrderDetail.objects.get(id = variant)
            get_variant.vendor_status = vendor_status
            get_variant.save()

            status_create = models.VendorOrderTracking.objects.create(
                order_id = order,
                variant_id = variant,
                status = vendor_status,
                created_at = date_time
            ).save()
            res={
                'message':"Status update successfully."
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)
        else:
            res={
                'message':"This status already used."
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=406)

@csrf_exempt
def order_status_update(request):
    if request.method == 'POST':
        python_data = JSONParser().parse(io.BytesIO(request.body))
        order = python_data.get('order')
        status = python_data.get('status')
        
        now = datetime.now()
        date_time = now.strftime('%Y-%m-%d, %H:%M:%S')
        # print(python_data, 'python_data')
        check_order = models.OrderDetail.objects.filter(id = order).count()
        if check_order == 1:
            # print('dafadg 1122')
            order_status = models.OrderDetail.objects.get(id = order)
            order_status.order_status = status
            order_status.save()
            
            res={
                'message':"Status update successfully."
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)
        else:
            res={
                'message':"This status already used."
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=406)



@csrf_exempt
def vendor_detail_admin(request):
    if request.method == 'POST':
        python_data = JSONParser().parse(io.BytesIO(request.body))
        vendor = python_data.get('vendor')
        
        get_vendor_data = models.VendorDetail.objects.get(id = vendor)
        data = VendorDetailSerializer(get_vendor_data).data
        
        res={
            'data':data
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)
        

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
def vendor_product_admin(request):
    if request.method == 'POST':
        python_data = JSONParser().parse(io.BytesIO(request.body))
        vendor = python_data.get('vendor')
        
        datadata = models.VendorProductPrice.objects.filter(vendor = vendor).values_list('product', 'model').distinct()
        get_all_product = models.VendorProductPrice.objects.filter(vendor = vendor).values_list('product', flat=True).distinct('product_id').order_by('product')
        print(get_all_product, 'get_all_product')
        list_data = []
        for product in get_all_product:
           
            get_product_data = models.ProductDetail.objects.get(id = product)
            product_data = AdminProductDataSerializer(get_product_data).data

            get_all_model = models.VendorProductPrice.objects.filter(product = product, vendor = vendor).values_list('model', flat=True).distinct()
            list_model = []
            for model in get_all_model:
                get_model_data = models.ProductModel.objects.get(id = model)
                model_data = AdminProductModelDataSerializer(get_model_data).data

                get_all_variant = models.VendorProductPrice.objects.filter(product = product, vendor = vendor, model = model).values_list('variant', flat=True).distinct()
                list_variant = []
                for variant in get_all_variant:
                    
                    get_variant_data = models.ProductModelVariant.objects.get(id = variant)
                    variant_data = AdminProductModelVariantSerializer(get_variant_data).data
                    
                    price_data = models.ProductModelVariant.objects.filter(product=product).aggregate(
                        max_price=Max('price'),
                        min_price=Min('price')
                    )
                    max_price = price_data['max_price']
                    min_price = price_data['min_price']

                    get_all_vendor = models.VendorProductPrice.objects.get(product = product, vendor = vendor, model = model, variant = variant)
                    vendor_data = VendorProductvariantSerializer(get_all_vendor).data
                    variant_data.update({'vendor_data':vendor_data})
                    list_variant.append(variant_data)
                model_data.update({'variant_data':list_variant})
                list_model.append(model_data)
            product_data.update({'model_data':list_model,  'max_price':max_price, 'min_price':min_price})
            list_data.append(product_data)
        
        # print(list_data, 'list_datalist_data')
        
        res={
            'data':list_data
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)
        
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




        # vendor = python_data.get('vendor')
        # date = python_data.get('date')
        # payment_type = python_data.get('payment_type')
        # send_currency = python_data.get('send_currency')
        # send_amount = python_data.get('send_amount')
        # receive_currency = python_data.get('receive_currency')
        # receive_amount = python_data.get('receive_amount')
        # remark = python_data.get('remark')
        
        # check_vendor = models.VendorDetail.objects.filter(id = vendor).count()
        # if check_vendor == 1:
        #     create_transaction = models.VendorTransactionDetail.objects.create(
        #         vendor_id = vendor,
        #         date = date,
        #         payment_type = payment_type,
        #         send_currency = send_currency,
        #         send_amount = send_amount,
        #         receive_currency = receive_currency,
        #         receive_amount = receive_amount,
        #         remark = remark,
        #     ).save()

        #     res={
        #         'message':"Transaction Record Create successfully."
        #     }
        #     return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)
        # else:

        #     res={
        #         'message':"Something Went wrong."
        #     }
        #     return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=406)


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
def product_order_list(request):
    if request.method == 'POST':
        python_data = JSONParser().parse(io.BytesIO(request.body))

        product = python_data.get('product')

        check_product = models.ProductDetail.objects.filter(id = product).count()
        if check_product == 1:
            list_data = []
            get_all_order = models.ProductOrderDetail.objects.filter(product = product)
            for order in get_all_order:
                order = models.ProductOrderDetail.objects.get(id = order.id)
                order_data = ProductOrderDetailSerializer(order).data

                vendor_check = models.VendorOrderDetail.objects.filter(variant = order.id).count()
                if vendor_check == 1:
                    vendor = models.VendorOrderDetail.objects.get(variant = order.id)
                    vendor_data = VendorOrderDataSerializer(vendor).data
                    order_data.update({'vendor_data':vendor_data, 'vendor_assign':True})
                    list_data.append(order_data)
                else:
                    order_data.update({'vendor_assign':False})
                    list_data.append(order_data)

            res={
                'data':list_data
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)
        else:
            res={
                'message':'Enter valid Product ID.'
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=406)


@csrf_exempt
def chat_room_list(request):
    if request.method == "POST":
        try:
            python_data = JSONParser().parse(io.BytesIO(request.body))
            room_status = python_data.get("room_status")

            if room_status == "open":
                rooms = models.ChatRoom.objects.filter(is_resolved__in = ["false","False"]).order_by("-updated_at")
            elif room_status == "unread":
                last_message_subquery = models.ChatConversion.objects.filter(
                    room=OuterRef('id')
                ).order_by('-create_at')

                rooms = models.ChatRoom.objects.annotate(
                    last_message_sender=Subquery(last_message_subquery.values('send_by')[:1])
                ).filter(
                    last_message_sender__in=["user", "User"]
                )
            elif room_status == "resolved":
                rooms = models.ChatRoom.objects.filter(is_resolved__in = ["true","True"]).order_by("-updated_at")
            
            else:
                rooms = models.ChatRoom.objects.all().order_by("-updated_at")


                # messages_serializer = ChatRoomSerializer(rooms, many=True).data
        except:
            rooms = models.ChatRoom.objects.all().order_by("-updated_at")
                    
        # messages = models.ChatRoom.objects.filter(is_resolved__in = ["false","False"]).order_by("-updated_at")
        messages_serializer = ChatRoomSerializer(rooms, many=True).data

        res={
            'chat_data':messages_serializer
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)


@csrf_exempt
def chat_room_and_agent_history(request):
    if request.method == "POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))

        # print("python_data-=--chat_room_and_agent_history-=-==->",python_data)

        room_id = python_data.get('room_id',None)
        previous_agents = models.AgentInChatRoomHistory.objects.filter(room__room = room_id).order_by('-assigned_date')
        previous_agents_serializer = AgentInChatRoomHistorySerializer(previous_agents, many=True).data

        res = {
            'data': previous_agents_serializer
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)
        




@csrf_exempt
def agent_chat_room_list(request):
    if request.method == "POST":
        try:
            python_data = JSONParser().parse(io.BytesIO(request.body))
            room_status = python_data.get("room_status")
            agent_id = python_data.get('agent_id',None)
            search_key = python_data.get('search_key',None)

            print("python_data-=-agent_chat_room_list-=-->", python_data)

            filter_query = Q()
            if search_key not in [None,'','null']:
                filter_query = Q(user__name__icontains=search_key) | Q(user__email__icontains=search_key) | Q(user__mobileNumber__icontains=search_key)

            if room_status == "open":
                rooms = models.ChatRoom.objects.filter(filter_query, chat_agent = agent_id,is_resolved__in = ["false","False"]).order_by("-updated_at")
            elif room_status == "unread":
                last_message_subquery = models.ChatConversion.objects.filter(
                    room=OuterRef('id')
                ).order_by('-create_at')

                rooms = models.ChatRoom.objects.annotate(
                    last_message_sender=Subquery(last_message_subquery.values('send_by')[:1])
                ).filter(
                    filter_query,
                    chat_agent = agent_id,
                    last_message_sender__in=["user", "User"]
                )
            elif room_status == "resolved":
                rooms = models.ChatRoom.objects.filter(filter_query, chat_agent = agent_id,is_resolved__in = ["true","True"]).order_by("-updated_at")
            
            else:
                rooms = models.ChatRoom.objects.filter(filter_query, chat_agent = agent_id).order_by("-updated_at")


                # messages_serializer = ChatRoomSerializer(rooms, many=True).data
        except:
            agent_id = python_data.get('agent_id',None)
            rooms = models.ChatRoom.objects.filter(filter_query,chat_agent = agent_id).order_by("created_at")


        messages_serializer = ChatRoomSerializer(rooms, many=True).data
        res={
            'chat_data':messages_serializer
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)


# @csrf_exempt
# def chat_room_assign_to_agent(request):
#     if request.method == "POST":
#         json_data = request.body
#         stream = io.BytesIO(json_data)
#         python_data = JSONParser().parse(stream)

#         print("python_data-=-=--->",python_data)

#         user = python_data.get('user')
#         admin = python_data.get('admin')
#         chat_agent = python_data.get('chat_agent')
#         room = python_data.get('room')
#         chat_room_id = python_data.get('chat_room_id')

#         if models.ChatRoom.objects.filter(id = chat_room_id).exists():
#             assign_agent = models.ChatRoom.objects.get(id = chat_room_id)
#             assign_agent.chat_agent = chat_agent
#             assign_agent.save()

#             res ={
#                 'message':'Agent Assign to Chat'
#             }
#             return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)
#         else:
#             res ={
#                 'message':'Room Not Found'
#             }
#             return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=406)

    



@csrf_exempt
def chat_history(request):
    json_data = request.body
    stream = io.BytesIO(json_data)
    python_data = JSONParser().parse(stream)
    
    room = python_data.get('room')
    user_type = python_data.get('user_type',None)

    # print("python_data--ChatHIstory-->",python_data)

    messages = models.ChatConversion.objects.filter(room__room=room).order_by("create_at")
    messages_serializer = ChatConversionSerializer(messages, many=True).data

    # Update Unseen Message toooo Seen
    if user_type in ["Agent","Admin"]:
        models.ChatConversion.objects.filter(room__room=room, status = "Unseen").exclude(send_by__in = ["Agent","Admin"]).update(status = "Seen")
    else:
        models.ChatConversion.objects.filter(room__room=room, status = "Unseen").exclude(send_by = "User").update(status = "Seen")

    res={
        'chat_data':messages_serializer,
    }
    return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)


@csrf_exempt
def user_new_message_count(request):
    if request.method == "POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))
        
        customer = python_data.get('customer')
        message_count = models.ChatConversion.objects.filter(user=customer, status = "Unseen").exclude(send_by = "User").count()
        
        cart_count = sum(
            int(qty) if qty not in [None, '', 'null'] else 0
            for qty in models.CartDetail.objects.filter(
                customer=customer,
                product__status='Active'
            ).values_list('quantity', flat=True)
        )
        print(cart_count, 'cart_countcart_count', flush=True)
        res={
            'message_count':message_count,
            'cart_count':cart_count
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)

# @csrf_exempt
# def create_message(request):
#     if request.method == "POST":
#         python_data={}
#         for i,j in request.FILES.items():
#             python_data.update({i:j})
        
#         for i,j in request.POST.items():
#             python_data.update({i:j})

#         print("python_data----crate_message--->", python_data)
#         user_id = python_data.get('user_id',None)
#         admin_id = python_data.get('admin_id',None)
#         agent_id = python_data.get('agent_id',None)
#         room = python_data.get('room',None)
#         message = python_data.get('message',None)
#         message_french = python_data.get('message_french',None)
#         message_type = python_data.get('message_type',None)
#         file = python_data.get('file',None)
#         file_type = python_data.get('file_type',None)
        
#         if user_id not in [None,'','null']:
#             send_by = "User"
#         elif admin_id not in [None,'','null']:
#             send_by = "Admin"
#         else:
#             send_by = "Agent"

#         # print("file linl-=-=-=-->",file)
#         # print("file linl-=-=-=-->",type(file))

#         if file not in [None,'','null']:
#             # print("here--1")
#             if isinstance(file,str):
#                 # print("here--2",file)
#                 if file and file.startswith("https://diaba-live.s3.amazonaws.com/"):
#                     # print("here--3",file)
#                     file = file.replace("https://diaba-live.s3.amazonaws.com/", "", 1)
#                     # print("here--4",file)

#         # print("file-----------------------=====================>",file)
        
#         if models.ChatRoom.objects.filter(room = room).exists():

                
#             room = models.ChatRoom.objects.get(room = room)
#             room_id = room.id
#             if room.chat_agent not in [None,'','null',False]:
#                 agent_id = room.chat_agent.id

#                 if message_type != "resolved":
#                     room.is_resolved = False
#                     room.save()
            
#             else:

#                 #Assigning Chat Agent Automatically
                
#                 all_agent = models.ChatAgentDetail.objects.filter(status="Active")

#                 unassigned_agent_found = False
#                 for check_already_assigned_agent in all_agent:
#                     if models.ChatRoom.objects.filter(chat_agent = check_already_assigned_agent.id).exists():
#                         pass
#                     else:
#                         agent_id = check_already_assigned_agent.id
#                         unassigned_agent_found = True
#                         break

#                 if not unassigned_agent_found:
#                     chat_room_agent = (
#                         models.ChatAgentDetail.objects.annotate(
#                         assigned_rooms=Count('chatroom', filter=Q(chatroom__status="Active"))
#                         ).order_by('assigned_rooms').first()
#                     )
                    
#                     agent_id = chat_room_agent.id
#                 room.chat_agent_id = agent_id
#                 if message_type != "resolved":
#                     room.is_resolved = False
#                     room.save()

#         else:

#             if not models.ChatAgentDetail.objects.filter(status="Active").exists():
#                 res={
#                     'message':'Agent Not Found'
#                 }
#                 return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=406)
            
#             #Assigning Chat Agent Automatically
            
#             all_agent = models.ChatAgentDetail.objects.filter(status="Active")

#             unassigned_agent_found = False
#             for check_already_assigned_agent in all_agent:
#                 if models.ChatRoom.objects.filter(chat_agent = check_already_assigned_agent.id).exists():
#                     pass
#                 else:
#                     agent_id = check_already_assigned_agent.id
#                     unassigned_agent_found = True
#                     break

#             if not unassigned_agent_found:
#                 chat_room_agent = (
#                     models.ChatAgentDetail.objects.annotate(
#                     assigned_rooms=Count('chatroom', filter=Q(chatroom__status="Active"))
#                     ).order_by('assigned_rooms').first()
#                 )
#                 print("chat_room_agent=====>",chat_room_agent)
#                 agent_id = chat_room_agent.id

#             create_room = models.ChatRoom.objects.create(
#                 user_id = user_id,
#                 admin_id = admin_id,
#                 room = room,
#                 chat_agent_id = agent_id,
#                 created_at = datetime.now(),
#             )
#             create_room.save()
#             room_id = create_room.id

#             models.AgentInChatRoomHistory.objects.create(
#                 room_id = room_id,
#                 agent_id = agent_id,
#                 assigned_date = datetime.now(),
#             )
        
#         # print("file--==-=-=-=-=-=-=", file)

#         conversation = models.ChatConversion.objects.create(
#             admin_id=admin_id,
#             user_id=user_id,
#             chat_agent_id = agent_id,
#             room_id=room_id,
#             send_by=send_by,
#             message = message,
#             message_french = message_french,
#             message_type = message_type,
#             file = file,
#             file_type = file_type,
#             create_at=datetime.now(),
#         )
#         conversation.save()

#         # if isinstance(file, str):
#         #     print("file=====>",file)
#         #     if file and os.path.exists(file):
#         #         print("file_name=====>",file_name)
#         #         file_name = os.path.basename(file)
#         #         with open(file, "rb") as f:
#         #             conversation.file.save(file_name, File(f), save=True)

#         # file = conversation.file.url if conversation.file not in [None,'','null'] else None

#         print("file--2---->",file)

#         res={
#             'room': conversation.room.id,
#             'message': conversation.message,
#             'message_type': conversation.message_type,
#             'file': 'https://diaba-live.s3.amazonaws.com/'+ f'{file}',
#             'file_type': conversation.file_type,
#             'conversation_id': conversation.id
#         }

#         # print("MESSGAE-=-=-=-=-REs-=-=-=-=--->",res)
#         return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)


@csrf_exempt
def create_message(request):
    if request.method == "POST":
        python_data={}
        for i,j in request.FILES.items():
            python_data.update({i:j})
        
        for i,j in request.POST.items():
            python_data.update({i:j})

        print("python_data----crate_message--->", python_data)
        user_id = python_data.get('user_id',None)
        admin_id = python_data.get('admin_id',None)
        agent_id = python_data.get('agent_id',None)
        room = python_data.get('room',None)
        message = python_data.get('message',None)
        message_french = python_data.get('message_french',None)
        message_type = python_data.get('message_type',None)
        file = python_data.get('file',None)
        file_type = python_data.get('file_type',None)
        product_id = python_data.get('product_id',None)
        
        if user_id not in [None,'','null']:
            send_by = "User"
        elif admin_id not in [None,'','null']:
            send_by = "Admin"
        else:
            send_by = "Agent"

        # print("file linl-=-=-=-->",file)
        # print("file linl-=-=-=-->",type(file))

        if file not in [None,'','null']:
            # print("here--1")
            if isinstance(file,str):
                # print("here--2",file)
                if file and file.startswith("https://diaba-live.s3.amazonaws.com/"):
                    # print("here--3",file)
                    file = file.replace("https://diaba-live.s3.amazonaws.com/", "", 1)

                if file and file.startswith("/media/"):
                    file = file.replace("/media/","",1)
                    # print("here--4",file)

        # print("file-----------------------=====================>",file)
        
        if models.ChatRoom.objects.filter(room = room).exists():

                
            room = models.ChatRoom.objects.get(room = room)
            room_id = room.id

            room.updated_at = datetime.now()
            room.save()

            if room.chat_agent not in [None,'','null',False]:
                agent_id = room.chat_agent.id

                if message_type != "resolved":
                    room.is_resolved = False
                    room.save()
            
            else:

                #Assigning Chat Agent Automatically
                
                all_agent = models.ChatAgentDetail.objects.filter(status="Active")

                unassigned_agent_found = False
                for check_already_assigned_agent in all_agent:
                    if models.ChatRoom.objects.filter(chat_agent = check_already_assigned_agent.id).exists():
                        pass
                    else:
                        agent_id = check_already_assigned_agent.id
                        unassigned_agent_found = True
                        break

                if not unassigned_agent_found:
                    chat_room_agent = (
                        models.ChatAgentDetail.objects.annotate(
                        assigned_rooms=Count('chatroom', filter=Q(chatroom__status="Active"))
                        ).order_by('assigned_rooms').first()
                    )
                    
                    agent_id = chat_room_agent.id
                room.chat_agent_id = agent_id
                if message_type != "resolved":
                    room.is_resolved = False
                    room.save()

        else:

            if not models.ChatAgentDetail.objects.filter(status="Active").exists():
                res={
                    'message':'Agent Not Found'
                }
                return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=406)
            
            #Assigning Chat Agent Automatically
            
            all_agent = models.ChatAgentDetail.objects.filter(status="Active")

            unassigned_agent_found = False
            for check_already_assigned_agent in all_agent:
                if models.ChatRoom.objects.filter(chat_agent = check_already_assigned_agent.id).exists():
                    pass
                else:
                    agent_id = check_already_assigned_agent.id
                    unassigned_agent_found = True
                    break

            if not unassigned_agent_found:
                chat_room_agent = (
                    models.ChatAgentDetail.objects.annotate(
                    assigned_rooms=Count('chatroom', filter=Q(chatroom__status="Active"))
                    ).order_by('assigned_rooms').first()
                )
                print("chat_room_agent=====>",chat_room_agent)
                agent_id = chat_room_agent.id

            create_room = models.ChatRoom.objects.create(
                user_id = user_id,
                admin_id = admin_id,
                room = room,
                chat_agent_id = agent_id,
                created_at = datetime.now(),
                updated_at = datetime.now(),
            )
            create_room.save()
            room_id = create_room.id

            models.AgentInChatRoomHistory.objects.create(
                room_id = room_id,
                agent_id = agent_id,
                assigned_date = datetime.now(),
            )
        
        # print("file--==-=-=-=-=-=-=", file)

        conversation = models.ChatConversion.objects.create(
            admin_id=admin_id,
            user_id=user_id,
            chat_agent_id = agent_id,
            room_id=room_id,
            send_by=send_by,
            message = message,
            message_french = message_french,
            message_type = message_type,
            product_id = product_id,
            file = file,
            file_type = file_type,
            create_at=datetime.now(),
        )
        conversation.save()

        FCMToken = conversation.room.user.FCMToken

        if file_type in ["Audio", "audio","photo","Photo"]:
            notification_message = "*New Message"
        else:
            notification_message = message

        notification_title = "Diaba Support"

        if send_by in ["Admin","Agent"]:
            try:
                message = messaging.Message(
                notification=messaging.Notification(
                        title=notification_title,
                        body=notification_message,
                    ),
                    data={
                        "room": room,
                        "notification_type": "support",
                        "sender": send_by
                    },
                    token=FCMToken
                )
                try:
                    response = messaging.send(message)

                    print("Notification Sent Successfully")

                except Exception as e:
                    print(f"An error occurred while sending multicast message: {e}")
            except Exception as e:
                print('Error---->',e)


        # if isinstance(file, str):
        #     print("file=====>",file)
        #     if file and os.path.exists(file):
        #         print("file_name=====>",file_name)
        #         file_name = os.path.basename(file)
        #         with open(file, "rb") as f:
        #             conversation.file.save(file_name, File(f), save=True)

        # file = conversation.file.url if conversation.file not in [None,'','null'] else None

        print("file--2---->",file)
        audio_path = ""
        if file_type in ["Audio", "audio","photo","Photo"]:
            audio_path = "chat/files/"

        res={
            'room': conversation.room.id,
            'message': conversation.message,
            'message_type': conversation.message_type,
            # 'file': 'https://diaba-live.s3.amazonaws.com/'+ f'{audio_path}{file}',
            'file': f'{audio_path}{file}',
            'file_type': conversation.file_type,
            'conversation_id': conversation.id
        }

        # print("MESSGAE-=-=-=-=-REs-=-=-=-=--->",res)
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)


@csrf_exempt
def chat_room_update(request):
    if request.method == "POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))
        
        print("Python_data--chat_room_update--=-->",python_data)
        id = python_data.get('id')

        if models.ChatRoom.objects.filter(id = id).exists():

            is_resolved = python_data.get('is_resolved', None)


            get_room = models.ChatRoom.objects.get(id = id)
            get_room.priority = python_data.get('priority', get_room.priority)
            if is_resolved in [True,'true']:
                get_room.is_resolved = is_resolved
            else:
                get_room.is_resolved = False

            get_room.save()

            if get_room.is_resolved in [True,'true']:
                get_room.chat_agent = None
                get_room.save()

            res = {
                'message':'ChatRoom Updated'
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)
        
        else:
            res = {
                'message':'ChatRoom not Found'
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=406)


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
def daily_price(request):
    price_update = models.DailyPrice.objects.last()
    price = DailyPriceSerializer(price_update).data
    res={
        'data':price
    }
    return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)



@csrf_exempt
def product_search(request):
    if request.method == "POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))

        # print("python_data--product_search-->",python_data)

        search = python_data.get('search')
        currencyCode = python_data.get('currencyCode',None)
        countryCallingCode = python_data.get('countryCallingCode',None)
        country = python_data.get('countryName','Egypt')
        ip_address = python_data.get('ip_address')
        user_id = python_data.get('user_id')

        try:
            if currencyCode not in [None,'','null']:
                country = models.CountryWithCurrency.objects.filter(currency_code = currencyCode).first().country_name
            elif countryCallingCode not in [None,'','null']:
                country = models.CountryWithCurrency.objects.filter(country_calling_code = countryCallingCode).first().country_name
                
            elif user_id:
                user = models.CustomerDetail.objects.get(id = user_id)
                countryCode = user.countryCode

                if models.CountryWithCurrency.objects.filter(country_calling_code = countryCode).exists():
                    country = models.CountryWithCurrency.objects.get(country_calling_code = countryCode).country_name
                else:
                    if country not in [None,'','null']:
                        country = country
                    else:
                        try:
                            response = requests.get(f'https://ipapi.co/{ip_address}/json/')
                            response = response.json()
                            country = response.get("country_name")
                            print("response====>",response)

                            if country in [None,'','null']:
                                country = "Egypt"

                        except Exception as e:
                            print("Errroooorrr----->",e)
                            country = "Egypt"
                        

            else:
                if country in [None,'','null']:
                    try:
                        response = requests.get(f'https://ipapi.co/{ip_address}/json/')
                        response = response.json()
                        country = response.get("country_name")
                        print("response====>",response)

                        if country in [None,'','null']:
                            country = "Egypt"

                    except Exception as e:
                        print("Errroooorrr----->",e)
                        country = "Egypt"
                else:
                    country = country
        except Exception as e:
            print("Error-=-=-=--->",e)
            country = 'Egypt'


        
        serach_query = Q()

#         # serach_query &= Q(product_name__icontains = search) | Q(product_name_french__icontains = search) | Q(category__category__icontains = search) | Q(category__category_french__icontains = search)
#         serach_query &= Q(product_name__icontains = search, status='Active') | Q(product_name_french__icontains = search, status='Active') | Q(refpro__icontains = search, status='Active')

# # __istartswith
#         product_list = models.ProductDetail.objects.filter(serach_query).distinct()

        ### code check ## 
        # product_list = models.ProductDetail.objects.filter(Q(product_name__icontains=search) |Q(product_name_french__icontains=search) |Q(refpro__icontains=search),status='Active').annotate(
        # priority=Case(
        # # STARTSWITH (Highest priority)
        # When(
        #     Q(product_name__istartswith=search) |
        #     Q(product_name_french__istartswith=search) |
        #     Q(refpro__istartswith=search),
        #     then=0
        # ),
        # # CONTAINS (Lower priority)
        # default=1,
        # output_field=IntegerField(),
        # )).order_by("priority", "product_name")


        search_clean = search.replace(" ", "").lower()

        product_list = (
            models.ProductDetail.objects
            .annotate(
                clean_name=Lower(
                    Replace('product_name', Value(' '), Value(''))
                ),
            )
            .annotate(
                similarity=TrigramSimilarity('clean_name', search_clean)
            )
            .filter(
                similarity__gt=0.25,
                status='Active'
            )
            .order_by('-similarity')
        )

        product_serializer = ProductDataSerializer(product_list, many=True,context = {'country':country}).data

        res={
            'data':product_serializer
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)


@csrf_exempt
def product_search_suggestion(request):
    if request.method == "POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))
        search = python_data.get('search')
        # print(search, 'search')
        search_query = Q()
        search_query &= Q(product_name__icontains = search, status='Active') | Q(product_name_french__icontains = search, status='Active') | Q(refpro__icontains = search, status='Active')
        count_product_list = models.ProductDetail.objects.filter(search_query).count()
        # print(count_product_list, 'count_product_list')
        product_list = models.ProductDetail.objects.filter(search_query).distinct()[:15]
        product_serializer = ProductNameSerializer(product_list, many=True).data

        res={
            'data':product_serializer
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)


# @csrf_exempt
# def product_search_by_tag(request):
#     if request.method == "POST":
#         python_data = JSONParser().parse(io.BytesIO(request.body))
#         search = python_data.get('search')
#         country = python_data.get('country')
       
#         tag_list = (
#             models.ProductTag.objects
#             .filter(
#                 tag__icontains=search,
#                 productdetail__available_country__id=country
#             )
#             .distinct()
#         )
#         serializer = ProductTagSearchSerializer(tag_list, many=True).data
#         search_by = "Tag"

#         if serializer == [] or len(serializer) == 0:
#             search_query = Q()
#             search_query &= Q(product_name__icontains = search, status='Active') | Q(refpro__icontains = search, status='Active')
#             search_query &= Q(available_country__id = country)
#             product_list = models.ProductDetail.objects.filter(search_query).distinct()[:15]
#             serializer = DummyTagProductNameEnglishSerializer(product_list, many=True).data
#             search_by = "product_english"

#         if serializer == [] or len(serializer) == 0:
#             search_query = Q()
#             search_query &= Q(product_name__icontains = search, status='Active')| Q(refpro__icontains = search, status='Active')
#             search_query &= Q(available_country__id = country)

#             product_list = models.ProductDetail.objects.filter(search_query).distinct()[:15]
#             serializer = DummyTagProductNameFrenchSerializer(product_list, many=True).data
#             search_by = "product_french"
 
#         res={
#             'data':serializer,
#             'search_by':search_by
#         }
#         return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)




# @csrf_exempt
# def product_search_by_tag(request):

#     if request.method == "POST":

#         python_data = JSONParser().parse(
#             io.BytesIO(request.body)
#         )

#         search = python_data.get('search')
#         country = python_data.get('country')

#         search_clean = ""

#         if search not in [None, '', 'null']:

#             search = str(search).strip()

#             # REMOVE SPACE + - + _
#             search_clean = (
#                 search
#                 .replace(" ", "")
#                 .replace("-", "")
#                 .replace("_", "")
#                 .lower()
#             )

#         tag_queryset = (

#             models.ProductTag.objects

#             .annotate(

#                 clean_tag=Lower(

#                     Replace(
#                         Replace(
#                             Replace(
#                                 'tag',
#                                 Value(' '),
#                                 Value('')
#                             ),
#                             Value('-'),
#                             Value('')
#                         ),
#                         Value('_'),
#                         Value('')
#                     )

#                 ),

#                 priority=Case(

#                     # EXACT MATCH
#                     When(
#                         clean_tag=search_clean,
#                         then=0
#                     ),

#                     # STARTS WITH
#                     When(
#                         clean_tag__startswith=search_clean,
#                         then=1
#                     ),

#                     # WORD STARTS WITH
#                     When(
#                         tag__istartswith=search,
#                         then=2
#                     ),

#                     # CONTAINS
#                     When(
#                         clean_tag__unaccent__icontains=search_clean,
#                         then=3
#                     ),

#                     default=4,

#                     output_field=IntegerField()
#                 )

#             )

#             .filter(

#                 (
#                     Q(tag__unaccent__icontains=search) |

#                     Q(clean_tag__icontains=search_clean)
#                 ),

#                 productdetail__available_country__id=country

#             )

#             .distinct()

#             .order_by(
#                 'priority',
#                 'clean_tag',
#                 'tag'
#             )

#         )

#         serializer = ProductTagSearchSerializer(
#             tag_queryset,
#             many=True
#         ).data

#         search_by = "Tag"

#         if not serializer:

#             product_queryset = (

#                 models.ProductDetail.objects

#                 .annotate(

#                     clean_product_name=Lower(

#                         Replace(
#                             Replace(
#                                 Replace(
#                                     'product_name',
#                                     Value(' '),
#                                     Value('')
#                                 ),
#                                 Value('-'),
#                                 Value('')
#                             ),
#                             Value('_'),
#                             Value('')
#                         )

#                     ),

#                     clean_refpro=Lower(

#                         Replace(
#                             Replace(
#                                 Replace(
#                                     'refpro',
#                                     Value(' '),
#                                     Value('')
#                                 ),
#                                 Value('-'),
#                                 Value('')
#                             ),
#                             Value('_'),
#                             Value('')
#                         )

#                     ),

#                     priority=Case(

#                         # EXACT MATCH
#                         When(
#                             clean_product_name=search_clean,
#                             then=0
#                         ),

#                         # STARTS WITH
#                         When(
#                             clean_product_name__startswith=search_clean,
#                             then=1
#                         ),

#                         # WORD STARTS WITH
#                         When(
#                             product_name__istartswith=search,
#                             then=2
#                         ),

#                         # CONTAINS
#                         When(
#                             clean_product_name__unaccent__icontains=search_clean,
#                             then=3
#                         ),

#                         default=4,

#                         output_field=IntegerField()
#                     )

#                 )

#                 .filter(

#                     (

#                         # NORMAL SEARCH
#                         Q(product_name__unaccent__icontains=search) |

#                         # CLEAN SEARCH
#                         Q(clean_product_name__unaccent__icontains=search_clean) |

#                         # REFPRO
#                         Q(refpro__unaccent__icontains=search) |

#                         Q(clean_refpro__unaccent__icontains=search_clean)

#                     ),

#                     available_country__id=country,
#                     status='Active'

#                 )

#                 .distinct()

#                 .order_by(
#                     'priority',
#                     'clean_product_name',
#                     'product_name'
#                 )[:15]

#             )

#             serializer = (
#                 DummyTagProductNameEnglishSerializer(
#                     product_queryset,
#                     many=True
#                 ).data
#             )

#             search_by = "product_english"

#         if not serializer:

#             product_queryset = (

#                 models.ProductDetail.objects

#                 .annotate(

#                     clean_product_name_french=Lower(

#                         Replace(
#                             Replace(
#                                 Replace(
#                                     'product_name_french',
#                                     Value(' '),
#                                     Value('')
#                                 ),
#                                 Value('-'),
#                                 Value('')
#                             ),
#                             Value('_'),
#                             Value('')
#                         )

#                     ),

#                     clean_refpro=Lower(

#                         Replace(
#                             Replace(
#                                 Replace(
#                                     'refpro',
#                                     Value(' '),
#                                     Value('')
#                                 ),
#                                 Value('-'),
#                                 Value('')
#                             ),
#                             Value('_'),
#                             Value('')
#                         )

#                     ),

#                     priority=Case(

#                         # EXACT MATCH
#                         When(
#                             clean_product_name_french=search_clean,
#                             then=0
#                         ),

#                         # STARTS WITH
#                         When(
#                             clean_product_name_french__startswith=search_clean,
#                             then=1
#                         ),

#                         # WORD STARTS WITH
#                         When(
#                             product_name_french__istartswith=search,
#                             then=2
#                         ),

#                         # CONTAINS
#                         When(
#                             clean_product_name_french__unaccent__icontains=search_clean,
#                             then=3
#                         ),

#                         default=4,

#                         output_field=IntegerField()
#                     )

#                 )

#                 .filter(

#                     (

#                         # NORMAL SEARCH
#                         Q(product_name_french__unaccent__icontains=search) |

#                         # CLEAN SEARCH
#                         Q(clean_product_name_french__unaccent__icontains=search_clean) |

#                         # REFPRO
#                         Q(refpro__unaccent__icontains=search) |

#                         Q(clean_refpro__unaccent__icontains=search_clean)

#                     ),

#                     available_country__id=country,
#                     status='Active'

#                 )

#                 .distinct()

#                 .order_by(
#                     'priority',
#                     'clean_product_name_french',
#                     'product_name_french'
#                 )[:15]

#             )

#             serializer = (
#                 DummyTagProductNameFrenchSerializer(
#                     product_queryset,
#                     many=True
#                 ).data
#             )

#             search_by = "product_french"

#         res = {
#             'data': serializer,
#             'search_by': search_by
#         }

#         return HttpResponse(
#             JSONRenderer().render(res),
#             content_type='application/json',
#             status=200
#         )



# @csrf_exempt
# def product_search_by_tag(request):

#     if request.method == "POST":

#         python_data = JSONParser().parse(
#             io.BytesIO(request.body)
#         )

#         search = python_data.get('search')
#         country = python_data.get('country')

#         # SAFE SEARCH
#         search = str(search or "").strip()

#         if search.lower() == 'null':
#             search = ""

#         # REMOVE SPACE + - + _
#         search_clean = (
#             search
#             .replace(" ", "")
#             .replace("-", "")
#             .replace("_", "")
#             .lower()
#         )

#         # =========================
#         # TAG SEARCH
#         # =========================
#         tag_queryset = (

#             models.ProductTag.objects

#             .annotate(

#                 clean_tag=Lower(

#                     Replace(
#                         Replace(
#                             Replace(
#                                 'tag',
#                                 Value(' '),
#                                 Value('')
#                             ),
#                             Value('-'),
#                             Value('')
#                         ),
#                         Value('_'),
#                         Value('')
#                     )

#                 ),

#                 priority=Case(

#                     # EXACT MATCH
#                     When(
#                         clean_tag=search_clean,
#                         then=0
#                     ),

#                     # STARTS WITH
#                     When(
#                         clean_tag__startswith=search_clean,
#                         then=1
#                     ),

#                     # WORD STARTS WITH
#                     When(
#                         tag__istartswith=search,
#                         then=2
#                     ),

#                     # CONTAINS
#                     When(
#                         clean_tag__icontains=search_clean,
#                         then=3
#                     ),

#                     default=4,
#                     output_field=IntegerField()
#                 )

#             )

#             .filter(

#                 (
#                     Q(tag__unaccent__icontains=search) |
#                     Q(clean_tag__icontains=search_clean)
#                 ),

#                 productdetail__available_country__id=country

#             )

#             .distinct()

#             .order_by(
#                 'priority',
#                 'clean_tag',
#                 'tag'
#             )
#         )

#         serializer = ProductTagSearchSerializer(
#             tag_queryset,
#             many=True
#         ).data

#         search_by = "Tag"

#         # =========================
#         # ENGLISH PRODUCT SEARCH
#         # =========================
#         if not serializer:

#             product_queryset = (

#                 models.ProductDetail.objects

#                 .annotate(

#                     clean_product_name=Lower(

#                         Replace(
#                             Replace(
#                                 Replace(
#                                     'product_name',
#                                     Value(' '),
#                                     Value('')
#                                 ),
#                                 Value('-'),
#                                 Value('')
#                             ),
#                             Value('_'),
#                             Value('')
#                         )
#                     ),

#                     clean_refpro=Lower(

#                         Replace(
#                             Replace(
#                                 Replace(
#                                     'refpro',
#                                     Value(' '),
#                                     Value('')
#                                 ),
#                                 Value('-'),
#                                 Value('')
#                             ),
#                             Value('_'),
#                             Value('')
#                         )
#                     ),

#                     priority=Case(

#                         # EXACT MATCH
#                         When(
#                             clean_product_name=search_clean,
#                             then=0
#                         ),

#                         # STARTS WITH
#                         When(
#                             clean_product_name__startswith=search_clean,
#                             then=1
#                         ),

#                         # WORD STARTS WITH
#                         When(
#                             product_name__istartswith=search,
#                             then=2
#                         ),

#                         # CONTAINS
#                         When(
#                             clean_product_name__icontains=search_clean,
#                             then=3
#                         ),

#                         default=4,
#                         output_field=IntegerField()
#                     )

#                 )

#                 .filter(

#                     (
#                         # PRODUCT NAME
#                         Q(product_name__unaccent__icontains=search) |

#                         # CLEAN PRODUCT NAME
#                         Q(clean_product_name__icontains=search_clean) |

#                         # REFPRO
#                         Q(refpro__unaccent__icontains=search) |

#                         # CLEAN REFPRO
#                         Q(clean_refpro__icontains=search_clean)

#                     ),

#                     available_country__id=country,
#                     status='Active'

#                 )

#                 .distinct()

#                 .order_by(
#                     'priority',
#                     'clean_product_name',
#                     'product_name'
#                 )[:15]

#             )

#             serializer = (
#                 DummyTagProductNameEnglishSerializer(
#                     product_queryset,
#                     many=True
#                 ).data
#             )

#             search_by = "product_english"

#         # =========================
#         # FRENCH PRODUCT SEARCH
#         # =========================
#         if not serializer:

#             product_queryset = (

#                 models.ProductDetail.objects

#                 .annotate(

#                     clean_product_name_french=Lower(

#                         Replace(
#                             Replace(
#                                 Replace(
#                                     'product_name_french',
#                                     Value(' '),
#                                     Value('')
#                                 ),
#                                 Value('-'),
#                                 Value('')
#                             ),
#                             Value('_'),
#                             Value('')
#                         )

#                     ),

#                     clean_refpro=Lower(

#                         Replace(
#                             Replace(
#                                 Replace(
#                                     'refpro',
#                                     Value(' '),
#                                     Value('')
#                                 ),
#                                 Value('-'),
#                                 Value('')
#                             ),
#                             Value('_'),
#                             Value('')
#                         )

#                     ),

#                     priority=Case(

#                         # EXACT MATCH
#                         When(
#                             clean_product_name_french=search_clean,
#                             then=0
#                         ),

#                         # STARTS WITH
#                         When(
#                             clean_product_name_french__startswith=search_clean,
#                             then=1
#                         ),

#                         # WORD STARTS WITH
#                         When(
#                             product_name_french__istartswith=search,
#                             then=2
#                         ),

#                         # CONTAINS
#                         When(
#                             clean_product_name_french__icontains=search_clean,
#                             then=3
#                         ),

#                         default=4,
#                         output_field=IntegerField()
#                     )

#                 )

#                 .filter(

#                     (
#                         # NORMAL SEARCH
#                         Q(product_name_french__unaccent__icontains=search) |

#                         # CLEAN SEARCH
#                         Q(clean_product_name_french__icontains=search_clean) |

#                         # REFPRO
#                         Q(refpro__unaccent__icontains=search) |

#                         # CLEAN REFPRO
#                         Q(clean_refpro__icontains=search_clean)

#                     ),

#                     available_country__id=country,
#                     status='Active'

#                 )

#                 .distinct()

#                 .order_by(
#                     'priority',
#                     'clean_product_name_french',
#                     'product_name_french'
#                 )[:15]

#             )

#             serializer = (
#                 DummyTagProductNameFrenchSerializer(
#                     product_queryset,
#                     many=True
#                 ).data
#             )

#             search_by = "product_french"

#         res = {
#             'data': serializer,
#             'search_by': search_by
#         }

#         return HttpResponse(
#             JSONRenderer().render(res),
#             content_type='application/json',
#             status=200
#         )

#     return HttpResponse(
#         JSONRenderer().render({
#             'message': 'Invalid request method'
#         }),
#         content_type='application/json',
#         status=405
#     )


# @csrf_exempt
# def product_search_by_tag(request):

#     if request.method != "POST":
#         return HttpResponse(
#             JSONRenderer().render({
#                 'message': 'Invalid request method'
#             }),
#             content_type='application/json',
#             status=405
#         )

#     try:

#         python_data = JSONParser().parse(
#             io.BytesIO(request.body)
#         )

#         print("python_data---->", python_data)

#         search = python_data.get('search')
#         country = python_data.get('country')
#         country_name = python_data.get(
#             'countryName',
#             'Egypt'
#         )

#         # =========================
#         # SAFE SEARCH
#         # =========================
#         search = str(search or "").strip()

#         if search.lower() == 'null':
#             search = ""

#         search_clean = (
#             search
#             .replace(" ", "")
#             .replace("-", "")
#             .replace("_", "")
#             .lower()
#         )

#         serializer_context = {
#             'country': country_name
#         }

#         # =========================
#         # TAG SEARCH
#         # =========================
#         tag_queryset = (

#             models.ProductTag.objects

#             .annotate(

#                 clean_tag=Lower(

#                     Replace(
#                         Replace(
#                             Replace(
#                                 'tag',
#                                 Value(' '),
#                                 Value('')
#                             ),
#                             Value('-'),
#                             Value('')
#                         ),
#                         Value('_'),
#                         Value('')
#                     )

#                 ),

#                 priority=Case(

#                     # EXACT MATCH
#                     When(
#                         clean_tag=search_clean,
#                         then=0
#                     ),

#                     # STARTS WITH
#                     When(
#                         clean_tag__startswith=search_clean,
#                         then=1
#                     ),

#                     # WORD STARTS WITH
#                     When(
#                         tag__istartswith=search,
#                         then=2
#                     ),

#                     # CONTAINS
#                     When(
#                         clean_tag__icontains=search_clean,
#                         then=3
#                     ),

#                     default=4,
#                     output_field=IntegerField()
#                 )

#             )

#             .filter(

#                 (
#                     Q(tag__unaccent__icontains=search) |
#                     Q(clean_tag__icontains=search_clean)
#                 ),

#                 productdetail__available_country__id=country

#             )

#             .distinct()

#             .order_by(
#                 'priority',
#                 'clean_tag',
#                 'tag'
#             )
#         )

#         serializer = ProductTagSearchSerializer(
#             tag_queryset,
#             many=True,
#             context=serializer_context
#         ).data

#         search_by = "Tag"

#         # =========================
#         # ENGLISH PRODUCT SEARCH
#         # =========================
#         if not serializer:

#             product_queryset = (

#                 models.ProductDetail.objects

#                 .annotate(

#                     clean_product_name=Lower(

#                         Replace(
#                             Replace(
#                                 Replace(
#                                     'product_name',
#                                     Value(' '),
#                                     Value('')
#                                 ),
#                                 Value('-'),
#                                 Value('')
#                             ),
#                             Value('_'),
#                             Value('')
#                         )

#                     ),

#                     clean_refpro=Lower(

#                         Replace(
#                             Replace(
#                                 Replace(
#                                     'refpro',
#                                     Value(' '),
#                                     Value('')
#                                 ),
#                                 Value('-'),
#                                 Value('')
#                             ),
#                             Value('_'),
#                             Value('')
#                         )

#                     ),

#                     priority=Case(

#                         # EXACT MATCH
#                         When(
#                             clean_product_name=search_clean,
#                             then=0
#                         ),

#                         # STARTS WITH
#                         When(
#                             clean_product_name__startswith=search_clean,
#                             then=1
#                         ),

#                         # WORD STARTS WITH
#                         When(
#                             product_name__istartswith=search,
#                             then=2
#                         ),

#                         # CONTAINS
#                         When(
#                             clean_product_name__icontains=search_clean,
#                             then=3
#                         ),

#                         default=4,
#                         output_field=IntegerField()
#                     )

#                 )

#                 .filter(

#                     (
#                         Q(product_name__unaccent__icontains=search) |

#                         Q(clean_product_name__icontains=search_clean) |

#                         Q(refpro__unaccent__icontains=search) |

#                         Q(clean_refpro__icontains=search_clean)

#                     ),

#                     available_country__id=country,
#                     status='Active'

#                 )

#                 .distinct()

#                 .order_by(
#                     'priority',
#                     'clean_product_name',
#                     'product_name'
#                 )[:15]

#             )

#             serializer = (
#                 DummyTagProductNameEnglishSerializer(
#                     product_queryset,
#                     many=True,
#                     context=serializer_context
#                 ).data
#             )

#             search_by = "product_english"

#         # =========================
#         # FRENCH PRODUCT SEARCH
#         # =========================
#         if not serializer:

#             product_queryset = (

#                 models.ProductDetail.objects

#                 .annotate(

#                     clean_product_name_french=Lower(

#                         Replace(
#                             Replace(
#                                 Replace(
#                                     'product_name_french',
#                                     Value(' '),
#                                     Value('')
#                                 ),
#                                 Value('-'),
#                                 Value('')
#                             ),
#                             Value('_'),
#                             Value('')
#                         )

#                     ),

#                     clean_refpro=Lower(

#                         Replace(
#                             Replace(
#                                 Replace(
#                                     'refpro',
#                                     Value(' '),
#                                     Value('')
#                                 ),
#                                 Value('-'),
#                                 Value('')
#                             ),
#                             Value('_'),
#                             Value('')
#                         )

#                     ),

#                     priority=Case(

#                         # EXACT MATCH
#                         When(
#                             clean_product_name_french=search_clean,
#                             then=0
#                         ),

#                         # STARTS WITH
#                         When(
#                             clean_product_name_french__startswith=search_clean,
#                             then=1
#                         ),

#                         # WORD STARTS WITH
#                         When(
#                             product_name_french__istartswith=search,
#                             then=2
#                         ),

#                         # CONTAINS
#                         When(
#                             clean_product_name_french__icontains=search_clean,
#                             then=3
#                         ),

#                         default=4,
#                         output_field=IntegerField()
#                     )

#                 )

#                 .filter(

#                     (
#                         Q(product_name_french__unaccent__icontains=search) |

#                         Q(clean_product_name_french__icontains=search_clean) |

#                         Q(refpro__unaccent__icontains=search) |

#                         Q(clean_refpro__icontains=search_clean)

#                     ),

#                     available_country__id=country,
#                     status='Active'

#                 )

#                 .distinct()

#                 .order_by(
#                     'priority',
#                     'clean_product_name_french',
#                     'product_name_french'
#                 )[:15]

#             )

#             serializer = (
#                 DummyTagProductNameFrenchSerializer(
#                     product_queryset,
#                     many=True,
#                     context=serializer_context
#                 ).data
#             )

#             search_by = "product_french"

#         res = {
#             'status': True,
#             'search_by': search_by,
#             'data': serializer
#         }

#         return HttpResponse(
#             JSONRenderer().render(res),
#             content_type='application/json',
#             status=200
#         )

#     except Exception as e:

#         print("error----->", str(e))

#         return HttpResponse(
#             JSONRenderer().render({
#                 'status': False,
#                 'message': str(e)
#             }),
#             content_type='application/json',
#             status=400
#         )




# @csrf_exempt
# def product_search_by_tag(request):

#     if request.method != "POST":
#         return HttpResponse(
#             JSONRenderer().render({
#                 'message': 'Invalid request method'
#             }),
#             content_type='application/json',
#             status=405
#         )

#     try:
#         python_data = JSONParser().parse(io.BytesIO(request.body))

#         search = python_data.get('search')
#         country = python_data.get('country')
#         country_name = python_data.get('countryName', 'Egypt')

#         search = str(search or "").strip()

#         if search.lower() == 'null':
#             search = ""

#         search_clean = (
#             search.replace(" ", "")
#                   .replace("-", "")
#                   .replace("_", "")
#                   .lower()
#         )

#         serializer_context = {
#             'country': country_name
#         }

#         # =========================
#         # TAG SEARCH (UNCHANGED)
#         # =========================
#         tag_queryset = (
#             models.ProductTag.objects.annotate(
#                 clean_tag=Lower(
#                     Replace(
#                         Replace(
#                             Replace('tag', Value(' '), Value('')),
#                             Value('-'), Value('')
#                         ),
#                         Value('_'), Value('')
#                     )
#                 ),
#                 priority=Case(
#                     When(clean_tag=search_clean, then=0),
#                     When(clean_tag__startswith=search_clean, then=1),
#                     When(tag__istartswith=search, then=2),
#                     When(clean_tag__icontains=search_clean, then=3),
#                     default=4,
#                     output_field=IntegerField()
#                 )
#             )
#             .filter(
#                 Q(tag__unaccent__icontains=search) |
#                 Q(clean_tag__icontains=search_clean),
#                 productdetail__available_country__id=country
#             )
#             .distinct()
#             .order_by('priority', 'clean_tag', 'tag')
#         )

#         serializer = ProductTagSearchSerializer(
#             tag_queryset,
#             many=True,
#             context=serializer_context
#         ).data

#         search_by = "Tag"

#         # =========================
#         # ENGLISH PRODUCT SEARCH (FUZZY ENABLED)
#         # =========================
#         if not serializer:

#             product_queryset = (
#                 models.ProductDetail.objects
#                 .annotate(
#                     similarity_name=TrigramSimilarity('product_name', search),
#                     similarity_ref=TrigramSimilarity('refpro', search),

#                     clean_product_name=Lower(
#                         Replace(
#                             Replace(
#                                 Replace('product_name', Value(' '), Value('')),
#                                 Value('-'), Value('')
#                             ),
#                             Value('_'), Value('')
#                         )
#                     ),

#                     clean_refpro=Lower(
#                         Replace(
#                             Replace(
#                                 Replace('refpro', Value(' '), Value('')),
#                                 Value('-'), Value('')
#                             ),
#                             Value('_'), Value('')
#                         )
#                     ),

#                     priority=Case(
#                         When(clean_product_name=search_clean, then=0),
#                         When(clean_product_name__startswith=search_clean, then=1),
#                         When(product_name__istartswith=search, then=2),
#                         When(clean_product_name__icontains=search_clean, then=3),
#                         default=4,
#                         output_field=IntegerField()
#                     )
#                 )
#                 .annotate(
#                     best_similarity=Greatest('similarity_name', 'similarity_ref')
#                 )
#                 .filter(
#                     Q(product_name__unaccent__icontains=search) |
#                     Q(clean_product_name__icontains=search_clean) |
#                     Q(refpro__unaccent__icontains=search) |
#                     Q(clean_refpro__icontains=search_clean) |
#                     Q(best_similarity__gt=0.2),

#                     available_country__id=country,
#                     status='Active'
#                 )
#                 .distinct()
#                 .order_by('-best_similarity', 'priority', 'clean_product_name')[:15]
#             )

#             serializer = DummyTagProductNameEnglishSerializer(
#                 product_queryset,
#                 many=True,
#                 context=serializer_context
#             ).data

#             search_by = "product_english"

#         # =========================
#         # FRENCH PRODUCT SEARCH (FUZZY ENABLED)
#         # =========================
#         if not serializer:

#             product_queryset = (
#                 models.ProductDetail.objects
#                 .annotate(
#                     similarity_name=TrigramSimilarity('product_name_french', search),
#                     similarity_ref=TrigramSimilarity('refpro', search),

#                     clean_product_name_french=Lower(
#                         Replace(
#                             Replace(
#                                 Replace('product_name_french', Value(' '), Value('')),
#                                 Value('-'), Value('')
#                             ),
#                             Value('_'), Value('')
#                         )
#                     ),

#                     clean_refpro=Lower(
#                         Replace(
#                             Replace(
#                                 Replace('refpro', Value(' '), Value('')),
#                                 Value('-'), Value('')
#                             ),
#                             Value('_'), Value('')
#                         )
#                     ),

#                     priority=Case(
#                         When(clean_product_name_french=search_clean, then=0),
#                         When(clean_product_name_french__startswith=search_clean, then=1),
#                         When(product_name_french__istartswith=search, then=2),
#                         When(clean_product_name_french__icontains=search_clean, then=3),
#                         default=4,
#                         output_field=IntegerField()
#                     )
#                 )
#                 .annotate(
#                     best_similarity=Greatest('similarity_name', 'similarity_ref')
#                 )
#                 .filter(
#                     Q(product_name_french__unaccent__icontains=search) |
#                     Q(clean_product_name_french__icontains=search_clean) |
#                     Q(refpro__unaccent__icontains=search) |
#                     Q(clean_refpro__icontains=search_clean) |
#                     Q(best_similarity__gt=0.2),

#                     available_country__id=country,
#                     status='Active'
#                 )
#                 .distinct()
#                 .order_by('-best_similarity', 'priority', 'clean_product_name_french')[:15]
#             )

#             serializer = DummyTagProductNameFrenchSerializer(
#                 product_queryset,
#                 many=True,
#                 context=serializer_context
#             ).data

#             search_by = "product_french"

#         # =========================
#         # RESPONSE
#         # =========================
#         res = {
#             'status': True,
#             'search_by': search_by,
#             'data': serializer
#         }

#         return HttpResponse(
#             JSONRenderer().render(res),
#             content_type='application/json',
#             status=200
#         )

#     except Exception as e:
#         return HttpResponse(
#             JSONRenderer().render({
#                 'status': False,
#                 'message': str(e)
#             }),
#             content_type='application/json',
#             status=400
#         )



def get_product_result(
    tag,
    country,
    search_by,
    search,
    country_name
):
    search_query = Q()

    search_query &= Q(available_country__id=country)

    # -----------------------------
    # TAG FILTER
    # -----------------------------
    if tag not in [None, '', 'null']:

        if search_by == "Tag":

            search_query &= Q(tag__id=tag)

        elif search_by == "product_english":

            product = models.ProductDetail.objects.filter(
                id=tag
            ).first()

            if product:
                search_query &= Q(
                    product_name__unaccent__icontains=
                    product.product_name
                )

        elif search_by == "product_french":

            product = models.ProductDetail.objects.filter(
                id=tag
            ).first()

            if product:
                search_query &= Q(
                    product_name_french__unaccent__icontains=
                    product.product_name_french
                )

    search_clean = ""

    if search not in [None, '', 'null']:
        search = search.strip()
        search_clean = search.replace(" ", "").lower()

    products = models.ProductDetail.objects.annotate(

        clean_product_name=Lower(
            Replace('product_name', Value(' '), Value(''))
        ),

        clean_product_name_french=Lower(
            Replace('product_name_french', Value(' '), Value(''))
        ),

        clean_refpro=Lower(
            Replace('refpro', Value(' '), Value(''))
        )
    )

    # -----------------------------
    # SEARCH FILTER
    # -----------------------------
    # if search_clean:

    #     products = products.annotate(

    #         similarity_name=TrigramSimilarity(
    #             'product_name',
    #             search
    #         ),

    #         similarity_name_french=TrigramSimilarity(
    #             'product_name_french',
    #             search
    #         ),

    #         similarity_refpro=TrigramSimilarity(
    #             'refpro',
    #             search
    #         )
    #     )

    #     search_words = search.lower().split()

    #     word_query = Q()

    #     for word in search_words:

    #         word_query |= Q(
    #             product_name__unaccent__icontains=word
    #         )

    #         word_query |= Q(
    #             product_name_french__unaccent__icontains=word
    #         )

    #         word_query |= Q(
    #             refpro__unaccent__icontains=word
    #         )

    #     search_query &= (
    #         word_query |
    #         Q(similarity_name__gt=0.15) |
    #         Q(similarity_name_french__gt=0.15) |
    #         Q(similarity_refpro__gt=0.15)
    #     )

    if search_clean:

        import re

        normalized_search = re.sub(
            r'(.)\1+',
            r'\1',
            search.lower()
        )

        products = products.annotate(

            similarity_name=TrigramSimilarity(
                'product_name',
                normalized_search
            ),

            similarity_name_word=TrigramWordSimilarity(
                normalized_search,
                'product_name'
            ),

            similarity_name_french=TrigramSimilarity(
                'product_name_french',
                normalized_search
            ),

            similarity_name_french_word=TrigramWordSimilarity(
                normalized_search,
                'product_name_french'
            ),

            similarity_refpro=TrigramSimilarity(
                'refpro',
                normalized_search
            ),

            similarity_refpro_word=TrigramWordSimilarity(
                normalized_search,
                'refpro'
            )

        ).annotate(

            best_similarity=Greatest(
                'similarity_name',
                'similarity_name_word',
                'similarity_name_french',
                'similarity_name_french_word',
                'similarity_refpro',
                'similarity_refpro_word'
            )
        )

        search_words = normalized_search.split()

        word_query = Q()

        for word in search_words:

            word_query |= Q(
                product_name__unaccent__icontains=word
            )

            word_query |= Q(
                product_name_french__unaccent__icontains=word
            )

            word_query |= Q(
                refpro__unaccent__icontains=word
            )

        search_query &= (
            word_query |
            Q(best_similarity__gt=0.30)
        )

    tag_result = (
        products
        .filter(
            search_query,
            status='Active'
        )
        .distinct()
        .order_by(
            '-best_similarity',
            'product_name'
        )
    )

    tag_result_serializer = ProductSearchSerializer(
        tag_result,
        many=True,
        context={'country': country_name}
    ).data

    # -----------------------------
    # FALLBACK SEARCH
    # -----------------------------
    if not tag_result_serializer:

        try:

            tag_name = (
                models.ProductTag.objects
                .get(id=tag)
                .tag
            )

            fallback_search = (
                tag_name
                .replace(" ", "")
                .lower()
            )

            without_tag_result = (
                products
                .filter(
                    (
                        Q(
                            clean_product_name__unaccent__icontains=
                            fallback_search
                        ) |
                        Q(
                            clean_product_name_french__unaccent__icontains=
                            fallback_search
                        ) |
                        Q(
                            clean_refpro__unaccent__icontains=
                            fallback_search
                        )
                    ),
                    available_country__id=country,
                    status='Active'
                )
                .distinct()
            )

            tag_result_serializer = ProductSearchSerializer(
                without_tag_result,
                many=True,
                context={
                    'country': country_name
                }
            ).data

        except Exception:

            without_tag_result = (
                products
                .filter(
                    (
                        Q(
                            clean_product_name__unaccent__icontains=
                            search_clean
                        ) |
                        Q(
                            clean_product_name_french__unaccent__icontains=
                            search_clean
                        ) |
                        Q(
                            clean_refpro__unaccent__icontains=
                            search_clean
                        )
                    ),
                    available_country__id=country,
                    status='Active'
                )
                .distinct()
            )

            tag_result_serializer = ProductSearchSerializer(
                without_tag_result,
                many=True,
                context={
                    'country': country_name
                }
            ).data

    return tag_result_serializer



@csrf_exempt
def product_search_by_tag(request):

    if request.method != "POST":
        return HttpResponse(
            JSONRenderer().render({
                'message': 'Invalid request method'
            }),
            content_type='application/json',
            status=405
        )

    try:

        python_data = JSONParser().parse(
            io.BytesIO(request.body)
        )

        search = python_data.get('search')
        country = python_data.get('country')
        country_name = python_data.get(
            'countryName',
            'Egypt'
        )

        search = str(search or "").strip()

        if search.lower() == 'null':
            search = ""

        search_clean = (
            search
            .replace(" ", "")
            .replace("-", "")
            .replace("_", "")
            .lower()
        )

        serializer_context = {
            'country': country_name
        }

        # =====================================
        # TAG SEARCH
        # =====================================

        tag_queryset = (
            models.ProductTag.objects
            .annotate(
                clean_tag=Lower(
                    Replace(
                        Replace(
                            Replace(
                                'tag',
                                Value(' '),
                                Value('')
                            ),
                            Value('-'),
                            Value('')
                        ),
                        Value('_'),
                        Value('')
                    )
                ),
                priority=Case(
                    When(
                        clean_tag=search_clean,
                        then=0
                    ),
                    When(
                        clean_tag__startswith=search_clean,
                        then=1
                    ),
                    When(
                        tag__istartswith=search,
                        then=2
                    ),
                    When(
                        clean_tag__icontains=search_clean,
                        then=3
                    ),
                    default=4,
                    output_field=IntegerField()
                )
            )
            .filter(
                Q(tag__unaccent__icontains=search) |
                Q(clean_tag__icontains=search_clean),
                productdetail__available_country__id=country
            )
            .distinct()
            .order_by(
                'priority',
                'clean_tag',
                'tag'
            )
        )

        serializer = ProductTagSearchSerializer(
            tag_queryset,
            many=True,
            context=serializer_context
        ).data

        # =====================================
        # TAG FOUND
        # =====================================

        if serializer:

            products = get_product_result(
                tag=serializer[0]['id'],
                country=country,
                search_by="Tag",
                search=search,
                country_name=country_name
            )

            return HttpResponse(
                JSONRenderer().render({
                    'status': True,
                    'search_by': 'Tag',
                    'data': serializer,
                    'products': products
                }),
                content_type='application/json',
                status=200
            )

        # =====================================
        # ENGLISH PRODUCT SEARCH
        # =====================================

        product_queryset = (
            models.ProductDetail.objects
            .annotate(
                similarity_name=TrigramWordSimilarity(
                    search,
                    'product_name'
                ),

                similarity_ref=TrigramWordSimilarity(
                    search,
                    'refpro'
                ),

                clean_product_name=Lower(
                    Replace(
                        Replace(
                            Replace(
                                'product_name',
                                Value(' '),
                                Value('')
                            ),
                            Value('-'),
                            Value('')
                        ),
                        Value('_'),
                        Value('')
                    )
                ),

                clean_refpro=Lower(
                    Replace(
                        Replace(
                            Replace(
                                'refpro',
                                Value(' '),
                                Value('')
                            ),
                            Value('-'),
                            Value('')
                        ),
                        Value('_'),
                        Value('')
                    )
                ),
            )
            .annotate(
                best_similarity=Greatest(
                    'similarity_name',
                    'similarity_ref'
                )
            )
            .filter(
                available_country__id=country,
                status='Active'
            )
            .filter(
                Q(product_name__unaccent__icontains=search) |
                Q(clean_product_name__icontains=search_clean) |
                Q(refpro__unaccent__icontains=search) |
                Q(clean_refpro__icontains=search_clean) |
                Q(best_similarity__gt=0.10)
            )
            .distinct()
            .order_by('-best_similarity', 'product_name')[:15]
        )

        serializer = DummyTagProductNameEnglishSerializer(
            product_queryset,
            many=True,
            context=serializer_context
        ).data

        if serializer:

            products = get_product_result(
                tag=serializer[0]['id'],
                country=country,
                search_by="product_english",
                search=search,
                country_name=country_name
            )

            return HttpResponse(
                JSONRenderer().render({
                    'status': True,
                    'search_by': 'product_english',
                    'data': serializer,
                    'products': products
                }),
                content_type='application/json',
                status=200
            )

        # =====================================
        # FRENCH PRODUCT SEARCH
        # =====================================

        product_queryset = (
            models.ProductDetail.objects
            .annotate(
                similarity_name=TrigramWordSimilarity(
                    search,
                    'product_name_french'
                ),

                similarity_ref=TrigramWordSimilarity(
                    search,
                    'refpro'
                ),

                clean_product_name_french=Lower(
                    Replace(
                        Replace(
                            Replace(
                                'product_name_french',
                                Value(' '),
                                Value('')
                            ),
                            Value('-'),
                            Value('')
                        ),
                        Value('_'),
                        Value('')
                    )
                ),

                clean_refpro=Lower(
                    Replace(
                        Replace(
                            Replace(
                                'refpro',
                                Value(' '),
                                Value('')
                            ),
                            Value('-'),
                            Value('')
                        ),
                        Value('_'),
                        Value('')
                    )
                ),
            )
            .annotate(
                best_similarity=Greatest(
                    'similarity_name',
                    'similarity_ref'
                )
            )
            .filter(
                available_country__id=country,
                status='Active'
            )
            .filter(
                Q(product_name_french__unaccent__icontains=search) |
                Q(clean_product_name_french__icontains=search_clean) |
                Q(refpro__unaccent__icontains=search) |
                Q(clean_refpro__icontains=search_clean) |
                Q(best_similarity__gt=0.10)
            )
            .distinct()
            .order_by('-best_similarity', 'product_name_french')[:15]
        )

        serializer = DummyTagProductNameFrenchSerializer(
            product_queryset,
            many=True,
            context=serializer_context
        ).data

        if serializer:

            products = get_product_result(
                tag=serializer[0]['id'],
                country=country,
                search_by="product_french",
                search=search,
                country_name=country_name
            )

            return HttpResponse(
                JSONRenderer().render({
                    'status': True,
                    'search_by': 'product_french',
                    'data': serializer,
                    'products': products
                }),
                content_type='application/json',
                status=200
            )

        return HttpResponse(
            JSONRenderer().render({
                'status': True,
                'search_by': '',
                'data': [],
                'products': []
            }),
            content_type='application/json',
            status=200
        )

    except Exception as e:

        return HttpResponse(
            JSONRenderer().render({
                'status': False,
                'message': str(e)
            }),
            content_type='application/json',
            status=400
        )





# @csrf_exempt
# def product_list_tag_result(request):
#     if request.method == "POST":
#         python_data = JSONParser().parse(io.BytesIO(request.body))

#         print("python_data---->",python_data)

#         tag = python_data.get('tag')
#         country = python_data.get('country')
#         search_by = python_data.get('search_by')
#         search = python_data.get('search')

#         search_query = Q()

#         if country not in [None,'','null'] and isinstance(country, int):
#             search_query &= Q(available_country__id = country)

#         if tag not in [None,'','null']:
#             if search_by == "Tag":
#                 search_query &= Q(tag__id = tag)

#             elif search_by == "product_english":
#                 product_name = models.ProductDetail.objects.filter(id = tag).first().product_name
#                 print("product_name=======>",product_name)
#                 search_query &= Q(product_name__icontains = product_name)
#             elif search_by == "product_french":
#                 product_name_french = models.ProductDetail.objects.filter(id = tag).first().product_name_french
#                 search_query &= Q(product_name_french__icontains = product_name_french)
#         if search not in [None,'','null']:
#             search_query &= Q(product_name__icontains = search)
#             search_query &= Q(product_name_french__icontains = search)
                
#         tag_result = models.ProductDetail.objects.filter(search_query, status='Active').distinct()
#         tag_result_serializer = ProductSearchSerializer(tag_result, many=True).data


#         if tag_result_serializer == []:
#             try:
#                 tag_name = models.ProductTag.objects.get(id = tag).tag
#                 without_tag_result = models.ProductDetail.objects.filter(Q(product_name__icontains = tag_name)|Q(product_name_french__icontains = tag_name),Q(available_country__id = country), status='Active').distinct()
#                 tag_result_serializer = ProductSearchSerializer(without_tag_result, many=True).data
#             except:
#                 try:
#                     without_tag_result = models.ProductDetail.objects.filter(Q(product_name__icontains = search)|Q(product_name_french__icontains = search),Q(available_country__id = country), status='Active').distinct()
#                     tag_result_serializer = ProductSearchSerializer(without_tag_result, many=True).data
#                 except:
#                     tag_result_serializer = []


#         print("tag_result_serializer=======>",tag_result_serializer)
            
        
#         res={
#             'data':tag_result_serializer
#         }
#         return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)


# @csrf_exempt
# def product_list_tag_result(request):
#     if request.method == "POST":
#         python_data = JSONParser().parse(io.BytesIO(request.body))
#         print("python_data---->", python_data)

#         tag = python_data.get('tag')
#         country = python_data.get('country')
#         search_by = python_data.get('search_by')
#         search = python_data.get('search')

#         search_query = Q(status='Active')

#         # 1. Country Filter
#         if country not in [None, '', 'null'] and isinstance(country, int):
#             search_query &= Q(available_country__id=country)

#         # 2. Tag / Search By Filter
#         if tag not in [None, '', 'null']:
#             if search_by == "Tag":
#                 search_query &= Q(tag__id=tag)
#             elif search_by == "product_english":
#                 product_obj = models.ProductDetail.objects.filter(id=tag).first()
#                 if product_obj:
#                     search_query &= Q(product_name__icontains=product_obj.product_name)
#             elif search_by == "product_french":
#                 product_obj = models.ProductDetail.objects.filter(id=tag).first()
#                 if product_obj and product_obj.product_name_french:
#                     search_query &= Q(product_name_french__icontains=product_obj.product_name_french)

                
#         # if search not in [None, '', 'null']:
#         #     search_words = search.split()
#         #     word_query = Q()
#         #     for word in search_words:
#         #         # If they typed 'Pistole', match 'pistolet' by checking the root 'pistol'
#         #         # If they typed 'auto', match 'automatique' by checking 'auto'
#         #         clean_word = word[:-1] if (len(word) > 5 and word.lower().endswith('e')) else word
                
#         #         # BOTH words must match somewhere in the product fields
#         #         word_query &= (Q(product_name__icontains=clean_word) | Q(product_name_french__icontains=clean_word))
            
#         #     search_query &= word_query
#         if search not in [None, '', 'null']:
#             # Annotate your query with a similarity score for both languages
#             tag_result = models.ProductDetail.objects.annotate(
#                 sim_en=TrigramSimilarity('product_name', search),
#                 sim_fr=TrigramSimilarity('product_name_french', search),
#             ).filter(
#                 # 0.2 means 20% similar. "iphne" vs "iphone" easily passes this threshold
#                 Q(sim_en__gt=0.2) | Q(sim_fr__gt=0.2), 
#                 status='Active',
#                 available_country__id=country
#             ).order_by('-sim_en', '-sim_fr') # This places the closest matches first!
            
#             tag_result_serializer = ProductSearchSerializer(tag_result, many=True).data


#         # # Execute primary query
#         # tag_result = models.ProductDetail.objects.filter(search_query).distinct()
#         # tag_result_serializer = ProductSearchSerializer(tag_result, many=True).data

#         # 4. Fallback Logic if no products found
#         if not tag_result_serializer:
#             # Fallback A: Try searching by Tag Name if tag is provided
#             if tag not in [None, '', 'null']:
#                 try:
#                     tag_name = models.ProductTag.objects.get(id=tag).tag
#                     without_tag_result = models.ProductDetail.objects.filter(
#                         (Q(product_name__icontains=tag_name) | Q(product_name_french__icontains=tag_name)),
#                         available_country__id=country, 
#                         status='Active'
#                     ).distinct()
#                     tag_result_serializer = ProductSearchSerializer(without_tag_result, many=True).data
#                 except models.ProductTag.DoesNotExist:
#                     pass

#             # Fallback B: If still empty and search keyword exists, broaden search (ignore country constraint if needed, or keep it)
#             if not tag_result_serializer and search not in [None, '', 'null']:
#                 without_tag_result = models.ProductDetail.objects.filter(
#                     (Q(product_name__icontains=search) | Q(product_name_french__icontains=search)),
#                     available_country__id=country, # Remove this line if you want global fallback when country matches fail
#                     status='Active'
#                 ).distinct()
#                 tag_result_serializer = ProductSearchSerializer(without_tag_result, many=True).data

#         print("tag_result_serializer=======>", tag_result_serializer)
            
#         return JsonResponse({'data': tag_result_serializer}, status=200)


### final code 
# @csrf_exempt
# def product_list_tag_result(request):
#     if request.method != "POST":
#         return JsonResponse({'error': 'Method not allowed'}, status=405)

#     try:
#         python_data = JSONParser().parse(io.BytesIO(request.body))
#     except Exception:
#         return JsonResponse({'error': 'Invalid JSON'}, status=400)

#     print("python_data---->", python_data)

#     tag = python_data.get('tag')
#     country = python_data.get('country')
#     search_by = python_data.get('search_by')
#     search = python_data.get('search')

#     # Initialize standard base query
#     search_query = Q(status='Active')

#     # 1. Country Filter
#     if country not in [None, '', 'null'] and isinstance(country, int):
#         search_query &= Q(available_country__id=country)

#     # 2. Tag / Search By Filter
#     if tag not in [None, '', 'null']:
#         if search_by == "Tag":
#             search_query &= Q(tag__id=tag)
#         elif search_by == "product_english":
#             product_obj = models.ProductDetail.objects.filter(id=tag).first()
#             if product_obj:
#                 search_query &= Q(product_name__icontains=product_obj.product_name)
#         elif search_by == "product_french":
#             product_obj = models.ProductDetail.objects.filter(id=tag).first()
#             if product_obj and product_obj.product_name_french:
#                 search_query &= Q(product_name_french__icontains=product_obj.product_name_french)

#     # 3. Base Query Execution
#     # Start with the base filters (Country, Tags, Status)
#     queryset = models.ProductDetail.objects.filter(search_query)

#     # Apply Fuzzy Search if search parameter is provided
#     if search not in [None, '', 'null']:
#         # We annotate the already-filtered queryset with similarity scores
#         queryset = queryset.annotate(
#             sim_en=TrigramSimilarity('product_name', search),
#             sim_fr=TrigramSimilarity('product_name_french', search),
#         ).filter(
#             # 0.15 - 0.20 is a sweet spot for typos like "iphne" or split words like "Pistole auto"
#             Q(sim_en__gt=0.18) | Q(sim_fr__gt=0.18)
#         ).order_by('-sim_en', '-sim_fr')

#     # Evaluate the database query and serialize
#     tag_result = queryset.distinct()
#     tag_result_serializer = ProductSearchSerializer(tag_result, many=True).data

#     # 4. Fallback Logic (Only runs if primary fuzzy search returned nothing)
#     if not tag_result_serializer:
#         # Fallback A: Try searching by Tag Name if tag is provided
#         if tag not in [None, '', 'null']:
#             try:
#                 tag_name = models.ProductTag.objects.get(id=tag).tag
#                 without_tag_result = models.ProductDetail.objects.filter(
#                     (Q(product_name__icontains=tag_name) | Q(product_name_french__icontains=tag_name)),
#                     available_country__id=country if isinstance(country, int) else None, 
#                     status='Active'
#                 ).distinct()
#                 tag_result_serializer = ProductSearchSerializer(without_tag_result, many=True).data
#             except models.ProductTag.DoesNotExist:
#                 pass

#         # Fallback B: Substring Match fallback if Trigram threshold was too strict
#         if not tag_result_serializer and search not in [None, '', 'null']:
#             without_tag_result = models.ProductDetail.objects.filter(
#                 (Q(product_name__icontains=search) | Q(product_name_french__icontains=search)),
#                 available_country__id=country if isinstance(country, int) else None,
#                 status='Active'
#             ).distinct()
#             tag_result_serializer = ProductSearchSerializer(without_tag_result, many=True).data

#     print("tag_result_serializer=======>", len(tag_result_serializer), "items found")
        
#     return JsonResponse({'data': tag_result_serializer}, status=200)







# @csrf_exempt
# def product_list_tag_result(request):
#     if request.method == "POST":
#         python_data = JSONParser().parse(io.BytesIO(request.body))

#         print("python_data---->", python_data)

#         tag = python_data.get('tag')
#         country = python_data.get('country')
#         search_by = python_data.get('search_by')
#         search = python_data.get('search')
#         currencyCode = python_data.get('currencyCode')

#         try:
#             if currencyCode not in [None,'','null']:
#                 country_name = models.CountryWithCurrency.objects.filter(currency_code = currencyCode).first().country_name
#             else:
#                 country_name = 'Senegal'

#         except Exception as e:
#             # print("Error-=-=-=--->",e)
#             country_name = 'Egypt'

#         search_query = Q()

#         # -----------------------------------
#         # COUNTRY FILTER
#         # -----------------------------------
#         if country not in [None, '', 'null'] and isinstance(country, int):

#             search_query &= Q(available_country__id=country)

#             # -----------------------------------
#             # TAG FILTER
#             # -----------------------------------
#             if tag not in [None, '', 'null']:

#                 if search_by == "Tag":

#                     search_query &= Q(tag__id=tag)

#                 elif search_by == "product_english":

#                     product = models.ProductDetail.objects.filter(id=tag).first()

#                     if product:
#                         search_query &= Q(
#                             product_name__unaccent__icontains=product.product_name
#                         )

#                 elif search_by == "product_french":

#                     product = models.ProductDetail.objects.filter(id=tag).first()

#                     if product:
#                         search_query &= Q(
#                             product_name_french__unaccent__icontains=product.product_name_french
#                         )

#             # -----------------------------------
#             # SEARCH TEXT
#             # -----------------------------------
#             search_clean = ""

#             if search not in [None, '', 'null']:

#                 search = search.strip()

#                 # remove spaces + lowercase
#                 search_clean = search.replace(" ", "").lower()

#             # -----------------------------------
#             # BASE QUERYSET
#             # -----------------------------------
#             products = models.ProductDetail.objects.annotate(

#                 clean_product_name=Lower(
#                     Replace('product_name', Value(' '), Value(''))
#                 ),

#                 clean_product_name_french=Lower(
#                     Replace('product_name_french', Value(' '), Value(''))
#                 ),

#                 clean_refpro=Lower(
#                     Replace('refpro', Value(' '), Value(''))
#                 ),
#             )

#             # -----------------------------------
#             # SEARCH FILTER
#             # -----------------------------------
#             if search_clean:

#                 products = products.annotate(

#                     similarity_name=TrigramWordSimilarity(
#                         search,
#                         'product_name'
#                     ),

#                     similarity_name_french=TrigramWordSimilarity(
#                         search,
#                         'product_name_french'
#                     ),

#                     similarity_refpro=TrigramWordSimilarity(
#                         search,
#                         'refpro'
#                     )
#                 )


#                 search_words = search.lower().split()

#                 word_query = Q()

#                 for word in search_words:
#                     word_query |= Q(
#                         product_name__unaccent__icontains=word
#                     )

#                     word_query |= Q(
#                         product_name_french__unaccent__icontains=word
#                     )

#                     word_query |= Q(
#                         refpro__unaccent__icontains=word
#                     )

#                 search_query &= (
#                     word_query |

#                     Q(similarity_name__gt=0.10) |

#                     Q(similarity_name_french__gt=0.10) |

#                     Q(similarity_refpro__gt=0.10)
#                 )
#             # -----------------------------------
#             # FINAL RESULT
#             # -----------------------------------
#             tag_result = (
#                 products
#                 .filter(
#                     search_query,
#                     status='Active'
#                 )
#                 .distinct()
#                 .order_by('product_name')
#             )

#             tag_result_serializer = ProductSearchSerializer(
#                 tag_result,
#                 many=True,
#                 context={'country': country_name}
#             ).data

#             # -----------------------------------
#             # FALLBACK SEARCH
#             # -----------------------------------
#             if not tag_result_serializer:

#                 try:

#                     tag_name = models.ProductTag.objects.get(id=tag).tag

#                     fallback_search = tag_name.replace(" ", "").lower()

#                     without_tag_result = (
#                         products
#                         .filter(
#                             (
#                                 Q(clean_product_name__unaccent__icontains=fallback_search) |
#                                 Q(clean_product_name_french__unaccent__icontains=fallback_search) |
#                                 Q(clean_refpro__unaccent__icontains=fallback_search)
#                             ),
#                             available_country__id=country,
#                             status='Active'
#                         )
#                         .distinct()
#                     )

#                     tag_result_serializer = ProductSearchSerializer(
#                         without_tag_result,
#                         many=True,
#                         context={'country': country_name}
#                     ).data

#                 except Exception:

#                     without_tag_result = (
#                         products
#                         .filter(
#                             (
#                                 Q(clean_product_name__unaccent__icontains=search_clean) |
#                                 Q(clean_product_name_french__unaccent__icontains=search_clean) |
#                                 Q(clean_refpro__unaccent__icontains=search_clean)
#                             ),
#                             available_country__id=country,
#                             status='Active'
#                         )
#                         .distinct()
#                     )

#                     tag_result_serializer = ProductSearchSerializer(
#                         without_tag_result,
#                         many=True,
#                         context={'country': country_name}
#                     ).data
#         res = {
#             'data': tag_result_serializer
#         }

#         return HttpResponse(JSONRenderer().render(res),content_type='application/json',status=200)


# @csrf_exempt
# def product_list_tag_result(request):

#     if request.method == "POST":

#         python_data = JSONParser().parse(
#             io.BytesIO(request.body)
#         )

#         print("python_data---->", python_data)

#         tag = python_data.get('tag')
#         country = python_data.get('country')
#         search_by = python_data.get('search_by')
#         search = python_data.get('search')
#         currencyCode = python_data.get('currencyCode')

#         try:

#             if currencyCode not in [None, '', 'null']:

#                 country_obj = (
#                     models.CountryWithCurrency.objects
#                     .filter(
#                         currency_code=currencyCode
#                     )
#                     .first()
#                 )

#                 country_name = (
#                     country_obj.country_name
#                     if country_obj
#                     else "Egypt"
#                 )

#             else:

#                 country_name = "Senegal"

#         except Exception:

#             country_name = "Egypt"

#         tag_result_serializer = []

#         search_query = Q()

#         if country not in [None, '', 'null'] and isinstance(country, int):

#             search_query &= Q(
#                 available_country__id=country
#             )

#             # =====================================
#             # TAG FILTER
#             # =====================================

#             if tag not in [None, '', 'null']:

#                 if search_by == "Tag":

#                     search_query &= Q(
#                         tag__id=tag
#                     )

#                 elif search_by == "product_english":

#                     # Don't restrict by exact product name.
#                     # Let fuzzy search handle it.
#                     pass

#                 elif search_by == "product_french":

#                     # Don't restrict by exact product name.
#                     # Let fuzzy search handle it.
#                     pass

#             # =====================================
#             # SEARCH CLEAN
#             # =====================================

#             search_clean = ""

#             if search not in [None, '', 'null']:

#                 search = str(search).strip()

#                 search_clean = (
#                     search
#                     .replace(" ", "")
#                     .replace("-", "")
#                     .replace("_", "")
#                     .lower()
#                 )

#             # =====================================
#             # BASE QUERYSET
#             # =====================================

#             products = (
#                 models.ProductDetail.objects
#                 .annotate(

#                     clean_product_name=Lower(
#                         Replace(
#                             Replace(
#                                 Replace(
#                                     'product_name',
#                                     Value(' '),
#                                     Value('')
#                                 ),
#                                 Value('-'),
#                                 Value('')
#                             ),
#                             Value('_'),
#                             Value('')
#                         )
#                     ),

#                     clean_product_name_french=Lower(
#                         Replace(
#                             Replace(
#                                 Replace(
#                                     'product_name_french',
#                                     Value(' '),
#                                     Value('')
#                                 ),
#                                 Value('-'),
#                                 Value('')
#                             ),
#                             Value('_'),
#                             Value('')
#                         )
#                     ),

#                     clean_refpro=Lower(
#                         Replace(
#                             Replace(
#                                 Replace(
#                                     'refpro',
#                                     Value(' '),
#                                     Value('')
#                                 ),
#                                 Value('-'),
#                                 Value('')
#                             ),
#                             Value('_'),
#                             Value('')
#                         )
#                     )
#                 )
#             )

#             # =====================================
#             # FUZZY SEARCH
#             # =====================================

#             # if search_clean:

#             #     products = products.annotate(

#             #         similarity_name=TrigramWordSimilarity(
#             #             search,
#             #             'product_name'
#             #         ),

#             #         similarity_name_french=TrigramWordSimilarity(
#             #             search,
#             #             'product_name_french'
#             #         ),

#             #         similarity_refpro=TrigramWordSimilarity(
#             #             search,
#             #             'refpro'
#             #         )
#             #     ).annotate(

#             #         best_similarity=Greatest(
#             #             'similarity_name',
#             #             'similarity_name_french',
#             #             'similarity_refpro'
#             #         )
#             #     )
#             #     search_words = search.lower().split()

#             #     word_query = Q()

#             #     for word in search_words:

#             #         word_query |= Q(
#             #             product_name__unaccent__icontains=word
#             #         )

#             #         word_query |= Q(
#             #             product_name_french__unaccent__icontains=word
#             #         )

#             #         word_query |= Q(
#             #             refpro__unaccent__icontains=word
#             #         )

#             #     search_query &= (

#             #         word_query |

#             #             Q(best_similarity__gt=0.35)
#             #     )
            
#             if search_clean:

#                 normalized_search = re.sub(
#                     r'(.)\1+',
#                     r'\1',
#                     search.lower()
#                 )

#                 products = products.annotate(

#                     similarity_name=TrigramSimilarity(
#                         'product_name',
#                         normalized_search
#                     ),

#                     similarity_name_word=TrigramWordSimilarity(
#                         normalized_search,
#                         'product_name'
#                     ),

#                     similarity_name_french=TrigramSimilarity(
#                         'product_name_french',
#                         normalized_search
#                     ),

#                     similarity_name_french_word=TrigramWordSimilarity(
#                         normalized_search,
#                         'product_name_french'
#                     ),

#                     similarity_refpro=TrigramSimilarity(
#                         'refpro',
#                         normalized_search
#                     ),

#                     similarity_refpro_word=TrigramWordSimilarity(
#                         normalized_search,
#                         'refpro'
#                     )

#                 ).annotate(

#                     best_similarity=Greatest(
#                         'similarity_name',
#                         'similarity_name_word',
#                         'similarity_name_french',
#                         'similarity_name_french_word',
#                         'similarity_refpro',
#                         'similarity_refpro_word'
#                     )
#                 )

#                 search_words = normalized_search.split()

#                 word_query = Q()

#                 for word in search_words:

#                     word_query |= Q(
#                         product_name__unaccent__icontains=word
#                     )

#                     word_query |= Q(
#                         product_name_french__unaccent__icontains=word
#                     )

#                     word_query |= Q(
#                         refpro__unaccent__icontains=word
#                     )

#                 search_query &= (
#                     word_query |
#                     Q(best_similarity__gt=0.30)
#                 )


#             # # =====================================
#             # FINAL RESULT
#             # =====================================
#             if search_clean:
#                 tag_result = (
#                     products
#                     .filter(
#                         search_query,
#                         status='Active'
#                     )
#                     .distinct()
#                     .order_by(
#                         '-best_similarity',
#                         'product_name'
#                     )
#                 )

#             else:

#                 tag_result = (
#                     products
#                     .filter(
#                         search_query,
#                         status='Active'
#                     )
#                     .distinct()
#                     .order_by(
#                         'product_name'
#                     )
#                 )

#             tag_result_serializer = (
#                 ProductSearchSerializer(
#                     tag_result,
#                     many=True,
#                     context={
#                         'country': country_name
#                     }
#                 ).data
#             )

#             # =====================================
#             # FALLBACK SEARCH
#             # =====================================

#             if not tag_result_serializer:

#                 try:

#                     tag_name = (
#                         models.ProductTag.objects
#                         .get(id=tag)
#                         .tag
#                     )

#                     fallback_search = (
#                         re.sub(
#                             r'(.)\1+',
#                             r'\1',
#                             tag_name.lower()
#                         )
#                         .replace(" ", "")
#                         .replace("-", "")
#                         .replace("_", "")
#                     )

#                     without_tag_result = (
#                         products
#                         .filter(
#                             (
#                                 Q(
#                                     clean_product_name__icontains=
#                                     fallback_search
#                                 ) |

#                                 Q(
#                                     clean_product_name_french__icontains=
#                                     fallback_search
#                                 ) |

#                                 Q(
#                                     clean_refpro__icontains=
#                                     fallback_search
#                                 )
#                             ),
#                             available_country__id=country,
#                             status='Active'
#                         )
#                         .distinct()
#                     )

#                     tag_result_serializer = (
#                         ProductSearchSerializer(
#                             without_tag_result,
#                             many=True,
#                             context={
#                                 'country': country_name
#                             }
#                         ).data
#                     )

#                 except Exception:

#                     without_tag_result = (
#                         products
#                         .filter(
#                             (
#                                 Q(
#                                     clean_product_name__icontains=
#                                     search_clean
#                                 ) |

#                                 Q(
#                                     clean_product_name_french__icontains=
#                                     search_clean
#                                 ) |

#                                 Q(
#                                     clean_refpro__icontains=
#                                     search_clean
#                                 )
#                             ),
#                             available_country__id=country,
#                             status='Active'
#                         )
#                         .distinct()
#                     )

#                     tag_result_serializer = (
#                         ProductSearchSerializer(
#                             without_tag_result,
#                             many=True,
#                             context={
#                                 'country': country_name
#                             }
#                         ).data
#                     )

#         res = {
#             "data": tag_result_serializer
#         }

#         return HttpResponse(
#             JSONRenderer().render(res),
#             content_type="application/json",
#             status=200
#         )


# @csrf_exempt
# def product_list_tag_result(request):
#     if request.method == "POST":
#         python_data = JSONParser().parse(io.BytesIO(request.body))
#         print("python_data---->", python_data)

#         tag = python_data.get('tag')
#         country = python_data.get('country')
#         search_by = python_data.get('search_by')
#         search = python_data.get('search')
#         currencyCode = python_data.get('currencyCode')

#         try:
#             if currencyCode not in [None, '', 'null']:
#                 country_obj = models.CountryWithCurrency.objects.filter(currency_code=currencyCode).first()
#                 country_name = country_obj.country_name if country_obj else "Egypt"
#             else:
#                 country_name = "Senegal"
#         except Exception:
#             country_name = "Egypt"

#         tag_result_serializer = []
#         base_country_query = Q()

#         if country not in [None, '', 'null'] and isinstance(country, int):
#             base_country_query &= Q(available_country__id=country)

#             # if tag not in [None, '', 'null'] and search_by == "Tag":
#             #     base_country_query &= Q(tag__id=tag)

                    
#             # 2. Tag / Search By Filter
#             if tag not in [None, '', 'null']:
#                 if search_by == "Tag":
#                     search_query &= Q(tag__id=tag)
#                 elif search_by == "product_english":
#                     product_obj = models.ProductDetail.objects.filter(id=tag).first()
#                     print(product_obj, 'product_obj')
#                     if product_obj:
#                         search_query &= Q(product_name__icontains=product_obj.product_name)
#                 elif search_by == "product_french":
#                     product_obj = models.ProductDetail.objects.filter(id=tag).first()
#                     if product_obj and product_obj.product_name_french:
#                         search_query &= Q(product_name_french__icontains=product_obj.product_name_french)

#             # =====================================
#             # SEARCH CLEANING
#             # =====================================
#             search_clean = ""
#             if search not in [None, '', 'null']:
#                 search = str(search).strip()
#                 search_clean = search.replace(" ", "").replace("-", "").replace("_", "").lower()

#             # =====================================
#             # BASE QUERYSET
#             # =====================================
#             products = models.ProductDetail.objects.filter(base_country_query, status='Active')

#             # =====================================
#             # STRICT TEXT & FUZZY SEARCH LOGIC
#             # =====================================
#             if search_clean:
#                 normalized_search = re.sub(r'(.)\1+', r'\1', search.lower())
#                 search_words = normalized_search.split()

#                 # 1. Build a strict keyword match (ALL words must match somewhere)
#                 strict_text_query = Q()
#                 for word in search_words:
#                     if len(word) <= 2 and not word.isdigit():
#                         continue  # Skip junk words like "du", "le"
                    
#                     # Each individual word must hit name, french name, OR refpro
#                     word_match = (
#                         Q(product_name__unaccent__icontains=word) |
#                         Q(product_name_french__unaccent__icontains=word) |
#                         Q(refpro__unaccent__icontains=word)
#                     )
                    
#                     if not strict_text_query:
#                         strict_text_query = word_match
#                     else:
#                         strict_text_query &= word_match  # AND condition forces all words to match

#                 # 2. Add Trigram scoring metrics for ranking relevance
#                 products = products.annotate(
#                     similarity_name=TrigramSimilarity('product_name', normalized_search),
#                     similarity_name_word=TrigramWordSimilarity(normalized_search, 'product_name'),
#                     similarity_name_french=TrigramSimilarity('product_name_french', normalized_search),
#                     similarity_name_french_word=TrigramWordSimilarity(normalized_search, 'product_name_french'),
#                     similarity_refpro=TrigramSimilarity('refpro', normalized_search),
#                     similarity_refpro_word=TrigramWordSimilarity(normalized_search, 'refpro')
#                 ).annotate(
#                     best_similarity=Greatest(
#                         'similarity_name', 'similarity_name_word',
#                         'similarity_name_french', 'similarity_name_french_word',
#                         'similarity_refpro', 'similarity_refpro_word'
#                     )
#                 )

#                 # Execute primary strict search first

#                 tag_result = products.filter(strict_text_query).distinct().order_by('-best_similarity', 'product_name')

#                 # If strict filtering returns nothing, fall back to high-confidence fuzzy match
#                 if not tag_result.exists():
#                     tag_result = products.filter(best_similarity__gt=0.40).distinct().order_by('-best_similarity', 'product_name')
#             else:
#                 tag_result = products.distinct().order_by('product_name')

#             # Serialize primary results
#             tag_result_serializer = ProductSearchSerializer(
#                 tag_result, many=True, context={'country': country_name}
#             ).data

#             # =====================================
#             # FALLBACK SEARCH (IF NO RESULTS FOUND)
#             # =====================================
#             if not tag_result_serializer and tag not in [None, '', 'null']:
#                 # Setup cleaner string manipulations on the fields for fallback matching
#                 products_clean_fields = models.ProductDetail.objects.filter(
#                     available_country__id=country, status='Active'
#                 ).annotate(
#                     clean_product_name=Lower(Replace(Replace(Replace('product_name', Value(' '), Value('')), Value('-'), Value('')), Value('_'), Value(''))),
#                     clean_product_name_french=Lower(Replace(Replace(Replace('product_name_french', Value(' '), Value('')), Value('-'), Value('')), Value('_'), Value(''))),
#                     clean_refpro=Lower(Replace(Replace(Replace('refpro', Value(' '), Value('')), Value('-'), Value('')), Value('_'), Value('')))
#                 )

#                 try:
#                     tag_name = models.ProductTag.objects.get(id=tag).tag
#                     fallback_search = re.sub(r'(.)\1+', r'\1', tag_name.lower()).replace(" ", "").replace("-", "").replace("_", "")

#                     without_tag_result = products_clean_fields.filter(
#                         Q(clean_product_name__icontains=fallback_search) |
#                         Q(clean_product_name_french__icontains=fallback_search) |
#                         Q(clean_refpro__icontains=fallback_search)
#                     ).distinct()

#                     tag_result_serializer = ProductSearchSerializer(
#                         without_tag_result, many=True, context={'country': country_name}
#                     ).data

#                 except Exception:
#                     if search_clean:
#                         without_tag_result = products_clean_fields.filter(
#                             Q(clean_product_name__icontains=search_clean) |
#                             Q(clean_product_name_french__icontains=search_clean) |
#                             Q(clean_refpro__icontains=search_clean)
#                         ).distinct()

#                         tag_result_serializer = ProductSearchSerializer(
#                             without_tag_result, many=True, context={'country': country_name}
#                         ).data

#         res = {"data": tag_result_serializer}
#         return HttpResponse(JSONRenderer().render(res), content_type="application/json", status=200)

@csrf_exempt
def product_list_tag_result(request):
    if request.method == "POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))
        print("python_data---->", python_data)

        tag = python_data.get('tag')
        country = python_data.get('country')
        search_by = python_data.get('search_by')
        search = python_data.get('search')
        currencyCode = python_data.get('currencyCode')

        try:
            if currencyCode not in [None, '', 'null']:
                country_obj = models.CountryWithCurrency.objects.filter(currency_code=currencyCode).first()
                country_name = country_obj.country_name if country_obj else "Egypt"
            else:
                country_name = "Senegal"
        except Exception:
            country_name = "Egypt"

        tag_result_serializer = []
        base_country_query = Q()

        if country not in [None, '', 'null'] and isinstance(country, int):
            base_country_query &= Q(available_country__id=country)

            # =======================================================
            # TAG / SEARCH BY FILTER (FIXED & LINKED TO BASE QUERY)
            # =======================================================
            if tag not in [None, '', 'null']:
                search_query = Q()  # Initialized to prevent NameError
                
                if search_by == "Tag":
                    search_query &= Q(tag__id=tag)
                elif search_by == "product_english":
                    product_obj = models.ProductDetail.objects.filter(id=tag).first()
                    print(product_obj, 'product_obj')
                    if product_obj:
                        search_query &= Q(product_name__icontains=product_obj.product_name)
                elif search_by == "product_french":
                    product_obj = models.ProductDetail.objects.filter(id=tag).first()
                    if product_obj and product_obj.product_name_french:
                        search_query &= Q(product_name_french__icontains=product_obj.product_name_french)
                
                # Append the search_by filters directly to your country query
                base_country_query &= search_query

            # =====================================
            # SEARCH CLEANING
            # =====================================
            search_clean = ""
            if search not in [None, '', 'null']:
                search = str(search).strip()
                search_clean = search.replace(" ", "").replace("-", "").replace("_", "").lower()

            # =====================================
            # BASE QUERYSET
            # =====================================
            products = models.ProductDetail.objects.filter(base_country_query, status='Active')

            # =====================================
            # STRICT TEXT & FUZZY SEARCH LOGIC
            # =====================================
            if search_clean:
                normalized_search = re.sub(r'(.)\1+', r'\1', search.lower())
                search_words = normalized_search.split()

                # 1. Build a strict keyword match (ALL words must match somewhere)
                strict_text_query = Q()
                for word in search_words:
                    if len(word) <= 2 and not word.isdigit():
                        continue  # Skip junk words like "du", "le"
                    
                    # Each individual word must hit name, french name, OR refpro
                    word_match = (
                        Q(product_name__unaccent__icontains=word) |
                        Q(product_name_french__unaccent__icontains=word) |
                        Q(refpro__unaccent__icontains=word)
                    )
                    
                    if not strict_text_query:
                        strict_text_query = word_match
                    else:
                        strict_text_query &= word_match  # AND condition forces all words to match

                # 2. Add Trigram scoring metrics for ranking relevance
                products = products.annotate(
                    similarity_name=TrigramSimilarity('product_name', normalized_search),
                    similarity_name_word=TrigramWordSimilarity(normalized_search, 'product_name'),
                    similarity_name_french=TrigramSimilarity('product_name_french', normalized_search),
                    similarity_name_french_word=TrigramWordSimilarity(normalized_search, 'product_name_french'),
                    similarity_refpro=TrigramSimilarity('refpro', normalized_search),
                    similarity_refpro_word=TrigramWordSimilarity(normalized_search, 'refpro')
                ).annotate(
                    best_similarity=Greatest(
                        'similarity_name', 'similarity_name_word',
                        'similarity_name_french', 'similarity_name_french_word',
                        'similarity_refpro', 'similarity_refpro_word'
                    )
                )

                # Execute primary strict search first
                tag_result = products.filter(strict_text_query).distinct().order_by('-best_similarity', 'product_name')

                # If strict filtering returns nothing, fall back to high-confidence fuzzy match
                if not tag_result.exists():
                    tag_result = products.filter(best_similarity__gt=0.40).distinct().order_by('-best_similarity', 'product_name')
            else:
                tag_result = products.distinct().order_by('product_name')

            # Serialize primary results
            tag_result_serializer = ProductSearchSerializer(
                tag_result, many=True, context={'country': country_name}
            ).data

            # =====================================
            # FALLBACK SEARCH (IF NO RESULTS FOUND)
            # =====================================
            if not tag_result_serializer and tag not in [None, '', 'null']:
                # Setup cleaner string manipulations on the fields for fallback matching
                products_clean_fields = models.ProductDetail.objects.filter(
                    available_country__id=country, status='Active'
                ).annotate(
                    clean_product_name=Lower(Replace(Replace(Replace('product_name', Value(' '), Value('')), Value('-'), Value('')), Value('_'), Value(''))),
                    clean_product_name_french=Lower(Replace(Replace(Replace('product_name_french', Value(' '), Value('')), Value('-'), Value('')), Value('_'), Value(''))),
                    clean_refpro=Lower(Replace(Replace(Replace('refpro', Value(' '), Value('')), Value('-'), Value('')), Value('_'), Value('')))
                )

                try:
                    tag_name = models.ProductTag.objects.get(id=tag).tag
                    fallback_search = re.sub(r'(.)\1+', r'\1', tag_name.lower()).replace(" ", "").replace("-", "").replace("_", "")

                    without_tag_result = products_clean_fields.filter(
                        Q(clean_product_name__icontains=fallback_search) |
                        Q(clean_product_name_french__icontains=fallback_search) |
                        Q(clean_refpro__icontains=fallback_search)
                    ).distinct()

                    tag_result_serializer = ProductSearchSerializer(
                        without_tag_result, many=True, context={'country': country_name}
                    ).data

                except Exception:
                    if search_clean:
                        without_tag_result = products_clean_fields.filter(
                            Q(clean_product_name__icontains=search_clean) |
                            Q(clean_product_name_french__icontains=search_clean) |
                            Q(clean_refpro__icontains=search_clean)
                        ).distinct()

                        tag_result_serializer = ProductSearchSerializer(
                            without_tag_result, many=True, context={'country': country_name}
                        ).data

        res = {"data": tag_result_serializer}
        return HttpResponse(JSONRenderer().render(res), content_type="application/json", status=200)


@csrf_exempt
def social_login(request):
    if request.method == "POST":
    
        python_data = JSONParser().parse(io.BytesIO(request.body))
        print("python_data---social_login-->",python_data)
        
        email = python_data.get('email')

        deviceId = python_data.get('deviceId')
        deviceType = python_data.get('deviceType')
        socialType = python_data.get('socialType')
        social_token = python_data.get('social_token')    
        fcm_token = python_data.get('FCMToken')
        name = python_data.get('name', None)

        ip_address = python_data.get('ip_address',None)
        country = python_data.get('country')

        # print("ip_address----social_login--->",ip_address)

        new_user = False

        
        now = datetime.now()
        date_time = now.strftime('%Y-%m-%d, %H:%M:%S')
        
        email_verify = models.CustomerDetail.objects.filter(email = email).count()

        if email_verify == 0:
            try:
                if country in [None,'','null']:
                    response = requests.get(f'https://ipapi.co/{ip_address}/json/')
                    response = response.json()

                    if not response.get('error'):
                        country = response.get("country_name")

                    print("response====>",response)

                # if country in [None,'','null']:
                #     country = "Egypt"

            except Exception as e:
                print("Errroooorrr----->",e)
                # country = "Egypt"

            customer = models.CustomerDetail.objects.create(
                email=email, 
                name = name,
                social_token=social_token,
                deviceId=deviceId,
                socialType=socialType,
                deviceType=deviceType,
                FCMToken = fcm_token,
                lastLoginDate = date_time,
                country = country,
                ip_address = ip_address,
                created_at = date_time
            )
            customer.save()

            serializer = CustomerDetailSerializer(customer).data
                
            check_login = models.CustomerLogin.objects.filter(customer_id = customer.id).count()
            if check_login == 0:
                login = models.CustomerLogin.objects.create(
                    customer_id = customer.id,
                    login_time = date_time,
                ).save()
            
            if check_login == 1:
                login_update = models.CustomerLogin.objects.get(customer_id = customer.id)
                login_update.login_time = date_time
                login_update.save()
                

            login_history = models.CustomerLoginHistory.objects.create(
                email = email,
                login_time = date_time,
            ).save()

            
            res={
                'message':"You're successfully registerd.",
                'data':serializer,
                'new_user':True
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)
        
        elif email_verify == 1:
            customer = models.CustomerDetail.objects.get(email=email) 

            if customer.mobileNumber in [None,'','null']:
                new_user = True

            if customer.ip_address != ip_address:
                if country in [None,'','null']:
                    try:
                        response = requests.get(f'https://ipapi.co/{ip_address}/json/')
                        response = response.json()

                        if not response.get('error'):
                            country = response.get("country_name",None)


                        print("response====>",response)

                        if country not in [None,'','null']:
                            customer.country = country
                            customer.ip_address = ip_address

                    except Exception as e:
                        print("Errroooorrr----->",e)
                        # country = "Egypt"

            # customer.name= python_data.get('name', customer.name) 
            customer.social_token= python_data.get('social_token', customer.social_token) 
            customer.deviceId= python_data.get('deviceId', customer.deviceId) 
            customer.socialType= python_data.get('socialType', customer.socialType) 
            customer.deviceType= python_data.get('deviceType', customer.deviceType) 
            customer.FCMToken =  python_data.get('fcm_token', customer.FCMToken) 
            customer.lastLoginDate =  date_time
    
            customer.save()

            serializer = CustomerDetailSerializer(customer).data
                
            check_login = models.CustomerLogin.objects.filter(customer_id = customer.id).count()
            if check_login == 0:
                login = models.CustomerLogin.objects.create(
                    customer_id = customer.id,
                    login_time = date_time,
                ).save()
            
            if check_login == 1:
                login_update = models.CustomerLogin.objects.get(customer_id = customer.id)
                login_update.login_time = date_time
                login_update.save()
                

            login_history = models.CustomerLoginHistory.objects.create(
                email = email,
                login_time = date_time,
            ).save()

            
            res={
                'message':"You're successfully login.",
                'data':serializer,
                'new_user':new_user
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)
        else:
            res={
                'message':'Something went wrong.',
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=406)


@csrf_exempt
def mobile_number_update(request):
    if request.method == "POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))
        print("python_data--mobile_number_update-->",python_data)

        customer = python_data.get('customer',None)
        countryCode = python_data.get('countryCode',None)
        mobileNumber = python_data.get('mobileNumber',None)
        country = python_data.get('country',None)
        

        if customer in [None,'','null']:
            res = {
                'message':'Customer Not Found'
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 406)
        
        else:
            if models.CustomerDetail.objects.filter(id = customer).exists():
                get_user = models.CustomerDetail.objects.get(id = customer)

                digits = '123456789' 
                OTP = ""
                for i in range(4):
                    OTP += digits[math.floor(random.random() * 9)]

                get_user.OTP = OTP
                get_user.country = country
                get_user.save()
                
                recipient = str(countryCode) + str(mobileNumber)
                # content = f'Your Diaba verification code is {OTP}. It will expire in 5 minutes. Do not share this code with anyone.'
                # result = send_sms(LOGIN, API_KEY, TOKEN, SUBJECT, SIGNATURE, recipient, content)
                
                url = "https://api.verifyway.com/api/v1/"
                headers = {
                    "Authorization": "Bearer 1515$iwLeuAjYrEcHnD8Rs2GymuXAefPF8M5fx7wV",
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                }
                payload = {
                    "recipient": recipient,
                    "type": "otp",
                    "channel": "whatsapp",
                    "fallback": "no",
                    "code": OTP,
                    "lang": "en",
                }
                response = requests.post(url, json=payload, headers=headers)
                # print(response, 'responseresponse')

                res={
                    'message':"Verification code sent successfully.", 
                    'OTP':OTP
                }
                return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)
            
            else:
                res = {
                    'message':'Customer Not Found'
                }
                return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 406)

@csrf_exempt
def mobile_number_update_verify(request):
    if request.method == "POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))
        # print("python_data--mobile_number_update-->",python_data)

        customer = python_data.get('customer',None)
        countryCode = python_data.get('countryCode',None)
        mobileNumber = python_data.get('mobileNumber',None)
        name = python_data.get('name',None)

        OTP = python_data.get('OTP',None)

        if customer in [None,'','null']:
            res = {
                'message':'Customer Not Found'
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 406)
        
        else:
            if models.CustomerDetail.objects.filter(id = customer).exists():
                get_user = models.CustomerDetail.objects.get(id = customer)

                if get_user.OTP == OTP:
                    get_user.countryCode = countryCode
                    get_user.mobileNumber = mobileNumber
                    get_user.name = name

                    get_user.save()
                    serializer = CustomerDetailSerializer(get_user).data
                    res={
                        'message':"Verification completed successfully.", 
                        'data':serializer
                    }
                    return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)
                else:
                    res={
                        'message':"OTP not Matched", 
                    }
                    return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 406)
            else:
                res = {
                    'message':'Customer Not Found'
                }
                return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 406)




@csrf_exempt
def customer_delete(request):
    if request.method == "POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))
        # print(python_data ,'python_data')
        customer = python_data.get('user_id')

        login_data = models.CustomerLogin.objects.filter(customer= customer)
        login_data.delete()

        address_data = models.CustomerAddressDetail.objects.filter(customer= customer)
        address_data.delete()

        wishlist_data = models.WishlistDetail.objects.filter(customer= customer)
        wishlist_data.delete()

        cart_data = models.CartDetail.objects.filter(customer= customer)
        cart_data.delete()

        # order_data = models.OrderDetail.objects.filter(customer= customer)
        # for order in order_data:
        #     order = models.OrderDetail.objects.filter(id = order.id)
        #     tracking_data = models.OrderTracking.objects.filter(order = order.id)
        #     tracking_data.delete()
        #     order.delete()

        customer_data = models.CustomerDetail.objects.filter(id= customer)
        customer_data.delete()

        
        res={
            'message':"Your account has been deleted successfully."
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)


@csrf_exempt
def chat_agent_register(request):
    if request.method == 'POST':
        python_data = JSONParser().parse(io.BytesIO(request.body))
        
        email = python_data.get('email')
        countryCode = python_data.get('countryCode')
        mobileNumber = python_data.get('mobileNumber')
        name = python_data.get('name')
        agent_type = python_data.get('agent_type','junior')
        # password = python_data.get('password')

        now = datetime.now()
        date_time = now.strftime('%Y-%m-%d, %H:%M:%S')

        digits = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ' 
        password = ""
        for i in range(6):
            password += digits[math.floor(random.random() * 52)]

        # password = "abcdef"

        role_id = models.Role.objects.filter(roleName = "chatagent").first().id
        
        check_email = models.ChatAgentDetail.objects.filter(email = email).count()
        if check_email == 0:
            create_customer = models.ChatAgentDetail.objects.create(
                email = email,
                countryCode = countryCode,
                mobileNumber = mobileNumber,
                name = name,
                userType_id = role_id,
                agent_type = agent_type,
                password = password,
                is_verified = False,
                status = 'Active',
                created_at = datetime.now()
            ).save()

            try:
                context = {
                    'agent_email':email,
                    'agent_password': password, 
                    'agent_name':name,
                    'current_year':datetime.now().year
                    }
                htmlgen = get_template("new_agent_register.html").render(context)
                # send_mail('Diaba - Team Onboarding',"password",'settings.EMAIL_HOST_USER',[email], fail_silently=False, html_message=htmlgen)

                send_mail(
                    subject='Diaba - Team Onboarding',
                    message='password',
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[email],
                    fail_silently=False,
                    html_message=htmlgen
                )
                
                # print("MAIL SENT SUCCESSFULLY-=-=-=-=-=-=-=-")
            except Exception as e:
                print("print------>",e)
                
        
            res={
                'message':"Welcome aboard! You've successfully registered."
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)
        else:
            res = {
                'message':"This email is already linked to an existing account. Please use another one."        
                }
            json_data = JSONRenderer().render(res)
            return HttpResponse(json_data, content_type= 'application/json', status=406)



@csrf_exempt
def chat_agent_credentials_resend(request):
    if request.method == 'POST':
        python_data = JSONParser().parse(io.BytesIO(request.body))
        id = python_data.get('id')
        if models.ChatAgentDetail.objects.filter(id = id).exists():
            agent = models.ChatAgentDetail.objects.get(id = id)
            email = agent.email
            password = agent.password
            name = agent.name
            try:
                context = {
                    'agent_email':email,
                    'agent_password': password, 
                    'agent_name':name,
                    'current_year':datetime.now().year
                    }
                htmlgen = get_template("resend_agent_creds.html").render(context)
                # send_mail('Diaba - Team Onboarding',"password",'settings.EMAIL_HOST_USER',[email], fail_silently=False, html_message=htmlgen)

                send_mail(
                    subject='Diaba - Team Onboarding',
                    message='password',
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[email],
                    fail_silently=False,
                    html_message=htmlgen
                )
                
                # print("MAIL SENT SUCCESSFULLY-=-=-=-=-=-=-=-")
            except Exception as e:
                print("print------>",e)
            res={
                'message':"Chat Agent credentials resent successfully."
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)
        else:
            res = {
                'message':'Chat Agent Not Found'
            }
            json_data = JSONRenderer().render(res)
            return HttpResponse(json_data, content_type= 'application/json', status=406)


@csrf_exempt
def sub_admin_register(request):
    if request.method == 'POST':
        python_data = JSONParser().parse(io.BytesIO(request.body))
        
        email = python_data.get('email')
        countryCode = python_data.get('countryCode')
        mobileNumber = python_data.get('mobileNumber')
        name = python_data.get('name')
        password = python_data.get('password')


        now = datetime.now()
        date_time = now.strftime('%Y-%m-%d, %H:%M:%S')

        # digits = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ' 
        # password = ""
        # for i in range(6):
        #     password += digits[math.floor(random.random() * 52)]

        # # password = "abcdef"

        role_id = models.Role.objects.filter(roleName = "subadmin").first().id
        
        check_email = models.AdminDetail.objects.filter(email = email).count()
        if check_email == 0:
            create_customer = models.AdminDetail.objects.create(
                email = email,
                countryCode = countryCode,
                mobileNumber = mobileNumber,
                name = name,
                userType_id = role_id,
                password = password,
                status = 'Inactive',
                created_at = datetime.now()
            ).save()

            
            try:
                context = {
                    'subadmin_email':email,
                    'subadmin_password': password, 
                    'subadmin_name':name,
                    'current_year':datetime.now().year
                    }
                htmlgen = get_template("sub_admin_registration.html").render(context)
                # send_mail('Diaba - Team Onboarding',"password",'settings.EMAIL_HOST_USER',[email], fail_silently=False, html_message=htmlgen)

                send_mail(
                    subject='Diaba - Team Onboarding',
                    message='password',
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[email],
                    fail_silently=False,
                    html_message=htmlgen
                )
                
                # print("MAIL SENT SUCCESSFULLY-=-=-=-=-=-=-=-")
            except Exception as e:
                print("print------>",e)
                
        
            res={
                'message':"Sub Admin registerd successfully."
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)
        else:
            res = {
                'message':"This email is already linked to an existing account. Please use another one."        
                }
            json_data = JSONRenderer().render(res)
            return HttpResponse(json_data, content_type= 'application/json', status=406)

@csrf_exempt
def subadmin_credentials_resend(request):
    if request.method == 'POST':
        python_data = JSONParser().parse(io.BytesIO(request.body))
        id = python_data.get('id')
        if models.AdminDetail.objects.filter(id = id).exists():
            sub_admin = models.AdminDetail.objects.get(id = id)
            try:
                context = {
                    'subadmin_email':sub_admin.email,
                    'subadmin_password': sub_admin.password, 
                    'subadmin_name':sub_admin.name,
                    'current_year':datetime.now().year
                    }
                htmlgen = get_template("resend_subadmin_creds.html").render(context)
                send_mail(
                    subject='Diaba - Login Credentials',
                    message='password',
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[sub_admin.email],
                    fail_silently=False,
                    html_message=htmlgen
                )
            except Exception as e:
                print("print------>",e)
            res={
                'message':"Sub Admin credentials resent successfully."
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)
        else:
            res = {
                'message':'Sub Admin Not Found'
            }
            json_data = JSONRenderer().render(res)
            return HttpResponse(json_data, content_type= 'application/json', status=406)        


@csrf_exempt
def sub_admin_update(request):
    if request.method == 'POST':
        python_data = JSONParser().parse(io.BytesIO(request.body))
        
        email = python_data.get('email')
        countryCode = python_data.get('countryCode')
        mobileNumber = python_data.get('mobileNumber')
        name = python_data.get('name')
        password = python_data.get('password')
        
        check_email = models.AdminDetail.objects.filter(email = email).count()
        if check_email == 1:
            sub_admin_update = models.AdminDetail.objects.get(email = email)
            
            sub_admin_update.countryCode =python_data.get('countryCode', sub_admin_update.countryCode)
            sub_admin_update.mobileNumber =python_data.get('mobileNumber', sub_admin_update.mobileNumber)
            sub_admin_update.name =python_data.get('name', sub_admin_update.name)
            sub_admin_update.password =python_data.get('password', sub_admin_update.password)
            sub_admin_update.status = python_data.get('status', sub_admin_update.status)
            sub_admin_update.save()
        
            res={
                'message':"Sub Admin update successfully."
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)
        else:
            res = {
                'message':"This email is already linked to an existing account. Please use another one."        
                }
            json_data = JSONRenderer().render(res)
            return HttpResponse(json_data, content_type= 'application/json', status=406)


@csrf_exempt
def sub_admin_list(request):
    if request.method == "POST":
        admin_list = models.AdminDetail.objects.filter(userType__roleName = 'subadmin').order_by('-id')
        admin_list_serializer = AdminDetailSerializer(admin_list, many=True).data

        res={
            'data':admin_list_serializer
        }
        json_data = JSONRenderer().render(res)
        return HttpResponse(json_data, content_type= 'application/json', status=200)


@csrf_exempt
def sub_admin_status_update(request):
    if request.method == "POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))
        id = python_data.get('id')
        status = python_data.get('status')
        
        message = 'SubAdmin Status update.'
        if status == 'Active':
            check_rights = models.AdminModuleRightsDetail.objects.filter(admin = id).count()
            if check_rights == 0:
                status = 'Inactive'
                message = 'Please complete the admin rights submission first.'

            else:
                status = 'Active'
                message = 'SubAdmin Status update.'

        
        sub_admin_update = models.AdminDetail.objects.get(id =id )
        sub_admin_update.status = status
        sub_admin_update.save()

        res={
            'message':message
        }
        json_data = JSONRenderer().render(res)
        return HttpResponse(json_data, content_type= 'application/json', status=200)

@csrf_exempt
def sub_admin_delete(request):
    if request.method == "POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))
        id = python_data.get('id')

        if models.AdminDetail.objects.filter(id = id).exists():
            sub_admin_delete = models.AdminDetail.objects.filter(id = id).delete()
            res={
                'message':'Sub Admin Deleted Successfully'
            }
            json_data = JSONRenderer().render(res)
            return HttpResponse(json_data, content_type= 'application/json', status=200)
        else:
            res = {
                'message':'Sub Admin Not Found'
            }
            json_data = JSONRenderer().render(res)
            return HttpResponse(json_data, content_type= 'application/json', status=406)

@csrf_exempt
def chat_agent_password_change(request):
    if request.method == "POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))

        # print("python_data--chat_agent_password_change--->",python_data)

        agent_id = python_data.get('agent_id',None)
        new_password = python_data.get('new_password',None)
        old_password = python_data.get('old_password',None)

        if models.ChatAgentDetail.objects.filter(id = agent_id).exists():
            if new_password == old_password:
                res = {
                    'message':'Old Password and New Password Cannot be same'
                }
                return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=406)
    
            else:
                get_agent = models.ChatAgentDetail.objects.get(id = agent_id)
                if old_password == get_agent.password:
                    get_agent.password = new_password
                    get_agent.is_verified = True
                    # get_agent.is_verified = False
                    get_agent.save()

                    res={
                        'message':'Password Updated Successfully'
                    }
                    return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)
                else:
                    res={
                        'message':'Incorrect Current Password'
                    }
                    return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=406)

        
        else:
            res={
                'message':'Agent Not Exist'
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=406)



@csrf_exempt
def chat_agent_list(request):
    if request.method == "POST":
        agent_list = models.ChatAgentDetail.objects.all().order_by('-id')
        agent_list_serializer = AdminChatAgentDetailSerializer(agent_list, many=True).data

        res={
            'data':agent_list_serializer
        }
        json_data = JSONRenderer().render(res)
        return HttpResponse(json_data, content_type= 'application/json', status=200)


@csrf_exempt
def senior_chat_agent_list(request):
    if request.method == "POST":
        agent_list = models.ChatAgentDetail.objects.filter(agent_type = 'senior')
        agent_list_serializer = AdminChatAgentDetailSerializer(agent_list, many=True).data

        res={
            'data':agent_list_serializer
        }
        json_data = JSONRenderer().render(res)
        return HttpResponse(json_data, content_type= 'application/json', status=200)




@csrf_exempt
def user_assigned_agent_list(request):
    if request.method == "POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))

        # print("python_data-=-=--->",python_data)

        agent_id = python_data.get('agent_id', None)

        if agent_id not in [None,'','null']:
            user_id_list = models.ChatRoom.objects.filter(chat_agent = agent_id).values_list('user', flat=True)
            user_list = models.CustomerDetail.objects.filter(id__in=user_id_list)
            user_list_serializer = ChatCustomerDetailSerializer(user_list, many = True).data

            res={
                'data':user_list_serializer,
            }
            json_data = JSONRenderer().render(res)
            return HttpResponse(json_data, content_type= 'application/json', status=200)
            
        else:
            res={
                'message':'Agent Not Found',
            }
            json_data = JSONRenderer().render(res)
            return HttpResponse(json_data, content_type= 'application/json', status=406)





@csrf_exempt
def chat_agent_update(request):
    if request.method == "POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))
        
        # print("python_data-=-=-=-chat_agent_update-=-=-=->", python_data)

        id = python_data.get('id')

        email = python_data.get('email')
        countryCode = python_data.get('countryCode')
        mobileNumber = python_data.get('mobileNumber')
        agent_type = python_data.get('agent_type')
        name = python_data.get('name')

        if models.ChatAgentDetail.objects.filter(id = id):
            get_agent = models.ChatAgentDetail.objects.get(id = id)
            get_agent.email = email
            get_agent.countryCode = countryCode
            get_agent.mobileNumber = mobileNumber
            get_agent.agent_type = agent_type
            get_agent.mobileNumber = mobileNumber
            get_agent.name = name
            get_agent.save()

            res={
                'message':'Chat Agent Updated'
            }
            json_data = JSONRenderer().render(res)
            return HttpResponse(json_data, content_type= 'application/json', status=200)
        
        else:
            res={
                'message':'Chat Agent not Found'
            }
            json_data = JSONRenderer().render(res)
            return HttpResponse(json_data, content_type= 'application/json', status=406)

@csrf_exempt     
def chat_agent_status_update(request):
    if request.method == "POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))
        
        # print("python_data-=-=-=- chat_agent_update-=-=-=->", python_data)

        id = python_data.get('id')
        status = python_data.get('status')

        if models.ChatAgentDetail.objects.filter(id = id):
            get_agent = models.ChatAgentDetail.objects.get(id = id)
            get_agent.status = status
            get_agent.save()

            res={
                'message':f'Agent {status}'
            }
            json_data = JSONRenderer().render(res)
            return HttpResponse(json_data, content_type= 'application/json', status=200)
        else:
            res={
                'message':'Chat Agent not Found'
            }
            json_data = JSONRenderer().render(res)
            return HttpResponse(json_data, content_type= 'application/json', status=406)      



@csrf_exempt
def chat_agent_login(request):
    if request.method == 'POST':
        python_data = JSONParser().parse(io.BytesIO(request.body))
        
        now = datetime.now()
        date_time = now.strftime('%Y-%m-%d, %H:%M:%S')

        email = python_data.get('email')
        password = python_data.get('password') 
        check_email = models.ChatAgentDetail.objects.filter(email = email).count()

        if check_email == 1:
            check_password = models.ChatAgentDetail.objects.filter(email = email, password = password).count()
            if check_password == 1:
                get_user = models.ChatAgentDetail.objects.get(email = email)
                get_user.lastLoginDate = datetime.now()
                get_user.save()
                user_serialiser = ChatAgentDetailSerializer(get_user).data

                res = {
                    'data':user_serialiser        
                    }
                json_data = JSONRenderer().render(res)
                return HttpResponse(json_data, content_type= 'application/json', status=200)
            else:
                res = {
                    'message':'Enter Valid Password'        
                    }
                json_data = JSONRenderer().render(res)
                return HttpResponse(json_data, content_type= 'application/json', status=406)
        else:
            res = {
                    'message':'Enter Valid email'
                }
            json_data = JSONRenderer().render(res)
            return HttpResponse(json_data, content_type= 'application/json', status=406)


@csrf_exempt
def chat_assign_to_agent(request):
    if request.method == "POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))

        # print("python_data-=----chat_assign_to_agent=--->", python_data)

        room_id = python_data.get('room_id',None)
        agent_id = python_data.get('agent_id',None)
        note = python_data.get('note',None)

        if models.ChatRoom.objects.filter(room = room_id).exists():
            assign_agent = models.ChatRoom.objects.get(room = room_id)

            if models.AgentInChatRoomHistory.objects.filter(agent = assign_agent.chat_agent.id, room = assign_agent.id):
                current_assigned_agent = models.AgentInChatRoomHistory.objects.filter(agent = assign_agent.chat_agent.id, room = assign_agent.id).first()
                current_assigned_agent.unassigned_date = datetime.now()
                current_assigned_agent.save()


            assign_agent.note = note
            assign_agent.chat_agent_id = agent_id
            assign_agent.save()

            models.AgentInChatRoomHistory.objects.create(
                room_id = assign_agent.id,
                agent_id = agent_id,
                assigned_date = datetime.now(),
            )

            res={
                'message':'New Agent to Chat'
            }
            json_data = JSONRenderer().render(res)
            return HttpResponse(json_data, content_type= 'application/json', status=200)
        else:
            res={
                'message':'Chat Room not found'
            }
            json_data = JSONRenderer().render(res)
            return HttpResponse(json_data, content_type= 'application/json', status=200)
        










### BULK IMPORT ##### BULK UPLOAD ###


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





# def send_sms(login, api_key, token, subject, signature, recipient, content,base_url="https://api.orangesmspro.sn:8443/api", verify_ssl=False):
#     """
#     Send SMS using Orange SMS Pro API
#     """
#     # Step 1: Generate timestamp and key
#     timestamp = int(time.time())
#     msg_to_encrypt = f"{token}{subject}{signature}{recipient}{content}{timestamp}"
#     key = hmac.new(api_key.encode("utf-8"), msg_to_encrypt.encode("utf-8"), hashlib.sha1).hexdigest()

#     # Step 2: Build query params
#     params = {
#         "token": token,
#         "subject": subject,
#         "signature": signature,
#         "recipient": recipient,
#         "content": content,
#         "timestamp": timestamp,
#         "key": key,
#     }

#     headers = {
#         "Content-Type": "application/x-www-form-urlencoded",
#         "Accept": "application/json",
#     }

#     try:
#         response = requests.get(
#             base_url,
#             params=params,
#             headers=headers,
#             auth=HTTPBasicAuth(login, token),
#             verify=verify_ssl
#         )

#         return {
#             "status_code": response.status_code,
#             "body": response.json() if response.headers.get("Content-Type") == "application/json" else response.text,
#         }

#     except requests.RequestException as e:
#         return {"status_code": 500, "error": str(e)}


# LOGIN = "toubasi"
# API_KEY = "5893b5f784a5e13fb525df276cbcbb49"
# TOKEN = "f4043c2be69d324bafbe1ea0ac00898c"
# SUBJECT = "test_API"
# SIGNATURE = "KIWIST1"

# class SendSMSView(APIView):
#     def post(self, request):
#         serializer = SendSMSSerializer(data=request.data)
#         if serializer.is_valid():
#             recipient = serializer.validated_data["recipient"]
#             content = serializer.validated_data["content"]

#             result = send_sms(
#                 LOGIN, API_KEY, TOKEN, SUBJECT, SIGNATURE, recipient, content
#             )
#             return Response(result, status=result.get("status_code", status.HTTP_200_OK))

#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
def about_us_list(request):
    if request.method == "POST":
        
        about_us = models.AboutUs.objects.all().first()
        about_us_serializer = AboutUsSerializer(about_us).data

        res={
            'data':about_us_serializer
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)

@csrf_exempt
def about_us_update(request):
    if request.method =="POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))

        # print("python_data-=----about_us_update=--->", python_data)

        id = python_data.get('id',None)
        about_us = python_data.get('about_us',None)

        get_about_us = models.AboutUs.objects.get(id = id)
        get_about_us.about_us = about_us
        get_about_us.save()

        res={
            'message':'About Us Updated Successfully'
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)


@csrf_exempt
def privacy_policy_list(request):
    if request.method == "POST":
        get_privacy_policy = models.PrivacyPolicy.objects.all().first()
        get_privacy_policy_serializer = PrivacyPolicySerializer(get_privacy_policy).data

        res={
            'data':get_privacy_policy_serializer
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)


@csrf_exempt
def privacy_policy_update(request):
    if request.method =="POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))

        # print("python_data-=----privacy_policy_update=--->", python_data)

        id = python_data.get('id',None)
        privacy_policy = python_data.get('privacy_policy',None)

        get_privacy_policy = models.PrivacyPolicy.objects.get(id = id)
        get_privacy_policy.privacy_policy = privacy_policy
        get_privacy_policy.save()

        res={
            'message':'About Us Updated Successfully'
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)



@csrf_exempt
def refund_policy_list(request):
    if request.method == "POST":
        get_refund_policy = models.RefundPolicy.objects.all().first()
        get_refund_policy_serializer = RefundPolicySerializer(get_refund_policy).data

        res={
            'data':get_refund_policy_serializer
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)

@csrf_exempt
def refund_policy_update(request):
    if request.method =="POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))

        # print("python_data-=----refund_policy_update=--->", python_data)

        id = python_data.get('id',None)
        refund_policy = python_data.get('refund_policy',None)

        get_refund_policy = models.RefundPolicy.objects.get(id = id)
        get_refund_policy.refund_policy = refund_policy
        get_refund_policy.save()

        res={
            'message':'Refund Policy Updated Successfully'
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)


@csrf_exempt
def terms_and_condition_list(request):
    if request.method == "POST":
        get_terms_and_condition = models.TermsAndCondition.objects.all().first()
        get_terms_and_condition_serializer = TermsAndConditionSerializer(get_terms_and_condition).data

        res={
            'data':get_terms_and_condition_serializer
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)


@csrf_exempt
def terms_and_condition_update(request):
    if request.method =="POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))

        # print("python_data-=----terms_and_condition=--->", python_data)

        id = python_data.get('id',None)
        terms_and_condition = python_data.get('terms_and_condition',None)

        get_privacy_policy = models.TermsAndCondition.objects.get(id = id)
        get_privacy_policy.terms_and_condition = terms_and_condition
        get_privacy_policy.save()

        res={
            'message':'Refund Policy Updated Successfully'
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)




# @csrf_exempt
# def recommend_products(request):
#     if request.method =="POST":

#         python_data={}
#         for i,j in request.FILES.items():
#             python_data.update({i:j})

#         for i,j in request.POST.items():
#             python_data.update({i:j})

#         currencyCode = python_data.get('currencyCode',None)
#         countryCallingCode = python_data.get('countryCallingCode',None)
#         country = python_data.get('countryName','Egypt')
#         ip_address = python_data.get('ip_address')
#         user_id = python_data.get('user_id')

#         try:
#             if currencyCode not in [None,'','null']:
#                 country = models.CountryWithCurrency.objects.filter(currency_code = currencyCode).first().country_name
#             elif countryCallingCode not in [None,'','null']:
#                 country = models.CountryWithCurrency.objects.filter(country_calling_code = countryCallingCode).first().country_name
                
#             elif user_id:
#                 user = models.CustomerDetail.objects.get(id = user_id)
#                 countryCode = user.countryCode

#                 if models.CountryWithCurrency.objects.filter(country_calling_code = countryCode).exists():
#                     country = models.CountryWithCurrency.objects.get(country_calling_code = countryCode).country_name
#                 else:
#                     if country not in [None,'','null']:
#                         country = country
#                     else:
#                         try:
#                             response = requests.get(f'https://ipapi.co/{ip_address}/json/')
#                             response = response.json()
#                             country = response.get("country_name")
#                             print("response====>",response)

#                             if country in [None,'','null']:
#                                 country = "Egypt"

#                         except Exception as e:
#                             print("Errroooorrr----->",e)
#                             country = "Egypt"
                        

#             else:
#                 if country in [None,'','null']:
#                     try:
#                         response = requests.get(f'https://ipapi.co/{ip_address}/json/')
#                         response = response.json()
#                         country = response.get("country_name")
#                         print("response====>",response)

#                         if country in [None,'','null']:
#                             country = "Egypt"

#                     except Exception as e:
#                         print("Errroooorrr----->",e)
#                         country = "Egypt"
#                 else:
#                     country = country
#         except Exception as e:
#             print("Error-=-=-=--->",e)
#             country = 'Egypt'
        
#         # print(python_data, 'python_data')
#         # ensure_product_vectors()

#         # file = request.FILES['image']
#         # file = python_data.get('image')
#         # print(request.FILES, 'request')
#         # query_vector = extract_features_from_file(file)
#         # print(query_vector, 'query_vector')

#         # try:
           
#         image_file = python_data.get("image")

#         if not image_file:
#             return JsonResponse(
#                 {"error": "Image is required"},
#                 status=400
#             )

#         query_vector = extract_features_from_file(image_file)

#         if query_vector is None or query_vector.size == 0:
#             return JsonResponse(
#                 {"error": "Failed to extract image features"},
#                 status=400
#             )

#         query_vector = np.asarray(
#             query_vector,
#             dtype="float32"
#         ).reshape(1, -1)

#         CACHE_CATEGORIES, TEXT_FEATURES = preload_clip_categories()

#         if not CACHE_CATEGORIES or TEXT_FEATURES is None:
#             return JsonResponse(
#                 {"error": "Category cache not loaded"},
#                 status=500
#             )

#         with torch.no_grad():

#             similarity = (
#                 torch.from_numpy(query_vector).to(device)
#                 @ TEXT_FEATURES.T
#             ).squeeze(0)

#             best_idx = similarity.argmax().item()

#             predicted_subcategory = CACHE_CATEGORIES[best_idx]

#             confidence = float(
#                 similarity[best_idx].cpu().numpy()
#             )

#         print(
#             f"Predicted Subcategory: "
#             f"{predicted_subcategory} | "
#             f"Confidence: {confidence:.3f}"
#         )

#         matched_category = (
#             models.ProductDetail.objects
#             .filter(
#                 subcategory__subcategory__iexact=predicted_subcategory,
#                 status="Active"
#             )
#             .values_list(
#                 "category__category",
#                 flat=True
#             )
#             .first()
#         )

#         if not matched_category:
#             return JsonResponse(
#                 {"message": "No matching category found"},
#                 status=404
#             )

#         category_products = (
#             models.ProductDetail.objects
#             .filter(
#                 category__category__iexact=matched_category,
#                 status="Active"
#             )
#             .filter(
#                 Q(product_image_1_vector__isnull=False) |
#                 Q(product_image_2_vector__isnull=False) |
#                 Q(product_image_3_vector__isnull=False) |
#                 Q(product_image_4_vector__isnull=False) |
#                 Q(product_image_5_vector__isnull=False) |
#                 Q(product_image_6_vector__isnull=False) |
#                 Q(product_image_7_vector__isnull=False) |
#                 Q(product_image_8_vector__isnull=False)
#             )
#             .select_related(
#                 "category",
#                 "subcategory"
#             )
#             .only(
#                 "id",
#                 "product_name",
#                 "product_name_french",
#                 "color",
#                 "product_image_1",
#                 "category__category",
#                 "subcategory__subcategory"
#             )
#         )

#         if not category_products.exists():

#             return JsonResponse({
#                 "message": "No products available"
#             }, status=404)

#         index, ids = get_faiss_index()

#         if index is None or ids is None:
#             return JsonResponse(
#                 {"error": "FAISS index unavailable"},
#                 status=500
#             )

#         results = search_similar_products(
#             query_vector=query_vector,
#             index=index,
#             ids=ids,
#             top_k=30
#         )

#         if not results:

#             fallback_products = []

#             for p in category_products[:10]:
#                 fallback_products.append({
#                     "id": p.id,
#                     "product_name": p.product_name,
#                     "product_name_french": p.product_name_french,
#                     "category": p.category.category if p.category else "",
#                     "subcategory": p.subcategory.subcategory if p.subcategory else "",
#                     "color": (p.color or "").lower(),
#                     "product_image_1": (
#                         p.product_image_1.url
#                         if p.product_image_1
#                         else ""
#                     )
#                 })

#             return JsonResponse({
#                 "country": country,
#                 "predicted_category": matched_category,
#                 "subcategory": predicted_subcategory,
#                 "similar_products": fallback_products
#             })

#         result_ids = [
#             r["id"]
#             for r in results
#         ]

#         products_map = {
#             p.id: p
#             for p in (
#                 models.ProductDetail.objects
#                 .filter(id__in=result_ids, status="Active")
#                 .select_related(
#                     "category",
#                     "subcategory"
#                 )
#             )
#         }

#         all_results = []

#         for r in results:
#             product = products_map.get(r["id"])

#             if not product:
#                 continue

#             similarity_score = round(
#                 r["similarity"],
#                 3
#             )

#             if similarity_score >= 0.999:
#                 continue

#             all_results.append({
#                 "id": product.id,
#                 "product_name": product.product_name,
#                 "product_name_french": product.product_name_french,
#                 "category": (
#                     product.category.category
#                     if product.category else ""
#                 ),
#                 "subcategory": (
#                     product.subcategory.subcategory
#                     if product.subcategory else ""
#                 ),
#                 "color": (product.color or "").lower(),
#                 "similarity": similarity_score,
#                 "product_image_1": (
#                     product.product_image_1.url
#                     if product.product_image_1
#                     else ""
#                 )
#             })

#         if not all_results:

#             fallback_products = []

#             for p in category_products[:10]:
#                 fallback_products.append({
#                     "id": p.id,
#                     "product_name": p.product_name,
#                     "product_name_french": p.product_name_french,
#                     "category": p.category.category if p.category else "",
#                     "subcategory": p.subcategory.subcategory if p.subcategory else "",
#                     "color": (p.color or "").lower(),
#                     "product_image_1": (
#                         p.product_image_1.url
#                         if p.product_image_1
#                         else ""
#                     )
#                 })

#             return JsonResponse({
#                 "country": country,
#                 "predicted_category": matched_category,
#                 "subcategory": predicted_subcategory,
#                 "similar_products": fallback_products
#             })

#         all_results.sort(
#             key=lambda x: x["similarity"],
#             reverse=True
#         )

#         top_product = all_results[0]
#         top_color = top_product["color"]
#         top_subcategory = top_product["subcategory"]

#         same_color_same_subcat = [
#             p for p in all_results
#             if (
#                 p["subcategory"] == top_subcategory
#                 and p["color"] == top_color
#             )
#         ]

#         same_subcat_other_color = [
#             p for p in all_results
#             if (
#                 p["subcategory"] == top_subcategory
#                 and p["color"] != top_color
#             )
#         ]

#         final_results = (
#             same_color_same_subcat +
#             same_subcat_other_color
#         )

#         if not final_results:
#             final_results = all_results

#         seen = set()

#         final_results = [
#             p for p in final_results
#             if not (
#                 p["id"] in seen
#                 or seen.add(p["id"])
#             )
#         ]

#         if not final_results:

#             fallback_products = []

#             for p in category_products[:10]:
#                 fallback_products.append({
#                     "id": p.id,
#                     "product_name": p.product_name,
#                     "product_name_french": p.product_name_french,
#                     "category": p.category.category if p.category else "",
#                     "subcategory": p.subcategory.subcategory if p.subcategory else "",
#                     "color": (p.color or "").lower(),
#                     "product_image_1": (
#                         p.product_image_1.url
#                         if p.product_image_1
#                         else ""
#                     )
#                 })

#             return JsonResponse({
#                 "country": country,
#                 "predicted_category": matched_category,
#                 "subcategory": top_subcategory,
#                 "similar_products": fallback_products
#             })

#         return JsonResponse({
#             "country": country,
#             "predicted_category": matched_category,
#             "subcategory": top_subcategory,
#             "similar_products": final_results
#         })

#     # except Exception as e:

#     #     print("recommend_products ERROR:", str(e))

#     #     return JsonResponse({
#     #         "error": str(e)
#     #     }, status=500)

def get_country(data):

    currency_code = data.get("currencyCode")
    calling_code = data.get("countryCallingCode")
    country = data.get("countryName")
    user_id = data.get("user_id")
    ip_address = data.get("ip_address")

    DEFAULT_COUNTRY = "Egypt"

    try:

        if currency_code not in [None, "", "null"]:

            obj = (
                models.CountryWithCurrency.objects
                .filter(currency_code=currency_code)
                .first()
            )

            if obj:
                return obj.country_name

        if calling_code not in [None, "", "null"]:

            obj = (
                models.CountryWithCurrency.objects
                .filter(
                    country_calling_code=calling_code
                )
                .first()
            )

            if obj:
                return obj.country_name

        if user_id:

            user = (
                models.CustomerDetail.objects
                .filter(id=user_id)
                .first()
            )

            if user:

                obj = (
                    models.CountryWithCurrency.objects
                    .filter(
                        country_calling_code=user.countryCode
                    )
                    .first()
                )

                if obj:
                    return obj.country_name

        if country not in [None, "", "null"]:
            return country

        if ip_address:

            response = requests.get(
                f"https://ipapi.co/{ip_address}/json/",
                timeout=3
            ).json()

            return response.get(
                "country_name",
                DEFAULT_COUNTRY
            )

    except Exception as e:
        print("Country Error =====>", e)

    return DEFAULT_COUNTRY


def serialize_product(product, similarity=None):

    data = {
        "id": product.id,
        "product_name": product.product_name,
        "product_name_french": product.product_name_french,
        "category": (
            product.category.category
            if product.category else ""
        ),
        "subcategory": (
            product.subcategory.subcategory
            if product.subcategory else ""
        ),
        "color": (product.color or "").lower(),
        "product_image_1": (
            product.product_image_1.url
            if product.product_image_1
            else ""
        )
    }

    if similarity is not None:
        data["similarity"] = round(
            similarity,
            3
        )

    return data


def build_fallback_products(products):

    return [
        serialize_product(p)
        for p in products[:10]
    ]


def fetch_products_by_ids(product_ids):

    queryset = (
        models.ProductDetail.objects
        .filter(
            id__in=product_ids,
            status="Active"
        )
        .select_related(
            "category",
            "subcategory"
        )
        .only(
            "id",
            "product_name",
            "product_name_french",
            "color",
            "product_image_1",
            "category__category",
            "subcategory__subcategory"
        )
    )

    return {
        p.id: p
        for p in queryset
    }


def build_similarity_results(
    results,
    products_map
):

    final = []

    for r in results:

        product = products_map.get(r["id"])

        if not product:
            continue

        similarity = round(
            r["similarity"],
            3
        )

        # Skip almost identical match
        if similarity > 0.995:
            continue

        final.append({
            "id": product.id,
            "product_name": product.product_name,
            "product_name_french": product.product_name_french,
            "category": (
                product.category.category
                if product.category else ""
            ),
            "subcategory": (
                product.subcategory.subcategory
                if product.subcategory else ""
            ),
            "color": (
                product.color or ""
            ).lower(),
            "similarity": similarity,
            "product_image_1": (
                product.product_image_1.url
                if product.product_image_1
                else ""
            )
        })

    return final


def apply_ranking_strategy(products):

    if not products:
        return []

    # Base similarity sorting
    products.sort(
        key=lambda x: x["similarity"],
        reverse=True
    )

    # Detect dominant subcategory
    subcategories = [
        p["subcategory"]
        for p in products
        if p["subcategory"]
    ]

    dominant_subcategory = None

    if subcategories:

        dominant_subcategory = (
            Counter(subcategories)
            .most_common(1)[0][0]
        )

    ranked_products = []

    for p in products:

        score = p["similarity"]

        # Small boost for dominant subcategory
        if (
            dominant_subcategory
            and p["subcategory"]
            == dominant_subcategory
        ):
            score += 0.03

        # Small boost if color exists
        if p["color"]:
            score += 0.01

        p["final_score"] = round(score, 4)

        ranked_products.append(p)

    ranked_products.sort(
        key=lambda x: x["final_score"],
        reverse=True
    )

    return ranked_products[:30]


def deduplicate_products(products):

    seen = set()

    return [
        p for p in products
        if not (
            p["id"] in seen
            or seen.add(p["id"])
        )
    ]


def rank_products(results):

    product_ids = [
        r["id"]
        for r in results
    ]

    products_map = fetch_products_by_ids(
        product_ids
    )

    similarity_results = (
        build_similarity_results(
            results,
            products_map
        )
    )

    ranked = apply_ranking_strategy(
        similarity_results
    )

    return deduplicate_products(
        ranked
    )


@csrf_exempt
def recommend_products(request):

    if request.method != "POST":

        return JsonResponse(
            {"error": "Invalid request method"},
            status=405
        )

    try:

        python_data={}
        for i,j in request.FILES.items():
            python_data.update({i:j})

        for i,j in request.POST.items():
            python_data.update({i:j})

        country = get_country(
            python_data
        )

        image_file = python_data.get(
            "image"
        )

        if not image_file:

            return JsonResponse(
                {"error": "Image is required"},
                status=400
            )

     

        query_vector = (
            extract_features_from_file(
                image_file
            )
        )

        if (
            query_vector is None
            or query_vector.size == 0
        ):

            return JsonResponse(
                {
                    "error":
                    "Failed to extract image features"
                },
                status=400
            )

        query_vector = np.asarray(
            query_vector,
            dtype="float32"
        ).reshape(1, -1)

        # IMPORTANT NORMALIZATION
        query_vector = (
            query_vector
            / np.linalg.norm(
                query_vector,
                axis=1,
                keepdims=True
            )
        )

    

        index, ids = get_faiss_index()

        if index is None or ids is None:

            return JsonResponse(
                {
                    "error":
                    "FAISS index unavailable"
                },
                status=500
            )

   

        results = search_similar_products(
            query_vector=query_vector,
            index=index,
            ids=ids,
            top_k=50
        )

        print(
            "FAISS Results =====>",
            results
        )

        if not results:

            fallback_products = list(
                models.ProductDetail.objects
                .filter(status="Active")
                .select_related(
                    "category",
                    "subcategory"
                )
                .only(
                    "id",
                    "product_name",
                    "product_name_french",
                    "color",
                    "product_image_1",
                    "category__category",
                    "subcategory__subcategory"
                )[:10]
            )

            return JsonResponse({
                "country": country,
                "predicted_subcategory": "",
                "similar_products":
                    build_fallback_products(
                        fallback_products
                    )
            })

  
        final_results = rank_products(
            results
        )


        if not final_results:

            fallback_products = list(
                models.ProductDetail.objects
                .filter(status="Active")
                .select_related(
                    "category",
                    "subcategory"
                )
                .only(
                    "id",
                    "product_name",
                    "product_name_french",
                    "color",
                    "product_image_1",
                    "category__category",
                    "subcategory__subcategory"
                )[:10]
            )

            return JsonResponse({
                "country": country,
                "predicted_subcategory": "",
                "similar_products":
                    build_fallback_products(
                        fallback_products
                    )
            })

        dominant_subcategory = ""

        subcategories = [
            p["subcategory"]
            for p in final_results
            if p["subcategory"]
        ]

        if subcategories:

            dominant_subcategory = (
                Counter(subcategories)
                .most_common(1)[0][0]
            )

    
        return JsonResponse({

            "country": country,

            "predicted_subcategory":
                dominant_subcategory,

            "similar_products":
                final_results

        })

    except Exception as e:

        print(
            "recommend_products ERROR =====>",
            str(e)
        )

        return JsonResponse(
            {"error": str(e)},
            status=500
        )


@csrf_exempt
def recently_view_product_list(request):
    if request.method =="POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))

        customer = python_data.get('customer')

        currencyCode = python_data.get('currencyCode',None)
        countryCallingCode = python_data.get('countryCallingCode',None)
        country = python_data.get('countryName','Egypt')
        ip_address = python_data.get('ip_address')
        user_id = python_data.get('customer')

        try:
            if currencyCode not in [None,'','null']:
                country = models.CountryWithCurrency.objects.filter(currency_code = currencyCode).first().country_name
            elif countryCallingCode not in [None,'','null']:
                country = models.CountryWithCurrency.objects.filter(country_calling_code = countryCallingCode).first().country_name
                
            elif user_id:
                user = models.CustomerDetail.objects.get(id = user_id)
                countryCode = user.countryCode

                if models.CountryWithCurrency.objects.filter(country_calling_code = countryCode).exists():
                    country = models.CountryWithCurrency.objects.get(country_calling_code = countryCode).country_name
                else:
                    if country not in [None,'','null']:
                        country = country
                    else:
                        try:
                            response = requests.get(f'https://ipapi.co/{ip_address}/json/')
                            response = response.json()
                            country = response.get("country_name")
                            print("response====>",response)

                            if country in [None,'','null']:
                                country = "Egypt"

                        except Exception as e:
                            print("Errroooorrr----->",e)
                            country = "Egypt"
                        

            else:
                if country in [None,'','null']:
                    try:
                        response = requests.get(f'https://ipapi.co/{ip_address}/json/')
                        response = response.json()
                        country = response.get("country_name")
                        print("response====>",response)

                        if country in [None,'','null']:
                            country = "Egypt"

                    except Exception as e:
                        print("Errroooorrr----->",e)
                        country = "Egypt"
                else:
                    country = country
        except Exception as e:
            print("Error-=-=-=--->",e)
            country = 'Egypt'

        product = models.RecentlyViewProduct.objects.filter(customer = customer).order_by('-id')
        serializer = RecentlyViewProductSerializer(product, many=True, context = {'country':country}).data

        res={
            'data':serializer
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)


@csrf_exempt
def category_delete(request):
    if request.method =="POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))

        category = python_data.get('id')

        check_category = models.CategoryDetail.objects.filter(id= category).count()
        if check_category == 1:
            delete_product = models.ProductDetail.objects.filter(category = category)
            delete_product.delete()
            
            delete_subcategory = models.SubCategoryDetail.objects.filter(category = category)
            delete_subcategory.delete()
            
            delete_category = models.CategoryDetail.objects.get(id = category)
            delete_category.delete()
        
            res={
                'message':'Category along with related Subcategory and Product deleted succesfully.' 
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)

        else:
            res={
                'message':'Something went wrong.' 
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 406)


@csrf_exempt
def subcategory_delete(request):
    if request.method =="POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))

        subcategory = python_data.get('id')

        check_category = models.SubCategoryDetail.objects.filter(id= subcategory).count()
        if check_category == 1:
            delete_product = models.ProductDetail.objects.filter(subcategory = subcategory)
            delete_product.delete()
            
            delete_subcategory = models.SubCategoryDetail.objects.get(id = subcategory)
            delete_subcategory.delete()
            
            res={
                'message':'Subcategory along with related Product deleted succesfully.' 
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)

        else:
            res={
                'message':'Something went wrong.' 
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 406)


@csrf_exempt
def product_delete(request):
    if request.method =="POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))

        product = python_data.get('id')

        check_category = models.ProductDetail.objects.filter(id= product).count()
        if check_category == 1:
            delete_product = models.ProductDetail.objects.get(id = product)
            delete_product.delete()
            
            res={
                'message':'Product deleted succesfully.' 
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)

        else:
            res={
                'message':'Something went wrong.' 
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 406)


@csrf_exempt
def category_status_update(request):
    if request.method =="POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))

        category = python_data.get('id')
        status = python_data.get('status')

        check_category = models.CategoryDetail.objects.filter(id= category).count()
        if check_category == 1:
            if status == 'Active':
                update_category = models.CategoryDetail.objects.get(id= category)
                update_category.status = status
                update_category.save()

            elif status == 'Inactive':
                update_category = models.CategoryDetail.objects.get(id= category)
                update_category.status = status
                update_category.save()

                get_all_subcategory = models.SubCategoryDetail.objects.filter(category=category).update(status=status)
                get_all_product = models.ProductDetail.objects.filter(category=category).update(status=status)
          
            res={
                'message':'Category Status update Succesfully.' 
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)

        else:
            res={
                'message':'Something went wrong.' 
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 406)




@csrf_exempt
def subcategory_status_update(request):
    if request.method =="POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))

        subcategory = python_data.get('id')
        status = python_data.get('status')

        check_category = models.SubCategoryDetail.objects.filter(id= subcategory).count()
        if check_category == 1:
            if status == 'Active':
                update_category = models.SubCategoryDetail.objects.get(id= subcategory)
                update_category.status = status
                update_category.save()

            elif status == 'Inactive':
                update_category = models.SubCategoryDetail.objects.get(id= subcategory)
                update_category.status = status
                update_category.save()

                get_all_product = models.ProductDetail.objects.filter(subcategory=subcategory).update(status=status)
          
            res={
                'message':'Subcategory Status update Succesfully.' 
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)

        else:
            res={
                'message':'Something went wrong.' 
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 406)


@csrf_exempt
def product_status_update(request):
    if request.method =="POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))

        product = python_data.get('id')
        status = python_data.get('status')

        check_product = models.ProductDetail.objects.filter(id= product).count()
        if check_product == 1:
           
            update_product = models.ProductDetail.objects.get(id= product)
            update_product.status = status
            update_product.save()

            if status == 'Inactive':
                cart_delete = models.CartDetail.objects.filter(product= product)
                cart_delete.delete()

            

            res={
                'message':'Product Status update Succesfully.' 
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)

        else:
            res={
                'message':'Something went wrong.' 
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 406)




@csrf_exempt
def product_filter_data(request):
    if request.method =="POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))

        category = python_data.get('category')
        min_price = float(python_data.get('min_price'))
        max_price = float(python_data.get('max_price'))


        product_list = models.ProductDetail.objects.filter(category= category, price__gte = min_price, price__lte = max_price, status= 'Active')
        product_serializer = ProductDataSerializer(product_list, many=True).data
        

        res={
            'data':product_serializer 
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)


@csrf_exempt
def get_product_data_update(request):
    if request.method =="POST":
        
        product_list = models.ProductDetail.objects.all().order_by('id')[:200]
        for product in product_list:
            print(product.id, 'product.id')
            product = models.ProductDetail.objects.get(id = product.id)
            get_all_variant_price = models.ProductModelVariant.objects.filter(product = product.id).values_list('price', flat=True)
            min_price = min(get_all_variant_price)
            # print(min_price, product.product_name)
            product.price = min_price
            product.save()


        res={
            'message':'Product Status update Succesfully.' 
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)

'''

{'data': 
{'dashboard': {'view': False}, 
'vendor': {'view': False, 'create': False, 'update': False, 'delete': False}, 
'product': {'view': False, 'create': False, 'update': False, 'delete': False}, 
'categories': {'view': False, 'create': False, 'update': False, 'delete': False}, 
'support': {'view': False, 'create': False, 'update': False, 'delete': False}, 
'chatAgent': {'view': False, 'create': False, 'update': False, 'delete': False}, 
'settings': {'view': False, 'create': False, 'update': False, 'delete': False}, 
'order': {'view': False}, 
'user': {'view': False}, 
'transaction': {'view': False}}, 
'id': '3'}
'''

@csrf_exempt
def sub_admin_module_rights_update(request):
    if request.method =="POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))
        id = python_data.get('id')
        data = python_data.get('data')
        print(python_data, 'python_data')
        now = datetime.now()
        date_time = now.strftime('%Y-%m-%d, %H:%M:%S')

        ## Dashboard
        check_dashboard = models.AdminModuleRightsDetail.objects.filter(admin = id, module_name= 'dashboard').count()
        if check_dashboard == 0:
            dashboard = models.AdminModuleRightsDetail.objects.create(
                admin_id = id, 
                module_name= 'dashboard',
                view = data['dashboard']['view'],
                create = data['dashboard']['create'],
                update = data['dashboard']['update'],
                delete = data['dashboard']['delete'],
                last_update = date_time
                ).save()
        else:
            dashboard_update = models.AdminModuleRightsDetail.objects.get(admin = id, module_name= 'dashboard')
            dashboard_update.view = data['dashboard']['view']
            dashboard_update.create = data['dashboard']['create']
            dashboard_update.update = data['dashboard']['update']
            dashboard_update.delete = data['dashboard']['delete']
            dashboard_update.last_update = date_time
            dashboard_update.save()

        ### Vendor
        check_vendor = models.AdminModuleRightsDetail.objects.filter(admin = id, module_name= 'vendor').count()
        if check_vendor == 0:
            vendor = models.AdminModuleRightsDetail.objects.create(
                admin_id = id, 
                module_name= 'vendor',
                view = data['vendor']['view'],
                create = data['vendor']['create'],
                update = data['vendor']['update'],
                delete = data['vendor']['delete'],
                last_update = date_time
                ).save()
        else:
            vendor_update = models.AdminModuleRightsDetail.objects.get(admin = id, module_name= 'vendor')
            vendor_update.view = data['vendor']['view']
            vendor_update.create = data['vendor']['create']
            vendor_update.update = data['vendor']['update']
            vendor_update.delete = data['vendor']['delete']
            vendor_update.last_update = date_time
            vendor_update.save()

        ### product
        check_product = models.AdminModuleRightsDetail.objects.filter(admin = id, module_name= 'product').count()
        if check_product == 0:
            product = models.AdminModuleRightsDetail.objects.create(
                admin_id = id, 
                module_name= 'product',
                view = data['product']['view'],
                create = data['product']['create'],
                update = data['product']['update'],
                delete = data['product']['delete'],
                last_update = date_time
                ).save()
        else:
            product_update = models.AdminModuleRightsDetail.objects.get(admin = id, module_name= 'product')
            product_update.view = data['product']['view']
            product_update.create = data['product']['create']
            product_update.update = data['product']['update']
            product_update.delete = data['product']['delete']
            product_update.last_update = date_time
            product_update.save()
        
        ## categories
        check_categories = models.AdminModuleRightsDetail.objects.filter(admin = id, module_name= 'categories').count()
        if check_categories == 0:
            categories = models.AdminModuleRightsDetail.objects.create(
                admin_id = id, 
                module_name= 'categories',
                view = data['categories']['view'],
                create = data['categories']['create'],
                update = data['categories']['update'],
                delete = data['categories']['delete'],
                last_update = date_time
                ).save()
        else:
            categories_update = models.AdminModuleRightsDetail.objects.get(admin = id, module_name= 'categories')
            categories_update.view = data['categories']['view']
            categories_update.create = data['categories']['create']
            categories_update.update = data['categories']['update']
            categories_update.delete = data['categories']['delete']
            categories_update.last_update = date_time
            categories_update.save()
        

        ## support
        check_support = models.AdminModuleRightsDetail.objects.filter(admin = id, module_name= 'support').count()
        if check_support == 0:
            support = models.AdminModuleRightsDetail.objects.create(
                admin_id = id, 
                module_name= 'support',
                view = data['support']['view'],
                create = data['support']['create'],
                update = data['support']['update'],
                delete = data['support']['delete'],
                last_update = date_time
                ).save()
        else:
            support_update = models.AdminModuleRightsDetail.objects.get(admin = id, module_name= 'support')
            support_update.view = data['support']['view']
            support_update.create = data['support']['create']
            support_update.update = data['support']['update']
            support_update.delete = data['support']['delete']
            support_update.last_update = date_time
            support_update.save()

        
        ## chatAgent
        check_chatAgent = models.AdminModuleRightsDetail.objects.filter(admin = id, module_name= 'chatAgent').count()
        if check_chatAgent == 0:
            chatAgent = models.AdminModuleRightsDetail.objects.create(
                admin_id = id, 
                module_name= 'chatAgent',
                view = data['chatAgent']['view'],
                create = data['chatAgent']['create'],
                update = data['chatAgent']['update'],
                delete = data['chatAgent']['delete'],
                last_update = date_time
                ).save()
        else:
            chatAgent_update = models.AdminModuleRightsDetail.objects.get(admin = id, module_name= 'chatAgent')
            chatAgent_update.view = data['chatAgent']['view']
            chatAgent_update.create = data['chatAgent']['create']
            chatAgent_update.update = data['chatAgent']['update']
            chatAgent_update.delete = data['chatAgent']['delete']
            chatAgent_update.last_update = date_time
            chatAgent_update.save()
        
        
        ## settings
        check_settings = models.AdminModuleRightsDetail.objects.filter(admin = id, module_name= 'settings').count()
        if check_settings == 0:
            settings = models.AdminModuleRightsDetail.objects.create(
                admin_id = id, 
                module_name= 'settings',
                view = data['settings']['view'],
                create = data['settings']['create'],
                update = data['settings']['update'],
                delete = data['settings']['delete'],
                last_update = date_time
                ).save()
        else:
            settings_update = models.AdminModuleRightsDetail.objects.get(admin = id, module_name= 'settings')
            settings_update.view = data['settings']['view']
            settings_update.create = data['settings']['create']
            settings_update.update = data['settings']['update']
            settings_update.delete = data['settings']['delete']
            settings_update.last_update = date_time
            settings_update.save()


        ## order
        check_order = models.AdminModuleRightsDetail.objects.filter(admin = id, module_name= 'order').count()
        if check_order == 0:
            order = models.AdminModuleRightsDetail.objects.create(
                admin_id = id, 
                module_name= 'order',
                view = data['order']['view'],
                create = data['order']['create'],
                update = data['order']['update'],
                delete = data['order']['delete'],
                last_update = date_time
                ).save()
        else:
            order_update = models.AdminModuleRightsDetail.objects.get(admin = id, module_name= 'order')
            order_update.view = data['order']['view']
            order_update.create = data['order']['create']
            order_update.update = data['order']['update']
            order_update.delete = data['order']['delete']
            order_update.last_update = date_time
            order_update.save()


        ## user
        check_user = models.AdminModuleRightsDetail.objects.filter(admin = id, module_name= 'user').count()
        if check_user == 0:
            user = models.AdminModuleRightsDetail.objects.create(
                admin_id = id, 
                module_name= 'user',
                view = data['user']['view'],
                create = data['user']['create'],
                update = data['user']['update'],
                delete = data['user']['delete'],
                last_update = date_time
                ).save()
        else:
            user_update = models.AdminModuleRightsDetail.objects.get(admin = id, module_name= 'user')
            user_update.view = data['user']['view']
            user_update.create = data['user']['create']
            user_update.update = data['user']['update']
            user_update.delete = data['user']['delete']
            user_update.last_update = date_time
            user_update.save()


         ## transaction
        # check_transaction = models.AdminModuleRightsDetail.objects.filter(admin = id, module_name= 'transaction').count()
        # if check_transaction == 0:
        #     transaction = models.AdminModuleRightsDetail.objects.create(
        #         admin_id = id, 
        #         module_name= 'transaction',
        #         view = data['transaction']['view'],
        #         create = data['transaction']['create'],
        #         update = data['transaction']['update'],
        #         delete = data['transaction']['delete'],
        #         last_update = date_time
        #         ).save()
        # else:
        #     transaction_update = models.AdminModuleRightsDetail.objects.get(admin = id, module_name= 'transaction')
        #     transaction_update.view = data['transaction']['view']
        #     transaction_update.create = data['transaction']['create']
        #     transaction_update.update = data['transaction']['update']
        #     transaction_update.delete = data['transaction']['delete']
        #     transaction_update.last_update = date_time
        #     transaction_update.save()

         # tags
        check_tags = models.AdminModuleRightsDetail.objects.filter(admin = id, module_name= 'tags').count()
        if check_tags == 0:
            if data['tags']:
                tags = models.AdminModuleRightsDetail.objects.create(
                    admin_id = id, 
                    module_name= 'tags',
                    view = data['tags']['view'],
                    create = data['tags']['create'],
                    update = data['tags']['update'],
                    delete = data['tags']['delete'],
                    last_update = date_time
                    ).save()
        else:
            tags_update = models.AdminModuleRightsDetail.objects.get(admin = id, module_name= 'tags')
            tags_update.view = data['tags']['view']
            tags_update.create = data['tags']['create']
            tags_update.update = data['tags']['update']
            tags_update.delete = data['tags']['delete']
            tags_update.last_update = date_time
            tags_update.save()
         
         # influencer
        check_influencer = models.AdminModuleRightsDetail.objects.filter(admin = id, module_name= 'influencer').count()
        if check_influencer == 0:
            if data['influencer']:
                influencer = models.AdminModuleRightsDetail.objects.create(
                    admin_id = id, 
                    module_name= 'influencer',
                    view = data['influencer']['view'],
                    create = data['influencer']['create'],
                    update = data['influencer']['update'],
                    delete = data['influencer']['delete'],
                    last_update = date_time
                    ).save()
        else:
            influencer_update = models.AdminModuleRightsDetail.objects.get(admin = id, module_name= 'influencer')
            influencer_update.view = data['influencer']['view']
            influencer_update.create = data['influencer']['create']
            influencer_update.update = data['influencer']['update']
            influencer_update.delete = data['influencer']['delete']
            influencer_update.last_update = date_time
            influencer_update.save()
        
         # promocode
        check_promocode = models.AdminModuleRightsDetail.objects.filter(admin = id, module_name= 'promocode').count()
        if check_promocode == 0:
            if data['promocode']:
                promocode = models.AdminModuleRightsDetail.objects.create(
                    admin_id = id, 
                    module_name= 'promocode',
                    view = data['promocode']['view'],
                    create = data['promocode']['create'],
                    update = data['promocode']['update'],
                    delete = data['promocode']['delete'],
                    last_update = date_time
                    ).save()
        else:
            promocode_update = models.AdminModuleRightsDetail.objects.get(admin = id, module_name= 'promocode')
            promocode_update.view = data['promocode']['view']
            promocode_update.create = data['promocode']['create']
            promocode_update.update = data['promocode']['update']
            promocode_update.delete = data['promocode']['delete']
            promocode_update.last_update = date_time
            promocode_update.save()
        
         # warehouse
        check_warehouse = models.AdminModuleRightsDetail.objects.filter(admin = id, module_name= 'warehouse').count()
        if check_warehouse == 0:
            if data['warehouse']:
                warehouse = models.AdminModuleRightsDetail.objects.create(
                    admin_id = id, 
                    module_name= 'warehouse',
                    view = data['warehouse']['view'],
                    create = data['warehouse']['create'],
                    update = data['warehouse']['update'],
                    delete = data['warehouse']['delete'],
                    last_update = date_time
                    ).save()
        else:
            warehouse_update = models.AdminModuleRightsDetail.objects.get(admin = id, module_name= 'warehouse')
            warehouse_update.view = data['warehouse']['view']
            warehouse_update.create = data['warehouse']['create']
            warehouse_update.update = data['warehouse']['update']
            warehouse_update.delete = data['warehouse']['delete']
            warehouse_update.last_update = date_time
            warehouse_update.save()
        
         # cargo
        check_cargo = models.AdminModuleRightsDetail.objects.filter(admin = id, module_name= 'cargo').count()
        if check_cargo == 0:
            if data['cargo']:
                cargo = models.AdminModuleRightsDetail.objects.create(
                    admin_id = id, 
                    module_name= 'cargo',
                    view = data['cargo']['view'],
                    create = data['cargo']['create'],
                    update = data['cargo']['update'],
                    delete = data['cargo']['delete'],
                    last_update = date_time
                    ).save()
        else:
            cargo_update = models.AdminModuleRightsDetail.objects.get(admin = id, module_name= 'cargo')
            cargo_update.view = data['cargo']['view']
            cargo_update.create = data['cargo']['create']
            cargo_update.update = data['cargo']['update']
            cargo_update.delete = data['cargo']['delete']
            cargo_update.last_update = date_time
            cargo_update.save()
        
         # country
        check_country = models.AdminModuleRightsDetail.objects.filter(admin = id, module_name= 'country').count()
        if check_country == 0:
            if data['country']:
                country = models.AdminModuleRightsDetail.objects.create(
                    admin_id = id, 
                    module_name= 'country',
                    view = data['country']['view'],
                    create = data['country']['create'],
                    update = data['country']['update'],
                    delete = data['country']['delete'],
                    last_update = date_time
                    ).save()
        else:
            country_update = models.AdminModuleRightsDetail.objects.get(admin = id, module_name= 'country')
            country_update.view = data['country']['view']
            country_update.create = data['country']['create']
            country_update.update = data['country']['update']
            country_update.delete = data['country']['delete']
            country_update.last_update = date_time
            country_update.save()
        
         # inquiry
        check_inquiry = models.AdminModuleRightsDetail.objects.filter(admin = id, module_name= 'inquiry').count()
        if check_inquiry == 0:
            if data['inquiry']:
                inquiry = models.AdminModuleRightsDetail.objects.create(
                    admin_id = id, 
                    module_name= 'inquiry',
                    view = data['inquiry']['view'],
                    create = data['inquiry']['create'],
                    update = data['inquiry']['update'],
                    delete = data['inquiry']['delete'],
                    last_update = date_time
                    ).save()
        else:
            inquiry_update = models.AdminModuleRightsDetail.objects.get(admin = id, module_name= 'inquiry')
            inquiry_update.view = data['inquiry']['view']
            inquiry_update.create = data['inquiry']['create']
            inquiry_update.update = data['inquiry']['update']
            inquiry_update.delete = data['inquiry']['delete']
            inquiry_update.last_update = date_time
            inquiry_update.save()

        res={
            'message':'User Rights update successfully.' 
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)


@csrf_exempt
def sub_admin_module_rights_list(request):
    if request.method =="POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))
        id = python_data.get('id')
        admin_rights = models.AdminModuleRightsDetail.objects.filter(admin = id)
        rights_serialiser = AdminModuleRightsDetailSerializer(admin_rights, many=True).data
        res={
            'data': rights_serialiser
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)


@csrf_exempt
def sub_admin_module_rights(request):
    if request.method =="POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))
        id = python_data.get('id')
        module_name = python_data.get('module_name')
        print(python_data, 'python_data')
        admin_rights = models.AdminModuleRightsDetail.objects.get(admin = id, module_name = module_name)
        rights_serialiser = AdminModuleRightsDetailSerializer(admin_rights).data
        res={
            'data': rights_serialiser
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)






@csrf_exempt
def cash_in_view(request):
    python_data = JSONParser().parse(io.BytesIO(request.body))

    amount = python_data.get("amount")
    phone = python_data.get("phone")
    network = python_data.get("network_code")  
    currency = python_data.get("currency", "XOF")

    result = APIDTSClient.cash_in(amount, phone, network, currency)

    res={
        'data': result
    }
    return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)



@csrf_exempt
def status_view(request, txn_id):
    result = APIDTSClient.check_status(txn_id)
    res={
        'data': result
    }
    return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)


@csrf_exempt
def pending_order_vendor_count(request):
    if request.method =="POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))
        vendor = python_data.get('vendor')

        product_count = models.VendorOrderDetail.objects.filter(vendor = vendor, variant__status = "pending").count()
        
        res={
            'total_count': product_count
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)



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
def send_otp_whatsapp(request):
    if request.method =="POST":
        url = "https://api.verifyway.com/api/v1/"
        headers = {
            "Authorization": "Bearer 1515$iwLeuAjYrEcHnD8Rs2GymuXAefPF8M5fx7wV",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        code = 986987
        payload = {
            "recipient": "+919265096459",
            "type": "otp",
            "channel": "whatsapp",
            "fallback": "no",
            "code": code,
            "lang": "en",
            "message": f"Hello! Your Secure Login Code for Diaba app is {code}. Do not share this with anyone."
        }
        response = requests.post(url, json=payload, headers=headers)
        print(response, 'responseresponse')
        res={
        "status_code": response.status_code,
        "response": response.json()
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)


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


@csrf_exempt
def create_countrywithcurrency(request):
    if request.method == "POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))

        print("python_data--create_countrywithcurrency---->",python_data)

        country_calling_code = python_data.get('country_calling_code',None)
        country_name = python_data.get('country_name',None)
        currency_code = python_data.get('currency_code',None)
        currency_symbol = python_data.get('currency_symbol',None)
        country_iso_alphaTwo_key = python_data.get('country_iso_alphaTwo_key',None)

        bank_detail = python_data.get('bank_detail',None)
        cash_limit = python_data.get('cash_limit',None)


        if models.CountryWithCurrency.objects.filter(country_calling_code = country_calling_code).exists():
            res = {
                'message':'Country Calling Code already Used'
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 406)
        
        if models.CountryWithCurrency.objects.filter(country_name = country_name).exists():
            res = {
                'message':'Country Name already Used'
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 406)
        
        country_add = models.CountryWithCurrency.objects.create(
            country_calling_code = country_calling_code,
            country_name = country_name,
            currency_code = currency_code,
            currency_symbol = currency_symbol,
            country_iso_alphaTwo_key = country_iso_alphaTwo_key,
        )

        if bank_detail not in [None,'','null',{}]:
            bank_detail_create = models.CountryWiseBankDetail.objects.create(
                country_id = country_add.id,
                holder_name = bank_detail['holder_name'],
                bank_name = bank_detail['bank_name'],
                account_number = bank_detail['account_number'],
                branch_name = bank_detail['branch_name'],
                branch_code = bank_detail['branch_code'],
            )

        if cash_limit not in [None,'','null',{}]:
            cash_limit_create = models.CountryCashLimit.objects.create(
                country_id = country_add.id,
                cash_limit = cash_limit,
            )
        
        res = {
            'message':'Country Added Successfully'
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)

@csrf_exempt
def countrywithcurrency_list_admin(request):
    if request.method == "POST":
        countrywithcurrency_list = models.CountryWithCurrency.objects.all().order_by('-id')
        countrywithcurrency_list_serializer = AdminCountryWithCurrencyListSerializer(countrywithcurrency_list, many=True).data

        res = {
            'data':countrywithcurrency_list_serializer
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)


@csrf_exempt
def update_countrywithcurrency(request):
    if request.method == "POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))

        print("python_data--update_countrywithcurrency---->",python_data)

        id = python_data.get('id',None)
        country_calling_code = python_data.get('country_calling_code',None)
        country_name = python_data.get('country_name',None)
        currency_code = python_data.get('currency_code',None)
        currency_symbol = python_data.get('currency_symbol',None)
        country_iso_alphaTwo_key = python_data.get('country_iso_alphaTwo_key',None)
        cash_limit = python_data.get('cash_limit',None)

        bank_detail = python_data.get('bank_detail',None)

        if models.CountryWithCurrency.objects.filter(country_calling_code = country_calling_code).exclude(id = id).exists():
            res = {
                'message':'Country Calling Code already Used'
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 406)
        
        if models.CountryWithCurrency.objects.filter(country_name = country_name).exclude(id = id).exists():
            res = {
                'message':'Country Name already Used'
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 406)

        get_countrywithcurrency = models.CountryWithCurrency.objects.get(id = id)
        get_countrywithcurrency.country_calling_code = country_calling_code
        get_countrywithcurrency.country_name = country_name
        get_countrywithcurrency.currency_code = currency_code
        get_countrywithcurrency.currency_symbol = currency_symbol
        get_countrywithcurrency.country_iso_alphaTwo_key = country_iso_alphaTwo_key

        get_countrywithcurrency.save()

        if bank_detail not in [None,'','null',{}]:
            if  models.CountryWiseBankDetail.objects.filter(country = get_countrywithcurrency.id).exists():
                get_bank_detail = models.CountryWiseBankDetail.objects.get(country = get_countrywithcurrency.id)
                get_bank_detail.holder_name = bank_detail['holder_name']
                get_bank_detail.bank_name = bank_detail['bank_name']
                get_bank_detail.account_number = bank_detail['account_number']
                get_bank_detail.branch_name = bank_detail['branch_name']
                get_bank_detail.branch_code = bank_detail['branch_code']
                get_bank_detail.save()
            else:
                bank_detail_create = models.CountryWiseBankDetail.objects.create(
                country_id = get_countrywithcurrency.id,
                holder_name = bank_detail['holder_name'],
                bank_name = bank_detail['bank_name'],
                account_number = bank_detail['account_number'],
                branch_name = bank_detail['branch_name'],
                branch_code = bank_detail['branch_code'],
            )
        else:
            if bank_detail == {}:
                if  models.CountryWiseBankDetail.objects.filter(country = get_countrywithcurrency.id).exists():
                    get_bank_detail = models.CountryWiseBankDetail.objects.get(country = get_countrywithcurrency.id)
                    get_bank_detail.delete()


        
        if cash_limit not in [None,'','null',{}]:
            if  models.CountryCashLimit.objects.filter(country = get_countrywithcurrency.id).exists():
                if cash_limit in [None,'','null',0]:
                    cash_limit = None
                    
                get_bank_detail = models.CountryCashLimit.objects.get(country = get_countrywithcurrency.id)
                get_bank_detail.cash_limit = cash_limit
                get_bank_detail.save()
            else:
                cash_limit_create = models.CountryCashLimit.objects.create(
                country_id = get_countrywithcurrency.id,
                cash_limit =cash_limit,
            )


        res = {
            'message':'Country Updated Successfully'
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)

@csrf_exempt
def update_countrywithcurrency_price_by(request):
    if request.method == "POST":

        python_data = JSONParser().parse(io.BytesIO(request.body))

        print("python_data--update_countrywithcurrency_price_by---->",python_data)

        prices = python_data.get('prices',None)

        for pr in prices:
            try:
                id = pr['country_id']
                price_by_air = pr.get('price_by_air',None)
                price_by_ship = pr.get('price_by_ship',None)
                express_shipping = pr.get('express_shipping',None)

                get_countrywithcurrency = models.CountryWithCurrency.objects.get(id = id)
                get_countrywithcurrency.price_by_air = price_by_air
                get_countrywithcurrency.price_by_ship = price_by_ship
                get_countrywithcurrency.express_shipping = express_shipping
                get_countrywithcurrency.save()

                if get_countrywithcurrency.price_by_air not in [None,'','null'] and get_countrywithcurrency.price_by_ship not in [None,'','null']:
                    get_countrywithcurrency.status = 'Active'
                    get_countrywithcurrency.save()

            except:
                res = {
                    'message':'Few Price has not updated due to server issue'
                }
                return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)


        res = {
            'message':'Price By Updated Successfully'
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)
    



@csrf_exempt
def delete_countrywithcurrency(request):
    if request.method == "POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))

        print("python_data--delete_countrywithcurrency---->",python_data)

        id = python_data.get('id',None)

        try:
            get_countrywithcurrency = models.CountryWithCurrency(id = id)
            get_countrywithcurrency.delete()

            res = {
                'message':'Country Deleted Successfully'
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)

        except:
            res = {
                'message':'Country Does not Exist'
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 406)


@csrf_exempt
def currency_coversion(request):
    if request.method == "POST":
        # python_data = JSONParser().parse(io.BytesIO(request.body))

        # print("python_data--currency_coversion---->",python_data)

        # url = "https://api.freecurrencyapi.com/v1/latest?apikey=fca_live_iQa2JUQuTqahib1SZyl54TBUkPUIY7UfIoGPGZ1z&base_curreency=USD"
        # url = "https://api.exchangerate.host/latest"

        endpoint = "convert"
        access_key = "f2fd2d4b28e2ea8b345524bf52fe8ff4"
        from_currency = "USD"
        to_currency = "INR"
        amount = 10

        # url = f"https://api.exchangerate.host/{endpoint}?access_key={access_key}&from={from_currency}&to={to_currency}&amount={amount}"

        # response = requests.get(url)
        # data = response.json()

        # print("Full Response:", data)

        # # Access conversion result
        # if data.get("result") is not None:
        #     print("Converted Amount:", data["result"])
        # else:
        #     print("Error:", data.get("error"))


        source = "USD"
        currencies = "XOF,XAF,INR"

        url = f"http://api.exchangerate.host/live?access_key={access_key}&source={source}&currencies={currencies}&format=1"

        response = requests.get(url)
        data = response.json()


        # response = requests.get(url)

        res={
            'data':response.json()
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)

@csrf_exempt
def currency_rates_update(request):
    if request.method == "POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))
        print("python_data--currency_rates_update---->",python_data)

        rates = python_data.get('rates', None)

        for rate in rates:
            currency_code = rate.get('currency_code', None)
            system_rate = rate.get('system_rate', None)

            if models.CurrencyConverter.objects.filter(currency_code = currency_code).exists():
                convert_currency = models.CurrencyConverter.objects.get(currency_code = currency_code)
                convert_currency.system_rate = system_rate
                convert_currency.save()
            
            else:
                res={
                    'message':f'{currency_code} - Currency not Found'
                }
                return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 406)

        res={
            'message':'Currency Updated Sucesssfully'
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)

@csrf_exempt
def currency_rates(request):
    if request.method == "POST":
        convert_currency = models.CurrencyConverter.objects.all().order_by('-id')
        convert_currency_serializer = AdminCurrencyConverterSerializer(convert_currency, many=True).data

        res={
            'data':convert_currency_serializer
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)

@csrf_exempt
def intro_banner_update(request):
    python_data={}
    for i,j in request.FILES.items():
        python_data.update({i:j})
 
    for i,j in request.POST.items():
        python_data.update({i:j})
   
    id = python_data.get('id')
    banner = python_data.get('banner')
 
 
    banner_update = models.IntroBanner.objects.get(id = id)
    if type(banner) != str:
        banner_update.banner = banner
    banner_update.save()
   
    res = {
        'message':"Updated successfully."        
        }
    json_data = JSONRenderer().render(res)
    return HttpResponse(json_data, content_type= 'application/json', status=200)


@csrf_exempt
def intro_banner_data(request):
    if request.method == 'POST':
        project_list = models.IntroBanner.objects.all().first()
       
        serialiser = IntroBannerSerializer(project_list).data
        res = {
            'data':serialiser        
            }
        json_data = JSONRenderer().render(res)
        return HttpResponse(json_data, content_type= 'application/json', status=200)  


@csrf_exempt
def file_update_test(request):
    if request.method == "POST":
        
        get_all_product = models.ProductDetail.objects.all().order_by('id')
        # get_all_product = models.ProductDetail.objects.filter(id = 260)
        for product in get_all_product:
            # print(product.product_image_1, 'product')
            for num in range(1, 9):
                field_name = f'product_image_{num}'

                
                image = getattr(product, field_name)
                print(field_name, 'fasfasf', image , 'product_image',product.id )

                # print(image, 'image')
                if image != None and image != 'null' and image != '':
                    # print('Test_data')
                    try:
                        img = Image.open(image)
                        if img.format == "AVIF":    
                            # print(img.format, 'Test data 1')    
                            if img.mode in ("RGBA", "LA"):
                                img = img.convert("RGB")

                            buffer = BytesIO()
                            img.save(buffer, format="JPEG", quality=90)
                            buffer.seek(0)

                            base_name, ext = os.path.splitext(image.name)
                            base_name = base_name.split("/")[-1]
                            jpg_name = base_name + ".jpg"
                            content = ContentFile(buffer.read(), name=jpg_name)
                            # print(content, 'field_name', field_name, 'base_nae', base_name )

                            save_data = models.ProductDetail.objects.get(id=product.id)

                            setattr(save_data, field_name, content)  # dynamic assignment
                            save_data.save()
                    except:
                        pass 
                
        res = {
                'message':'File save '
            }
        return HttpResponse(res, content_type= 'application/json', status=200)




@csrf_exempt
def model_file_update_test(request):
    if request.method == "POST":
        
        get_all_product = models.ProductModel.objects.all().order_by('-id')
        for product in get_all_product:
            image = product.model_image
            field_name = 'model_image'
            
            # print(image, 'image')
            if image != None and image != 'null' and image != '':
                try:
                    img = Image.open(image)
                    if img.format == "AVIF":        
                        if img.mode in ("RGBA", "LA"):
                            img = img.convert("RGB")

                        buffer = BytesIO()
                        img.save(buffer, format="JPEG", quality=90)
                        buffer.seek(0)

                        base_name, ext = os.path.splitext(image.name)
                        base_name = base_name.split("/")[-1]
                        jpg_name = base_name + ".jpg"
                        content = ContentFile(buffer.read(), name=jpg_name)
                        print(content, 'field_name', field_name, 'base_nae', base_name )

                        save_data = models.ProductModel.objects.get(id=product.id)

                        setattr(save_data, field_name, content)  # dynamic assignment
                        save_data.save()
                except:
                    pass
        res = {
                'message':'File save '
            }
        return HttpResponse(res, content_type= 'application/json', status=200)



@csrf_exempt
def variant_file_update_test(request):
    if request.method == "POST":
        count = 0
        get_all_product = models.ProductModelVariant.objects.all().order_by('id')
        for product in get_all_product:
            image = product.image
            field_name = 'image'
            
            # print(image, 'image')
            if image != None and image != 'null' and image != '':
                try:
                    img = Image.open(image)
                    if img.format == "AVIF":        
                        if img.mode in ("RGBA", "LA"):
                            img = img.convert("RGB")

                        buffer = BytesIO()
                        img.save(buffer, format="JPEG", quality=90)
                        buffer.seek(0)

                        base_name, ext = os.path.splitext(image.name)
                        base_name = base_name.split("/")[-1]
                        jpg_name = base_name + ".jpg"
                        content = ContentFile(buffer.read(), name=jpg_name)
                        print(content, 'field_name', field_name, 'base_nae', base_name )

                        save_data = models.ProductModelVariant.objects.get(id=product.id)

                        setattr(save_data, field_name, content)  # dynamic assignment
                        save_data.save()
                        count += 1
                        print(count, 'count')
                except:
                    pass
        res = {
                'message':'File save',
                'count':count
            }
        print(res)
        return HttpResponse(res, content_type= 'application/json', status=200)
    

@csrf_exempt
def influencer_register(request):
    if request.method == 'POST':
        python_data = JSONParser().parse(io.BytesIO(request.body))

        email = python_data.get('email')
        countryCode = python_data.get('countryCode')
        mobileNumber = python_data.get('mobileNumber')
        name = python_data.get('name')
        commission = python_data.get('commission')
        country = python_data.get('country')

 
        digits = "abcdefghjiklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
        password = ""
        for i in range(8) :
            password += digits[math.floor(random.random() * 52)]

        now = datetime.now()
        date_time = now.strftime('%Y-%m-%d, %H:%M:%S')

        check_email = models.InfluencerDetail.objects.filter(email = email).count()
        if check_email == 0:
        
            create_influencer = models.InfluencerDetail.objects.create(
                email = email,
                countryCode = countryCode,
                mobileNumber = mobileNumber,
                name = name,
                password = password,
                commission = commission,
                country = country,
                status = 'Active',
                created_at = datetime.now()
            ).save()

            res={
                'message':"Influencer registerd successfully."
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)
        else:
            res = {
                'message':"This email is already linked to an existing account. Please use another one."        
                }
            json_data = JSONRenderer().render(res)
            return HttpResponse(json_data, content_type= 'application/json', status=406)




@csrf_exempt
def influencer_update(request):
    if request.method == 'POST':
        python_data = JSONParser().parse(io.BytesIO(request.body))
        print(python_data, 'python_data')
        email = python_data.get('email')
        countryCode = python_data.get('countryCode')
        mobileNumber = python_data.get('mobileNumber')
        name = python_data.get('name')
        commission = python_data.get('commission')
        id = python_data.get('id')

        now = datetime.now()
        date_time = now.strftime('%Y-%m-%d, %H:%M:%S')

        check_email = models.InfluencerDetail.objects.filter(email = email).count()
        if check_email == 1:
            influencer = models.InfluencerDetail.objects.get(id = id)
            influencer.countryCode = python_data.get('countryCode', influencer.countryCode)
            influencer.mobileNumber = python_data.get('mobileNumber', influencer.mobileNumber)
            influencer.name = python_data.get('name', influencer.name)
            influencer.commission = python_data.get('commission', influencer.commission)
            influencer.country = python_data.get('country', influencer.country)
            influencer.password = python_data.get('password', influencer.password)
            influencer.save()

            res={
                'message':"Influencer update successfully."
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)
        else:
            res = {
                'message':"This email is already linked to an existing account. Please use another one."        
                }
            json_data = JSONRenderer().render(res)
            return HttpResponse(json_data, content_type= 'application/json', status=406)
        

@csrf_exempt
def influencer_status_update(request):
    if request.method == 'POST':
        python_data = JSONParser().parse(io.BytesIO(request.body))

        id = python_data.get('id')
        status = python_data.get('status')
      

        check_email = models.InfluencerDetail.objects.filter(id = id).count()
        if check_email == 1:
            influencer = models.InfluencerDetail.objects.get(id = id)
            influencer.status = python_data.get('status', influencer.status)
            influencer.save()
            res={
                'message':"Influencer status update successfully."
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)
        else:
            res={
                'message':"Something went Wrong."
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=406)


@csrf_exempt
def all_influencer_list(request):
    all_influencer = models.InfluencerDetail.objects.all().order_by('-id')
    serializer = InfluencerDetailSerializer(all_influencer, many=True).data

    res = {
        'data': serializer 
    }
    json_data = JSONRenderer().render(res)
    return HttpResponse(json_data, content_type= 'application/json', status=200)



@csrf_exempt
def influencer_login(request):
    if request.method == "POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))
        print(python_data, 'python_data')
        email = python_data.get('email')
        password = python_data.get('password')
        
        if models.InfluencerDetail.objects.filter(email = email).exists():
            check_user = models.InfluencerDetail.objects.filter(email = email, password = password).count()
            print(check_user, 'check_user')
            
            if check_user == 1:
                
                user = models.InfluencerDetail.objects.get(email = email, password = password)
                user_id = user.id
                res={
                    'message':'Login Successfully.',
                    'influencer_id':user_id
                }
                return JsonResponse(res, content_type= 'application/json', status=200)
            else:
                res={
                    'message':'Enter valid password.'
                }
                return JsonResponse(res, content_type= 'application/json', status=406)


        else:
            res={
                'message':'Influencer Not Found Contact Admin '
            }
            return JsonResponse(res, content_type= 'application/json', status=406)

                        
@csrf_exempt
def influencer_login_verify(request):
    if request.method == "POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))

        mobileNumber = python_data.get('mobile_number')
        countryCode = python_data.get('countryCode')
        OTP = python_data.get('OTP')
        
        if models.InfluencerDetail.objects.filter(countryCode = countryCode, mobileNumber = mobileNumber).exists():
            check_otp = models.InfluencerDetail.objects.filter(countryCode = countryCode, mobileNumber = mobileNumber, OTP = OTP).count()
            if check_otp == 1:
                res = {
                    'message': 'Login Successfully!' 
                }
                json_data = JSONRenderer().render(res)
                return HttpResponse(json_data, content_type= 'application/json', status=200)
            res = {
                'data': 'Enter valid OTP.' 
            }
            json_data = JSONRenderer().render(res)
            return HttpResponse(json_data, content_type= 'application/json', status=406)

        res = {
            'data': 'Enter valid credentials.' 
        }
        json_data = JSONRenderer().render(res)
        return HttpResponse(json_data, content_type= 'application/json', status=406)


 

@csrf_exempt
def promocode_create(request):
    if request.method == 'POST':
        python_data = JSONParser().parse(io.BytesIO(request.body))

        influencer = python_data.get('influencer')
        promocode = python_data.get('promocode')
        no_of_promocode = python_data.get('no_of_promocode')
        expiry_date = python_data.get('expiry_date')
        discount = python_data.get('discount')

        now = datetime.now()
        date_time = now.strftime('%Y-%m-%d, %H:%M:%S')

        check_promocode = models.PromocodeDetail.objects.filter(promocode = promocode).count()
        if check_promocode == 0:
            promocode_create = models.PromocodeDetail.objects.create(
                influencer_id = influencer,
                promocode = promocode,
                no_of_promocode = no_of_promocode,
                remaining_promocode = no_of_promocode,
                expiry_date = expiry_date,
                discount = discount,
                status = 'Active',
                created_at = datetime.now()
            ).save()

            res={
                'message':"Promocode Create successfully."
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)
        else:
            res={
                'message':"Promocode with this name already exists."
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=406)
                        
@csrf_exempt
def all_promocode_list(request):
    all_promocode = models.PromocodeDetail.objects.all().order_by('-id')
    serializer = PromocodeDetailSerializer(all_promocode, many=True).data

    res = {
        'data': serializer 
    }
    json_data = JSONRenderer().render(res)
    return HttpResponse(json_data, content_type= 'application/json', status=200)


@csrf_exempt
def promocode_list_influencer(request):
    python_data = JSONParser().parse(io.BytesIO(request.body))
    influencer = python_data.get('influencer')
    all_promocode = models.PromocodeDetail.objects.filter(influencer = influencer).order_by('-id')
    serializer = PromocodeDetailSerializer(all_promocode, many=True).data

    res = {
        'data': serializer 
    }
    json_data = JSONRenderer().render(res)
    return HttpResponse(json_data, content_type= 'application/json', status=200)



@csrf_exempt
def promocode_status_update(request):
    if request.method == 'POST':
        python_data = JSONParser().parse(io.BytesIO(request.body))

        id = python_data.get('id')
        status = python_data.get('status')
      

        check_email = models.PromocodeDetail.objects.filter(id = id).count()
        if check_email == 1:
            promocode = models.PromocodeDetail.objects.get(id = id)
            promocode.status = python_data.get('status', promocode.status)
            promocode.save()
            res={
                'message':"promocode status update successfully."
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=200)
        else:
            res={
                'message':"Something went Wrong."
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=406)

                        
@csrf_exempt
def influencer_detail(request):
    if request.method == "POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))
        influencer = python_data.get('influencer')
        
        if models.InfluencerDetail.objects.filter(id = influencer).exists():
            influencer_data = models.InfluencerDetail.objects.get(id = influencer)
            serializer = InfluencerDetailSerializer(influencer_data).data
                
            res = {
                'data': serializer 
            }
            json_data = JSONRenderer().render(res)
            return HttpResponse(json_data, content_type= 'application/json', status=200)
        else:
            res={
                'message':"Influencer Not Found."
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status=406)



@csrf_exempt
def all_money_network_list(request):
    list_data = []
    all_country = models.CountryMoneyNetwork.objects.all()
    for country in all_country:
        country = models.CountryMoneyNetwork.objects.get(id = country.id)
        country_dict = {}
        title = country.country_name
        key = country.key

        all_network = models.MoneyNetwork.objects.filter(country = country.id).order_by('id')
        serializer = MoneyNetworkSerializer(all_network, many=True).data
        country_dict.update({'title':title, 'key':key, 'options':serializer})
        list_data.append(country_dict)

    res = {
        'data': list_data 
    }
    json_data = JSONRenderer().render(res)
    return HttpResponse(json_data, content_type= 'application/json', status=200)


@csrf_exempt
def money_network_list(request):
    if request.method == "POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))
        country_key = python_data.get('country_key')
        amount = python_data.get('amount')
        print(python_data, 'python_data')
        all_network = models.MoneyNetwork.objects.filter(country__key = country_key, status="Active").order_by('id')
        serializer = MoneyNetworkSerializer(all_network, many=True).data
                
        check_cash_record = models.CountryCashLimit.objects.filter(country__country_iso_alphaTwo_key = country_key).count()
        if check_cash_record == 1:
            cash_record = models.CountryCashLimit.objects.get(country__country_iso_alphaTwo_key = country_key)
            print(cash_record, int(cash_record.cash_limit))
            if int(cash_record.cash_limit) > int(amount):
                print(True)
                all_network = models.MoneyNetwork.objects.filter(country__key = country_key,status="Active").exclude(value__in = ["cash","bank"]).order_by('id')
                serializer = MoneyNetworkSerializer(all_network, many=True).data
            else:
                print(False)
                all_network = models.MoneyNetwork.objects.filter(country__key = country_key,status="Active").order_by('id')
                serializer = MoneyNetworkSerializer(all_network, many=True).data
                
                print("serializer---->",serializer)

                bank_detail  = models.CountryWiseBankDetail.objects.filter(country__country_iso_alphaTwo_key = country_key).order_by('id').first()
                bank_detail_serializer = CountryWiseBankDetailSerializer(bank_detail).data

                [item.update({'bank_detail': bank_detail_serializer}) for item in serializer if item.get('value') == 'bank']

                print("serializer--->",serializer)
            

        else:
           serializer = [{
            "label": "Inquiry",
            "value": "cash",
            "icon": "https://diaba-live.s3.eu-west-3.amazonaws.com/image/network_icon/ic_cash_EG9Hcsv.png",
            }]

        if serializer == []:
           serializer = [{
            "label": "Inquiry",
            "value": "cash",
            "icon": "https://diaba-live.s3.eu-west-3.amazonaws.com/image/network_icon/ic_cash_EG9Hcsv.png",
            }]
            
                
        res = {
            'data': serializer 
        }
        json_data = JSONRenderer().render(res)
        return HttpResponse(json_data, content_type= 'application/json', status=200)


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
def status_change_product(request):
    list_data = []
    all_product = models.ProductDetail.objects.all()
    for product in all_product:
        print(product.id, '<--id')
        product = models.ProductDetail.objects.get(id = product.id)
        product.status = "Inactive"
        product.save()

    res = {
        'data': 'list_data' 
    }
    json_data = JSONRenderer().render(res)
    return HttpResponse(json_data, content_type= 'application/json', status=200)


@csrf_exempt
def cargo_create(request):
    if request.method == "POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))

        country = python_data.get('country')
        cargo_name = python_data.get('cargo_name')
        email = python_data.get('email')
        air_express_address = python_data.get('air_express_address')
        air_express_number = python_data.get('air_express_number')
        air_express_postal_code = python_data.get('air_express_postal_code')
        ship_address = python_data.get('ship_address')
        ship_number = python_data.get('ship_number')
        ship_postal_code = python_data.get('ship_postal_code')
        status = python_data.get('status')
        
        now = datetime.now()
        date_time = now.strftime('%Y-%m-%d, %H:%M:%S')

        create_cargo = models.CargoDetail.objects.create(
            country_id = country,
            cargo_name = cargo_name,
            email = email,
            air_express_address = air_express_address,
            air_express_number = air_express_number,
            air_express_postal_code = air_express_postal_code,
            ship_address = ship_address,
            ship_number = ship_number,
            ship_postal_code = ship_postal_code,
            status = "Active",
            created_at = date_time
        ).save()        
        res = {
            'message': 'Cargo Added Successfully.' 
        }
        json_data = JSONRenderer().render(res)
        return HttpResponse(json_data, content_type= 'application/json', status=200)


@csrf_exempt
def all_cargo_list(request):
    all_cargo = models.CargoDetail.objects.all()
    serialiser = CargoDetailSerializer(all_cargo, many=True).data
    res = {
        'data': serialiser 
    }
    json_data = JSONRenderer().render(res)
    return HttpResponse(json_data, content_type= 'application/json', status=200)


@csrf_exempt
def cargo_update(request):
    if request.method == "POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))

        id = python_data.get('id')
        update = models.CargoDetail.objects.get(id = id)
        update.country_id = python_data.get('country', update.country)
        update.cargo_name = python_data.get('cargo_name', update.cargo_name)
        update.email = python_data.get('email', update.email)
        
        update.air_express_address = python_data.get('air_express_address', update.air_express_address)
        update.air_express_number = python_data.get('air_express_number', update.air_express_number)
        update.air_express_postal_code = python_data.get('air_express_postal_code', update.air_express_postal_code)
        update.ship_address = python_data.get('ship_address', update.ship_address)
        update.ship_number = python_data.get('ship_number', update.ship_number)
        update.ship_postal_code = python_data.get('ship_postal_code', update.ship_postal_code)
        update.status = python_data.get('status', update.status)
        update.save()        
        
        res = {
            'message': 'Cargo data update Successfully.' 
        }
        json_data = JSONRenderer().render(res)
        return HttpResponse(json_data, content_type= 'application/json', status=200)


@csrf_exempt
def cargo_status_update(request):
    if request.method == "POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))

        id = python_data.get('id')
        update = models.CargoDetail.objects.get(id = id)
        update.status = python_data.get('status', update.status)
        update.save()        
        
        res = {
            'message': 'Status update Successfully.' 
        }
        json_data = JSONRenderer().render(res)
        return HttpResponse(json_data, content_type= 'application/json', status=200)



@csrf_exempt
def country_list_admin(request):
    if request.method == "POST":
        country = models.Country.objects.all()
        serializer = AdminCountrySerializer(country, many=True).data

        res = {
            'data':serializer
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
def cargo_list_app(request):
    python_data = JSONParser().parse(io.BytesIO(request.body))
    country_calling_code = python_data.get('country_calling_code')
    check_country = models.CountryWithCurrency.objects.filter(country_calling_code = country_calling_code).count()
    if check_country == 1:
        country = models.CountryWithCurrency.objects.get(country_calling_code = country_calling_code)    
        all_cargo = models.CargoDetail.objects.filter(is_cargo_for_all=True)
        serialiser = CargoDetailSerializer(all_cargo, many=True).data
        print(country, 'country')
        country_cargo = models.CargoDetail.objects.filter(country = country.id)
        country_serialiser = CargoDetailSerializer(country_cargo, many=True).data
        serialiser.extend(country_serialiser)
    else:
        all_cargo = models.CargoDetail.objects.filter(is_cargo_for_all=True)
        serialiser = CargoDetailSerializer(all_cargo, many=True).data

    res = {
        'data': serialiser 
    }
    json_data = JSONRenderer().render(res)
    return HttpResponse(json_data, content_type= 'application/json', status=200)


def success_url(request):
    return render(request, "success_url.html")

def error_url(request):
    return render(request, "error_url.html")





PIX_BASE_URL = "https://api.pixprovider.com"
PIX_API_KEY = 'PIX_560e8b6f-6038-41f8-8469-89c54f3611dd'

@csrf_exempt
def pay_pix_test(request):
    python_data = JSONParser().parse(io.BytesIO(request.body))
    amount = python_data.get("amount")
    txid = str(uuid.uuid4())
    print(txid, 'txidtxid')
    payload = {
        "txid": txid,
        "amount": float(amount),
        "description": "PIX Payment"
    }

    headers = {
        "Authorization": f"Bearer {PIX_API_KEY}",
        "Content-Type": "application/json",
    }
    print('try')
    try:
        response = requests.post(
            f"{PIX_BASE_URL}/pix/charges",
            json=payload,
            headers=headers,
            timeout=1,
        )
        response.raise_for_status()
    except requests.RequestException as e:
        res = {
            "error": "PIX provider error", "details": str(e)
        }
        json_data = JSONRenderer().render(res)
        return HttpResponse(json_data, content_type= 'application/json', status=502)


    data = response.json()
    return render(request, "error_url.html")



@csrf_exempt
def product_value_update_test(request):
    
    all_product = models.ProductDetail.objects.all()
    list_data = []
    for product in all_product:
        product = models.ProductDetail.objects.get(id = product.id)
        carton_length = product.carton_length
        if carton_length == '-':       
            product.carton_length = 0 
            product.carton_width = 0 
            product.carton_height = 0 
            product.carton_weight = 0 
            product.save()
            
            data = {'carton_weight':product.carton_weight,'product':product.id } 
            list_data.append(data)
    
    res = {
        'data': list_data
    }
    json_data = JSONRenderer().render(res)
    return HttpResponse(json_data, content_type= 'application/json', status=200)



@csrf_exempt
def all_payment_cargo_banner_list(request):
    if request.method == "POST":
        
        payment_data = models.PaymentCargoSlider.objects.all()
        serialser = PaymentCargoSliderSerializer(payment_data, many=True).data
        res = {
            'data':serialser
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)




@csrf_exempt
def payment_cargo_banner_create(request):
    if request.method == "POST":
        python_data = {}
        for i,j in request.FILES.items():
            python_data.update({i:j})
        
        for i,j in request.POST.items():
            python_data.update({i:j})

        now = datetime.now()
        date_time = now.strftime('%Y-%m-%d, %H:%M:%S')

        payment = models.PaymentCargoSlider.objects.create(
            banner = python_data.get('banner'),
            status = 'Active',
            created_at = date_time
        ).save()
        
        res = {
            'message':"Banner Added successfully."
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)



@csrf_exempt
def payment_cargo_banner_update(request):
    if request.method == "POST":
        python_data = {}
        for i,j in request.FILES.items():
            python_data.update({i:j})
        
        for i,j in request.POST.items():
            python_data.update({i:j})

        now = datetime.now()
        date_time = now.strftime('%Y-%m-%d, %H:%M:%S')
        id = python_data.get('id')
        check_payment = models.PaymentCargoSlider.objects.filter(id = id).count()
        if check_payment == 1:
            payment = models.PaymentCargoSlider.objects.get(id = id)
            if type(python_data.get('banner')) != str:
                payment.banner = python_data.get('banner', payment.banner)
            payment.status = python_data.get('status', payment.status)
            payment.save()
        
            res = {
                'message':"Banner update successfully."
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)
        else:
            res = {
                'message':"Something went wrong."
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 406)


@csrf_exempt
def payment_cargo_banner_status_update(request):
    if request.method == "POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))
        id = python_data.get('id')
        check_payment = models.PaymentCargoSlider.objects.filter(id = id).count()
        if check_payment == 1:
            payment = models.PaymentCargoSlider.objects.get(id = id)
            payment.status = python_data.get('status', payment.status)
            payment.save()
        
            res = {
                'message':"Banner update Successfully."
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)
        else:
            res = {
                'message':"Something went wrong."
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 406)




@csrf_exempt
def all_product_country(request):
    # print("PRint check")
    if request.method == "POST":
        try:
            python_data = JSONParser().parse(io.BytesIO(request.body))
            countryCode = python_data.get('countryCode',None)
            # print("python_data--->",python_data)
            # print("countryCode--->",countryCode)
            if countryCode in [None,'','null']:
                country_list = models.ProductCountry.objects.annotate(
                    all_first=Case(
                        When(name='All', then=Value(0)),
                        default=Value(1),
                        output_field=IntegerField(),
                    )
                ).order_by('all_first', 'name')
            else:
                country_list = models.ProductCountry.objects.filter(Q(name = 'All')|Q(countryCode = countryCode)).order_by('id')

        except:

            country_list = models.ProductCountry.objects.annotate(
                all_first=Case(   
                    When(name='All', then=Value(0)),
                    default=Value(1),
                    output_field=IntegerField(),
                )
            ).order_by('all_first', 'name')
        
        serialser = ProductCountrySerializer(country_list, many=True).data

        # print("country_list------>",country_list)
        # print("serialser------>",serialser)
                
        res = {
            'data':serialser
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)




@csrf_exempt
def product_country_update(request):
    if request.method == "POST":
        all_product = models.ProductDetail.objects.all()
        available_country = [1, 8]
        
        for product in all_product:
            print(product.id, 'product')
            product = models.ProductDetail.objects.get(id = product.id)


            product.available_country.set(available_country)

        res = {
            'data':"serialser"
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)



@csrf_exempt
def order_delete_admin(request):
    if request.method == "POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))
        order = python_data.get('id')
        
        product = models.ProductOrderDetail.objects.filter(order=order)
        if product.exists():
            product.delete()

        vendor = models.VendorOrderDetail.objects.filter(order=order)
        if vendor.exists():
            vendor.delete()

        vendor_tracking = models.VendorOrderTracking.objects.filter(order=order)
        if vendor_tracking.exists():
            vendor_tracking.delete()
        
        order_tracking = models.OrderTracking.objects.filter(order=order)
        if order_tracking.exists():
            order_tracking.delete()
        
        order_transaction = models.OrderTransaction.objects.filter(order=order)
        if order_transaction.exists():
            order_transaction.delete()
        
        promocode = models.PromocodeTracking.objects.filter(order=order)
        if promocode.exists():
            promocode.delete()
                
        commission = models.PromocodeCommissionDetail.objects.filter(order=order)
        if commission.exists():
            commission.delete()

        order = models.OrderDetail.objects.filter(id=order)
        if order.exists():
            order.delete()
        
        res = {
            'data':"serialser"
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)

@csrf_exempt
def product_tag_list(request):
    if request.method == "POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))
        category = python_data.get('category')

        all_product = models.ProductTag.objects.filter(category = category)
        serialiser = ProductTagSerializer(all_product, many=True).data
        
        res = {
            'data':serialiser
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)


@csrf_exempt
def product_tag_create(request):
    if request.method == "POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))
        tag = python_data.get('tag')
        category = python_data.get('category')
        if models.ProductTag.objects.filter(category = category, tag = tag).count() == 0:
            create = models.ProductTag.objects.create(
                category_id = category,
                tag = tag
            ).save()
            res = {
                'message':'Tag Added succesfully.'
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)
        else:
            res = {
                'message':'Something Went Wrong.'
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 406)

@csrf_exempt
def product_tag_delete(request):
    if request.method == "POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))
        id = python_data.get('id')

        print("models.ProductTag.objects.filter(id = id).count()------>",models.ProductTag.objects.filter(id = id).count())

        if models.ProductTag.objects.filter(id = id).count() == 1:
            tag = models.ProductTag.objects.get(id = id)
            tag.delete()
            res = {
                'message':'Tag Delete succesfully.'
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)
        else:
            res = {
                'message':'Something Went Wrong.'
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 406)


@csrf_exempt
def product_tag_update(request):
    if request.method == "POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))
        id = python_data.get('id')
        category = python_data.get('category')
        tag = python_data.get('tag')
        
        if models.ProductTag.objects.filter(category=category,tag =tag, id = id).count() == 1:
            res = {
                'message':'Tags update succesfully.'
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)
        elif models.ProductTag.objects.filter(category=category,tag =tag).count() != 0:
            res = {
                'message':'Tags already added.'
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 406)
        else:
            tag_count = models.ProductTag.objects.filter(category=category,tag =tag).count()
            if tag_count == 0:
                tag_update = models.ProductTag.objects.get(id = id)
                tag_update.category_id = category 
                tag_update.tag = tag
                tag_update.save()
                res = {
                    'message':'Tags update succesfully.'
                }
                return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)
            else:
                res = {
                    'message':'Something Went Wrong.'
                }
                return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 406)

# @csrf_exempt
# def all_product_tag_list(request):
#     json_data = request.body
#     stream = io.BytesIO(json_data)
#     python_data = JSONParser().parse(stream)
    
#     page_number = int(python_data.get('page_number', 1))
#     row_size = int(python_data.get('row_data', 10))
#     last_row = row_size * page_number
#     first_row = last_row - row_size

#     total_tags = models.ProductTag.objects.filter().count()
#     all_product = models.ProductTag.objects.filter()[first_row:last_row]
#     serializer = ProductTagSerializer(all_product, many=True).data

#     res = {
#         'data': serializer,
#         'total_tags':total_tags
#     }
#     json_data = JSONRenderer().render(res)
#     return HttpResponse(json_data, content_type= 'application/json', status=200)



@csrf_exempt
def all_product_tag_list(request):
    json_data = request.body
    stream = io.BytesIO(json_data)
    python_data = JSONParser().parse(stream)

    page_number = int(python_data.get('page_number', 1))
    row_size = int(python_data.get('row_data', 10))

    cache_key = f"product_tags_page_{page_number}_size_{row_size}"

    # Check cache first
    cached_data = cache.get(cache_key)
    if cached_data:
        return HttpResponse(
            JSONRenderer().render(cached_data),
            content_type='application/json',
            status=200
        )

    last_row = row_size * page_number
    first_row = last_row - row_size

    total_tags = models.ProductTag.objects.count()

    all_product = models.ProductTag.objects.all().order_by('-id')[first_row:last_row]

    serializer = ProductTagSerializer(all_product, many=True).data

    res = {
        'data': serializer,
        'total_tags': total_tags
    }

    # Save response in Redis for 5 minutes
    cache.set(cache_key, res, timeout=300)

    json_data = JSONRenderer().render(res)

    return HttpResponse(json_data, content_type='application/json', status=200)


@csrf_exempt
def vendor_revenue(request):
    if request.method == "POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))
        vendor = python_data.get('vendor')

        today = datetime.today()
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)

        start_of_month = today.replace(day=1)

        if today.month == 12:
            next_month = today.replace(year=today.year + 1, month=1, day=1)
        else:
            next_month = today.replace(month=today.month + 1, day=1)

        end_of_month = next_month - timedelta(days=1)
        
        # today_data = list(models.VendorPaymentTracker.objects.filter(vendor = vendor, created_at__date = today.date()).values_list('amount', flat=True))
        # today_revenue = int(sum(today_data))

        active_products = models.ProductDetail.objects.filter(vendor = vendor, status = "Active").count()

        total_orders_count = models.VendorOrderDetail.objects.filter(vendor = vendor).count()
        total_order_data = models.VendorOrderDetail.objects.filter(vendor = vendor)
        total_variants = models.VendorProductPrice.objects.filter(vendor = vendor).count()

        total_revenue = 0
        for order in total_order_data:
            get_vendor_variant = models.VendorProductPrice.objects.filter(variant = order.variant.variant.id, vendor = vendor).first()
            total_revenue += int(int(get_vendor_variant.price) * int(order.variant.quantity))
        
        amount_data = list(models.VendorPaymentTracker.objects.filter(vendor = vendor, payment_type="Pay").values_list('amount', flat=True))
        # total_order_data = models.VendorPaymentTracker.objects.filter(vendor = vendor, payment_type="Pay").count()
        # total_revenue = int(sum(amount_data))

        average_order_value = round(total_revenue / total_orders_count) if total_orders_count > 0 else 0

        pending_order_count =  models.VendorOrderDetail.objects.filter(vendor = vendor, variant__vendor_status = "pending").count()

        pending_products = models.ProductDetail.objects.filter(vendor = vendor, product_verification = "Pending").count()

        res = {
            'active_products' : active_products,
            'total_orders_count' : total_orders_count,
            'total_variants' : total_variants,

            # 'total_order_data' : total_order_data,
            'total_revenue':total_revenue,
            'average_order_value':average_order_value,

            'pending_order_count':pending_order_count,
            'pending_products':pending_products,

        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)


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


@csrf_exempt
def vendor_total_income(request):
    if request.method == "POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))
        vendor = python_data.get('vendor')
        total_income = models.VendorPaymentTracker.objects.filter(vendor = vendor, payment_type = 'Pay').aggregate(total_income = Sum('amount'))['total_income'] or 0
        res = {
            'total_income': total_income
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)

@csrf_exempt
def vendor_total_payout(request):
    if request.method == "POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))
        vendor = python_data.get('vendor')
        total_payout = models.VendorPaymentTracker.objects.filter(vendor = vendor, payment_type = 'Paid').aggregate(total_payout = Sum('amount'))['total_payout'] or 0
        res = {
            'total_payout': total_payout
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)
    
@csrf_exempt
def vendor_pending_payment(request):
    if request.method == "POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))
        vendor = python_data.get('vendor')
        pending_payment = models.VendorPaymentTracker.objects.filter(vendor = vendor).order_by('-id').values_list('remaining_amount', flat=True).first() or 0
        res = {
            'pending_payment': pending_payment
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)
    


from django.http import JsonResponse
from django.db import connection, transaction

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
def all_delivery_days_list(request):
    if request.method == "POST":
        delivery_data = models.DeliveryDayDetail.objects.first()
        serialser = DeliveryDayDetailSerializer(delivery_data).data
        res = {
            'data':serialser
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)


@csrf_exempt
def delivery_days_update(request):
    if request.method == "POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))
        id = python_data.get('id')
        update_data = models.DeliveryDayDetail.objects.get(id = id)
        update_data.express_delivery = python_data.get('express_delivery', update_data.express_delivery)
        update_data.air_delivery = python_data.get('air_delivery', update_data.air_delivery)
        update_data.ship_delivery = python_data.get('ship_delivery', update_data.ship_delivery)
        update_data.save()

        res = {
            'message':'Delivery days updated Succesfully.'
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




# @csrf_exempt
# def price_exchange(request):
#     if request.method == "POST":
#         python_data = JSONParser().parse(io.BytesIO(request.body))
#         amount = python_data.get('amount')
#         from_currency = python_data.get('from_currency')
#         to_currency = python_data.get('to_currency')

#         # url = f"https://api.exchangerate-api.com/v4/latest/{from_currency}"
#         url = f"https://api.fxratesapi.com/latest?base={from_currency}"


#         response = requests.get(url)
#         data = response.json()

#         rate = data["rates"][to_currency]
#         converted = amount * rate

#         print(f"{amount} {from_currency} = {converted:.2f} {to_currency}")


#         res = {
#             'data':f"{amount} {from_currency} = {converted:.2f} {to_currency}"
#         }
#         return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)

@csrf_exempt
def important_note_update(request):
    if request.method == "POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))
        id = python_data.get('id')
        note_update = models.ImportantNote.objects.get(id = id)
        note_update.note = python_data.get('note', note_update.note)
        note_update.note_french = python_data.get('note_french', note_update.note_french)
        note_update.status = python_data.get('status', note_update.status)
        note_update.save()
       
        res = {
            'message':'Note update.'
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)
 
@csrf_exempt
def important_note_list(request):
    if request.method == "POST":
        important_note = models.ImportantNote.objects.all().first()
        note_serialser = ImportantNoteSerializer(important_note).data
        res = {
            'data':note_serialser
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)
 

@csrf_exempt
def product_inquiry_form(request):
    if request.method == "POST":        
        product_data = json.loads(request.POST.get("product_data", "[]"))
        customer_id = request.POST.get("customer_id")


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
def vendor_list_with_delay_note(request):
    if request.method == "POST":
        vendor_list = models.VendorDetail.objects.all().order_by('vendor_name')
        vendor_list_serializer = VendorDetailExistsInDelayNote(vendor_list, many=True).data

        res={
            'data':vendor_list_serializer
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
def create_wave_checkout(request):
    if request.method == "POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))
        print(python_data, 'python_data')
        amount = python_data.get('amount')
        # amount = 10
        currency = python_data.get('currency', 'XOF')
        success_url = "https://diaba.store/payment-success/"
        error_url = "https://diaba.store/payment-failed/"


        url = "https://api.wave.com/v1/checkout/sessions"

        payload = {
            "amount": amount,
            "currency": currency,
            "error_url": error_url,
            "success_url": success_url
        }

        timestamp = str(int(time.time()))

        body_str = json.dumps(payload, separators=(',', ':'))  # IMPORTANT
        message = f"{timestamp}{body_str}"

        signature = hmac.new(
            settings.WAVE_SIGNING_SECRET.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()

        headers = {
            "Authorization": f"Bearer {settings.WAVE_API_KEY}",
            "Wave-Signature": f"t={timestamp},v1={signature}",
            "Content-Type": "application/json"
        }

        response = requests.post(url, data=body_str, headers=headers)

        res = {
            'data': response.json()
        }
        return HttpResponse(JSONRenderer().render(res),content_type='application/json',status=response.status_code)



@csrf_exempt
def get_wave_checkout_session(request):
    if request.method == "POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))
        id = python_data.get('id')
        url = f"https://api.wave.com/v1/checkout/sessions/{id}"

        timestamp = str(int(time.time()))
        body_str = ""   # VERY IMPORTANT
        message = f"{timestamp}{body_str}"

        signature = hmac.new(
            settings.WAVE_SIGNING_SECRET.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()

        headers = {
            "Authorization": f"Bearer {settings.WAVE_API_KEY}",
            "Wave-Signature": f"t={timestamp},v1={signature}",
        }

        try:
            response = requests.get(url, headers=headers)
            res = {
                "data": response.json()
            }
            return HttpResponse(JSONRenderer().render(res),content_type='application/json',status=response.status_code)

        except Exception as e:
            return HttpResponse(JSONRenderer().render({"error": str(e)}),content_type='application/json',status=500)

# @csrf_exempt
# def bulk_upload(request):
#     if (request.method == "POST"):
#         python_data={}
#         for i,j in request.FILES.items():
#             python_data.update({i:j})
        
#         for i,j in request.POST.items():
#             python_data.update({i:j})
        
#         excel_file = python_data.get('excel_file')
#         flag = python_data.get('flag')

        
#         letters = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z',\
#                 'AA','AB','AC','AD','AE','AF','AG','AH','AI','AJ','AK','AL','AM','AN','AO','AP','AQ','AR','AS','AT','AU','AV','AW','AX','AY','AZ', \
#                 'BA','BB','BC','BD','BE','BF','BG','BH','BI','BJ','BK','BL','BM','BN','BO','BP','BQ','BR','BS','BT','BU','BV','BW','BX','BY','BZ']
            
#         # all_subcategory_list = models.SubCategoryDetail.objects.all()
#         # for get_subcategory in all_subcategory_list:
#         #     get_subcategory.subcategory = get_subcategory.subcategory.strip()
#         #     get_subcategory.subcategory_french = get_subcategory.subcategory_french.strip()
#         #     get_subcategory.save()

#         try:
#             fs = FileSystemStorage()
#             fs.delete('product_import.xlsx')
#         except:
#             pass
            
#         fs = FileSystemStorage()
#         filename = fs.save('product_import.xlsx', excel_file)
#         file_url = fs.url(filename)
#         file_path = fs.path(filename)  
#         workbook = load_workbook(file_path)
#         sheet = workbook.active
#         invalid_count = 0

#         new_filename = 'product_import_data.xlsx'
#         new_file_url = fs.url(new_filename)
#         new_file_path = fs.path(new_filename)  

#         wb = load_workbook(new_file_path)
#         ws = wb.active
#         ws.delete_rows(2, ws.max_row) 
#         wb.save(new_file_path)
        
#         new_workbook = load_workbook(new_file_path)
#         new_sheet = new_workbook.active

#         for row_index, row in enumerate(sheet.iter_rows(values_only=True), start=1):
#             if row_index == 1:
#                 continue
            
#             if row[0] == None:
#                 break
            
#             print(row[0], 'row')
                        
#             category = 	(row[0]).strip()
#             subcategory = (row[1]).strip()
#             unit_of_measure = (row[2]).lower()
#             shipping_via = row[3]
#             country_of_origin = (row[4]).strip()
#             available_country = [v.strip() for v in row[5].split(",")]
#             tags = [t.strip() for t in row[6].split(",")]
#             product_name = 	row[7]
#             description = 	row[8]
#             price = row[9]            
#             final_price = row[10]
#             min_order_quantity = row[11]
#             length = row[12]
#             width = row[13]
#             height = row[14]
#             weight = row[15]
#             vendor = row[16]
#             reuser =row[17]
#             refpro =row[18]
#             product_type =row[19]
#             product_packaging =row[20]
#             product_packaging_value =row[21]

#             print(tags, 'tags')
            

#             get_new_cell = str(letters[0]) + str(row_index)
#             cell_new_bg = new_sheet[get_new_cell]
#             new_sheet[get_new_cell].value = row[0]  
#             new_workbook.save(new_file_path)
    
#             get_new_cell = str(letters[1]) + str(row_index)
#             cell_new_bg = new_sheet[get_new_cell]
#             new_sheet[get_new_cell].value = row[1]  
#             new_workbook.save(new_file_path)
            
#             get_new_cell = str(letters[2]) + str(row_index)
#             cell_new_bg = new_sheet[get_new_cell]
#             new_sheet[get_new_cell].value = row[2]
#             new_workbook.save(new_file_path)
            
#             get_new_cell = str(letters[3]) + str(row_index)
#             cell_new_bg = new_sheet[get_new_cell]
#             new_sheet[get_new_cell].value = row[3]  
#             new_workbook.save(new_file_path)
            
#             get_new_cell = str(letters[4]) + str(row_index)
#             cell_new_bg = new_sheet[get_new_cell]
#             new_sheet[get_new_cell].value = row[4]  
#             new_workbook.save(new_file_path)
            
#             get_new_cell = str(letters[5]) + str(row_index)
#             cell_new_bg = new_sheet[get_new_cell]
#             new_sheet[get_new_cell].value = row[5]  
#             new_workbook.save(new_file_path)
            
#             get_new_cell = str(letters[6]) + str(row_index)
#             cell_new_bg = new_sheet[get_new_cell]
#             new_sheet[get_new_cell].value = row[6]  
#             new_workbook.save(new_file_path)
            
#             get_new_cell = str(letters[7]) + str(row_index)
#             cell_new_bg = new_sheet[get_new_cell]
#             new_sheet[get_new_cell].value = row[7]  
#             new_workbook.save(new_file_path)
            
#             get_new_cell = str(letters[8]) + str(row_index)
#             cell_new_bg = new_sheet[get_new_cell]
#             new_sheet[get_new_cell].value = row[8]  
#             new_workbook.save(new_file_path)

#             get_new_cell = str(letters[9]) + str(row_index)
#             cell_new_bg = new_sheet[get_new_cell]
#             new_sheet[get_new_cell].value = row[9]  
#             new_workbook.save(new_file_path)


#             get_new_cell = str(letters[10]) + str(row_index)
#             cell_new_bg = new_sheet[get_new_cell]
#             new_sheet[get_new_cell].value = row[10]  
#             new_workbook.save(new_file_path)
            
#             get_new_cell = str(letters[11]) + str(row_index)
#             cell_new_bg = new_sheet[get_new_cell]
#             new_sheet[get_new_cell].value = row[11]  
#             new_workbook.save(new_file_path)
            
#             get_new_cell = str(letters[12]) + str(row_index)
#             cell_new_bg = new_sheet[get_new_cell]
#             new_sheet[get_new_cell].value = row[12]  
#             new_workbook.save(new_file_path)
            
#             get_new_cell = str(letters[13]) + str(row_index)
#             cell_new_bg = new_sheet[get_new_cell]
#             new_sheet[get_new_cell].value = row[13]  
#             new_workbook.save(new_file_path)
            
#             get_new_cell = str(letters[14]) + str(row_index)
#             cell_new_bg = new_sheet[get_new_cell]
#             new_sheet[get_new_cell].value = row[14]  
#             new_workbook.save(new_file_path)
            
#             get_new_cell = str(letters[15]) + str(row_index)
#             cell_new_bg = new_sheet[get_new_cell]
#             new_sheet[get_new_cell].value = row[15]  
#             new_workbook.save(new_file_path)
            
#             get_new_cell = str(letters[16]) + str(row_index)
#             cell_new_bg = new_sheet[get_new_cell]
#             new_sheet[get_new_cell].value = row[16]  
#             new_workbook.save(new_file_path)
            
#             get_new_cell = str(letters[17]) + str(row_index)
#             cell_new_bg = new_sheet[get_new_cell]
#             new_sheet[get_new_cell].value = row[17]  
#             new_workbook.save(new_file_path)


#             get_new_cell = str(letters[18]) + str(row_index)
#             cell_new_bg = new_sheet[get_new_cell]
#             new_sheet[get_new_cell].value = row[18]  
#             new_workbook.save(new_file_path)

            
#             get_new_cell = str(letters[19]) + str(row_index)
#             cell_new_bg = new_sheet[get_new_cell]
#             new_sheet[get_new_cell].value = row[19]  
#             new_workbook.save(new_file_path)

#             get_new_cell = str(letters[20]) + str(row_index)
#             cell_new_bg = new_sheet[get_new_cell]
#             new_sheet[get_new_cell].value = row[20]  
#             new_workbook.save(new_file_path)

#             get_new_cell = str(letters[21]) + str(row_index)
#             cell_new_bg = new_sheet[get_new_cell]
#             new_sheet[get_new_cell].value = row[21]  
#             new_workbook.save(new_file_path)


#             get_new_cell = str(letters[23]) + str(1)
#             cell_new_bg = new_sheet[get_new_cell]
#             new_sheet[get_new_cell].value = 'Status' 
#             new_workbook.save(new_file_path)
            
#             get_new_cell = str(letters[24]) + str(1)
#             cell_new_bg = new_sheet[get_new_cell]
#             new_sheet[get_new_cell].value = 'Reasons' 
#             new_workbook.save(new_file_path)



#             category_reason = None
#             print("category---->",category)
#             print("subcategory---->",subcategory)
#             check_category = models.CategoryDetail.objects.filter(Q(category__iexact = category)| Q(category_french__iexact = category)).count()
#             # print(check_category, 'check_category')
#             if check_category == 0:
#                 get_cell = str(letters[0]) + str(row_index)
#                 cell_bg = new_sheet[get_cell]
#                 cell_bg.fill = PatternFill(start_color="FFFF00", end_color="FFFF00",fill_type = "solid")
#                 new_workbook.save(new_file_path)
#                 category_reason = 'Enter Valid Category'
#                 invalid_count += 1
#                 category_id = None
#             else:
#                 category_id = models.CategoryDetail.objects.get(Q(category__iexact = category)| Q(category_french__iexact = category)).id
                
#             print(category_id, 'category_id')
            
#             sub_category_reason = None
#             check_subcategory = models.SubCategoryDetail.objects.filter(Q(subcategory__iexact =subcategory) | Q(subcategory_french__iexact = subcategory)).count()
#             # print(check_subcategory, 'check_subcategory')
#             if check_subcategory == 1:
#                 check_category_subcategory = models.SubCategoryDetail.objects.annotate(
#                     category_clean=Trim('category__category'),
#                     category_fr_clean=Trim('category__category_french'),
#                     subcategory_clean=Trim('subcategory'),
#                     subcategory_fr_clean=Trim('subcategory_french'),
#                 ).filter(
#                     (Q(category_clean__iexact=category) | Q(category_fr_clean__iexact=category)) &
#                     (Q(subcategory_clean__iexact=subcategory) | Q(subcategory_fr_clean__iexact=subcategory))
#                 ).count()                
                
#                 if check_category_subcategory == 0:
#                     get_cell = str(letters[1]) + str(row_index)
#                     cell_bg = new_sheet[get_cell]
#                     cell_bg.fill = PatternFill(start_color="FFFF00", end_color="FFFF00",fill_type = "solid")
#                     new_workbook.save(new_file_path)
#                     sub_category_reason = 'This Subcategory not associate with this category'
#                     invalid_count += 1
#             else:
#                 get_cell = str(letters[1]) + str(row_index)
#                 cell_bg = new_sheet[get_cell]
#                 cell_bg.fill = PatternFill(start_color="FFFF00", end_color="FFFF00",fill_type = "solid")
#                 new_workbook.save(new_file_path)
#                 sub_category_reason = 'Enter Valid Subcategory'
#                 invalid_count += 1
            
                        
#             unit_of_measure_reason = None
#             if unit_of_measure not in ['kg', 'pcs', 'liters', 'meters', 'tons', 'carton', 'douzaine', "1/2douzaine"]:
#                 get_cell = str(letters[2]) + str(row_index)
#                 cell_bg = new_sheet[get_cell]
#                 cell_bg.fill = PatternFill(start_color="FFFF00", end_color="FFFF00",fill_type = "solid")
#                 new_workbook.save(new_file_path)
#                 unit_of_measure_reason = 'Please select one value from the following options: kg, pcs, liters, meters, tons, carton, douzaine, or 1/2 douzaine.'
#                 invalid_count += 1
            


#             shipping_via_reason = None
#             if shipping_via.lower() not in ['By Air', 'by air', 'By Ship', 'by ship', 'Both', 'both']:
#                 get_cell = str(letters[3]) + str(row_index)
#                 cell_bg = new_sheet[get_cell]
#                 cell_bg.fill = PatternFill(start_color="FFFF00", end_color="FFFF00",fill_type = "solid")
#                 new_workbook.save(new_file_path)
#                 shipping_via_reason = 'Please select one value from the following options: By Air, By Ship, or Both.'
#                 invalid_count += 1


            

#             country_of_origin_reason = None
#             check_country_of_origin = models.Country.objects.filter(country_name__iexact = country_of_origin).count()
#             # print(check_category, 'check_category')
#             if check_country_of_origin == 0:
#                 get_cell = str(letters[4]) + str(row_index)
#                 cell_bg = new_sheet[get_cell]
#                 cell_bg.fill = PatternFill(start_color="FFFF00", end_color="FFFF00",fill_type = "solid")
#                 new_workbook.save(new_file_path)
#                 country_of_origin_reason = 'Enter Valid country of origin'
#                 invalid_count += 1


#             available_country_reason = None
#             list_not_list_country = []

#             available_country = [c.strip() for c in available_country if c.strip()]

#             has_all = any(c.lower() == 'all' for c in available_country)

#             if has_all:
#                 get_new_cell = str(letters[5]) + str(row_index)
#                 cell_new_bg = new_sheet[get_new_cell]
#                 cell_new_bg.value = 'All'
#             else:
#                 for country in available_country:
#                     check_country = models.ProductCountry.objects.filter(Q(name__iexact=country) | Q(name_french__iexact=country)).exists()
#                     if not check_country:
#                         print(country, 'country')
#                         list_not_list_country.append(country)

#                 if list_not_list_country:
#                     get_cell = str(letters[5]) + str(row_index)
#                     cell_bg = new_sheet[get_cell]
#                     cell_bg.fill = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")
#                     available_country_reason = f'{list_not_list_country} country not mention in system'
#                     invalid_count += 1

#             for tag in tags:
#                 check_tag = models.ProductTag.objects.filter(category_id =category_id, tag = tag ).exists()
#                 if check_tag == 0:
#                     check_tag = models.ProductTag.objects.create(
#                         category_id =category_id, 
#                         tag = tag 
#                     ).save()

#             price_reason = None
#             price_str = str(price).strip()

#             get_cell = str(letters[9]) + str(row_index)
#             cell_bg = new_sheet[get_cell]

#             if price_str.startswith("="):
#                 cell_bg.fill = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")
#                 price_reason = 'Formula not allowed. Enter numeric value'
#                 invalid_count += 1

#             else:
#                 try:
#                     # Remove commas and convert
#                     price_value = float(price_str.replace(",", ""))

#                     if price_value < 0:
#                         cell_bg.fill = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")
#                         price_reason = 'Price cannot be negative'
#                         invalid_count += 1

#                     else:
#                         # Round if needed
#                         price_value = round(price_value)

#                         new_sheet[get_cell].value = price_value
#                         new_workbook.save(new_file_path)

#                 except ValueError:
#                     cell_bg.fill = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")
#                     price_reason = 'Enter numeric value only'
#                     invalid_count += 1


#             final_price_reason = None
#             final_price_str = str(final_price).strip()

#             get_cell = str(letters[10]) + str(row_index)
#             cell_bg = new_sheet[get_cell]

#             if final_price_str.startswith("="):
#                 cell_bg.fill = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")
#                 final_price_reason = 'Formula not allowed. Enter numeric value'
#                 invalid_count += 1

#             else:
#                 try:
#                     # Convert safely
#                     final_price_value = float(final_price_str.replace(",", ""))

#                     if final_price_value < 0:
#                         cell_bg.fill = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")
#                         final_price_reason = 'Price cannot be negative'
#                         invalid_count += 1

#                     else:
#                         final_price_value = round(final_price_value)

#                         new_sheet[get_cell].value = final_price_value
#                         new_workbook.save(new_file_path)

#                 except ValueError:
#                     cell_bg.fill = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")
#                     final_price_reason = 'Enter numeric value only'
#                     invalid_count += 1

#             # min_order_quantity_reason = None
#             # if int(min_order_quantity) < 1:
#             #     get_cell = str(letters[10]) + str(row_index)
#             #     cell_bg = new_sheet[get_cell]
#             #     cell_bg.fill = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")
#             #     min_order_quantity_reason = 'Min order qunatity not less than 0'
#             #     invalid_count += 1

#             min_order_quantity_reason = None
#             min_order_quantity_str = str(min_order_quantity).strip()

#             get_cell = str(letters[11]) + str(row_index)
#             cell_bg = new_sheet[get_cell]

#             if min_order_quantity_str.startswith("="):
#                 cell_bg.fill = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")
#                 min_order_quantity_reason = 'Formula not allowed in Min order quantity. Enter numeric value'
#                 invalid_count += 1

#             else:
#                 try:
#                     # Convert safely (also handles commas)
#                     min_qty_value = int(float(min_order_quantity_str.replace(",", "")))

#                     if min_qty_value < 1:
#                         cell_bg.fill = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")
#                         min_order_quantity_reason = 'Min order quantity must be at least 1'
#                         invalid_count += 1

#                     else:
#                         new_sheet[get_cell].value = min_qty_value
#                         new_workbook.save(new_file_path)

#                 except ValueError:
#                     cell_bg.fill = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")
#                     min_order_quantity_reason = 'Enter numeric value only'
#                     invalid_count += 1

             
#             vendor_reason = None
#             check_vendor = models.VendorDetail.objects.filter(email__iexact = vendor).count()
#             # print(check_category, 'check_category')
#             if check_vendor == 0:
#                 get_cell = str(letters[16]) + str(row_index)
#                 cell_bg = new_sheet[get_cell]
#                 cell_bg.fill = PatternFill(start_color="FFFF00", end_color="FFFF00",fill_type = "solid")
#                 new_workbook.save(new_file_path)
#                 vendor_reason = 'Enter valid seller email'
#                 invalid_count += 1

#             length_reason = None
#             try:
#                 length_value = float(length)

#                 if length_value < 0:
#                     length_reason = 'Value cannot be negative'
#                 elif length_value == 0:
#                     length_reason = 'Value must be greater than 0'

#             except ValueError:
#                 length_reason = 'Enter numeric values only'

#             if length_reason:
#                 get_cell = str(letters[12]) + str(row_index)
#                 cell_bg = new_sheet[get_cell]
#                 cell_bg.fill = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")
#                 new_workbook.save(new_file_path)
#                 invalid_count += 1

            
#             width_reason = None
#             try:
#                 width_value = float(width)

#                 if width_value < 0:
#                     width_reason = 'Value cannot be negative'
#                 elif width_value == 0:
#                     width_reason = 'Value must be greater than 0'

#             except ValueError:
#                 width_reason = 'Enter numeric values only'

#             if width_reason:
#                 get_cell = str(letters[13]) + str(row_index)
#                 cell_bg = new_sheet[get_cell]
#                 cell_bg.fill = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")
#                 new_workbook.save(new_file_path)
#                 invalid_count += 1
            

#             height_reason = None
#             try:
#                 height_value = float(height)

#                 if height_value < 0:
#                     height_reason = 'Value cannot be negative'
#                 elif height_value == 0:
#                     height_reason = 'Value must be greater than 0'

#             except ValueError:
#                 height_reason = 'Enter numeric values only'

#             if height_reason:
#                 get_cell = str(letters[14]) + str(row_index)
#                 cell_bg = new_sheet[get_cell]
#                 cell_bg.fill = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")
#                 new_workbook.save(new_file_path)
#                 invalid_count += 1

#             weight_reason = None
#             if shipping_via.lower() == "by ship":
#                 try:
#                     weight_value = float(weight)

#                     if weight_value < 0:
#                         weight_reason = 'Value cannot be negative'
#                     elif weight_value == 0:
#                         weight_reason = 'Value must be greater than 0'

#                 except ValueError:
#                     weight_reason = 'Enter numeric values only'

#             if weight_reason:
#                 get_cell = str(letters[15]) + str(row_index)
#                 cell_bg = new_sheet[get_cell]
#                 cell_bg.fill = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")
#                 new_workbook.save(new_file_path)
#                 invalid_count += 1

#             reuser_reason = None
#             if reuser is None or str(reuser).strip() == "":
#                 reuser_reason = 'This field cannot be empty'

#             if reuser_reason:
#                 get_cell = str(letters[17]) + str(row_index)
#                 cell_bg = new_sheet[get_cell]
#                 cell_bg.fill = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")
#                 new_workbook.save(new_file_path)
#                 invalid_count += 1


#             # Refpro validation
#             refpro_reason = None
#             if refpro is None or str(refpro).strip() == "":
#                 refpro_reason = 'This field cannot be empty'

#             if refpro_reason:
#                 get_cell = str(letters[18]) + str(row_index)
#                 cell_bg = new_sheet[get_cell]
#                 cell_bg.fill = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")
#                 new_workbook.save(new_file_path)
#                 invalid_count += 1

#             product_type_reason = None
#             check_product_type = models.ProductType.objects.filter(product_type = product_type).count()
#             if check_product_type == 0:
#                 get_cell = str(letters[19]) + str(row_index)
#                 cell_bg = new_sheet[get_cell]
#                 cell_bg.fill = PatternFill(start_color="FFFF00", end_color="FFFF00",fill_type = "solid")
#                 new_workbook.save(new_file_path)
#                 category_reason = 'Enter Valid Product Type'
#                 invalid_count += 1

#             product_packaging_reason = None
#             check_product_packaging = models.ProductPackagingBy.objects.filter(product_packaging = product_packaging).count()
#             if check_product_packaging == 0:
#                 get_cell = str(letters[20]) + str(row_index)
#                 cell_bg = new_sheet[get_cell]
#                 cell_bg.fill = PatternFill(start_color="FFFF00", end_color="FFFF00",fill_type = "solid")
#                 new_workbook.save(new_file_path)
#                 category_reason = 'Enter Valid Product Packaging By'
#                 invalid_count += 1

#             product_packaging_value_reason = None

#             if isinstance(product_packaging_value, float):
#                 product_packaging_value_reason = 'Enter integer values only'

#             elif not str(product_packaging_value).isdigit():
#                 product_packaging_value_reason = 'Enter integer values only'

#             else:
#                 product_packaging_value_value = int(product_packaging_value)

#                 if product_packaging_value_value < 0:
#                     product_packaging_value_reason = 'Value cannot be negative'
#                 elif product_packaging_value_value == 0:
#                     product_packaging_value_reason = 'Value must be greater than 0'


#             if product_packaging_value_reason:
#                 get_cell = str(letters[21]) + str(row_index)
#                 cell_bg = new_sheet[get_cell]
#                 cell_bg.fill = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")
#                 new_workbook.save(new_file_path)
#                 invalid_count += 1
                        
#             list_reason = []
#             if category_reason != None:
#                 list_reason.append(category_reason)

#             if sub_category_reason != None:
#                 list_reason.append(sub_category_reason)            
            
#             if unit_of_measure_reason != None:
#                 list_reason.append(unit_of_measure_reason)            
            
#             if shipping_via_reason != None:
#                 list_reason.append(shipping_via_reason)
            
#             if country_of_origin_reason != None:
#                 list_reason.append(country_of_origin_reason)
            
#             if available_country_reason != None:
#                 list_reason.append(available_country_reason)

#             if price_reason != None:
#                 list_reason.append(price_reason)
    
#             if final_price_reason != None:
#                 list_reason.append(final_price_reason)
            
#             if min_order_quantity_reason != None:
#                 list_reason.append(min_order_quantity_reason)
            
#             if vendor_reason != None:
#                 list_reason.append(vendor_reason)
            
#             if length_reason != None:
#                 list_reason.append(length_reason)
    
#             if width_reason != None:
#                 list_reason.append(width_reason)
            
#             if height_reason != None:
#                 list_reason.append(height_reason)
            
#             if weight_reason != None:
#                 list_reason.append(weight_reason)    
            
#             if product_type_reason != None:
#                 list_reason.append(product_type_reason)    

#             if product_packaging_reason != None:
#                 list_reason.append(product_packaging_reason)    
            
#             if product_packaging_value_reason != None:
#                 list_reason.append(product_packaging_value_reason)    
    
#             if reuser_reason != None:
#                 list_reason.append(reuser_reason)    
    
#             if refpro_reason != None:
#                 list_reason.append(refpro_reason)    
    


#             # final_reason = ', '.join(map(str, list_reason)) 

#             final_reason = ', '.join(f"'{item}'" for item in list_reason)


#             # print(final_reason, 'fdinal reason check ')
#             if final_reason == '':
#                 row_status = 'Valid'
#                 start_color="3d7d13" 
#                 end_color="3d7d13"
#             else:
#                 row_status = 'Invalid'
#                 start_color="e39830"
#                 end_color="e39830"


#             get_new_cell = str(letters[23]) + str(row_index)
#             cell_new_bg = new_sheet[get_new_cell]
#             new_sheet[get_new_cell].value = str(row_status)
#             cell_new_bg.fill = PatternFill(start_color=start_color, end_color=end_color,fill_type = "solid")
#             new_workbook.save(new_file_path)


#             get_new_cell = str(letters[24]) + str(row_index)
#             cell_new_bg = new_sheet[get_new_cell]
#             new_sheet[get_new_cell].value = str(final_reason)  
#             new_workbook.save(new_file_path)

#         if invalid_count == 0:
#             flag = 'Valid'
#         else:
#             flag = 'Invalid'
#         # link = SITE_MEDIA_BASE_URL + new_filename
#         link = SITE_MEDIA_BASE_URL + new_filename
#         response_data = {
#             "statuscode":200,
#             "status":"Success",
#             'message':'File Upload successulfully.',
#             "invalid_count":invalid_count,
#             "flag":flag,
#             "link":link
#         }
#         json_data = JSONRenderer().render(response_data)
#         return HttpResponse(json_data, content_type= 'application/json')



# @csrf_exempt
# def bulk_upload_submit(request):
#     if (request.method == "POST"):

#         python_data = JSONParser().parse(io.BytesIO(request.body))

#         # flag = python_data.get('flag')
#         link = python_data.get('link')

#         now = datetime.now()
#         current_time = now.strftime("%Y-%m-%d, %H:%M:%S")
        
#         letters = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z',\
#                 'AA','AB','AC','AD','AE','AF','AG','AH','AI','AJ','AK','AL','AM','AN','AO','AP','AQ','AR','AS','AT','AU','AV','AW','AX','AY','AZ']
            
        
        
#         fs = FileSystemStorage()
#         file_path = fs.path(link)  
#         workbook = load_workbook(file_path)
#         sheet = workbook.active
#         invalid_count = 0
#         for row_index, row in enumerate(sheet.iter_rows(values_only=True), start=1):
#             if row_index == 1:
#                 continue

                                    
#             category = 	(row[0]).strip()
#             subcategory = (row[1]).strip()
#             unit_of_measure = (row[2]).lower()
#             shipping_via = row[3]
#             country_of_origin = (row[4]).strip()
#             available_country = [v.strip() for v in row[5].split(",")]
#             tags = [t.strip() for t in row[6].split(",")]
#             product_name = 	row[7]
#             description = row[8]
#             price = row[9]            
#             final_price = row[10]
#             min_order_quantity = row[11]
#             length = row[12]
#             width = row[13]
#             height = row[14]
#             weight = row[15]
#             vendor = row[16]
#             reuser =row[17]
#             refpro =row[18]
#             product_type =row[19]
#             product_packaging =row[20]
#             product_packaging_value =row[21]


#             digits = '123456789' 
#             random_number = ""
#             for i in range(3) :
#                 random_number += digits[math.floor(random.random() * 9)]



#             category_name = models.CategoryDetail.objects.filter(Q(category__iexact = category)| Q(category_french__iexact = category)).values_list('category', flat=True)[0][:3].upper()
#             subcategory_name = models.SubCategoryDetail.objects.filter(Q(subcategory__iexact = subcategory)| Q(subcategory_french__iexact = subcategory)).values_list('subcategory', flat=True)[0][:3].upper()
#             product_name_data = (product_name)[:3].upper()
#             product_code =  category_name+'_'+subcategory_name+ '_'+ product_name_data + '_' + random_number

#             category_id = models.CategoryDetail.objects.get(Q(category__iexact = category)| Q(category_french__iexact = category)).id
#             subcategory_id = models.SubCategoryDetail.objects.get(Q(subcategory__iexact = subcategory)| Q(subcategory_french__iexact = subcategory)).id
#             product_type_id = models.ProductType.objects.get(product_type__iexact = product_type).id
#             product_packaging_id = models.ProductPackagingBy.objects.get(product_packaging__iexact = product_packaging).id
            
#             country_of_origin_id = models.Country.objects.get(country_name = country_of_origin).id
#             vendor_id = models.VendorDetail.objects.get(email = vendor).id

#             list_available_country = []
#             for available in available_country:
#                 available_id = models.ProductCountry.objects.get(Q(name__iexact=available) | Q(name_french__iexact=available)).id
#                 list_available_country.append(available_id)

#             list_tags = []
#             for tag in tags:
#                 tag_id = models.ProductTag.objects.get(category =category_id,  tag__exact=tag).id
#                 list_tags.append(tag_id)
            
#             shipping_via = ' '.join(word.capitalize() for word in shipping_via.split())
#             print(shipping_via, 'shipping_via')
#             product = models.ProductDetail.objects.create(
#                 product_name = product_name,
#                 product_name_french = product_name,
#                 product_code = product_code,
#                 vendor_id = vendor_id,
#                 category_id = category_id,
#                 subcategory_id = subcategory_id,
#                 description = description,
#                 description_french = description,
#                 unit_of_measure = unit_of_measure,
#                 length = length,
#                 height = height,
#                 width = width,
#                 weight = weight,
#                 country_of_origin_id = country_of_origin_id,
#                 carton_length = length,
#                 carton_width = width,
#                 carton_height = height,
#                 carton_weight = weight,
#                 product_verification = 'Approved',
#                 min_order_quantity = min_order_quantity,
#                 price = price,
#                 discount = 0,
#                 final_price = final_price,
#                 status = 'bulk',
#                 # status = 'Active',
#                 product_added_from = 'bulk',
#                 refpro = refpro,
#                 reuser = reuser,
#                 product_type_id = product_type_id,
#                 product_packaging_id = product_packaging_id,
#                 product_packaging_value = product_packaging_value,
#                 shipping_via = shipping_via,
#             )
#             product.save()
#             try: 
#                 product.available_country.set(list_available_country)
#             except:
#                 product.available_country.clear()

#             try: 
#                 product.tag.set(list_tags)
#             except:
#                 product.tag.clear()

#             product_id = product.id 
#             create_model = models.ProductModel.objects.create(
#                 product_id = product_id,
#                 model_name = product_name,
#                 model_name_french = product_name,
#                 # model_image = model_image,
#                 status = 'Active'
#             )
#             create_model.save()
#             list_price = []
            
#             create_variant = models.ProductModelVariant.objects.create(
#                 product_id = product_id,
#                 model_id = create_model.id,
#                 name = product_name,
#                 name_french = product_name,
#                 # image = variant_image,
#                 price = final_price,
#                 variant_verification = 'Approved',
#                 status = 'Active'

#             )
#             create_variant.save()
#             variant_id = create_variant.id
         
#             price = models.VendorProductPrice.objects.create(
#                 product_id = product_id,
#                 model_id = create_model.id,
#                 vendor_id = vendor_id,
#                 variant_id = variant_id,
#                 price = price,
#                 # quantity = quantity,
#                 status = 'Active'
#             ).save()

#             smallest_price = final_price
#             product_update = models.ProductDetail.objects.get(id = product_id)
#             product_update.price = smallest_price
#             product_update.save()
            
#         response_data = {
#             "statuscode":200,
#             "status":"Success",
#             'message':'Data submitted successfully.',
#         }
#         json_data = JSONRenderer().render(response_data)
#         return HttpResponse(json_data, content_type= 'application/json')

############## S3 File Store start here ##############
#####          DO NOT DELETE THIS CODE           #####
######################################################

from openpyxl import Workbook

@csrf_exempt
def bulk_upload(request):
    if request.method != "POST":
        return HttpResponse(status=405)


    python_data = {}
    for i, j in request.FILES.items():
        python_data[i] = j
    for i, j in request.POST.items():
        python_data[i] = j

    excel_file = python_data.get('excel_file')
    flag = python_data.get('flag')

    letters = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z',
               'AA','AB','AC','AD','AE','AF','AG','AH','AI','AJ','AK','AL','AM','AN','AO','AP','AQ','AR','AS','AT','AU','AV','AW','AX','AY','AZ',
               'BA','BB','BC','BD','BE','BF','BG','BH','BI','BJ','BK','BL','BM','BN','BO','BP','BQ','BR','BS','BT','BU','BV','BW','BX','BY','BZ']

    # -------- SAVE INPUT FILE TO S3 -------- #
    if fs.exists('product_import.xlsx'):
        fs.delete('product_import.xlsx')

    filename = fs.save('product_import.xlsx', excel_file)

    with fs.open(filename, 'rb') as f:
        workbook = load_workbook(f)

    sheet = workbook.active
    invalid_count = 0
    new_workbook = Workbook()
    new_sheet = new_workbook.active

    for row_index, row in enumerate(sheet.iter_rows(values_only=True), start=1):

        if row_index == 1:
            for col_index in range(len(row)):
                new_sheet[f"{letters[col_index]}1"] = row[col_index]

            # Add your extra headers
            new_sheet[f"{letters[23]}1"] = "Status"
            new_sheet[f"{letters[24]}1"] = "Reasons"
            continue

        if row[0] is None:
            break

        # -------- READ VALUES -------- #
        category = str(row[0]).strip()
        subcategory = str(row[1]).strip()
        unit_of_measure = str(row[2]).lower()
        shipping_via = row[3]
        country_of_origin = str(row[4]).strip()
        available_country = [v.strip() for v in str(row[5]).split(",")]
        tags = [t.strip() for t in str(row[6]).split(",")]

        product_name = row[7]
        description = row[8]
        price = row[9]
        final_price = row[10]
        min_order_quantity = row[11]

        length = row[12]
        width = row[13]
        height = row[14]
        weight = row[15]
        vendor = row[16]
        reuser = row[17]
        refpro = row[18]
        product_type = row[19]
        product_packaging = row[20]
        product_packaging_value = row[21]

        # -------- COPY ROW -------- #
        for col_index in range(len(row)):
            new_sheet[f"{letters[col_index]}{row_index}"] = row[col_index]

        list_reason = []

        # -------- CATEGORY -------- #
        category_id = None
        if not models.CategoryDetail.objects.filter(
            Q(category__iexact=category) | Q(category_french__iexact=category)
        ).exists():
            new_sheet[f"{letters[0]}{row_index}"].fill = PatternFill(fill_type="solid", start_color="FFFF00")
            list_reason.append("Enter Valid Category")
            invalid_count += 1
        else:
            category_id = models.CategoryDetail.objects.filter(
                Q(category__iexact=category) | Q(category_french__iexact=category)
            ).first().id

        # -------- SUBCATEGORY -------- #
        if not models.SubCategoryDetail.objects.filter(
            Q(subcategory__iexact=subcategory) | Q(subcategory_french__iexact=subcategory)
        ).exists():
            new_sheet[f"{letters[1]}{row_index}"].fill = PatternFill(fill_type="solid", start_color="FFFF00")
            list_reason.append("Enter Valid Subcategory")
            invalid_count += 1

        # -------- UNIT -------- #
        if unit_of_measure not in ['kg','pcs','liters','meters','tons','carton','douzaine','1/2douzaine']:
            new_sheet[f"{letters[2]}{row_index}"].fill = PatternFill(fill_type="solid", start_color="FFFF00")
            list_reason.append("Invalid unit")
            invalid_count += 1

        # -------- SHIPPING -------- #
        if shipping_via not in ['By Air','by air','By Ship','by ship','Both','both']:
            new_sheet[f"{letters[3]}{row_index}"].fill = PatternFill(fill_type="solid", start_color="FFFF00")
            list_reason.append("Please select one value from the following options: By Air, By Ship, or Both.")
            invalid_count += 1

        # -------- COUNTRY -------- #
        if not models.Country.objects.filter(country_name__iexact=country_of_origin).exists():
            new_sheet[f"{letters[4]}{row_index}"].fill = PatternFill(fill_type="solid", start_color="FFFF00")
            list_reason.append("Invalid country")
            invalid_count += 1

        # -------- AVAILABLE COUNTRY -------- #
#         for country in available_country:
#             if country.lower() != 'all':
#                 if not models.ProductCountry.objects.filter(name__iexact=country).exists():
#                     new_sheet[f"{letters[5]}{row_index}"].fill = PatternFill(fill_type="solid", start_color="FFFF00")
#                     list_reason.append(f"{country} not found")
#                     invalid_count += 1

        available_country = [c.strip() for c in available_country if c.strip()]

        # If 'all' exists, keep only 'All'
        if any(country.lower() == 'all' for country in available_country):
            available_country = ['All']

        for country in available_country:
            if country.lower() != 'all':
                if not models.ProductCountry.objects.filter(
                    name__iexact=country
                ).exists():

                    new_sheet[f"{letters[5]}{row_index}"].fill = PatternFill(
                        fill_type="solid",
                        start_color="FFFF00"
                    )

                    list_reason.append(f"{country} not found")
                    invalid_count += 1




        # -------- PRICE -------- #
        try:
            price_val = float(str(price).replace(",", ""))
            if price_val < 0:
                raise Exception()
            new_sheet[f"{letters[9]}{row_index}"] = round(price_val)
        except:
            new_sheet[f"{letters[9]}{row_index}"].fill = PatternFill(fill_type="solid", start_color="FFFF00")
            list_reason.append("Invalid price")
            invalid_count += 1

        # -------- FINAL PRICE -------- #
        try:
            val = float(str(final_price).replace(",", ""))
            if val < 0:
                raise Exception()
            new_sheet[f"{letters[10]}{row_index}"] = round(val)
        except:
            new_sheet[f"{letters[10]}{row_index}"].fill = PatternFill(fill_type="solid", start_color="FFFF00")
            list_reason.append("Invalid final price")
            invalid_count += 1

        # -------- MIN QTY -------- #
        try:
            val = int(float(str(min_order_quantity)))
            if val < 1:
                raise Exception()
            new_sheet[f"{letters[11]}{row_index}"] = val
        except:
            new_sheet[f"{letters[11]}{row_index}"].fill = PatternFill(fill_type="solid", start_color="FFFF00")
            list_reason.append("Invalid min qty")
            invalid_count += 1

        # -------- DIMENSIONS -------- #
        for idx, val in [(12,length),(13,width),(14,height)]:
            try:
                v = float(val)
                if v <= 0:
                    raise Exception()
            except:
                new_sheet[f"{letters[idx]}{row_index}"].fill = PatternFill(fill_type="solid", start_color="FFFF00")
                list_reason.append("Invalid dimension")
                invalid_count += 1

        if weight is None or str(weight).strip().lower() in ['null', '', '-']:
            # weight = 0
            new_sheet[f"{letters[15]}{row_index}"] =  0
        # -------- VENDOR -------- #
        if not models.VendorDetail.objects.filter(email__iexact=vendor).exists():
            new_sheet[f"{letters[16]}{row_index}"].fill = PatternFill(fill_type="solid", start_color="FFFF00")
            list_reason.append("Invalid vendor")
            invalid_count += 1

        # -------- REQUIRED FIELDS -------- #
        if not reuser:
            new_sheet[f"{letters[17]}{row_index}"].fill = PatternFill(fill_type="solid", start_color="FFFF00")
            list_reason.append("Reuser empty")
            invalid_count += 1

        if not refpro:
            new_sheet[f"{letters[18]}{row_index}"].fill = PatternFill(fill_type="solid", start_color="FFFF00")
            list_reason.append("Refpro empty")
            invalid_count += 1

        # -------- PRODUCT TYPE -------- #
        if not models.ProductType.objects.filter(product_type=product_type).exists():
            new_sheet[f"{letters[19]}{row_index}"].fill = PatternFill(fill_type="solid", start_color="FFFF00")
            list_reason.append("Invalid product type")
            invalid_count += 1

        # -------- PACKAGING -------- #
        if not models.ProductPackagingBy.objects.filter(product_packaging=product_packaging).exists():
            new_sheet[f"{letters[20]}{row_index}"].fill = PatternFill(fill_type="solid", start_color="FFFF00")
            list_reason.append("Invalid packaging")
            invalid_count += 1

        # -------- PACKAGING VALUE -------- #
        if not str(product_packaging_value).isdigit() or int(product_packaging_value) <= 0:
            new_sheet[f"{letters[21]}{row_index}"].fill = PatternFill(fill_type="solid", start_color="FFFF00")
            list_reason.append("Invalid packaging value")
            invalid_count += 1

        # -------- STATUS -------- #
        status = "Valid" if not list_reason else "Invalid"
        color = "3d7d13" if status == "Valid" else "e39830"

        new_sheet[f"{letters[23]}{row_index}"] = status
        new_sheet[f"{letters[23]}{row_index}"].fill = PatternFill(fill_type="solid", start_color=color)

        # new_sheet[f"{letters[24]}{row_index}"] = ", ".join(list_reason)
        new_sheet[f"{letters[24]}{row_index}"] = ', '.join(f"'{item}'" for item in list_reason)

    # -------- SAVE OUTPUT TO S3 -------- #
    output = BytesIO()
    new_workbook.save(output)
    output.seek(0)

    new_filename = "product_import_data.xlsx"

    if fs.exists(new_filename):
        fs.delete(new_filename)

    fs.save(new_filename, output)

    link = SITE_MEDIA_BASE_URL + new_filename
    print(link, 'link')

    response_data = {
        "statuscode": 200,
        "status": "Success",
        "message": "File processed successfully",
        "invalid_count": invalid_count,
        "flag": "Valid" if invalid_count == 0 else "Invalid",
        "link": link
    }

    return HttpResponse(JSONRenderer().render(response_data), content_type='application/json')


@csrf_exempt
def bulk_upload_submit(request):
    if request.method != "POST":
        return HttpResponse(status=405)

    try:
        python_data = JSONParser().parse(io.BytesIO(request.body))
        link = python_data.get('link')
        link = SITE_MEDIA_BASE_URL + link


        if not link:
            return HttpResponse(
                JSONRenderer().render({"status": "Error", "message": "File link required"}),
                content_type='application/json'
            )

        # -------- READ FILE FROM S3 -------- #
        filename = os.path.basename(link)

        with fs.open(filename, 'rb') as f:

            workbook = load_workbook(f)

        sheet = workbook.active

        # -------- LOOP THROUGH EXCEL -------- #
        for row_index, row in enumerate(sheet.iter_rows(values_only=True), start=1):

            if row_index == 1:
                continue  # skip header

            if not row or not row[0]:
                continue

            # -------- SAFE DATA EXTRACTION -------- #
            category = str(row[0] or "").strip()
            subcategory = str(row[1] or "").strip()
            unit_of_measure = str(row[2] or "").lower()
            shipping_via = str(row[3] or "").title()
            country_of_origin = str(row[4] or "").strip()

            available_country = [v.strip() for v in str(row[5] or "").split(",") if v]
            tags = [t.strip() for t in str(row[6] or "").split(",") if t]

            product_name = str(row[7] or "").strip()
            description = str(row[8] or "").strip()

            price = float(row[9] or 0)
            final_price = float(row[10] or 0)
            min_order_quantity = int(float(row[11] or 1))

            length = float(row[12] or 0)
            width = float(row[13] or 0)
            height = float(row[14] or 0)
            weight = float(row[15] or 0)

            vendor = str(row[16] or "").strip()
            reuser = row[17]
            refpro = row[18]

            product_type = str(row[19] or "").strip()
            product_packaging = str(row[20] or "").strip()
            product_packaging_value = int(row[21] or 0)

            # -------- FETCH DATABASE OBJECTS -------- #
            category_obj = models.CategoryDetail.objects.filter(
                Q(category__iexact=category) | Q(category_french__iexact=category)
            ).first()

            subcategory_obj = models.SubCategoryDetail.objects.filter(
                Q(subcategory__iexact=subcategory) | Q(subcategory_french__iexact=subcategory)
            ).first()

            product_type_obj = models.ProductType.objects.filter(
                product_type__iexact=product_type
            ).first()

            packaging_obj = models.ProductPackagingBy.objects.filter(
                product_packaging__iexact=product_packaging
            ).first()

            country_obj = models.Country.objects.filter(
                country_name__iexact=country_of_origin
            ).first()

            vendor_obj = models.VendorDetail.objects.filter(
                email__iexact=vendor
            ).first()

            # -------- SKIP INVALID ROW -------- #
            if not all([category_obj, subcategory_obj, product_type_obj, packaging_obj, country_obj, vendor_obj]):
                continue

            # -------- GENERATE PRODUCT CODE -------- #
            random_number = str(random.randint(1000, 9999))
            product_code = (
                category_obj.category[:3].upper() + "_" +
                subcategory_obj.subcategory[:3].upper() + "_" +
                product_name[:3].upper() + "_" +
                random_number
            )

            # -------- AVAILABLE COUNTRIES -------- #
            list_available_country = []
            for available in available_country:
                obj = models.ProductCountry.objects.filter(
                    Q(name__iexact=available) | Q(name_french__iexact=available)
                ).first()
                if obj:
                    list_available_country.append(obj.id)

            # -------- TAGS -------- #
            list_tags = []
            for tag in tags:
                obj = models.ProductTag.objects.filter(
                    category=category_obj.id,
                    tag__iexact=tag
                ).first()
                if obj:
                    list_tags.append(obj.id)

            # -------- CREATE PRODUCT -------- #
            product = models.ProductDetail.objects.create(
                product_name=product_name,
                product_name_french=product_name,
                product_code=product_code,
                vendor_id=vendor_obj.id,
                category_id=category_obj.id,
                subcategory_id=subcategory_obj.id,
                description=description,
                description_french=description,
                unit_of_measure=unit_of_measure,
                length=length,
                height=height,
                width=width,
                weight=weight,
                country_of_origin_id=country_obj.id,
                carton_length=length,
                carton_width=width,
                carton_height=height,
                carton_weight=weight,
                product_verification='Approved',
                min_order_quantity=min_order_quantity,
                price=price,
                discount=0,
                final_price=final_price,
                status='bulk',
                refpro=refpro,
                reuser=reuser,
                product_type_id=product_type_obj.id,
                product_packaging_id=packaging_obj.id,
                product_packaging_value=product_packaging_value,
                shipping_via=shipping_via,
            )

            # -------- MANY TO MANY -------- #
            if list_available_country:
                product.available_country.set(list_available_country)

            if list_tags:
                product.tag.set(list_tags)

            # -------- MODEL -------- #
            model_obj = models.ProductModel.objects.create(
                product_id=product.id,
                model_name=product_name,
                model_name_french=product_name,
                status='Active'
            )

            # -------- VARIANT -------- #
            variant = models.ProductModelVariant.objects.create(
                product_id=product.id,
                model_id=model_obj.id,
                name=product_name,
                name_french=product_name,
                price=final_price,
                variant_verification='Approved',
                status='Active'
            )

            # -------- VENDOR PRICE -------- #
            models.VendorProductPrice.objects.create(
                product_id=product.id,
                model_id=model_obj.id,
                vendor_id=vendor_obj.id,
                variant_id=variant.id,
                price=price,
                status='Active'
            )

            # -------- UPDATE FINAL PRICE -------- #
            product.price = final_price
            product.save()

        return HttpResponse(
            JSONRenderer().render({
                "statuscode": 200,
                "status": "Success",
                "message": "Data submitted successfully"
            }),
            content_type='application/json'
        )

    except Exception as e:
        return HttpResponse(
            JSONRenderer().render({
                "status": "Error",
                "message": str(e)
            }),
            content_type='application/json'
        )


############## S3 File Store end here ##############
#####          DO NOT DELETE THIS CODE           #####
######################################################


@csrf_exempt
def all_bulk_product_list(request):
    python_data = JSONParser().parse(io.BytesIO(request.body))
    
    print("python_data--all_product_list--->", python_data)

    today = timezone.now()

    page_number = int(python_data.get('page_number', 1))
    row_size = int(python_data.get('row_data', 10))
    last_row = row_size * page_number
    first_row = last_row - row_size

    category_name = python_data.get('category_name',None)
    search_key = python_data.get('search_key',None)
    subcategory_name = python_data.get('subcategory_name',None)

    filter_condition = Q()

    if category_name not in [None,'','null']:
        filter_condition &= Q(category__category = category_name)
    if subcategory_name not in [None,'','null']:
        filter_condition &= Q(subcategory__subcategory = subcategory_name)
    if search_key not in [None,'','null']:
        filter_condition &= Q(product_name__icontains = search_key)|Q(refpro__icontains = search_key)
    
    total_records = models.ProductDetail.objects.filter(filter_condition, status= 'bulk').count()
    print(total_records, 'total_records')
    list_data = []
    all_product = models.ProductDetail.objects.filter(filter_condition, status= 'bulk').order_by('-id')[first_row:last_row]
    for product in all_product:
        product = models.ProductDetail.objects.get(id = product.id)
        price_data = models.ProductModelVariant.objects.filter(product=product).aggregate(
            max_price=Max('price'),
            min_price=Min('price')
        )

        max_price = price_data['max_price']
        min_price = price_data['min_price']
        serializer = ProductDetailSerializer(product).data
        serializer.update({'max_price': max_price, 'min_price':min_price})
        list_data.append(serializer)

    
    res = {
        'data': list_data ,
        'total_records':total_records,
        'current_page':page_number,
        'total_pages': int(np.ceil(total_records/row_size))
        }
    json_data = JSONRenderer().render(res)
    return HttpResponse(json_data, content_type= 'application/json', status=200)


@csrf_exempt
def product_type_create(request):
    if request.method == "POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))
        product_type = python_data.get('product_type')
        
        if models.ProductType.objects.filter(product_type = product_type).count() == 0:
            create = models.ProductType.objects.create(
                product_type = product_type
            ).save()
            res = {
                'message':'Product Type Added succesfully.'
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)
        else:
            res = {
                'message':'Something Went Wrong.'
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 406)


@csrf_exempt
def product_type_update(request):
    if request.method == "POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))
        id = python_data.get('id')
        product_type = python_data.get('product_type')
        
        if models.ProductType.objects.filter(product_type=product_type, id = id).count() == 1:
            res = {
                'message':'Type update succesfully.'
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)
        elif models.ProductType.objects.filter(product_type=product_type).count() != 0:
            res = {
                'message':'Type already added.'
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 406)
        else:
            type_count = models.ProductType.objects.filter(product_type=product_type).count()
            if type_count == 0:
                type_update = models.ProductType.objects.get(id = id)
                type_update.product_type = product_type 
                type_update.save()
                res = {
                    'message':'Type update succesfully.'
                }
                return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)
            else:
                res = {
                    'message':'Something Went Wrong.'
                }
                return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 406)

@csrf_exempt
def product_type_list(request):
    if request.method == "POST":

        all_type = models.ProductType.objects.all()
        serialiser = ProductTypeSerializer(all_type, many=True).data
        
        res = {
            'data':serialiser
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)




@csrf_exempt
def product_packaging_create(request):
    if request.method == "POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))
        product_packaging = python_data.get('product_packaging')
        
        if models.ProductPackagingBy.objects.filter(product_packaging = product_packaging).count() == 0:
            create = models.ProductPackagingBy.objects.create(
                product_packaging = product_packaging
            ).save()
            res = {
                'message':'Product Type Added succesfully.'
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)
        else:
            res = {
                'message':'Something Went Wrong.'
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 406)


@csrf_exempt
def product_packaging_update(request):
    if request.method == "POST":
        python_data = JSONParser().parse(io.BytesIO(request.body))
        id = python_data.get('id')
        product_packaging = python_data.get('product_packaging')
        
        if models.ProductPackagingBy.objects.filter(product_packaging=product_packaging, id = id).count() == 1:
            res = {
                'message':'Type update succesfully.'
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)
        elif models.ProductPackagingBy.objects.filter(product_packaging=product_packaging).count() != 0:
            res = {
                'message':'Type already added.'
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 406)
        else:
            type_count = models.ProductPackagingBy.objects.filter(product_packaging=product_packaging).count()
            if type_count == 0:
                type_update = models.ProductPackagingBy.objects.get(id = id)
                type_update.product_packaging = product_packaging 
                type_update.save()
                res = {
                    'message':'Type update succesfully.'
                }
                return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)
            else:
                res = {
                    'message':'Something Went Wrong.'
                }
                return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 406)

@csrf_exempt
def product_packaging_list(request):
    if request.method == "POST":

        all_type = models.ProductPackagingBy.objects.all()
        serialiser = ProductPackagingBySerializer(all_type, many=True).data
        
        res = {
            'data':serialiser
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)
    
@csrf_exempt
def update_vector(request):
    if request.method == "POST":
        all_products = models.ProductDetail.objects.all().order_by('id')

        for product in all_products:
            print("product------>",product)
            get_product_image_1 = product.product_image_1
            get_product_image_2 = product.product_image_2
            get_product_image_3 = product.product_image_3
            get_product_image_4 = product.product_image_4
            get_product_image_5 = product.product_image_5
            get_product_image_6 = product.product_image_6
            get_product_image_7 = product.product_image_7
            get_product_image_8 = product.product_image_8

            domain_path = ""


            if get_product_image_1 != None and get_product_image_1 != 'null' and get_product_image_1 != '':
                feat = extract_features_from_url(domain_path+get_product_image_1.url)
                try:
                    if feat.size > 0:
                        product.product_image_1_vector = feat.tolist()
                        product.save()
                except:
                    pass
            
            if get_product_image_2 != None and get_product_image_2 != 'null' and get_product_image_2 != '':
                feat = extract_features_from_url(domain_path+get_product_image_2.url)
                try:
                    if feat.size > 0:
                        product.product_image_2_vector = feat.tolist()
                        product.save()
                except:
                    pass

            if get_product_image_3 != None and get_product_image_3 != 'null' and get_product_image_3 != '':
                feat = extract_features_from_url(domain_path+get_product_image_3.url)
                try:
                    if feat.size > 0:
                        product.product_image_3_vector = feat.tolist()
                        product.save()
                except:
                    pass

            if get_product_image_4 != None and get_product_image_4 != 'null' and get_product_image_4 != '':
                feat = extract_features_from_url(domain_path+get_product_image_4.url)
                try:
                    if feat.size > 0:
                        product.product_image_4_vector = feat.tolist()
                        product.save()
                
                except:
                    pass


            if get_product_image_5 != None and get_product_image_5 != 'null' and get_product_image_5 != '':
                feat = extract_features_from_url(domain_path+get_product_image_5.url)
                try:
                    if feat.size > 0:
                        product.product_image_5_vector = feat.tolist()
                        product.save()
                except:
                    pass

            if get_product_image_6 != None and get_product_image_6 != 'null' and get_product_image_6 != '':
                feat = extract_features_from_url(domain_path+get_product_image_6.url)
                try:
                    if feat.size > 0:
                        product.product_image_6_vector = feat.tolist()
                        product.save()
                except:
                    pass

            if get_product_image_7 != None and get_product_image_7 != 'null' and get_product_image_7 != '':
                feat = extract_features_from_url(domain_path+get_product_image_7.url)
                try:
                    if feat.size > 0:
                        product.product_image_7_vector = feat.tolist()
                        product.save()
                except:
                    pass

            if get_product_image_8 != None and get_product_image_8 != 'null' and get_product_image_8 != '':
                feat = extract_features_from_url(domain_path+get_product_image_8.url)
                try:
                    if feat.size > 0:
                        product.product_image_8_vector = feat.tolist()
                        product.save()
                except:
                    pass

        res={
            'message':'Product Vector Updated for all image'
        }
        return HttpResponse(JSONRenderer().render(res), content_type="application/json", status=200)



###### Orange Money #####


# -------------------------------
# Utility: Get Orange Access Token
# -------------------------------
# def get_access_token():
#     url = "https://api.orange.com/oauth/v3/token"

#     try:
#         response = requests.post(
#             url,
#             auth=(settings.ORANGE_CLIENT_ID, settings.ORANGE_CLIENT_SECRET),
#             data={"grant_type": "client_credentials"},
#             timeout=10
#         )

#         response.raise_for_status()
#         return response.json().get("access_token")

#     except requests.RequestException as e:
#         print("Token Error:", e)
#         return None


def get_access_token():
    url = "https://api.orange.com/oauth/v3/token"

    try:
        response = requests.post(
            url,
            auth=(settings.ORANGE_CLIENT_ID, settings.ORANGE_CLIENT_SECRET),
            data={"grant_type": "client_credentials"},
            timeout=10
        )

        print("STATUS:", response.status_code)
        print("RESPONSE:", response.text)

        response.raise_for_status()
        return response.json().get("access_token")

    except requests.RequestException as e:
        print("FULL ERROR:", str(e))
        return None


# -------------------------------
# Initiate Payment API
# -------------------------------
@csrf_exempt
def initiate_payment(request):
    python_data = JSONParser().parse(io.BytesIO(request.body))
    amount = python_data.get('amount')
    # amount = request.data.get("amount")

    if not amount:
        res={
            "error": "Amount is required"
            }
        return HttpResponse(JSONRenderer().render(res), content_type="application/json", status=400)
    token = get_access_token()
    
    if not token:
        res={
            "error": "Failed to get access token"
            }
        return HttpResponse(JSONRenderer().render(res), content_type="application/json", status=400)

    order_id = str(uuid.uuid4())

    # Save initial payment record
    # payment = Payment.objects.create(
    #     order_id=order_id,
    #     amount=amount,
    #     status="PENDING"
    # )

    url = "https://api.orange.com/orange-money-webpay/dev/v1/webpayment"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    payload = {
        "merchant_key": settings.ORANGE_MERCHANT_KEY,
        "currency": "XOF",
        "order_id": order_id,
        "amount": amount,
        "return_url": "https://diaba.store/payment-failed/",
        "cancel_url": "https://diaba.store/payment-failed/",
        # success_url = "https://diaba.store/payment-success/"
        # error_url = "https://diaba.store/payment-failed/"
        "notif_url": "https://api.diaba.store.com/api/orange/callback",
        "lang": "en"
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        # return Response({
        #     "payment_url": data.get("payment_url"),
        #     "order_id": order_id
        # })

        res={
            "payment_url": data.get("payment_url"),
            "order_id": order_id
        }
        return HttpResponse(JSONRenderer().render(res), content_type="application/json", status=200)

    except requests.RequestException as e:
        # payment.status = "FAILED"
        # payment.save()

        # return Response(
        #     {"error": "Payment initiation failed", "details": str(e)},
        #     status=status.HTTP_500_INTERNAL_SERVER_ERROR
        # )
        res={
            "error": "Payment initiation failed", 
            "details": str(e)
        }
        return HttpResponse(JSONRenderer().render(res), content_type="application/json", status=500)


# -------------------------------
# Callback (Webhook)
# -------------------------------
@csrf_exempt
def orange_callback(request):
    data = request.data

    order_id = data.get("order_id")
    status_value = data.get("status")

    try:
        payment = Payment.objects.get(order_id=order_id)

        if status_value == "SUCCESS":
            payment.status = "SUCCESS"
        else:
            payment.status = "FAILED"

        payment.save()

        return Response({"message": "Callback processed"})

    except Payment.DoesNotExist:
        return Response(
            {"error": "Payment not found"},
            status=status.HTTP_404_NOT_FOUND
        )

####### EXTRA APIS #######
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





####### APP Admin apis #######

@csrf_exempt
def app_admin_counts(request):
    if request.method == "POST":
        total_vendors = models.VendorDetail.objects.all().count()
        total_orders = models.OrderDetail.objects.all().count()
        total_customer = models.CustomerDetail.objects.all().count()
        
        res={
            "total_vendors":total_vendors,
            "total_orders":total_orders,
            "total_customer":total_customer,
            "total_revenue":0,
        }
        return HttpResponse(JSONRenderer().render(res), content_type="application/json", status=200)
    
# Vendor Analytics API

@csrf_exempt
def vendor_analytics_count(request):
    if request.method == "POST":
        current_dt = datetime.now()

        last_30_days = current_dt - timedelta(days=30)

        total_vendor = models.VendorDetail.objects.all().count()
        new_vendor = models.VendorDetail.objects.filter(created_at_datetime__gt = last_30_days).count()

        all_vendor_profit = list(models.VendorOrderDetail.objects.annotate(
            total_profit = Sum('variant__total_vendor_price')
        ).values_list('total_profit', flat=True))
        print("all_vendor_profit===>",all_vendor_profit)

        total_vendor_profit = sum(profit for profit in all_vendor_profit if isinstance(profit,int))

        res={
            "total_vendor":total_vendor,
            "new_vendor":new_vendor,
            "total_vendor_profit":total_vendor_profit,
        }
        return HttpResponse(JSONRenderer().render(res), content_type="application/json", status=200)

@csrf_exempt
def vendor_monthly_user(request):
    if request.method == "POST":
        try:
            json_data = request.body
            stream = io.BytesIO(json_data)
            python_data = JSONParser().parse(stream)
        except:
            res={
                "message":"Send Me atleast Year with value None/null in Payload"
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 406)
        
        year = python_data.get('year')

        if year in [None,'','null']:
            year = datetime.now().year

        year = int(year)

        start = datetime(year, 1, 1)
        end = datetime(year+1, 1, 1)

        customer_qs = models.VendorDetail.objects.filter(
            created_at_datetime__gt = start, 
            created_at_datetime__lt = end
        )

        monthly_data = (
            customer_qs.annotate(month = ExtractMonth('created_at_datetime')).values('month').annotate(count=Count('id')).order_by('month')
        )
        total_customer_count = customer_qs.count()

        result = {calendar.month_abbr[i].upper(): 0 for i in range(1, 13)}

        result.update({
            calendar.month_abbr[item['month']].upper(): item['count']
            for item in monthly_data
        })

        res = {
            "year": year,
            "data": result,
            "total_customer_count":total_customer_count
        }

        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)

        
@csrf_exempt
def top_vendor_net_profit(request):
    if request.method == "POST":
        vendor_order_detail = models.VendorOrderDetail.objects.values(
            'vendor',
            company_name = F('vendor__company_name'),
            ).annotate(
            total_profit = Sum('variant__total_vendor_price')
        ).filter(total_profit__isnull = False).order_by('-total_profit')[:5]

        res = {
            'vendor_order_detail':vendor_order_detail
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)


@csrf_exempt
def categories_wise_vendor(request):
    if request.method == "POST":
        vendor_order_detail = models.VendorOrderDetail.objects.values(
            category_french = F('variant__product__category__category_french'),
        ).annotate(vendor_count = Count('vendor',distinct=True))

        res = {
            'vendor_order_detail':vendor_order_detail
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)


@csrf_exempt
def vendor_list_analyse(request):
    if request.method == "POST":
        vendor_order_detail = models.VendorOrderDetail.objects.values(
            'vendor',
            company_name = F('vendor__company_name'),
            status = F('vendor__status'),
            category_name = F('variant__product__category__category'),
            ).annotate(
            total_profit = Sum('variant__total_vendor_price'),
            total_order = Count('vendor'),
        ).filter(total_profit__isnull = False).order_by('-total_profit')[:5]

        res = {
            'vendor_order_detail':vendor_order_detail
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)

# Product Analytics API

@csrf_exempt
def product_analytics_count(request):
    if request.method == "POST":
        active_products = models.ProductDetail.objects.filter(status = 'Active').count()
        inactive_products = models.ProductDetail.objects.filter(status = 'Inactive').count()
        total_products = models.ProductDetail.objects.all().count()
        check_total_products = active_products + inactive_products

        total_product_inquiries = models.ProductInquiry.objects.all().count()
        pending_inquiries = models.ProductInquiry.objects.filter(status = 'Pending').count()

        res={
            'active_products':active_products,
            'inactive_products':inactive_products,
            'total_products':total_products,
            'check_total_products':check_total_products,
            'total_product_inquiries':total_product_inquiries,
            'pending_inquiries':pending_inquiries,
        }
        return HttpResponse(JSONRenderer().render(res), content_type="application/json", status=200)

@csrf_exempt
def product_monthly_addition_graph(request):
    if request.method == "POST":
        try:
            json_data = request.body
            stream = io.BytesIO(json_data)
            python_data = JSONParser().parse(stream)
        except:
            res={
                "message":"Send Me atleast Year with value None/null in Payload"
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 406)
        
        year = python_data.get('year')
        if year in [None,'','null']:
            year = datetime.now().year
        year = int(year)
        
        start = datetime(year, 1, 1)
        end = datetime(year+1, 1, 1)

        product_qs = models.ProductDetail.objects.filter(
            created_at__gt = start, 
            created_at__lt = end
        )
        monthly_data = (
            product_qs.annotate(month = ExtractMonth('created_at')).values('month').annotate(count=Count('id')).order_by('month')
        )
        total_product_count = product_qs.count()

        result = {calendar.month_abbr[i].upper(): 0 for i in range(1, 13)}

        result.update({
            calendar.month_abbr[item['month']].upper(): item['count']
            for item in monthly_data
        })

        res = {
            "year": year,
            "data": result,
            "total_product_count":total_product_count
        }

        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)

@csrf_exempt
def product_category_based_analysis(request):
    if request.method == "POST":
        total_products = models.ProductDetail.objects.count()
        category_data = (
            models.ProductDetail.objects
            .values(
                category_name=F('category__category')
            )
            .annotate(
                total_product=Count('id')
            )
            .annotate(
                percentage=Cast(
                    (F('total_product') * 100.0) / total_products,
                    output_field=FloatField()
                )
            ).order_by('-total_product')
        )

        res={
            "category_data":category_data,
            "total_products":total_products
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)

@csrf_exempt
def product_top_selling_variants(request):
    if request.method == "POST":
        top_variants = (
            models.ProductOrderDetail.objects.values(
                variantId=F('variant__id'),
                product_name=F('variant__product__product_name'),
                orderId=F('order__order_id'),
            )
            .annotate(
                total_sold=Sum('quantity')
            )
            .order_by('-total_sold')[:10]
        )
        res={
            "top_variants":top_variants
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)


@csrf_exempt
def product_remove_add_to_cart(request):
    if request.method == "POST":
        removed_carted_products = models.WishlistDetail.objects.filter(product__isnull=True)
        res={
            "removed_carted_products":removed_carted_products
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)


@csrf_exempt
def product_top_add_to_cart_analysis(request):
    if request.method == "POST":
        top_carted_products = (
            models.CartDetail.objects.values(
                product_name=F('product__product_name'),
                productId=F('product__id'),
            )
            .annotate(
                total_carted=Count('id')
            )
            .order_by('-total_carted')[:10]
        )
        res={
            "top_carted_products":top_carted_products
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)

@csrf_exempt
def product_wishlist_analysis(request):
    if request.method == "POST":
        top_wishlisted_products = (
            models.WishlistDetail.objects.values(
                product_name=F('product__product_name'),
                productId=F('product__id'),
            )
            .annotate(
                total_wishlisted=Count('id')
            )
            .order_by('-total_wishlisted')[:10]
        )
        res={
            "top_wishlisted_products":top_wishlisted_products
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)
    

@csrf_exempt
def product_recent_inquiry_list_analysis(request):
    if request.method == "POST":
        recent_inquired_products = (
            models.ProductInquiry.objects.values(
                'id',
                'status',
                'created_at',
                'product_name',
                customer_name=F('customer__name'),
            ).order_by('-created_at')[:10])

        res={
            "recent_inquired_products":recent_inquired_products
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)


# Order Analytics API

@csrf_exempt
def order_status_analytics_count(request): 
    if request.method == "POST":
        order_qs = models.OrderDetail.objects
        
        confirmed_orders = order_qs.filter(Q(status = "completed")|Q(status = "pending", payment_type__in = ["cash","bank transfer"]), order_status="pending").count()
        in_progress_orders = order_qs.filter(order_status = "In Progress").count()
        completed_orders = order_qs.filter(order_status = "Completed").count()
        failed_orders = order_qs.filter(order_status = "failed").count()
        inquiry_orders = order_qs.filter(order_status = "inquiry").count()

        res={
            "confirmed_orders":confirmed_orders,
            "in_progress_orders":in_progress_orders,
            "completed_orders":completed_orders,
            "failed_orders":failed_orders,
            "inquiry_orders":inquiry_orders,
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)

@csrf_exempt
def order_monthly_analysis(request):
    if request.method == "POST":
        try:
            json_data = request.body
            stream = io.BytesIO(json_data)
            python_data = JSONParser().parse(stream)
        except:
            res={
                "message":"Send Me atleast Year with value None/null in Payload"
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 406)
        
        if python_data.get('year') in [None,'','null']:
            year = datetime.now().year
        else:
            year = int(python_data.get('year'))

        start = datetime(year, 1, 1)
        end = datetime(year+1, 1, 1)

        order_qs = models.OrderDetail.objects.filter(
            Q(status = "completed")|Q(status = "pending", payment_type__in = ["cash","bank transfer"]),
            created_at__gt = start, 
            created_at__lt = end,
        )

        total_revenue = (
            order_qs.aggregate(
                total_revenue=Sum('total_price')
            )['total_revenue'] or 0
        )
        total_order_count = order_qs.count()

        avearage_order_value = total_revenue / total_order_count if total_order_count > 0 else 0

        monthly_data = (
            order_qs.annotate(month = ExtractMonth('created_at')).values('month').annotate(count=Count('id')).order_by('month')
        )

        result = {calendar.month_abbr[i].upper(): 0 for i in range(1, 13)}
        for item in monthly_data:
            month_abbr = calendar.month_abbr[item['month']].upper()
            result[month_abbr] = item['count']
            
        res = {
            "year": year,
            "data": result,
            "total_order_count":total_order_count,
            "total_revenue":total_revenue,
            "avearage_order_value":avearage_order_value,
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)

@csrf_exempt
def top_orders_analysis(request):
    if request.method == "POST":
        top_orders = (
            models.OrderDetail.objects.filter(Q(status = "completed")|Q(status = "pending", payment_type__in = ["cash","bank transfer"])).values(
                'order_id',
                'total_price',
                'created_at',
                customer_name = F('customer__name'),
            ).order_by('-total_price')[:10]
        )
        res={
            "top_orders":top_orders
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)

@csrf_exempt
def order_source_and_ship_by(request):
    if request.method == "POST":
        order_qs = models.OrderDetail.objects.filter(Q(status = "completed")|Q(status = "pending", payment_type__in = ["cash","bank transfer"]))

        total_order = order_qs.count()

        source_data =(
            order_qs.values(
                'order_from',
        ).annotate(
            ratio=Round(
                (Count('id') * 100.0) / total_order,
                precision=2
            )
        )
        )

        res={
            "source_data":source_data
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)

@csrf_exempt
def top_order_category_based_analysis(request):
    if request.method == "POST":
        top_categories = (
            models.ProductOrderDetail.objects.filter(Q(order__status = "completed")|Q(order__status = "pending", order__payment_type__in = ["cash","bank transfer"])).values(
                category_name=F('product__category__category'),
                category_name_french=F('product__category__category_french'),
            ).annotate(
                total_order=Count('order',distinct=True)
            ).order_by('-total_order')[:10]
        )
        res={
            "top_categories":top_categories
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)


@csrf_exempt
def order_recent_list_analysis(request):
    if request.method == "POST":
        recent_orders = (
            models.OrderDetail.objects
            .filter(
                Q(status="completed") |
                Q(status="pending", payment_type__in=["cash", "bank transfer"])
            )
            .annotate(
                customer_name=F('customer__name'),

                ship_by=ArrayAgg(
                    'productorderdetail__shipping_via',
                    distinct=True
                )
            )
            .values(
                'order_id',
                'total_price',
                'created_at',
                'status',
                'order_status',
                'customer_name',
                'ship_by',
            )
            .order_by('-created_at')[:10]
        )

        res={
            "recent_orders":recent_orders
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)

# Customer Analytics API

@csrf_exempt
def customer_analytics_count(request):
    if request.method == "POST":

        all_customers = models.CustomerDetail.objects.all()
        total_customers = all_customers.count()
        new_last_thirty_days = all_customers.filter(created_at_datetime__gt = datetime.now()-timedelta(days=30)).count()
        customer_used_promocode = models.OrderDetail.objects.filter(promocode__isnull=False).distinct('customer').count()

        res={
            "total_customers": total_customers,
            "new_last_thirty_days": new_last_thirty_days,
            "customer_used_promocode": customer_used_promocode
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)



@csrf_exempt
def monthly_customer_analysis(request):
    if request.method == "POST":
        try:
            json_data = request.body
            stream = io.BytesIO(json_data)
            python_data = JSONParser().parse(stream)
        except:
            res={
                "message":"Send Me atleast Year with value None/null in Payload"
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 406)
        
        if python_data.get('year') in [None,'','null']:
            year = datetime.now().year
        else:
            year = int(python_data.get('year'))

        start = datetime(year, 1, 1)
        end = datetime(year+1, 1, 1)

        customer_qs = models.CustomerDetail.objects.filter(
            created_at_datetime__gt = start, 
            created_at_datetime__lt = end,
        )

        total_customer_qs_count = customer_qs.count()

        monthly_data = (
            customer_qs.annotate(month = ExtractMonth('created_at_datetime')).values('month').annotate(count=Count('id')).order_by('month')
        )

        result = {calendar.month_abbr[i].upper(): 0 for i in range(1, 13)}
        for item in monthly_data:
            month_abbr = calendar.month_abbr[item['month']].upper()
            result[month_abbr] = item['count']
            
        res = {
            "year": year,
            "data": result,
            "total_customer_qs_count":total_customer_qs_count,
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)

@csrf_exempt
def customer_by_country_analysis(request):
    if request.method == "POST":
        country_data = (
            models.CustomerDetail.objects
            .exclude(
                country__isnull=True
            )
            .exclude(
                country__in=["", "null"]
            )
            .values('country')
            .annotate(
                count=Count('id')
            )
            .order_by('-count')
        )
        res={
            "country_data":country_data
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)

@csrf_exempt
def customer_top_spenders_analysis(request):
    if request.method == "POST":
        top_spenders = (
            models.OrderDetail.objects.filter(Q(status = "completed")|Q(status = "pending", payment_type__in = ["cash","bank transfer"])).values(
                customer_name=F('customer__name'),
                customerId=F('customer__id'),
            ).annotate(
                total_spent=Sum('total_price')
            ).order_by('-total_spent')[:10]
        )
        res={
            "top_spenders":top_spenders
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)

@csrf_exempt
def customer_order_frequency_distribution_analysis(request):
    if request.method == "POST":
        order_qs = models.OrderDetail.objects.filter(
            Q(status="completed") |
            Q(status="pending", payment_type__in=["cash", "bank transfer"])
        )

      
        customer_orders = (
            order_qs
            .values('customer_id')
            .annotate(
                total_orders=Count('id')
            )
        )


        total_customers = customer_orders.count()

        frequency_rate = (
            customer_orders
            .annotate(
                frequency_rate=Case(
                    When(total_orders=1, then=Value('1 order')),
                    When(total_orders__gte=2, total_orders__lte=5, then=Value('2-5 orders')),
                    When(total_orders__gte=6, total_orders__lte=10, then=Value('6-10 orders')),
                    When(total_orders__gt=10, then=Value('10+ orders')),
                    output_field=CharField()
                )
            )
            .values('frequency_rate')
            .annotate(
                customer_count=Count('customer_id')
            )
            .annotate(
                percentage=Round(
                    (F('customer_count') * 100.0) / total_customers,
                    precision=2
                )
)
            .order_by('frequency_rate')
        )
        res={
            "frequency_rate":frequency_rate
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)

@csrf_exempt
def customer_recent_registered_list_analysis(request):
    if request.method == "POST":
        recent_customers = (
            models.CustomerDetail.objects
            .annotate(
                total_orders=Count(
                    'orderdetail',
                    filter=(
                        Q(orderdetail__status="completed") |
                        Q(
                            orderdetail__status="pending",
                            orderdetail__payment_type__in=[
                                "cash",
                                "bank transfer"
                            ]
                        )
                    ),
                    distinct=True
                ),

                total_spent=Coalesce(
                    Sum(
                        'orderdetail__total_price',
                        filter=(
                            Q(orderdetail__status="completed") |
                            Q(
                                orderdetail__status="pending",
                                orderdetail__payment_type__in=[
                                    "cash",
                                    "bank transfer"
                                ]
                            )
                        )
                    ),
                    0
                ),

                promo_used=ArrayAgg(
                    'orderdetail__promocode__promocode',
                    distinct=True,
                    filter=Q(
                        orderdetail__promocode__promocode__isnull=False
                    )
                ),
            )
            .values(
                'id',
                'name',
                'email',
                'created_at_datetime',
                'country',
                'total_orders',
                'total_spent',
                'promo_used',
                'status',
            )
            .order_by('-created_at_datetime')
        )

        res = {
            "recent_customers": list(recent_customers)
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)

# Dashboard Analytics API

@csrf_exempt
def dashboard_overview(request):
    if request.method == "POST":
        total_vendors = models.VendorDetail.objects.all().count()
        total_orders = models.OrderDetail.objects.all().count()
        confirmed_orders = models.OrderDetail.objects.filter(Q(status = "completed")|Q(status = "pending", payment_type__in = ["cash","bank transfer"]), order_status="pending").count()
        total_products = models.ProductDetail.objects.all().count()
        active_customer = models.CustomerDetail.objects.filter(status = "Active").count()
        chat_agents_count = models.ChatAgentDetail.objects.all().count()
        influencers_count = models.InfluencerDetail.objects.all().count()
        warehouses_count = models.WarehouseDetail.objects.all().count()

        res={
            "total_vendors" : total_vendors,
            "total_orders" : total_orders,
            "confirmed_orders" : confirmed_orders,
            "total_products" : total_products,
            "active_customer" : active_customer,
            "chat_agents_count" : chat_agents_count,
            "influencers_count" : influencers_count,
            "warehouses_count" : warehouses_count,
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)


@csrf_exempt
def dashboard_order_status_graph(request):
    if request.method == "POST":

        try:
            json_data = request.body
            stream = io.BytesIO(json_data)
            python_data = JSONParser().parse(stream)
        except:
            res={
                "message":"Send Me atleast last_record with value None/null in Payload"
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 406)

        last_record = python_data.get('last_record',7)

        if last_record in [None,'','null']:
            last_record = 7

        last_days = datetime.now() - timedelta(days=last_record)

        print("python_data===>",python_data)
        print("last_days===>",last_days)

        order_status_data = (
            models.OrderDetail.objects
            .filter(created_at__gte=last_days)
            .annotate(day=TruncDate('created_at'))
            .values('day')
            .annotate(

                # Raw Counts
                confirmed_count=Count(
                    'id',
                    filter=Q(
                        status="completed",
                        order_status="pending"
                    )
                ),

                pending_count=Count(
                    'id',
                    filter=Q(
                        status="pending",
                        payment_type__in=["cash", "bank transfer"],
                        order_status="pending"
                    )
                ),

                in_progress_count=Count(
                    'id',
                    filter=Q(order_status="In Progress")
                ),

                failed_count=Count(
                    'id',
                    filter=Q(order_status="failed")
                ),

                inquiry_count=Count(
                    'id',
                    filter=Q(order_status="inquiry")
                ),

                completed_count=Count(
                    'id',
                    filter=Q(order_status="Completed")
                ),

                total_orders=Count('id')
            )

            # Percentages
            .annotate(

                confirmed=ExpressionWrapper(
                    (F('confirmed_count') * 100.0) / F('total_orders'),
                    output_field=FloatField()
                ),

                pending=ExpressionWrapper(
                    (F('pending_count') * 100.0) / F('total_orders'),
                    output_field=FloatField()
                ),

                in_progress=ExpressionWrapper(
                    (F('in_progress_count') * 100.0) / F('total_orders'),
                    output_field=FloatField()
                ),

                failed=ExpressionWrapper(
                    (F('failed_count') * 100.0) / F('total_orders'),
                    output_field=FloatField()
                ),

                inquiry=ExpressionWrapper(
                    (F('inquiry_count') * 100.0) / F('total_orders'),
                    output_field=FloatField()
                ),

                completed=ExpressionWrapper(
                    (F('completed_count') * 100.0) / F('total_orders'),
                    output_field=FloatField()
                ),
            )

            .values(
                'day',
                'confirmed',
                'pending',
                'in_progress',
                'failed',
                'inquiry',
                'completed',
                'total_orders'
            )

            .order_by('day')
        )
    
        res={
            "order_status_data":order_status_data
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)


@csrf_exempt
def monthly_dashboard_revenue_graph(request):
    if request.method == "POST":
        try:
            python_data = JSONParser().parse(io.BytesIO(request.body))

        except:
            res={
                "message":"Send Me atleast Year with value None/null in Payload"
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 406)

        year = python_data.get('year')
        if year in [None,'','null']:
            year = datetime.now().year
        year = int(year)

        start = datetime(year, 1, 1)
        end = datetime(year+1, 1, 1)
        revenue_data = (
            models.OrderDetail.objects.filter(
                Q(status = "completed")|Q(status = "pending", payment_type__in = ["cash","bank transfer"], ordertransaction__cash_status = "True"),
                created_at__gt = start, 
                created_at__lt = end,
            )
            .annotate(month = ExtractMonth('created_at'))
            .values('month')
            .annotate(total_revenue=Sum('total_price'))
            .order_by('month')
        )
        result = {calendar.month_abbr[i].upper(): 0 for i in range(1, 13)}
        
        for item in revenue_data:
            month_abbr = calendar.month_abbr[item['month']].upper()
            result[month_abbr] = item['total_revenue'] or 0
        
        res = {
            "year": year,
            "revenue_data": result,
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)

@csrf_exempt
def dashboard_platform_module_count(request):
    if request.method == "POST":
        modules_list = []

        agent_count = models.ChatAgentDetail.objects.filter(status="Active").count()
        currency_converter_count = models.CurrencyConverter.objects.filter(status="Active").count() + 1
        total_bank_details_count = models.CountryWiseBankDetail.objects.filter(status="Active").count()
        category_count = models.CategoryDetail.objects.filter(status="Active").count()
        subcategory_count = models.SubCategoryDetail.objects.filter(status="Active").count()
        super_subcategory_count = models.SuperSubCategoryDetail.objects.filter(status="Active").count()
        vendor_count = models.VendorDetail.objects.filter(status="Active").count()
        cargo_count = models.CargoDetail.objects.filter(status="Active").count()
        chat_room_count = models.ChatRoom.objects.filter(status="Active").count()

        
        modules_list.append(
            {
                "module_name":"Chat Agent",
                "count":agent_count
            },
            {
                "module_name":"Currency Converter",
                "count":currency_converter_count
            },
            {
                "module_name":"Total Bank Details",
                "count":total_bank_details_count
            },
            {
                "module_name":"Category",
                "count":category_count
            },
            {
                "module_name":"Subcategory",
                "count":subcategory_count
            },
            {
                "module_name":"Super Subcategory",
                "count":super_subcategory_count
            },
            {
                "module_name":"Vendor",
                "count":vendor_count
            },
            {
                "module_name":"Cargo",
                "count":cargo_count
            },
            {
                "module_name":"Chat Room",
                "count":chat_room_count
            },
        )

        res={
            "modules_list":modules_list
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)

@csrf_exempt
def dashboard_currencry_exchange_rate_base(request):
    if request.method == "POST":
        try:
            python_data = JSONParser().parse(io.BytesIO(request.body))

        except:
            res={
                "message":"Send Me atleast base_currency with value None/null in Payload"
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 406)
        
        base_currency = python_data.get('base_currency')
        if base_currency in [None,'','null']:
            base_currency = 'XOF'

        all_currency = models.CurrencyConverter.objects.all().exclude(currency_code=base_currency).values('currency_code', 'system_rate')

        get_base_rate = 0
        try:
            get_base_rate = models.CurrencyConverter.objects.filter(currency_code=base_currency).values_list('system_rate', flat=True).first()
        except:
            res={
                "message":"Base currency not found"
            }
            return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 406)

        for currency in all_currency:
            currency['system_rate'] = round(currency['system_rate'] / get_base_rate if currency['system_rate'] else 0, 2)

        res={
            "base_currency":base_currency,
            "all_currency":all_currency,
            "get_base_rate":get_base_rate,
        }
        return HttpResponse(JSONRenderer().render(res), content_type = 'application/json', status = 200)

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
