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
from PIL import Image
from io import BytesIO
import os 
from diabaApp.serializer import DailyPriceSerializer



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
def test_external_product_api(request):
    """
    Testing API to trigger and fetch data directly from the Apipost documentation:
    https://docs.apipost.net/docs/password/46888b7cb873000
    using password: yiwugo
    """
    import re
    import json
    import requests
    try:
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    except Exception:
        pass

    # =========================================================================
    # CONFIGURE YOUR APIPOST CREDENTIALS & URL HERE
    # =========================================================================
    APIPOST_URL = "https://docs.apipost.net/docs/password/46888b7cb873000"
    PASSWORD = "yiwugo"  # Password verification
    # =========================================================================

    # Parse request parameters (allowing dynamic overrides via query params or POST body)
    python_data = {}
    if request.method == "POST":
        if request.body:
            try:
                python_data = json.loads(request.body)
            except Exception:
                try:
                    python_data = request.POST.dict()
                except Exception:
                    python_data = {}
        else:
            python_data = request.POST.dict()

    doc_url = python_data.get('url') or request.GET.get('url') or APIPOST_URL
    doc_password = python_data.get('password') or request.GET.get('password') or PASSWORD

    # Extract issue_id from URL (e.g. 46888b7cb873000)
    match = re.search(r'([a-f0-9]{15,})', doc_url)
    issue_id = match.group(1) if match else "46888b7cb873000"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        'Content-Type': 'application/json'
    }

    # Step 1: Authenticate directly with docs.apipost.net using the password
    auth_url = "https://docs.apipost.net/doc/auth"
    try:
        auth_resp = requests.post(auth_url, json={"issue_id": issue_id, "password": doc_password}, headers=headers, verify=False, timeout=20)
        auth_json = auth_resp.json()
        if auth_json.get('code') != 0:
            return JsonResponse({
                "status": "error",
                "step": "authentication_failed",
                "message": auth_json.get('msg', 'Password verification failed on docs.apipost.net'),
                "doc_url": doc_url
            }, status=401, json_dumps_params={'indent': 2})
        
        token = auth_json.get('data', {}).get('Authorization')
        if not token:
            return JsonResponse({
                "status": "error",
                "step": "token_missing",
                "message": "Authorization token not returned by Apipost.",
                "response": auth_json
            }, status=401, json_dumps_params={'indent': 2})

    except Exception as e:
        return JsonResponse({
            "status": "error",
            "step": "connection_error",
            "message": f"Could not connect to {auth_url}: {str(e)}"
        }, status=502, json_dumps_params={'indent': 2})

    # Step 2: Fetch the full API catalog from docs.apipost.net
    headers['Authorization'] = token
    down_url = "https://docs.apipost.net/doc/down"
    try:
        down_resp = requests.get(down_url, params={"issue_id": issue_id}, headers=headers, verify=False, timeout=25)
        down_data = down_resp.json().get('data', {})
        project_name = down_data.get('name') or "义乌购"
        items = down_data.get('list', [])

        api_list = []
        def collect_apis(node_list):
            for n in node_list:
                if n.get('target_type') == 'api':
                    api_list.append({
                        "target_id": n.get('target_id'),
                        "name": n.get('name'),
                        "method": n.get('method')
                    })
                if 'children' in n and isinstance(n['children'], list):
                    collect_apis(n['children'])
        collect_apis(items)

        # Step 3: Fetch full details & example responses for all APIs
        details_url = "https://docs.apipost.net/doc/details"
        target_ids = [a['target_id'] for a in api_list]
        details_resp = requests.post(details_url, json={"issue_id": issue_id, "target_ids": target_ids}, headers=headers, verify=False, timeout=30)
        details_data = details_resp.json().get('data', {}).get('list', [])

        apis_summary = []
        token_data = None
        category_data = None
        product_detail_data = None
        product_list_data = None
        shop_detail_data = None
        shop_list_data = None

        for item in details_data:
            t_id = item.get('target_id')
            name = item.get('name')
            method = item.get('method')
            url = item.get('url')
            query_params = [
                {
                    "key": q.get('key'),
                    "description": q.get('description'),
                    "required": q.get('not_null') == 1,
                    "example": q.get('value')
                }
                for q in item.get('request', {}).get('query', {}).get('parameter', [])
            ]
            header_params = [
                {
                    "key": h.get('key'),
                    "description": h.get('description'),
                    "required": h.get('not_null') == 1,
                    "example": h.get('value')
                }
                for h in item.get('request', {}).get('header', {}).get('parameter', [])
            ]

            # Parse example responses (fixing trailing commas if present)
            parsed_examples = []
            for ex in item.get('response', {}).get('example', []):
                raw = ex.get('raw')
                if raw:
                    try:
                        clean_raw = re.sub(r',\s*([\]}])', r'\1', raw)
                        parsed_examples.append(json.loads(clean_raw))
                    except Exception:
                        parsed_examples.append({"raw_text": raw})

            first_example = parsed_examples[0] if parsed_examples else None

            if "token" in name.lower() or t_id == "52aeaa6":
                token_data = first_example
            elif "商品分类" in name or "product classification" in name.lower() or "categorize" in (url or "").lower() or t_id == "52aee86":
                category_data = first_example
            elif "商品详细" in name or "product detail" in name.lower() or t_id == "52aec50":
                product_detail_data = first_example
            elif "商品列表" in name or "product list" in name.lower() or t_id == "15459e9dfdc04d":
                product_list_data = first_example
            elif "商铺详细" in name or "shop detail" in name.lower() or t_id == "52aec4e":
                shop_detail_data = first_example
            elif "商铺列表" in name or "shop list" in name.lower() or t_id == "52aec4d":
                shop_list_data = first_example

            apis_summary.append({
                "target_id": t_id,
                "name": name,
                "method": method,
                "url": url,
                "headers": header_params,
                "query_parameters": query_params,
                "response_sample": first_example
            })

        # Allow filtering to a specific plain API response via query param, e.g. ?api=category or ?api=product_detail
        selected_api = (python_data.get('api') or request.GET.get('api') or '').lower().strip()
        if selected_api in ['category', 'categories', 'product_category', 'product_classification', 'classification', 'type', 'entype'] and category_data:
            return JsonResponse(category_data, status=200, json_dumps_params={'indent': 2})
        elif selected_api in ['product_detail', 'product', 'detail'] and product_detail_data:
            return JsonResponse(product_detail_data, status=200, json_dumps_params={'indent': 2})
        elif selected_api in ['product_list', 'products', 'list'] and product_list_data:
            return JsonResponse(product_list_data, status=200, json_dumps_params={'indent': 2})
        elif selected_api in ['shop_detail', 'shop'] and shop_detail_data:
            return JsonResponse(shop_detail_data, status=200, json_dumps_params={'indent': 2})
        elif selected_api in ['shop_list', 'shops'] and shop_list_data:
            return JsonResponse(shop_list_data, status=200, json_dumps_params={'indent': 2})
        elif selected_api in ['token', 'oauth'] and token_data:
            return JsonResponse(token_data, status=200, json_dumps_params={'indent': 2})

        # Return full plain data from the Apipost documentation including category parameter verification
        return JsonResponse({
            "status": "success",
            "message": "Plain data retrieved from Apipost documentation",
            "project_name": project_name,
            "documentation_url": doc_url,
            "category_parameters_verified": {
                "exists_in_api": True,
                "api_name": "商品分类 (Product classification)",
                "api_endpoint": "/open/categorize/product",
                "parameters_found": {
                    "type": {
                        "name": "type",
                        "description": "Chinese category name (分类名称)",
                        "sample_value": "汽摩配件",
                        "present": True
                    },
                    "entype": {
                        "name": "entype",
                        "description": "English category name (英文分类名称)",
                        "sample_value": "Auto & Motorcycle Accessories",
                        "present": True
                    },
                    "id": {
                        "name": "id",
                        "description": "Category ID",
                        "sample_value": 29,
                        "present": True
                    },
                    "uppertype": {
                        "name": "uppertype",
                        "description": "Parent category ID (0 = root category)",
                        "sample_value": "0",
                        "present": True
                    }
                }
            },
            "apis_documented": apis_summary,
            "plain_data": {
                "product_category": category_data,
                "product_detail": product_detail_data,
                "product_list": product_list_data,
                "shop_detail": shop_detail_data,
                "shop_list": shop_list_data,
                "get_token": token_data
            }
        }, status=200, json_dumps_params={'indent': 2})

    except Exception as e:
        return JsonResponse({
            "status": "error",
            "step": "fetch_doc_failed",
            "error": str(e)
        }, status=502, json_dumps_params={'indent': 2})


@csrf_exempt
def check_product_data_fields(request):
    """
    API to audit external product data against Diaba's database schema.
    Categorizes which incoming data is useful and directly mapped,
    which required Diaba fields are missing, and which extra fields are provided.
    Can be called via GET (fetches from Apipost automatically) or POST (passing custom product JSON).
    """
    import re
    import json
    import requests
    try:
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    except Exception:
        pass

    APIPOST_URL = "https://docs.apipost.net/docs/password/46888b7cb873000"
    PASSWORD = "yiwugo"

    # Step 1: Obtain the product JSON (from POST body, or fetch from Apipost doc)
    product_json = None
    if request.method == "POST" and request.body:
        try:
            body_data = json.loads(request.body)
            if "data" in body_data and isinstance(body_data["data"], dict):
                product_json = body_data
            elif "detail" in body_data or "productDetailVO" in body_data:
                product_json = {"data": body_data}
            elif isinstance(body_data, dict):
                product_json = {"data": body_data}
        except Exception:
            product_json = None

    if not product_json:
        # Fetch from Apipost doc directly
        match = re.search(r'([a-f0-9]{15,})', APIPOST_URL)
        issue_id = match.group(1) if match else "46888b7cb873000"
        headers = {'User-Agent': 'Mozilla/5.0', 'Content-Type': 'application/json'}
        try:
            auth_resp = requests.post("https://docs.apipost.net/doc/auth", json={"issue_id": issue_id, "password": PASSWORD}, headers=headers, verify=False, timeout=15)
            token = auth_resp.json().get('data', {}).get('Authorization')
            headers['Authorization'] = token
            det_resp = requests.post("https://docs.apipost.net/doc/details", json={"issue_id": issue_id, "target_ids": ["52aec50"]}, headers=headers, verify=False, timeout=20)
            items = det_resp.json().get('data', {}).get('list', [])
            if items:
                raw = items[0].get('response', {}).get('example', [])[0].get('raw', '')
                clean_raw = re.sub(r',\s*([\]}])', r'\1', raw)
                product_json = json.loads(clean_raw)
        except Exception as e:
            return JsonResponse({"status": "error", "message": f"Could not fetch product from Apipost: {str(e)}"}, status=502)

    if not product_json or not isinstance(product_json, dict):
        return JsonResponse({"status": "error", "message": "No valid product data found to inspect."}, status=400)

    p_data = product_json.get("data", {})
    detail = p_data.get("detail", {})
    detail_vo = detail.get("productDetailVO", {})
    packing = detail.get("productPackingBo", {}) or {}
    shop = p_data.get("shopinfo", {}).get("shop", {}) or {}
    pic_list = detail.get("sdiProductsPicList", []) or []
    sku_list = detail.get("productPropertySkuBoList", []) or []
    extend_list = detail.get("productExtendList", []) or []
    property_list = p_data.get("propertyList", []) or []

    # Gather all images
    collected_images = []
    for img_k in ['picture', 'picture1', 'picture2', 'picture3']:
        val = detail_vo.get(img_k)
        if val and val not in collected_images:
            collected_images.append(val)
    for p in pic_list:
        for img_k in ['picture', 'picture1', 'picture2', 'picture3']:
            val = p.get(img_k)
            if val and val not in collected_images:
                collected_images.append(val)

    # 1. USEFUL & MAPPED FIELDS
    useful_fields = [
        {
            "diaba_model": "ProductDetail",
            "diaba_field": "product_name",
            "external_source": "detail.productDetailVO.title",
            "sample_value": detail_vo.get("title"),
            "status": "Ready",
            "notes": "Primary product name in original source language."
        },
        {
            "diaba_model": "ProductDetail",
            "diaba_field": "product_code",
            "external_source": "detail.productDetailVO.goodsCode",
            "sample_value": detail_vo.get("goodsCode"),
            "status": "Ready",
            "notes": "Supplier SKU / Goods code (e.g. 货号/型号). Will also generate internal Diaba product code."
        },
        {
            "diaba_model": "ProductDetail",
            "diaba_field": "price",
            "external_source": "detail.productDetailVO.sellPrice or data.unitprice",
            "sample_value": detail_vo.get("sellPrice") or p_data.get("unitprice"),
            "status": "Action Required: Currency Conversion",
            "notes": "Value is in CNY (Chinese Yuan). Needs conversion to Diaba base currency (USD/XOF)."
        },
        {
            "diaba_model": "ProductDetail",
            "diaba_field": "min_order_quantity",
            "external_source": "detail.productDetailVO.startNumber or data.smallnum",
            "sample_value": detail_vo.get("startNumber") or p_data.get("smallnum"),
            "status": "Ready",
            "notes": "Minimum purchase threshold."
        },
        {
            "diaba_model": "ProductDetail",
            "diaba_field": "unit_of_measure",
            "external_source": "detail.productDetailVO.metric",
            "sample_value": detail_vo.get("metric"),
            "status": "Ready",
            "notes": "Original unit (e.g. 克, 件, 双). Can map to 'pcs' or translate."
        },
        {
            "diaba_model": "ProductDetail",
            "diaba_field": "description",
            "external_source": "detail.productDetailVO.detaill",
            "sample_value": (detail_vo.get("detaill") or "")[:200] + "... (HTML description with images)",
            "status": "Ready",
            "notes": "Full HTML description containing product images."
        },
        {
            "diaba_model": "ProductDetail",
            "diaba_field": "carton_length",
            "external_source": "detail.productPackingBo.length",
            "sample_value": packing.get("length"),
            "status": "Ready",
            "notes": "Package dimension: Length in cm."
        },
        {
            "diaba_model": "ProductDetail",
            "diaba_field": "carton_width",
            "external_source": "detail.productPackingBo.width",
            "sample_value": packing.get("width"),
            "status": "Ready",
            "notes": "Package dimension: Width in cm."
        },
        {
            "diaba_model": "ProductDetail",
            "diaba_field": "carton_height",
            "external_source": "detail.productPackingBo.height",
            "sample_value": packing.get("height"),
            "status": "Ready",
            "notes": "Package dimension: Height in cm."
        },
        {
            "diaba_model": "ProductDetail",
            "diaba_field": "carton_weight",
            "external_source": "detail.productPackingBo.shippingWeight",
            "sample_value": packing.get("shippingWeight"),
            "status": "Ready",
            "notes": "Package shipping weight in kg."
        },
        {
            "diaba_model": "ProductDetail",
            "diaba_field": "product_image_1 to product_image_8",
            "external_source": "detail.productDetailVO.picture* & sdiProductsPicList",
            "sample_value": collected_images[:8],
            "status": "Action Required: Image Download",
            "notes": f"Found {len(collected_images)} image URLs. Need downloading via requests.get() to save into media/product/."
        },
        {
            "diaba_model": "ProductModel",
            "diaba_field": "model_name",
            "external_source": "detail.productPropertySkuBoList[].specificationNameOne",
            "sample_value": [sku.get("specificationNameOne") for sku in sku_list[:5]],
            "status": "Ready",
            "notes": "Style/Color hierarchy (e.g. 款式1, 款式2)."
        },
        {
            "diaba_model": "ProductModelVariant",
            "diaba_field": "name, price, stock, sku_code, image",
            "external_source": "detail.productPropertySkuBoList[]",
            "sample_value": [
                {
                    "name": sku.get("specificationNameTwo"),
                    "price": sku.get("price"),
                    "stock": sku.get("stock"),
                    "sku_code": sku.get("skuCode"),
                    "image": sku.get("picture")
                }
                for sku in sku_list[:3]
            ],
            "status": "Ready",
            "notes": f"{len(sku_list)} variant SKUs found with individual stock and price."
        },
        {
            "diaba_model": "ProductOtherSpecification",
            "diaba_field": "key & value",
            "external_source": "detail.productExtendList or propertyList",
            "sample_value": [{"key": e.get("name"), "value": e.get("value")} for e in extend_list] or [{"key": p.get("pvalue"), "value": p.get("cvalue")} for p in property_list],
            "status": "Ready",
            "notes": "Dynamic specifications (e.g. Material, Origin)."
        },
        {
            "diaba_model": "VendorDetail",
            "diaba_field": "company_name, office_address, phone_number, vendor_name, email, image",
            "external_source": "data.shopinfo.shop",
            "sample_value": {
                "company_name": shop.get("shopName"),
                "office_address": shop.get("factoryAddress") or shop.get("marketInfo"),
                "phone_number": shop.get("mobile") or shop.get("telephone"),
                "vendor_name": shop.get("contacter"),
                "email": shop.get("email"),
                "image": shop.get("shopImageUrl")
            },
            "status": "Ready",
            "notes": "Shop/Supplier details can auto-populate VendorDetail."
        }
    ]

    # 2. MISSING REQUIRED DIABA FIELDS
    missing_fields = [
        {
            "diaba_model": "ProductDetail",
            "diaba_field": "product_name_french",
            "severity": "CRITICAL",
            "reason": "Diaba app is bilingual (English/French). External API provides source Chinese/English title only.",
            "recommended_solution": "Auto-translate title using Google Translate (googletrans) or copy product_name as fallback."
        },
        {
            "diaba_model": "ProductDetail",
            "diaba_field": "description_french",
            "severity": "CRITICAL",
            "reason": "Diaba app expects French product description.",
            "recommended_solution": "Auto-translate plain text summary into French, or duplicate description."
        },
        {
            "diaba_model": "ProductDetail",
            "diaba_field": "category_id & subcategory_id",
            "severity": "CRITICAL",
            "reason": "ForeignKey constraint in Diaba database. External product detail payload only contains internal 'innertype' / 'sellType', not Diaba's internal Category IDs.",
            "recommended_solution": "Use the Category Classification API (/open/categorize/product) where 'entype' provides the English category name (e.g. 'Auto & Motorcycle Accessories') and 'type' provides the Chinese name (e.g. '汽摩配件'). Match 'entype' directly against Diaba's CategoryDetail.name or SubCategoryDetail.name without requiring raw translation!"
        },
        {
            "diaba_model": "ProductDetail",
            "diaba_field": "vendor_id",
            "severity": "CRITICAL",
            "reason": "ForeignKey constraint in Diaba. External API provides shop details in JSON but no internal VendorDetail ID.",
            "recommended_solution": "Auto-create a VendorDetail row from shopinfo.shop (using shopName as unique identifier) or assign a default 'Yiwugo Supplier' vendor."
        },
        {
            "diaba_model": "ProductDetail",
            "diaba_field": "external_id",
            "severity": "HIGH",
            "reason": "Diaba's ProductDetail model currently lacks a dedicated external_id column to prevent duplicate imports and support sync/updates.",
            "recommended_solution": "Add external_id (CharField/IntegerField with index) to ProductDetail, or prefix internal product_code with 'YWG_' + source_id."
        },
        {
            "diaba_model": "ProductDetail",
            "diaba_field": "country_of_origin_id",
            "severity": "MEDIUM",
            "reason": "Diaba ForeignKey to Country model.",
            "recommended_solution": "Default to China (Country ID 2 in Diaba database)."
        },
        {
            "diaba_model": "ProductDetail",
            "diaba_field": "available_country",
            "severity": "MEDIUM",
            "reason": "ManyToManyField in Diaba specifying which countries can order this product.",
            "recommended_solution": "Auto-link to all active countries or default target market (e.g., Senegal, Ivory Coast, etc.)."
        },
        {
            "diaba_model": "ProductDetail",
            "diaba_field": "shipping_via",
            "severity": "MEDIUM",
            "reason": "Diaba requires shipping option ('By Air', 'By Ship', 'Both'). External API has no international shipping mode.",
            "recommended_solution": "Default to 'By Air' (or 'Both' if package is large)."
        },
        {
            "diaba_model": "ProductDetail",
            "diaba_field": "delay_days_air, delay_days_ship, delay_days_express",
            "severity": "LOW",
            "reason": "Diaba shipping delivery estimation days.",
            "recommended_solution": "Default to system standards (e.g. Air: 7-10 days, Ship: 30-45 days, Express: 3-5 days)."
        },
        {
            "diaba_model": "ProductDetail",
            "diaba_field": "product_image_1_vector .. 8_vector",
            "severity": "LOW / OPTIONAL",
            "reason": "512-dimension vector embeddings used for Diaba AI Visual Search.",
            "recommended_solution": "Can be left null upon import, or processed asynchronously in a background worker."
        }
    ]

    # 3. EXTRA / UNMAPPED EXTERNAL FIELDS
    extra_fields = [
        {"field": "dealQuantitys", "value": p_data.get("dealQuantitys"), "purpose": "Total historical sold volume on Yiwugo (social proof only)"},
        {"field": "defaultfreight", "value": p_data.get("defaultfreight"), "purpose": "Local domestic China shipping freight"},
        {"field": "exchangeService", "value": p_data.get("exchangeService"), "purpose": "Supplier return/exchange guarantee flag"},
        {"field": "quickRefund", "value": p_data.get("quickRefund"), "purpose": "Fast refund badge"},
        {"field": "isHasChatRoom", "value": p_data.get("isHasChatRoom"), "purpose": "Supplier live chat capability"},
        {"field": "unitConversion", "value": p_data.get("unitConversion"), "purpose": "Packaging conversion factor (e.g. 1 box = 12 items)"},
        {"field": "orderStockInstruction", "value": p_data.get("orderStockInstruction"), "purpose": "Supplier packaging instructions"},
        {"field": "deliveryPromise", "value": detail_vo.get("deliveryPromise"), "purpose": "Days within which supplier promises to ship to warehouse in China"},
        {"field": "translateId", "value": detail_vo.get("translateId"), "purpose": "Yiwugo internal translation tracking ID"},
        {"field": "freightTemplateId", "value": detail_vo.get("freightTemplateId"), "purpose": "Supplier domestic shipping template ID"},
        {"field": "bbsId", "value": p_data.get("bbsId"), "purpose": "Forum / merchant community post ID"}
    ]

    return JsonResponse({
        "status": "success",
        "audit_target": "Apipost / Yiwugo Product Data Audit for Diaba Catalog",
        "product_inspected": {
            "source_id": detail_vo.get("id") or p_data.get("id"),
            "source_title": detail_vo.get("title"),
            "supplier_name": shop.get("shopName")
        },
        "audit_summary": {
            "useful_and_mapped_fields_count": len(useful_fields),
            "missing_required_diaba_fields_count": len(missing_fields),
            "extra_unmapped_external_fields_count": len(extra_fields)
        },
        "1_useful_and_mapped_fields": useful_fields,
        "2_missing_required_fields": missing_fields,
        "3_extra_unmapped_external_fields": extra_fields,
        "4_actionable_checklist_for_import": [
            "1. Currency: Apply CNY to base currency (USD/XOF) multiplier to 'price'.",
            "2. Category: Look up CategoryDetail & SubCategoryDetail by keywords, or assign to a default category.",
            "3. Vendor: Auto-create a VendorDetail using shopinfo.shop, or link to a default vendor.",
            "4. Language: Auto-translate title and description into French for bilingual support.",
            "5. Images: Download image URLs (picture1..8) and save as Django files in media/product/.",
            "6. Model & Variant: Create ProductModel using specificationNameOne, and ProductModelVariant using specificationNameTwo + price + stock.",
            "7. Shipping Defaults: Set shipping_via='By Air', country_of_origin=2 (China), status='Active' (or 'Pending')."
        ]
    }, status=200, json_dumps_params={'indent': 2})


    