import os
import re
import html
import uuid
import json
import base64
import random
import asyncio
import inspect
import threading
import requests
import math
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache
from django.conf import settings
from django.core.cache import cache
from django.core.files.base import ContentFile
from django.db import close_old_connections, transaction
from django.db.models import Q
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from googletrans import Translator
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from diabaApp import models

try:
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
except Exception:
    pass

APIPOST_DEFAULT_URL = "https://docs.apipost.net/docs/password/46888b7cb873000"
APIPOST_DEFAULT_PASSWORD = "yiwugo"
APIPOST_ISSUE_ID = "46888b7cb873000"
TARGET_PRODUCT_LIST = "15459e9dfdc04d"
TARGET_PRODUCT_DETAIL = "52aec50"
TARGET_CATEGORY = "52aee86"
YIWUGO_CNY_TO_USD_RATE = 7.0
YUWI_GO_SOURCE = "yuwi_go"
YUWI_GO_IMPORT_JOBS = {}
YUWI_GO_JOBS_LOCK = threading.Lock()
YIWUGO_TOKEN_CACHE_KEY = "yiwugo_oauth_access_token"


def _fetch_yiwugo_oauth_token(force_refresh=False):
    """Fetch and cache a live Yiwugo OAuth accessToken using YIWUGO_CLIENT_ID / YIWUGO_CLIENT_SECRET."""
    if not force_refresh:
        cached = cache.get(YIWUGO_TOKEN_CACHE_KEY)
        if cached:
            return cached

    client_id = getattr(settings, "YIWUGO_CLIENT_ID", None) or os.getenv("YIWUGO_CLIENT_ID")
    client_secret = getattr(settings, "YIWUGO_CLIENT_SECRET", None) or os.getenv("YIWUGO_CLIENT_SECRET")
    if not client_id or not client_secret:
        return None

    raw_creds = f"{client_id}:{client_secret}".encode("utf-8")
    auth_header = base64.b64encode(raw_creds).decode("ascii")
    try:
        resp = requests.post(
            "https://open.yiwugo.com/oauth/token",
            params={"grant_type": "client_credentials", "client_id": client_id},
            headers={"Authorization": auth_header},
            timeout=15,
            verify=False,
        )
        resp_json = resp.json()
        if resp_json.get("code") == 0:
            data = resp_json.get("data") or {}
            token = data.get("accessToken")
            expires_in = int(data.get("expiresIn") or 20000)
            if token:
                cache.set(YIWUGO_TOKEN_CACHE_KEY, token, max(60, expires_in - 300))
                return token
    except Exception:
        pass
    return None


def _get_yiwugo_access_token(explicit_token=None, force_refresh=False):
    """Resolve explicit token, settings.YIWUGO_ACCESS_TOKEN, or auto-fetched OAuth token."""
    if explicit_token:
        return explicit_token, False
    configured = getattr(settings, "YIWUGO_ACCESS_TOKEN", None) or os.getenv("YIWUGO_ACCESS_TOKEN")
    if configured:
        return configured, False
    return _fetch_yiwugo_oauth_token(force_refresh=force_refresh), True


def _fetch_apipost_docs(issue_id=APIPOST_ISSUE_ID, password=APIPOST_DEFAULT_PASSWORD, target_ids=None):
    """
    Helper to authenticate and fetch detailed schema/examples from Apipost documentation.
    """
    if target_ids is None:
        target_ids = [TARGET_PRODUCT_LIST, TARGET_PRODUCT_DETAIL, TARGET_CATEGORY]

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        'Content-Type': 'application/json'
    }

    # Step 1: Authenticate
    auth_resp = requests.post(
        "https://docs.apipost.net/doc/auth",
        json={"issue_id": issue_id, "password": password},
        headers=headers,
        verify=False,
        timeout=15
    )
    auth_json = auth_resp.json()
    if auth_json.get('code') != 0:
        raise ValueError(f"Apipost authentication failed: {auth_json.get('msg', 'Unknown error')}")

    token = auth_json.get('data', {}).get('Authorization')
    if not token:
        raise ValueError("Apipost authorization token missing in response.")

    # Step 2: Fetch details for requested target_ids
    headers['Authorization'] = token
    details_resp = requests.post(
        "https://docs.apipost.net/doc/details",
        json={"issue_id": issue_id, "target_ids": target_ids},
        headers=headers,
        verify=False,
        timeout=25
    )
    details_json = details_resp.json()
    items = details_json.get('data', {}).get('list', [])

    result = {}
    for item in items:
        t_id = item.get('target_id')
        parsed_examples = []
        for ex in item.get('response', {}).get('example', []):
            raw = ex.get('raw', '')
            if raw:
                try:
                    clean_raw = re.sub(r',\s*([\]}])', r'\1', raw)
                    parsed_examples.append(json.loads(clean_raw))
                except Exception:
                    parsed_examples.append({"raw_text": raw})

        query_params = [
            {
                "key": q.get('key'),
                "description": q.get('description'),
                "required": q.get('not_null') == 1,
                "example": q.get('value')
            }
            for q in item.get('request', {}).get('query', {}).get('parameter', [])
        ]

        result[t_id] = {
            "target_id": t_id,
            "name": item.get('name'),
            "method": item.get('method'),
            "url": item.get('url'),
            "query_parameters": query_params,
            "example_response": parsed_examples[0] if parsed_examples else None
        }

    return result


def _parse_request_params(request):
    """Extract query/POST/JSON parameters uniformly from GET or POST requests."""
    if request.method == "GET":
        return request.GET.dict()
    if request.body:
        try:
            return json.loads(request.body)
        except Exception:
            return request.POST.dict()
    return request.POST.dict()


def _fetch_third_party_products_data(params, headers=None):
    """Core logic behind fetch_third_party_products returning (payload_dict, http_status)."""
    headers = headers or {}
    page = int(params.get('page') or params.get('cpage') or 1)
    page_size = int(params.get('page_size') or params.get('pageSize') or 20)
    if page_size > 60:
        page_size = 60
    if page < 1:
        page = 1

    search_query = params.get('q') or params.get('query') or ""
    product_id_filter = params.get('product_id') or params.get('productId')
    explicit_token = params.get('access_token') or headers.get('X-Access-Token')
    live_access_token, is_oauth_token = _get_yiwugo_access_token(explicit_token)

    live_data_fetched = False
    live_error = None
    raw_response_data = None

    if live_access_token:
        for attempt in range(2 if is_oauth_token else 1):
            try:
                live_url = "https://open.yiwugo.com/open/cn_product/list"
                live_params = {
                    "access_token": live_access_token,
                    "cpage": page,
                    "pageSize": page_size
                }
                if search_query:
                    live_params["q"] = search_query

                resp = requests.get(live_url, params=live_params, timeout=15, verify=False)
                resp_json = resp.json()
                if resp_json.get('code') == 0:
                    raw_response_data = resp_json.get('data', {})
                    live_data_fetched = True
                    live_error = None
                    break
                if resp_json.get('code') == 501 and is_oauth_token and attempt == 0:
                    live_access_token, _ = _get_yiwugo_access_token(force_refresh=True)
                    if live_access_token:
                        continue
                live_error = resp_json.get('message') or f"Yiwugo API error code {resp_json.get('code')}"
                break
            except Exception as exc:
                live_data_fetched = False
                live_error = str(exc)
                break

    if not live_data_fetched:
        try:
            doc_data = _fetch_apipost_docs(target_ids=[TARGET_PRODUCT_LIST, TARGET_PRODUCT_DETAIL])
            list_doc = doc_data.get(TARGET_PRODUCT_LIST, {})
            example_resp = list_doc.get('example_response', {})
            raw_response_data = example_resp.get('data', {})
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to fetch data from third-party API documentation: {str(e)}"
            }, 502

    if not raw_response_data:
        return {
            "status": "error",
            "message": "No product data received from third-party API."
        }, 404

    raw_products = raw_response_data.get('prslist', [])
    total_found = raw_response_data.get('numfound') or len(raw_products)
    if isinstance(total_found, str) and total_found.isdigit():
        total_found = int(total_found)
    elif not isinstance(total_found, int):
        total_found = len(raw_products)

    total_pages = max(1, math.ceil(total_found / page_size))

    translate_fetch = str(params.get('translate', 'true')).lower() not in ['false', '0', 'no']
    cjk_fetch_inputs = []
    for item in raw_products:
        if not isinstance(item, dict):
            continue
        for field_val in (item.get('title'), item.get('shopName')):
            if _contains_cjk(field_val):
                cjk_fetch_inputs.append(field_val)
    if cjk_fetch_inputs:
        _translate_many(cjk_fetch_inputs, dest="en")
    if translate_fetch:
        en_titles = [
            _translate_to_english(item.get('title') or '', enabled=True)
            for item in raw_products
            if isinstance(item, dict) and item.get('title')
        ]
        if en_titles:
            _translate_many(en_titles, dest="fr")

    formatted_products = []
    all_param_keys = set()

    for item in raw_products:
        all_param_keys.update(item.keys())
        p_id = item.get('id')
        raw_p_title = item.get('title') or ''
        p_title = _translate_to_english(raw_p_title, enabled=True, fallback=f"Yiwugo Product {p_id}" if p_id else "")
        p_title_french = _translate_to_french(p_title, enabled=translate_fetch) if p_title else ""
        p_price = item.get('sellPrice')
        p_start_num = item.get('startNum')
        p_metric = _normalize_measure_to_english(item.get('metric'))

        images = []
        for img_k in ['picture1', 'picture2', 'picture3', 'picture']:
            val = item.get(img_k)
            if val:
                full_img_url = val if val.startswith('http') else f"https://img1.yiwugou.com/{val}"
                if full_img_url not in images:
                    images.append(full_img_url)

        supplier_info = {
            "shop_id": item.get('shopId'),
            "shop_name": _translate_to_english(item.get('shopName'), enabled=True) if item.get('shopName') else item.get('shopName'),
            "market_info": item.get('marketinfo'),
            "market_address": item.get('marketOrAdress'),
            "booth_no": item.get('boothNo'),
            "factory_address": item.get('factoryAddress')
        }

        formatted_products.append({
            "id": p_id,
            "title": p_title,
            "title_french": p_title_french,
            "goods_code": item.get('goodsCode') or item.get('goodsModel'),
            "sell_price": p_price,
            "min_order_quantity": p_start_num,
            "unit_of_measure": p_metric,
            "category_code": item.get('innertype'),
            "images": images,
            "supplier": supplier_info,
            "metrics": {
                "deal_quantity": item.get('dealQuantity') or item.get('dealQuantitys'),
                "total_sales_count": item.get('sellCounts'),
                "credit_score": item.get('credit')
            },
            "shipping_and_delivery": {
                "delivery_promise_days": item.get('deliveryPromise'),
                "online_order_supported": bool(item.get('onlineOrderFlag') == 1)
            },
            "raw_third_party_parameters": item
        })

    if product_id_filter:
        formatted_products = [p for p in formatted_products if str(p['id']) == str(product_id_filter)]

    api_source = {
        "name": "Apipost Documentation / Yiwugo Open Platform",
        "url": APIPOST_DEFAULT_URL,
        "mode": "Live Gateway" if live_data_fetched else "Documentation Catalog & Examples"
    }
    if live_error:
        api_source["live_error"] = live_error

    return {
        "status": "success",
        "api_source": api_source,
        "pagination": {
            "current_page": page,
            "page_size": page_size,
            "total_products_available": total_found,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_previous": page > 1,
            "count_returned_in_this_response": len(formatted_products)
        },
        "parameters_summary": {
            "total_distinct_parameters_found": len(all_param_keys),
            "all_available_parameter_keys": sorted(list(all_param_keys))
        },
        "query_filters_applied": {
            "page": page,
            "page_size": page_size,
            "search_query": search_query or None,
            "product_id_filter": product_id_filter or None
        },
        "products": formatted_products
    }, 200


@csrf_exempt
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def fetch_third_party_products(request):
    """
    Fetch and list all products directly from the third-party API:
    https://docs.apipost.net/docs/password/46888b7cb873000

    Supports pagination (page / cpage, page_size / pageSize), search (q),
    and filters. Returns structured product data with all detected parameters.
    """
    params = _parse_request_params(request)
    payload, status_code = _fetch_third_party_products_data(params, headers=request.headers)
    return JsonResponse(payload, status=status_code, json_dumps_params={'indent': 2})


@csrf_exempt
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def compare_product_flow(request):
    """
    Compares the third-party product parameters (from https://docs.apipost.net/docs/password/46888b7cb873000)
    directly with the Diaba product flow specifications (models, serializers, required fields).

    Strictly satisfies:
    - Does NOT fetch any product list from the Diaba database.
    - Does NOT modify existing product APIs, models, or business logic.
    - Clearly identifies:
        1. Common parameters (mapped fields)
        2. Missing parameters in Diaba (third-party fields not captured in Diaba)
        3. Extra parameters in Diaba (Diaba required/used fields not provided by third-party)
        4. Field mapping issues (hierarchy, language, media, relational constraints, currency)
        5. Data type differences (CharField vs Int/Float, Booleans, Status codes)
    """
    # 1. Inspect third-party product parameters from documentation (list and detail)
    try:
        doc_data = _fetch_apipost_docs(target_ids=[TARGET_PRODUCT_LIST, TARGET_PRODUCT_DETAIL, TARGET_CATEGORY])
        list_doc = doc_data.get(TARGET_PRODUCT_LIST, {})
        detail_doc = doc_data.get(TARGET_PRODUCT_DETAIL, {})
        category_doc = doc_data.get(TARGET_CATEGORY, {})

        list_example = list_doc.get('example_response', {}).get('data', {})
        prslist = list_example.get('prslist', [])
        sample_list_item = prslist[0] if prslist else {}

        detail_example = detail_doc.get('example_response', {}).get('data', {})
        detail_vo = detail_example.get('detail', {}).get('productDetailVO', {})
        packing_bo = detail_example.get('detail', {}).get('productPackingBo', {}) or {}
        sku_list = detail_example.get('detail', {}).get('productPropertySkuBoList', []) or []
        shop_info = detail_example.get('shopinfo', {}).get('shop', {}) or {}
        cat_list = category_doc.get('example_response', {}).get('data', {}).get('list', [])
        sample_cat = cat_list[0] if cat_list else {}
    except Exception as e:
        # Fallback to predefined schema if external doc network fails
        sample_list_item = {"id": 929740414, "title": "...", "sellPrice": 500, "startNum": 1, "metric": "个"}
        detail_vo = {"id": 969901190, "title": "...", "goodsCode": "123", "sellPrice": 35, "startNumber": 1, "metric": "个"}
        packing_bo = {"length": 10, "width": 10, "height": 10, "shippingWeight": 1}
        sku_list = [{"specificationNameOne": "Color", "specificationNameTwo": "Size", "price": 35, "stock": 1000}]
        shop_info = {"shopName": "Supplier Store"}
        sample_cat = {"id": 29, "type": "汽摩配件", "entype": "Auto & Motorcycle Accessories"}

    # =========================================================================
    # SECTION 1: COMMON / MAPPED PARAMETERS
    # =========================================================================
    common_parameters = [
        {
            "third_party_field": "title (in detail.productDetailVO & prslist)",
            "third_party_type": "String",
            "third_party_sample": detail_vo.get("title") or sample_list_item.get("title"),
            "diaba_model": "ProductDetail",
            "diaba_field": "product_name",
            "diaba_type": "CharField (max_length=255)",
            "mapping_status": "Direct Match",
            "notes": "Primary product name in original source language (Chinese/English)."
        },
        {
            "third_party_field": "goodsCode (in productDetailVO) / goodsModel (prslist)",
            "third_party_type": "String",
            "third_party_sample": detail_vo.get("goodsCode") or "123",
            "diaba_model": "ProductDetail",
            "diaba_field": "product_code",
            "diaba_type": "CharField (max_length=255)",
            "mapping_status": "Direct Match",
            "notes": "Original factory/vendor product model code. Can also be prefixed as YWG_<goodsCode>."
        },
        {
            "third_party_field": "sellPrice (productDetailVO / prslist) or unitprice",
            "third_party_type": "Float / Integer",
            "third_party_sample": detail_vo.get("sellPrice") or sample_list_item.get("sellPrice"),
            "diaba_model": "ProductDetail",
            "diaba_field": "price",
            "diaba_type": "FloatField",
            "mapping_status": "Currency Conversion Required",
            "notes": "Value is in Chinese Yuan (CNY). Needs exchange multiplier to Diaba base currency (USD/XOF)."
        },
        {
            "third_party_field": "startNumber (productDetailVO) / startNum (prslist)",
            "third_party_type": "Integer",
            "third_party_sample": detail_vo.get("startNumber") or sample_list_item.get("startNum"),
            "diaba_model": "ProductDetail",
            "diaba_field": "min_order_quantity",
            "diaba_type": "CharField",
            "mapping_status": "Type Conversion (int -> str)",
            "notes": "Minimum purchase order threshold for wholesale orders."
        },
        {
            "third_party_field": "metric (productDetailVO / prslist)",
            "third_party_type": "String",
            "third_party_sample": detail_vo.get("metric") or sample_list_item.get("metric"),
            "diaba_model": "ProductDetail",
            "diaba_field": "unit_of_measure",
            "diaba_type": "CharField",
            "mapping_status": "Direct Match / Translation",
            "notes": "Unit of measurement (e.g. '个' -> 'pcs', '套' -> 'set', '箱' -> 'carton')."
        },
        {
            "third_party_field": "detaill (productDetailVO)",
            "third_party_type": "HTML String",
            "third_party_sample": (detail_vo.get("detaill") or "<p>HTML Description with Images</p>")[:120] + "...",
            "diaba_model": "ProductDetail",
            "diaba_field": "description",
            "diaba_type": "TextField",
            "mapping_status": "Direct Match",
            "notes": "Rich HTML product details containing embedded description images."
        },
        {
            "third_party_field": "picture, picture1 .. picture3 (productDetailVO / prslist)",
            "third_party_type": "Array / URL Strings",
            "third_party_sample": "https://img1.yiwugou.com/...",
            "diaba_model": "ProductDetail",
            "diaba_field": "product_image_1 to product_image_8",
            "diaba_type": "FileField (Image)",
            "mapping_status": "Download & Storage Required",
            "notes": "Third-party provides remote CDN URLs. Diaba requires downloading and saving into media/product/."
        },
        {
            "third_party_field": "length (productPackingBo)",
            "third_party_type": "Float / Integer",
            "third_party_sample": packing_bo.get("length") or 10,
            "diaba_model": "ProductDetail",
            "diaba_field": "carton_length",
            "diaba_type": "CharField",
            "mapping_status": "Type Conversion (numeric -> str)",
            "notes": "Package carton length in cm."
        },
        {
            "third_party_field": "width (productPackingBo)",
            "third_party_type": "Float / Integer",
            "third_party_sample": packing_bo.get("width") or 10,
            "diaba_model": "ProductDetail",
            "diaba_field": "carton_width",
            "diaba_type": "CharField",
            "mapping_status": "Type Conversion (numeric -> str)",
            "notes": "Package carton width in cm."
        },
        {
            "third_party_field": "height (productPackingBo)",
            "third_party_type": "Float / Integer",
            "third_party_sample": packing_bo.get("height") or 10,
            "diaba_model": "ProductDetail",
            "diaba_field": "carton_height",
            "diaba_type": "CharField",
            "mapping_status": "Type Conversion (numeric -> str)",
            "notes": "Package carton height in cm."
        },
        {
            "third_party_field": "shippingWeight (productPackingBo)",
            "third_party_type": "Float / Integer",
            "third_party_sample": packing_bo.get("shippingWeight") or 1,
            "diaba_model": "ProductDetail",
            "diaba_field": "carton_weight",
            "diaba_type": "CharField",
            "mapping_status": "Type Conversion (numeric -> str)",
            "notes": "Gross shipping package weight in kg."
        },
        {
            "third_party_field": "specificationNameOne (productPropertySkuBoList)",
            "third_party_type": "String",
            "third_party_sample": sku_list[0].get("specificationNameOne") if sku_list else "红色",
            "diaba_model": "ProductModel",
            "diaba_field": "model_name",
            "diaba_type": "CharField",
            "mapping_status": "Relational Split Required",
            "notes": "Primary product variation / style / color name."
        },
        {
            "third_party_field": "specificationNameTwo (productPropertySkuBoList)",
            "third_party_type": "String",
            "third_party_sample": sku_list[0].get("specificationNameTwo") if sku_list else "1000ml",
            "diaba_model": "ProductModelVariant",
            "diaba_field": "name",
            "diaba_type": "CharField",
            "mapping_status": "Relational Split Required",
            "notes": "Secondary product variation / size / sub-variant name."
        },
        {
            "third_party_field": "price (productPropertySkuBoList)",
            "third_party_type": "Float / Integer",
            "third_party_sample": sku_list[0].get("price") if sku_list else 35,
            "diaba_model": "ProductModelVariant",
            "diaba_field": "price",
            "diaba_type": "CharField",
            "mapping_status": "Currency & Type Conversion",
            "notes": "Variant specific unit price."
        },
        {
            "third_party_field": "picture (productPropertySkuBoList)",
            "third_party_type": "URL String",
            "third_party_sample": sku_list[0].get("picture") if sku_list else "http://...",
            "diaba_model": "ProductModelVariant",
            "diaba_field": "image",
            "diaba_type": "FileField",
            "mapping_status": "Download & Storage Required",
            "notes": "Variant thumbnail image."
        },
        {
            "third_party_field": "productExtendList / propertyList (name & value)",
            "third_party_type": "Array of {name, value}",
            "third_party_sample": [{"name": "材质", "value": "304不锈钢"}],
            "diaba_model": "ProductOtherSpecification",
            "diaba_field": "key & value",
            "diaba_type": "CharField",
            "mapping_status": "Direct Match",
            "notes": "Custom technical specifications and product properties."
        },
        {
            "third_party_field": "shop.shopName (shopinfo.shop)",
            "third_party_type": "String",
            "third_party_sample": shop_info.get("shopName") or "王国旺手表",
            "diaba_model": "VendorDetail",
            "diaba_field": "company_name",
            "diaba_type": "CharField",
            "mapping_status": "ForeignKey Lookup / Auto-Create",
            "notes": "Supplier shop name matches or creates a VendorDetail record in Diaba."
        },
        {
            "third_party_field": "entype & type (/open/categorize/product)",
            "third_party_type": "String",
            "third_party_sample": f"{sample_cat.get('entype')} / {sample_cat.get('type')}",
            "diaba_model": "CategoryDetail / SubCategoryDetail",
            "diaba_field": "category (name)",
            "diaba_type": "ForeignKey to CategoryDetail",
            "mapping_status": "Keyword Lookup by English 'entype'",
            "notes": "'entype' (English) maps directly to Diaba CategoryDetail without Chinese translation errors."
        }
    ]

    # =========================================================================
    # SECTION 2: MISSING PARAMETERS IN DIABA (Present in 3rd-party, not in Diaba)
    # =========================================================================
    missing_in_diaba = [
        {
            "third_party_parameter": "dealQuantitys / dealQuantity",
            "data_type": "Integer / String",
            "sample_value": sample_list_item.get("dealQuantitys") or "7397",
            "third_party_purpose": "Historical order transaction count on Yiwugo marketplace.",
            "impact_on_diaba": "Not stored in Diaba ProductDetail. Useful as social proof / popularity ranking if added."
        },
        {
            "third_party_parameter": "sellCounts",
            "data_type": "Integer",
            "sample_value": sample_list_item.get("sellCounts") or 50147,
            "third_party_purpose": "Total historical items sold across all buyer transactions.",
            "impact_on_diaba": "Not currently captured in Diaba product models."
        },
        {
            "third_party_parameter": "onlineOrderFlag",
            "data_type": "Integer (1 or 0)",
            "sample_value": sample_list_item.get("onlineOrderFlag") or 1,
            "third_party_purpose": "Indicates whether the supplier accepts direct online platform checkout.",
            "impact_on_diaba": "Useful for deciding whether an item can be fulfilled automatically or needs manual procurement."
        },
        {
            "third_party_parameter": "deliveryPromise",
            "data_type": "Integer (days/hours)",
            "sample_value": detail_vo.get("deliveryPromise") or 0,
            "third_party_purpose": "Supplier SLA for dispatching goods to the domestic consolidation warehouse.",
            "impact_on_diaba": "Diaba tracks delay_days_air/ship, but not supplier domestic fulfillment commitment."
        },
        {
            "third_party_parameter": "freightTemplateId",
            "data_type": "String / Integer",
            "sample_value": detail_vo.get("freightTemplateId") or "0",
            "third_party_purpose": "Domestic Chinese shipping freight rate matrix ID.",
            "impact_on_diaba": "Not relevant to Diaba's international shipping fee structure."
        },
        {
            "third_party_parameter": "exchangeService",
            "data_type": "Integer / Boolean",
            "sample_value": detail_example.get("exchangeService") or 1,
            "third_party_purpose": "Supplier return & exchange guarantee policy badge.",
            "impact_on_diaba": "Not stored in Diaba."
        },
        {
            "third_party_parameter": "quickRefund",
            "data_type": "Integer / Boolean",
            "sample_value": detail_example.get("quickRefund") or 0,
            "third_party_purpose": "Fast-track buyer refund eligibility indicator.",
            "impact_on_diaba": "Not stored in Diaba."
        },
        {
            "third_party_parameter": "isHasChatRoom",
            "data_type": "Integer / Boolean",
            "sample_value": detail_example.get("isHasChatRoom") or 1,
            "third_party_purpose": "Real-time instant messaging availability with the factory booth.",
            "impact_on_diaba": "Not stored in Diaba."
        },
        {
            "third_party_parameter": "unitConversion",
            "data_type": "Integer",
            "sample_value": detail_example.get("unitConversion") or 1,
            "third_party_purpose": "Packaging packing unit conversion multiplier (e.g. 1 box = 24 pcs).",
            "impact_on_diaba": "Diaba has product_packaging_value, but not an integer conversion factor."
        },
        {
            "third_party_parameter": "marketinfo / boothNo / marketOrAdress",
            "data_type": "String",
            "sample_value": sample_list_item.get("marketinfo") or "义乌国际商贸城二区44门3楼中街18358",
            "third_party_purpose": "Physical booth location inside Yiwu International Trade Mart.",
            "impact_on_diaba": "Stored in Diaba VendorDetail.office_address if vendor is auto-created, but not on ProductDetail."
        },
        {
            "third_party_parameter": "sellType & priceType",
            "data_type": "String / Integer",
            "sample_value": "sellType=1 (in stock), priceType=1 (fixed)",
            "third_party_purpose": "Wholesale pricing type and stock readiness (in-stock vs manufactured on order).",
            "impact_on_diaba": "Diaba currently supports fixed single prices and variant prices, not dynamic price tiers."
        }
    ]

    # =========================================================================
    # SECTION 3: EXTRA PARAMETERS IN DIABA (Required/Used in Diaba, absent in 3rd-party)
    # =========================================================================
    extra_parameters_in_diaba = [
        {
            "diaba_model": "ProductDetail",
            "diaba_field": "product_name_french",
            "diaba_type": "CharField",
            "required_in_diaba": True,
            "why_absent_in_third_party": "Third-party platform is Chinese/English only. Diaba is bilingual (English/French).",
            "ingestion_strategy": "Auto-translate title using Google Translate (googletrans) or AI translation worker."
        },
        {
            "diaba_model": "ProductDetail",
            "diaba_field": "description_french",
            "diaba_type": "TextField",
            "required_in_diaba": True,
            "why_absent_in_third_party": "French description not provided by Chinese suppliers.",
            "ingestion_strategy": "Auto-translate plain text description into French, or copy description as fallback."
        },
        {
            "diaba_model": "ProductDetail",
            "diaba_field": "category_id & subcategory_id",
            "diaba_type": "ForeignKey (integer IDs)",
            "required_in_diaba": True,
            "why_absent_in_third_party": "Third-party API returns external category strings ('entype' / 'type') and internal Yiwugo IDs.",
            "ingestion_strategy": "Query CategoryDetail by name matching 'entype' (e.g. 'Auto & Motorcycle Accessories' -> 'Voiture, Moto, Vélo') or assign default category."
        },
        {
            "diaba_model": "ProductDetail",
            "diaba_field": "vendor_id",
            "diaba_type": "ForeignKey (integer ID)",
            "required_in_diaba": True,
            "why_absent_in_third_party": "Third-party API returns supplier store information as nested JSON strings, not internal Diaba Vendor IDs.",
            "ingestion_strategy": "Lookup VendorDetail by company_name=shopName; if not found, auto-create a new VendorDetail record."
        },
        {
            "diaba_model": "ProductDetail",
            "diaba_field": "country_of_origin_id",
            "diaba_type": "ForeignKey (integer ID)",
            "required_in_diaba": True,
            "why_absent_in_third_party": "External platform products all originate in China, so origin ID is not explicitly given.",
            "ingestion_strategy": "Default to China (Country ID 2 in Diaba database)."
        },
        {
            "diaba_model": "ProductDetail",
            "diaba_field": "shipping_via",
            "diaba_type": "CharField ('By Air', 'By Ship', 'Both')",
            "required_in_diaba": True,
            "why_absent_in_third_party": "Supplier only handles domestic logistics; international transit mode is Diaba's business domain.",
            "ingestion_strategy": "Default to 'By Air' (or 'Both' if package weight > 20kg)."
        },
        {
            "diaba_model": "ProductDetail",
            "diaba_field": "available_country",
            "diaba_type": "ManyToManyField (ProductCountry)",
            "required_in_diaba": True,
            "why_absent_in_third_party": "Diaba specific target markets (Senegal, Ivory Coast, Guinea, France).",
            "ingestion_strategy": "Associate with all active target delivery countries upon product creation."
        },
        {
            "diaba_model": "ProductDetail",
            "diaba_field": "product_verification & status",
            "diaba_type": "CharField",
            "required_in_diaba": True,
            "why_absent_in_third_party": "Diaba administrative lifecycle control flags.",
            "ingestion_strategy": "Set status='Active' (or 'Pending') and product_verification='Verified' (or 'Pending')."
        },
        {
            "diaba_model": "ProductDetail",
            "diaba_field": "delay_days_air, delay_days_ship, delay_days_express",
            "diaba_type": "IntegerField",
            "required_in_diaba": False,
            "why_absent_in_third_party": "Diaba international delivery SLA estimation.",
            "ingestion_strategy": "Populate from default platform delivery settings (e.g. Air: 7, Ship: 35, Express: 4)."
        },
        {
            "diaba_model": "ProductDetail",
            "diaba_field": "product_image_1_vector .. product_image_8_vector",
            "diaba_type": "JSONField (512-dim CLIP embeddings)",
            "required_in_diaba": False,
            "why_absent_in_third_party": "Proprietary AI visual search vector embeddings for Diaba image matching.",
            "ingestion_strategy": "Generate asynchronously via background worker after image download."
        }
    ]

    # =========================================================================
    # SECTION 4: FIELD MAPPING ISSUES (Architectural / Structural Gaps)
    # =========================================================================
    field_mapping_issues = [
        {
            "issue_title": "Product Model & Variant Hierarchy (Flat SKU vs 2-Tier Relational)",
            "severity": "CRITICAL",
            "problem": "Third-party provides a flat SKU array (productPropertySkuBoList) combining Color (specificationNameOne) and Size (specificationNameTwo). Diaba requires a 2-tier relational database structure: ProductDetail -> ProductModel -> ProductModelVariant.",
            "solution": "Group SKUs by specificationNameOne to create ProductModel instances, then create ProductModelVariant children for each specificationNameTwo."
        },
        {
            "issue_title": "Bilingual Requirement (French Translation Missing)",
            "severity": "CRITICAL",
            "problem": "Diaba's web and mobile apps require bilingual content for West African and Francophone markets (product_name_french, description_french, model_name_french, name_french). Third-party API only provides Chinese and English.",
            "solution": "Integrate an automated translation step (e.g. googletrans library or DeepL / Google Cloud Translation API) during the import pipeline."
        },
        {
            "issue_title": "Foreign Key Relational Integrity",
            "severity": "CRITICAL",
            "problem": "Diaba models enforce strict ForeignKey constraints (category_id, subcategory_id, vendor_id, country_of_origin_id). Third-party API returns loose strings and external IDs.",
            "solution": "Import script must resolve or auto-provision corresponding relational records prior to inserting ProductDetail."
        },
        {
            "issue_title": "Remote CDN URLs vs Local Django FileField Storage",
            "severity": "HIGH",
            "problem": "Third-party returns remote CDN image paths (img1.yiwugou.com/...). Diaba models use Django FileField, which expects files stored in the local media directory (/media/product/).",
            "solution": "Download images via HTTP GET (requests.get) and wrap the buffer into Django ContentFile(buffer, name='...') during import."
        },
        {
            "issue_title": "Currency Discrepancy (CNY vs USD / XOF)",
            "severity": "HIGH",
            "problem": "Third-party API quotes all prices in Chinese Yuan (CNY). Diaba operates in international currencies (USD, XOF, EUR).",
            "solution": "Apply a configurable currency conversion rate and wholesale markup margin before saving to ProductDetail.price."
        }
    ]

    # =========================================================================
    # SECTION 5: DATA TYPE DIFFERENCES
    # =========================================================================
    data_type_differences = [
        {
            "parameter": "carton_length, carton_width, carton_height, carton_weight",
            "third_party_type": "Integer / Float (e.g. 10, 1.5)",
            "diaba_type": "CharField (string in database)",
            "conversion_handling": "Convert numeric values to string using str(val) before saving to Diaba."
        },
        {
            "parameter": "price",
            "third_party_type": "Integer / Float (e.g. 35, 500)",
            "diaba_type": "ProductDetail: FloatField | ProductModelVariant: CharField",
            "conversion_handling": "Save as float in ProductDetail.price; save as str(price) in ProductModelVariant.price."
        },
        {
            "parameter": "min_order_quantity",
            "third_party_type": "Integer (e.g. startNum: 1)",
            "diaba_type": "CharField",
            "conversion_handling": "Convert integer to str(val)."
        },
        {
            "parameter": "onlineOrderFlag vs is_inquiry / is_deleted",
            "third_party_type": "Integer (1 or 0)",
            "diaba_type": "BooleanField (True or False)",
            "conversion_handling": "Convert 1 -> True, 0 -> False."
        },
        {
            "parameter": "status",
            "third_party_type": "Integer / Code (e.g. 1, 0, sellflag)",
            "diaba_type": "CharField ('Active', 'Pending', 'Deactive')",
            "conversion_handling": "Map 1 -> 'Active', 0 -> 'Pending'."
        }
    ]

    # =========================================================================
    # SUMMARY METRICS (NO DB QUERY PERFORMED)
    # =========================================================================
    summary = {
        "comparison_method": "Schema & Flow Analysis (No DB product query performed)",
        "third_party_source": APIPOST_DEFAULT_URL,
        "metrics": {
            "common_parameters_count": len(common_parameters),
            "missing_in_diaba_count": len(missing_in_diaba),
            "extra_in_diaba_count": len(extra_parameters_in_diaba),
            "field_mapping_issues_count": len(field_mapping_issues),
            "data_type_differences_count": len(data_type_differences)
        },
        "integration_feasibility": "High. All essential catalog fields (title, price, dimensions, weight, images, variants, vendor) have direct or convertible mappings."
    }

    return JsonResponse({
        "status": "success",
        "title": "Third-Party API vs Diaba Product Flow Parameter Comparison",
        "summary": summary,
        "1_common_parameters": common_parameters,
        "2_missing_parameters_in_diaba": missing_in_diaba,
        "3_extra_parameters_in_diaba": extra_parameters_in_diaba,
        "4_field_mapping_issues": field_mapping_issues,
        "5_data_type_differences": data_type_differences,
        "6_actionable_import_pipeline_steps": [
            "Step 1: Ingest product list (/open/cn_product/list) or product detail (/open/cn_product/detail).",
            "Step 2: Resolve or create VendorDetail using shopinfo.shop data.",
            "Step 3: Resolve CategoryDetail using English category 'entype' (/open/categorize/product).",
            "Step 4: Translate title and description to French for bilingual compliance.",
            "Step 5: Apply CNY -> USD/XOF currency conversion to price.",
            "Step 6: Download remote images into local FileFields (product_image_1..8).",
            "Step 7: Insert ProductDetail record with default country_of_origin=2 (China) and shipping_via='By Air'.",
            "Step 8: Split flat SKU array into ProductModel (Color) and ProductModelVariant (Size/SKU).",
            "Step 9: Insert technical specifications into ProductOtherSpecification.",
            "Step 10: Link product to target delivery countries in available_country."
        ]
    }, status=200, json_dumps_params={'indent': 2})


def _convert_cny_to_usd(amount, rate=YIWUGO_CNY_TO_USD_RATE):
    """Convert a CNY amount to USD using the configured rate (default: 7 CNY = 1 USD)."""
    if amount is None or str(amount).strip() in ["", "null", "None"]:
        return 0.0
    try:
        val = float(str(amount).replace(",", "").strip())
        if val < 0:
            val = 0.0
        return round(val / float(rate), 2)
    except (ValueError, TypeError, ZeroDivisionError):
        return 0.0


_CJK_RE = re.compile(r"[\u4e00-\u9fff\u3400-\u4dbf\uf900-\ufaff]+")
_HTML_TAG_RE = re.compile(r"<[^>]+>")
_TRANSLATION_CACHE = {}
_TRANSLATION_CACHE_LOCK = threading.Lock()

_YIWUGO_UNIT_MAP = {
    "公斤": "kg",
    "千克": "kg",
    "kg": "kg",
    "kgs": "kg",
    "kilogram": "kg",
    "kilograms": "kg",
    "斤": "kg",
    "克": "grams",
    "g": "grams",
    "gram": "grams",
    "grams": "grams",
    "吨": "tons",
    "t": "tons",
    "ton": "tons",
    "tons": "tons",
    "升": "liters",
    "公升": "liters",
    "l": "liters",
    "liter": "liters",
    "liters": "liters",
    "litre": "liters",
    "litres": "liters",
    "毫升": "ml",
    "ml": "ml",
    "milliliter": "ml",
    "milliliters": "ml",
    "米": "meters",
    "公尺": "meters",
    "m": "meters",
    "meter": "meters",
    "meters": "meters",
    "metre": "meters",
    "metres": "meters",
    "厘米": "cm",
    "公分": "cm",
    "cm": "cm",
    "毫米": "mm",
    "mm": "mm",
    "箱": "carton",
    "纸箱": "carton",
    "ctn": "carton",
    "carton": "carton",
    "cartons": "carton",
    "case": "carton",
    "cases": "carton",
    "打": "douzaine",
    "dozen": "douzaine",
    "dozens": "douzaine",
    "doz": "douzaine",
    "douzaine": "douzaine",
    "半打": "1/2douzaine",
    "halfdozen": "1/2douzaine",
    "half dozen": "1/2douzaine",
    "1/2douzaine": "1/2douzaine",
    "1/2 douzaine": "1/2douzaine",
    "1/2 dozen": "1/2douzaine",
    "双": "pair",
    "对": "pair",
    "pair": "pair",
    "pairs": "pair",
    "套": "set",
    "组": "set",
    "副": "set",
    "set": "set",
    "sets": "set",
    "盒": "box",
    "box": "box",
    "boxes": "box",
    "袋": "pack",
    "包": "pack",
    "bag": "pack",
    "bags": "pack",
    "pack": "pack",
    "packs": "pack",
    "packet": "pack",
    "packets": "pack",
    "瓶": "bottle",
    "bottle": "bottle",
    "bottles": "bottle",
    "罐": "can",
    "can": "can",
    "cans": "can",
    "jar": "can",
    "jars": "can",
    "卷": "roll",
    "筒": "roll",
    "roll": "roll",
    "rolls": "roll",
    "个": "pcs",
    "件": "pcs",
    "只": "pcs",
    "支": "pcs",
    "条": "pcs",
    "把": "pcs",
    "张": "pcs",
    "块": "pcs",
    "颗": "pcs",
    "粒": "pcs",
    "片": "pcs",
    "根": "pcs",
    "台": "pcs",
    "部": "pcs",
    "款": "pcs",
    "份": "pcs",
    "朵": "pcs",
    "枝": "pcs",
    "枚": "pcs",
    "扇": "pcs",
    "面": "pcs",
    "盏": "pcs",
    "辆": "pcs",
    "架": "pcs",
    "本": "pcs",
    "册": "pcs",
    "pc": "pcs",
    "pcs": "pcs",
    "piece": "pcs",
    "pieces": "pcs",
    "unit": "pcs",
    "units": "pcs",
    "each": "pcs",
    "ea": "pcs",
}


def _contains_cjk(text):
    """Return True if text contains any CJK/Chinese characters."""
    return bool(text and _CJK_RE.search(str(text)))


def _strip_cjk(text):
    """Remove CJK characters and collapse leftover whitespace cleanly."""
    if text is None:
        return ""
    cleaned = _CJK_RE.sub(" ", str(text))
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" ,;:/-|")
    return cleaned


def _translate_many(texts, dest="en"):
    """Translate a sequence of distinct texts concurrently via Google Translate, caching results."""
    unique_inputs = []
    seen = set()
    for raw in texts or []:
        if raw is None:
            continue
        clean = str(raw).strip()
        if not clean:
            continue
        snippet = clean[:4500]
        if dest == "en" and not _contains_cjk(snippet):
            continue
        key = (snippet, dest)
        if key in seen:
            continue
        seen.add(key)
        with _TRANSLATION_CACHE_LOCK:
            if key in _TRANSLATION_CACHE:
                continue
        unique_inputs.append(snippet)

    if unique_inputs:
        async def _async_translate_batch(batch_items, target_lang):
            async with Translator() as translator:
                coros = [translator.translate(s, dest=target_lang) for s in batch_items]
                return await asyncio.gather(*coros, return_exceptions=True)

        def _run_batch(batch_items):
            try:
                asyncio.get_running_loop()
                with ThreadPoolExecutor(max_workers=1) as pool:
                    return pool.submit(asyncio.run, _async_translate_batch(batch_items, dest)).result(timeout=25)
            except RuntimeError:
                return asyncio.run(_async_translate_batch(batch_items, dest))

        for start in range(0, len(unique_inputs), 25):
            chunk = unique_inputs[start:start + 25]
            try:
                results = _run_batch(chunk)
            except Exception:
                results = []
            with _TRANSLATION_CACHE_LOCK:
                if len(_TRANSLATION_CACHE) > 20000:
                    _TRANSLATION_CACHE.clear()
                for snippet, res in zip(chunk, results):
                    translated = getattr(res, "text", None) if not isinstance(res, Exception) else None
                    if translated:
                        _TRANSLATION_CACHE[(snippet, dest)] = translated.strip()

    output = {}
    for raw in texts or []:
        if raw is None:
            continue
        clean = str(raw).strip()
        if not clean:
            continue
        snippet = clean[:4500]
        if dest == "en" and not _contains_cjk(snippet):
            output[clean] = clean
        else:
            with _TRANSLATION_CACHE_LOCK:
                output[clean] = _TRANSLATION_CACHE.get((snippet, dest), clean)
    return output


def _translate_to_english(text, enabled=True, fallback=""):
    """Translate Chinese/CJK text to English without leaving Chinese words."""
    if text is None:
        return fallback
    clean = str(text).strip()
    if not clean:
        return fallback
    if not _contains_cjk(clean):
        return clean

    translated = clean
    if enabled:
        translated = _translate_many([clean], dest="en").get(clean, clean)

    if _contains_cjk(translated):
        stripped = _strip_cjk(translated)
        return stripped or fallback
    return translated or fallback


def _translate_to_french(text, enabled=True):
    """Translate text to French via googletrans (cached, supports sync/async), falling back on error."""
    if text is None:
        return ""
    clean = str(text).strip()
    if not clean or not enabled:
        return clean

    translated = _translate_many([clean], dest="fr").get(clean, clean)
    if _contains_cjk(translated):
        stripped = _strip_cjk(translated)
        if stripped:
            return stripped
    return translated or clean


def _normalize_measure_to_english(raw_measure, fallback="pcs"):
    """Normalize a Yiwugo measure/unit (no Chinese) to English or Diaba standard unit."""
    if raw_measure is None:
        return fallback
    raw_str = str(raw_measure).strip()
    if not raw_str or raw_str.lower() in ["null", "none"]:
        return fallback

    compact = re.sub(r"[\s()（）]+", "", raw_str).lower().strip("/\\.,;:")
    if compact in _YIWUGO_UNIT_MAP:
        return _YIWUGO_UNIT_MAP[compact]

    lowered = raw_str.lower().strip("/\\.,;: ")
    if lowered in _YIWUGO_UNIT_MAP:
        return _YIWUGO_UNIT_MAP[lowered]

    # Strip leading quantities like "1/个" or "12双"
    alpha_part = re.sub(r"^[\d./\-\s]+", "", lowered).strip()
    if alpha_part in _YIWUGO_UNIT_MAP:
        return _YIWUGO_UNIT_MAP[alpha_part]

    if _contains_cjk(raw_str):
        translated = _translate_to_english(raw_str, enabled=True, fallback="").lower()
        translated = re.sub(r"[^a-z0-9/ ]+", " ", translated).strip()
        if translated in _YIWUGO_UNIT_MAP:
            return _YIWUGO_UNIT_MAP[translated]
        no_space = translated.replace(" ", "")
        if no_space in _YIWUGO_UNIT_MAP:
            return _YIWUGO_UNIT_MAP[no_space]
        # Handle plural/singular or leading "a "/"one " from machine translation (e.g. "a pair")
        tokens = [t for t in translated.split() if t not in {"a", "an", "one", "per", "by"}]
        if tokens:
            candidate = " ".join(tokens)
            if candidate in _YIWUGO_UNIT_MAP:
                return _YIWUGO_UNIT_MAP[candidate]
            return tokens[-1][:30]
        return fallback

    clean_ascii = _strip_cjk(lowered)
    return clean_ascii[:30] if clean_ascii else fallback


def _clean_description_text(raw_desc, fallback_title=""):
    """Extract readable text from Yiwugo description HTML/text cleanly."""
    if raw_desc is None:
        return fallback_title
    raw_str = str(raw_desc).strip()
    if not raw_str or raw_str.lower() in ["null", "none"]:
        return fallback_title
    if "<" in raw_str and ">" in raw_str:
        stripped = html.unescape(_HTML_TAG_RE.sub(" ", raw_str))
        stripped = re.sub(r"\s+", " ", stripped).strip()
        return stripped or fallback_title
    return re.sub(r"\s+", " ", html.unescape(raw_str)).strip() or fallback_title


def _normalize_yiwugo_image_url(url):
    if not url or str(url).strip() in ["", "null", "None"]:
        return None
    val = str(url).strip()
    return val if val.startswith("http") else f"https://img1.yiwugou.com/{val.lstrip('/')}"


def _download_image_as_content_file(url, prefix="ywg"):
    """Download a remote image URL into a Django ContentFile with a validated extension."""
    full_url = _normalize_yiwugo_image_url(url)
    if not full_url:
        return None
    try:
        resp = requests.get(full_url, timeout=15, verify=False)
        if resp.status_code != 200 or not resp.content:
            return None
        ext = os.path.splitext(full_url.split("?")[0])[1].lower()
        if ext not in [".jpg", ".jpeg", ".png", ".webp"]:
            ext = ".jpg"
        return ContentFile(resp.content, name=f"{prefix}_{uuid.uuid4().hex[:10]}{ext}")
    except Exception:
        return None


def _resolve_category_and_subcategory(category_hint=None, category_id=None, subcategory_id=None):
    """Resolve Diaba CategoryDetail and SubCategoryDetail with sensible fallbacks."""
    category_obj = None
    subcategory_obj = None

    if category_id:
        category_obj = models.CategoryDetail.objects.filter(id=category_id).first()
    if subcategory_id:
        subcategory_obj = models.SubCategoryDetail.objects.filter(id=subcategory_id).first()
        if subcategory_obj and not category_obj:
            category_obj = subcategory_obj.category

    if not category_obj and category_hint:
        hint = str(category_hint).strip()
        category_obj = models.CategoryDetail.objects.filter(
            Q(category__iexact=hint) | Q(category_french__iexact=hint)
        ).first()
        if not category_obj:
            category_obj = models.CategoryDetail.objects.filter(
                Q(category__icontains=hint) | Q(category_french__icontains=hint)
            ).first()

    if not category_obj:
        category_obj = (
            models.CategoryDetail.objects.filter(status="Active").first()
            or models.CategoryDetail.objects.first()
        )

    if not subcategory_obj and category_obj:
        subcategory_obj = (
            models.SubCategoryDetail.objects.filter(category=category_obj, status="Active").first()
            or models.SubCategoryDetail.objects.filter(category=category_obj).first()
        )
    if not subcategory_obj:
        subcategory_obj = (
            models.SubCategoryDetail.objects.filter(status="Active").first()
            or models.SubCategoryDetail.objects.first()
        )
        if subcategory_obj and not category_obj:
            category_obj = subcategory_obj.category

    return category_obj, subcategory_obj


def _resolve_or_create_vendor(shop_info=None, vendor_id=None, category_obj=None, subcategory_obj=None):
    """Look up an existing VendorDetail or create one for the Yiwugo shop."""
    if vendor_id:
        vendor = models.VendorDetail.objects.filter(id=vendor_id).first()
        if vendor:
            return vendor

    shop_info = shop_info or {}
    raw_shop_name = (shop_info.get("shopName") or shop_info.get("shop_name") or "").strip()
    shop_name = _translate_to_english(raw_shop_name, enabled=True, fallback="Yiwugo Supplier") if raw_shop_name else ""

    if shop_name:
        vendor = models.VendorDetail.objects.filter(
            Q(company_name__iexact=shop_name)
            | Q(vendor_name__iexact=shop_name)
            | Q(company_name__iexact=raw_shop_name)
        ).first()
        if vendor:
            updated_fields = []
            if _contains_cjk(vendor.company_name):
                vendor.company_name = shop_name[:200]
                updated_fields.append("company_name")
            if _contains_cjk(vendor.vendor_name):
                vendor.vendor_name = _translate_to_english(vendor.vendor_name, enabled=True, fallback=shop_name)[:200]
                updated_fields.append("vendor_name")
            if _contains_cjk(vendor.office_address):
                vendor.office_address = _translate_to_english(vendor.office_address, enabled=True)[:500]
                updated_fields.append("office_address")
            if updated_fields:
                vendor.save(update_fields=updated_fields)
            return vendor

        raw_contacter = (shop_info.get("contacter") or "").strip()
        vendor_contact = _translate_to_english(raw_contacter, enabled=True, fallback=shop_name) if raw_contacter else shop_name
        raw_address = (
            shop_info.get("factoryAddress")
            or shop_info.get("factory_address")
            or shop_info.get("marketInfo")
            or shop_info.get("market_info")
            or shop_info.get("marketOrAdress")
            or shop_info.get("market_address")
            or ""
        )
        office_address = _translate_to_english(raw_address, enabled=True) if raw_address else ""

        return models.VendorDetail.objects.create(
            category=category_obj,
            subcategory=subcategory_obj,
            company_name=shop_name[:200],
            vendor_name=vendor_contact[:200],
            office_address=office_address[:500],
            phone_number=(shop_info.get("mobile") or shop_info.get("telephone") or "")[:200],
            email=(shop_info.get("email") or "")[:200] or None,
            country="China",
            is_verify="Approved",
            status="Active",
        )

    default_vendor = (
        models.VendorDetail.objects.filter(company_name__iexact="Yiwugo Supplier").first()
        or models.VendorDetail.objects.first()
    )
    if default_vendor:
        return default_vendor

    return models.VendorDetail.objects.create(
        category=category_obj,
        subcategory=subcategory_obj,
        company_name="Yiwugo Supplier",
        vendor_name="Yiwugo Supplier",
        country="China",
        is_verify="Approved",
        status="Active",
    )


def _fetch_yiwugo_product_detail(product_id, access_token=None, is_oauth_token=False):
    """Fetch Yiwugo product detail payload via live API when an access_token is supplied."""
    if not access_token or not product_id:
        return None
    for attempt in range(2 if is_oauth_token else 1):
        try:
            resp = requests.get(
                "https://open.yiwugo.com/open/cn_product/detail",
                params={"access_token": access_token, "productId": product_id},
                timeout=15,
                verify=False,
            )
            resp_json = resp.json()
            if resp_json.get("code") == 0:
                return resp_json.get("data") or {}
            if resp_json.get("code") == 501 and is_oauth_token and attempt == 0:
                refreshed, _ = _get_yiwugo_access_token(force_refresh=True)
                if refreshed:
                    access_token = refreshed
                    continue
            break
        except Exception:
            break
    return None


def _extract_dimensions_and_quantities(detail_data, detail_vo, packing_bo, extend_list, sku_list, item, base):
    """Extract packaging dimensions, weights, and min/max/available quantities from Yiwugo payloads."""
    def _clean_num_str(val):
        if val is None:
            return None
        s = str(val).strip()
        if not s or s.lower() in ["null", "none", "0", "0.0"]:
            return None
        return s

    carton_length = _clean_num_str(packing_bo.get("length"))
    carton_width = _clean_num_str(packing_bo.get("width"))
    carton_height = _clean_num_str(packing_bo.get("height"))
    carton_weight = _clean_num_str(packing_bo.get("shippingWeight"))
    packing_qty = _clean_num_str(packing_bo.get("packingQuantity"))

    length = _clean_num_str(item.get("length")) or carton_length
    width = _clean_num_str(item.get("width")) or carton_width
    height = _clean_num_str(item.get("height")) or carton_height
    weight = _clean_num_str(item.get("weight")) or _clean_num_str(detail_vo.get("weightetc")) or carton_weight

    # Fallback: parse dimensions/weight from productExtendList if productPackingBo is empty
    dim_re = re.compile(r"(\d+(?:\.\d+)?)\s*[*xX×]\s*(\d+(?:\.\d+)?)(?:\s*[*xX×]\s*(\d+(?:\.\d+)?))?")
    num_re = re.compile(r"(\d+(?:\.\d+)?)")
    for spec in extend_list or []:
        k = str(spec.get("name") or spec.get("pvalue") or "").strip()
        v = str(spec.get("value") or spec.get("cvalue") or "").strip()
        if not k or not v:
            continue
        k_lower = k.lower()
        is_carton_key = any(w in k_lower for w in ["箱", "carton", "外箱", "包装"])
        if any(w in k_lower for w in ["重量", "毛重", "净重", "克重", "单重", "weight"]):
            m = num_re.search(v)
            if m:
                if not weight:
                    weight = m.group(1)
                if not carton_weight and is_carton_key:
                    carton_weight = m.group(1)
        elif any(w in k_lower for w in ["尺寸", "规格", "size", "dimension"]):
            m = dim_re.search(v)
            if m:
                d1, d2, d3 = m.group(1), m.group(2), m.group(3)
                if not length:
                    length = d1
                if not width:
                    width = d2
                if d3 and not height:
                    height = d3
                if is_carton_key:
                    carton_length = carton_length or d1
                    carton_width = carton_width or d2
                    if d3:
                        carton_height = carton_height or d3
        elif any(w in k_lower for w in ["长度", "length"]) or k == "长":
            m = num_re.search(v)
            if m and not length:
                length = m.group(1)
        elif any(w in k_lower for w in ["宽度", "width"]) or k == "宽":
            m = num_re.search(v)
            if m and not width:
                width = m.group(1)
        elif any(w in k_lower for w in ["高度", "height"]) or k == "高":
            m = num_re.search(v)
            if m and not height:
                height = m.group(1)

    if not carton_weight and weight:
        carton_weight = weight

    min_order_qty = (
        detail_vo.get("startNumber")
        or detail_data.get("smallnum")
        or item.get("min_order_quantity")
        or base.get("startNum")
        or 1
    )

    sku_stock_total = 0
    for sku in sku_list or []:
        stock_val = sku.get("stock")
        if stock_val not in [None, "", "null"]:
            try:
                sku_stock_total += max(0, int(float(str(stock_val))))
            except (ValueError, TypeError):
                pass

    sale_num = _clean_num_str(detail_vo.get("saleNumber"))
    if sale_num:
        m = num_re.search(sale_num)
        sale_num = m.group(1) if m else None

    available_qty = str(sku_stock_total) if sku_stock_total > 0 else sale_num
    max_order_qty = (
        _clean_num_str(item.get("max_order_quantity"))
        or _clean_num_str(detail_vo.get("maxNumber"))
        or available_qty
    )

    return {
        "length": length,
        "width": width,
        "height": height,
        "weight": weight,
        "carton_length": carton_length,
        "carton_width": carton_width,
        "carton_height": carton_height,
        "carton_weight": carton_weight,
        "packing_quantity": packing_qty,
        "min_order_quantity": str(min_order_qty),
        "max_order_quantity": str(max_order_qty) if max_order_qty else None,
        "available_quantity": str(available_qty) if available_qty else None,
    }


def _extract_product_payload(item, detail_data=None):
    """Normalize either a raw Yiwugo item or a formatted item into a consistent dict."""
    raw = item.get("raw_third_party_parameters") if isinstance(item, dict) else None
    base = raw if isinstance(raw, dict) else (item if isinstance(item, dict) else {})

    if not detail_data and isinstance(item, dict):
        if item.get("detail_data"):
            detail_data = item.get("detail_data")
        elif "detail" in item or "shopinfo" in item:
            detail_data = item
    detail_data = detail_data or {}
    detail_section = detail_data.get("detail") or {}
    detail_vo = detail_section.get("productDetailVO") or item.get("productDetailVO") or {}
    packing_bo = detail_section.get("productPackingBo") or item.get("productPackingBo") or {}
    sku_list = detail_section.get("productPropertySkuBoList") or item.get("productPropertySkuBoList") or []
    pic_list = detail_section.get("sdiProductsPicList") or []
    extend_list = detail_section.get("productExtendList") or detail_data.get("propertyList") or []
    shop_info = (detail_data.get("shopinfo") or {}).get("shop") or item.get("supplier") or {}
    if not shop_info and (base.get("shopName") or base.get("shopId")):
        shop_info = {
            "shopName": base.get("shopName"),
            "marketInfo": base.get("marketinfo"),
            "marketOrAdress": base.get("marketOrAdress"),
            "factoryAddress": base.get("factoryAddress"),
        }

    source_id = detail_vo.get("id") or item.get("id") or base.get("id")
    raw_title = (detail_vo.get("title") or item.get("title") or base.get("title") or "").strip()
    title = _translate_to_english(
        raw_title,
        enabled=True,
        fallback=f"Yiwugo Product {source_id}" if source_id else "",
    )
    goods_code = (
        detail_vo.get("goodsCode")
        or item.get("goods_code")
        or base.get("goodsCode")
        or base.get("goodsModel")
        or ""
    )
    raw_price_cny = (
        detail_vo.get("sellPrice")
        if detail_vo.get("sellPrice") not in [None, "", "null"]
        else detail_data.get("unitprice")
        if detail_data.get("unitprice") not in [None, "", "null"]
        else item.get("sell_price")
        if item.get("sell_price") not in [None, "", "null"]
        else base.get("sellPrice")
    )
    min_order_qty = (
        detail_vo.get("startNumber")
        or detail_data.get("smallnum")
        or item.get("min_order_quantity")
        or base.get("startNum")
        or 1
    )
    raw_unit_of_measure = (
        detail_vo.get("metric")
        or item.get("unit_of_measure")
        or base.get("metric")
        or "pcs"
    )
    unit_of_measure = _normalize_measure_to_english(raw_unit_of_measure, fallback="pcs")
    raw_description = detail_vo.get("detaill") or item.get("description") or base.get("detaill") or ""
    cleaned_raw_desc = _clean_description_text(raw_description, fallback_title="")
    if not cleaned_raw_desc or cleaned_raw_desc == raw_title:
        description = title
    else:
        description = _translate_to_english(cleaned_raw_desc, enabled=True, fallback=title)

    image_urls = []
    for url in (item.get("images") or []):
        norm = _normalize_yiwugo_image_url(url)
        if norm and norm not in image_urls:
            image_urls.append(norm)
    for src in (detail_vo, base):
        for k in ["picture", "picture1", "picture2", "picture3"]:
            norm = _normalize_yiwugo_image_url(src.get(k))
            if norm and norm not in image_urls:
                image_urls.append(norm)
    for pic in pic_list:
        for k in ["picture", "picture1", "picture2", "picture3"]:
            norm = _normalize_yiwugo_image_url(pic.get(k))
            if norm and norm not in image_urls:
                image_urls.append(norm)

    dims_and_qty = _extract_dimensions_and_quantities(
        detail_data=detail_data,
        detail_vo=detail_vo,
        packing_bo=packing_bo,
        extend_list=extend_list,
        sku_list=sku_list,
        item=item,
        base=base,
    )

    return {
        "source_id": source_id,
        "title": title,
        "goods_code": str(goods_code).strip(),
        "raw_price_cny": raw_price_cny,
        "min_order_quantity": dims_and_qty["min_order_quantity"],
        "max_order_quantity": dims_and_qty["max_order_quantity"],
        "available_quantity": dims_and_qty["available_quantity"],
        "length": dims_and_qty["length"],
        "width": dims_and_qty["width"],
        "height": dims_and_qty["height"],
        "weight": dims_and_qty["weight"],
        "carton_length": dims_and_qty["carton_length"],
        "carton_width": dims_and_qty["carton_width"],
        "carton_height": dims_and_qty["carton_height"],
        "carton_weight": dims_and_qty["carton_weight"],
        "packing_quantity": dims_and_qty["packing_quantity"],
        "unit_of_measure": str(unit_of_measure).strip() or "pcs",
        "description": description,
        "image_urls": image_urls[:8],
        "packing_bo": packing_bo,
        "sku_list": sku_list,
        "extend_list": extend_list,
        "shop_info": shop_info,
        "category_hint": item.get("category_name") or item.get("entype") or detail_vo.get("innertype") or base.get("innertype"),
        "category_id": item.get("category_id"),
        "subcategory_id": item.get("subcategory_id"),
    }


def _import_single_yuwi_go_product(
    normalized,
    cny_rate=YIWUGO_CNY_TO_USD_RATE,
    default_category_id=None,
    default_subcategory_id=None,
    default_vendor_id=None,
    available_country_ids=None,
    translate_enabled=True,
    download_images=True,
):
    """Create a ProductDetail (status='yuwi_go', product_added_from='yuwi_go') and its children."""
    product_name = normalized["title"]
    category_obj, subcategory_obj = _resolve_category_and_subcategory(
        category_hint=normalized.get("category_hint"),
        category_id=normalized.get("category_id") or default_category_id,
        subcategory_id=normalized.get("subcategory_id") or default_subcategory_id,
    )
    vendor_obj = _resolve_or_create_vendor(
        shop_info=normalized.get("shop_info"),
        vendor_id=default_vendor_id,
        category_obj=category_obj,
        subcategory_obj=subcategory_obj,
    )

    country_obj = (
        models.Country.objects.filter(id=2).first()
        or models.Country.objects.filter(country_name__icontains="China").first()
        or models.Country.objects.first()
    )
    product_type_obj = (
        models.ProductType.objects.filter(product_type__iexact="Normal").first()
        or models.ProductType.objects.first()
    )
    packaging_obj = (
        models.ProductPackagingBy.objects.filter(product_packaging__iexact="Carton").first()
        or models.ProductPackagingBy.objects.first()
    )

    if normalized["goods_code"]:
        product_code = f"YWG_{normalized['goods_code']}"
    elif normalized["source_id"]:
        product_code = f"YWG_{normalized['source_id']}"
    else:
        cat_code = (category_obj.category if category_obj and category_obj.category else "YWG")[:3].upper()
        sub_code = (subcategory_obj.subcategory if subcategory_obj and subcategory_obj.subcategory else "PRO")[:3].upper()
        product_code = f"{cat_code}_{sub_code}_{random.randint(1000, 9999)}"

    price_usd = _convert_cny_to_usd(normalized["raw_price_cny"], cny_rate)

    extend_list = normalized.get("extend_list") or []
    sku_list = normalized.get("sku_list") or []

    # Warm English translations concurrently for any remaining CJK in specs/SKUs
    cjk_inputs = []
    for spec in extend_list:
        for s_val in (spec.get("name") or spec.get("pvalue"), spec.get("value") or spec.get("cvalue")):
            if _contains_cjk(s_val):
                cjk_inputs.append(str(s_val).strip())
    for sku in sku_list:
        for s_val in (sku.get("specificationNameOne"), sku.get("specificationNameTwo")):
            if _contains_cjk(s_val):
                cjk_inputs.append(str(s_val).strip())
    if cjk_inputs:
        _translate_many(cjk_inputs, dest="en")

    translated_specs = []
    for spec in extend_list:
        raw_k = (spec.get("name") or spec.get("pvalue") or "").strip()
        raw_v = (spec.get("value") or spec.get("cvalue") or "").strip()
        key = _translate_to_english(raw_k, enabled=True) if raw_k else ""
        val = _translate_to_english(raw_v, enabled=True) if raw_v else ""
        if key or val:
            translated_specs.append((key, val))

    grouped_skus = {}
    for sku in sku_list:
        raw_model_key = (sku.get("specificationNameOne") or "").strip()
        model_key = _translate_to_english(raw_model_key, enabled=True, fallback=product_name) if raw_model_key else product_name
        raw_variant_name = (sku.get("specificationNameTwo") or "").strip()
        variant_name = _translate_to_english(raw_variant_name, enabled=True, fallback=model_key) if raw_variant_name else model_key
        grouped_skus.setdefault(model_key, []).append((variant_name, sku))

    if translate_enabled:
        fr_inputs = [product_name, normalized["description"]]
        for k, v in translated_specs:
            fr_inputs.extend([k, v])
        for m_name, sku_pairs in grouped_skus.items():
            fr_inputs.append(m_name)
            for v_name, _ in sku_pairs:
                fr_inputs.append(v_name)
        _translate_many(fr_inputs, dest="fr")

    product_name_french = _translate_to_french(product_name, enabled=translate_enabled)
    description_french = _translate_to_french(normalized["description"], enabled=translate_enabled)

    packing = normalized.get("packing_bo") or {}
    carton_length = normalized.get("carton_length") or (str(packing.get("length")) if packing.get("length") not in [None, ""] else None)
    carton_width = normalized.get("carton_width") or (str(packing.get("width")) if packing.get("width") not in [None, ""] else None)
    carton_height = normalized.get("carton_height") or (str(packing.get("height")) if packing.get("height") not in [None, ""] else None)
    carton_weight = normalized.get("carton_weight") or (str(packing.get("shippingWeight")) if packing.get("shippingWeight") not in [None, ""] else None)
    prod_length = normalized.get("length") or carton_length
    prod_width = normalized.get("width") or carton_width
    prod_height = normalized.get("height") or carton_height
    prod_weight = normalized.get("weight") or carton_weight
    packing_value = normalized.get("packing_quantity") or (str(packing.get("packingQuantity")) if packing.get("packingQuantity") not in [None, ""] else None)

    image_kwargs = {}
    if download_images:
        for idx, img_url in enumerate(normalized["image_urls"][:8], start=1):
            img_file = _download_image_as_content_file(img_url, prefix=f"ywg_{idx}")
            if img_file:
                image_kwargs[f"product_image_{idx}"] = img_file

    with transaction.atomic():
        product = models.ProductDetail.objects.create(
            product_name=product_name,
            product_name_french=product_name_french,
            product_code=product_code,
            vendor_id=vendor_obj.id if vendor_obj else None,
            category_id=category_obj.id if category_obj else None,
            subcategory_id=subcategory_obj.id if subcategory_obj else None,
            description=normalized["description"],
            description_french=description_french,
            unit_of_measure=normalized["unit_of_measure"],
            length=prod_length,
            height=prod_height,
            width=prod_width,
            weight=prod_weight,
            country_of_origin_id=country_obj.id if country_obj else None,
            carton_length=carton_length,
            carton_width=carton_width,
            carton_height=carton_height,
            carton_weight=carton_weight,
            product_verification="Approved",
            available_quantity=normalized.get("available_quantity"),
            quantity=normalized.get("available_quantity"),
            min_order_quantity=normalized["min_order_quantity"],
            max_order_quantity=normalized.get("max_order_quantity"),
            product_packaging_value=packing_value,
            price=price_usd,
            discount="0",
            final_price=str(price_usd),
            status=YUWI_GO_SOURCE,
            product_added_from=YUWI_GO_SOURCE,
            product_type_id=product_type_obj.id if product_type_obj else None,
            product_packaging_id=packaging_obj.id if packaging_obj else None,
            shipping_via="By Air",
            created_at=timezone.now(),
            is_deleted=False,
            **image_kwargs,
        )

        if available_country_ids:
            country_ids = available_country_ids
        else:
            all_country = (
                models.ProductCountry.objects.filter(name__iexact="All").first()
                or models.ProductCountry.objects.filter(id=1).first()
            )
            country_ids = [all_country.id] if all_country else []
        if country_ids:
            product.available_country.set(country_ids)

        for key, val in translated_specs:
            models.ProductOtherSpecification.objects.create(
                product_id=product.id,
                key=key,
                key_french=_translate_to_french(key, enabled=translate_enabled),
                value=val,
                value_french=_translate_to_french(val, enabled=translate_enabled),
            )

        variant_prices = []
        if grouped_skus:
            for model_name, sku_pairs in grouped_skus.items():
                model_obj = models.ProductModel.objects.create(
                    product_id=product.id,
                    model_name=model_name,
                    model_name_french=_translate_to_french(model_name, enabled=translate_enabled),
                    status="Active",
                )
                for variant_name, sku in sku_pairs:
                    sku_cny = sku.get("price") if sku.get("price") not in [None, "", "null"] else normalized["raw_price_cny"]
                    variant_price_usd = _convert_cny_to_usd(sku_cny, cny_rate)
                    variant_prices.append(variant_price_usd)
                    variant_image = (
                        _download_image_as_content_file(sku.get("picture"), prefix="ywg_var")
                        if download_images and sku.get("picture")
                        else None
                    )
                    variant_obj = models.ProductModelVariant.objects.create(
                        product_id=product.id,
                        model_id=model_obj.id,
                        name=variant_name,
                        name_french=_translate_to_french(variant_name, enabled=translate_enabled),
                        image=variant_image,
                        price=str(variant_price_usd),
                        variant_verification="Approved",
                        status="Active",
                    )
                    if vendor_obj:
                        models.VendorProductPrice.objects.create(
                            product_id=product.id,
                            model_id=model_obj.id,
                            vendor_id=vendor_obj.id,
                            variant_id=variant_obj.id,
                            price=str(variant_price_usd),
                            quantity=str(sku.get("stock")) if sku.get("stock") is not None else None,
                            status="Active",
                        )
        else:
            model_obj = models.ProductModel.objects.create(
                product_id=product.id,
                model_name=product_name,
                model_name_french=product_name_french,
                status="Active",
            )
            variant_obj = models.ProductModelVariant.objects.create(
                product_id=product.id,
                model_id=model_obj.id,
                name=product_name,
                name_french=product_name_french,
                price=str(price_usd),
                variant_verification="Approved",
                status="Active",
            )
            if vendor_obj:
                models.VendorProductPrice.objects.create(
                    product_id=product.id,
                    model_id=model_obj.id,
                    vendor_id=vendor_obj.id,
                    variant_id=variant_obj.id,
                    price=str(price_usd),
                    status="Active",
                )

        if price_usd == 0.0 and variant_prices:
            min_variant_price = min(variant_prices)
            product.price = min_variant_price
            product.final_price = str(min_variant_price)
            product.save(update_fields=["price", "final_price"])

    return product


def _fetch_yiwugo_live_page(access_token=None, page=1, page_size=20, search_query="", is_oauth_token=False):
    """Fetch a single product list page from open.yiwugo.com (auto-refreshing OAuth token on 501)."""
    if not access_token:
        access_token, is_oauth_token = _get_yiwugo_access_token()
    if not access_token:
        raise ValueError("No Yiwugo access_token or OAuth credentials configured.")

    for attempt in range(2 if is_oauth_token else 1):
        live_params = {"access_token": access_token, "cpage": page, "pageSize": page_size}
        if search_query:
            live_params["q"] = search_query
        resp = requests.get(
            "https://open.yiwugo.com/open/cn_product/list",
            params=live_params,
            timeout=20,
            verify=False,
        )
        resp_json = resp.json()
        if resp_json.get("code") == 0:
            return resp_json.get("data") or {}
        if resp_json.get("code") == 501 and is_oauth_token and attempt == 0:
            refreshed, _ = _get_yiwugo_access_token(force_refresh=True)
            if refreshed:
                access_token = refreshed
                continue
        raise ValueError(
            f"Yiwugo live API rejected request (code={resp_json.get('code')}): {resp_json.get('message') or resp_json}"
        )
    return {}


def _process_yuwi_go_items(
    raw_items,
    access_token=None,
    is_oauth_token=False,
    doc_detail_example=None,
    cny_rate=YIWUGO_CNY_TO_USD_RATE,
    default_category_id=None,
    default_subcategory_id=None,
    default_vendor_id=None,
    available_country_ids=None,
    translate_enabled=True,
    download_images=True,
):
    """Import a batch of raw/formatted Yiwugo items and return (created, skipped, failed)."""
    created_products = []
    skipped_products = []
    failed_products = []

    raw_batch_titles = [
        item.get("title")
        for item in raw_items
        if isinstance(item, dict) and _contains_cjk(item.get("title"))
    ]
    if raw_batch_titles:
        _translate_many(raw_batch_titles, dest="en")

    for item in raw_items:
        source_id = item.get("id") if isinstance(item, dict) else None
        detail_data = None
        if access_token and source_id and not item.get("detail_data"):
            active_token = (cache.get(YIWUGO_TOKEN_CACHE_KEY) or access_token) if is_oauth_token else access_token
            detail_data = _fetch_yiwugo_product_detail(
                source_id,
                access_token=active_token,
                is_oauth_token=is_oauth_token,
            )
        elif doc_detail_example:
            doc_vo_id = (doc_detail_example.get("detail") or {}).get("productDetailVO", {}).get("id")
            if doc_vo_id and str(doc_vo_id) == str(source_id):
                detail_data = doc_detail_example

        normalized = _extract_product_payload(item, detail_data=detail_data)
        product_name = normalized["title"]

        if not product_name:
            skipped_products.append({
                "source_id": normalized["source_id"],
                "product_name": "",
                "reason": "Missing product title",
            })
            continue

        # Duplicate check scoped strictly to product_added_from = 'yuwi_go'
        if models.ProductDetail.objects.filter(
            product_added_from=YUWI_GO_SOURCE,
            product_name__iexact=product_name,
            is_deleted=False,
        ).exists():
            skipped_products.append({
                "source_id": normalized["source_id"],
                "product_name": product_name,
                "reason": f"Product name already exists in product_added_from='{YUWI_GO_SOURCE}'",
            })
            continue

        try:
            product = _import_single_yuwi_go_product(
                normalized=normalized,
                cny_rate=cny_rate,
                default_category_id=default_category_id,
                default_subcategory_id=default_subcategory_id,
                default_vendor_id=default_vendor_id,
                available_country_ids=available_country_ids,
                translate_enabled=translate_enabled,
                download_images=download_images,
            )
            created_products.append({
                "id": product.id,
                "source_id": normalized["source_id"],
                "product_name": product.product_name,
                "product_name_french": product.product_name_french,
                "unit_of_measure": product.unit_of_measure,
                "product_code": product.product_code,
                "price_cny": normalized["raw_price_cny"],
                "price_usd": product.price,
                "status": product.status,
                "product_added_from": product.product_added_from,
            })
        except Exception as exc:
            failed_products.append({
                "source_id": normalized["source_id"],
                "product_name": product_name,
                "reason": str(exc),
            })

    return created_products, skipped_products, failed_products


def _run_yuwi_go_bulk_job(
    job_id,
    access_token,
    first_page_data,
    start_page,
    end_page,
    page_size,
    search_query,
    product_id_filter,
    cny_rate,
    default_category_id,
    default_subcategory_id,
    default_vendor_id,
    available_country_ids,
    translate_enabled,
    download_images,
    is_oauth_token=False,
    first_page_items=None,
    page_fetcher=None,
):
    """Background worker to import all requested Yiwugo pages sequentially."""
    try:
        for current_page in range(start_page, end_page + 1):
            close_old_connections()
            active_token = (cache.get(YIWUGO_TOKEN_CACHE_KEY) or access_token) if (access_token and is_oauth_token) else access_token
            if page_fetcher is not None:
                if current_page == start_page and first_page_items is not None:
                    page_items = list(first_page_items)
                else:
                    page_items = list(page_fetcher(current_page) or [])
            else:
                page_data = first_page_data if current_page == start_page else _fetch_yiwugo_live_page(
                    access_token=active_token,
                    page=current_page,
                    page_size=page_size,
                    search_query=search_query,
                    is_oauth_token=is_oauth_token,
                )
                page_items = list((page_data or {}).get("prslist") or [])

            if product_id_filter:
                page_items = [
                    item for item in page_items
                    if str(item.get("id")) == str(product_id_filter)
                ]

            if not page_items and current_page > start_page:
                break

            if access_token and is_oauth_token:
                active_token = cache.get(YIWUGO_TOKEN_CACHE_KEY) or active_token

            created, skipped, failed = _process_yuwi_go_items(
                raw_items=page_items,
                access_token=active_token,
                is_oauth_token=is_oauth_token,
                cny_rate=cny_rate,
                default_category_id=default_category_id,
                default_subcategory_id=default_subcategory_id,
                default_vendor_id=default_vendor_id,
                available_country_ids=available_country_ids,
                translate_enabled=translate_enabled,
                download_images=download_images,
            )

            with YUWI_GO_JOBS_LOCK:
                job = YUWI_GO_IMPORT_JOBS[job_id]
                job["current_page"] = current_page
                job["pages_processed"] += 1
                job["total_received"] += len(page_items)
                job["created_count"] += len(created)
                job["skipped_count"] += len(skipped)
                job["failed_count"] += len(failed)
                job["last_error"] = None

        with YUWI_GO_JOBS_LOCK:
            YUWI_GO_IMPORT_JOBS[job_id]["job_status"] = "completed"
    except Exception as exc:
        with YUWI_GO_JOBS_LOCK:
            YUWI_GO_IMPORT_JOBS[job_id]["job_status"] = "failed"
            YUWI_GO_IMPORT_JOBS[job_id]["last_error"] = str(exc)
    finally:
        close_old_connections()


@csrf_exempt
@api_view(["GET", "POST"])
@permission_classes([AllowAny])
def import_yuwi_go_products(request):
    """
    Import Yiwugo products into Diaba:
    - Sets status='yuwi_go' and product_added_from='yuwi_go'
    - Converts CNY prices to USD using 7 CNY = 1 USD (configurable via cny_rate, default 7.0)
    - Skips products whose product_name already exists under product_added_from='yuwi_go'
    - Supports single-page, multi-page (import_all=true, start_page, end_page, max_pages),
      background execution (background=true + job_id status polling), or direct products payload.
    """
    if request.method == "GET":
        params = request.GET.dict()
    elif request.body:
        try:
            params = json.loads(request.body)
        except Exception:
            params = request.POST.dict()
    else:
        params = request.POST.dict()

    job_id_query = params.get("job_id")
    if job_id_query:
        with YUWI_GO_JOBS_LOCK:
            job = YUWI_GO_IMPORT_JOBS.get(job_id_query)
            snapshot = dict(job) if job else None
        if not snapshot:
            return JsonResponse(
                {"status": "error", "message": f"Import job '{job_id_query}' not found."},
                status=404,
                json_dumps_params={"indent": 2},
            )
        return JsonResponse(
            {"status": "success", "job": snapshot},
            status=200,
            json_dumps_params={"indent": 2},
        )

    try:
        cny_rate = float(params.get("cny_rate") or YIWUGO_CNY_TO_USD_RATE)
        if cny_rate <= 0:
            cny_rate = YIWUGO_CNY_TO_USD_RATE
    except (ValueError, TypeError):
        cny_rate = YIWUGO_CNY_TO_USD_RATE

    default_category_id = params.get("category_id")
    default_subcategory_id = params.get("subcategory_id")
    default_vendor_id = params.get("vendor_id")
    available_country_ids = params.get("available_country_ids")
    if isinstance(available_country_ids, str):
        available_country_ids = [int(x.strip()) for x in available_country_ids.split(",") if x.strip().isdigit()]
    translate_enabled = str(params.get("translate", "true")).lower() not in ["false", "0", "no"]
    download_images = str(params.get("download_images", "true")).lower() not in ["false", "0", "no"]
    import_all = str(params.get("import_all", "false")).lower() in ["true", "1", "yes"]

    explicit_token = params.get("access_token") or request.headers.get("X-Access-Token")
    access_token, is_oauth_token = _get_yiwugo_access_token(explicit_token)
    incoming_products = params.get("products")
    doc_detail_example = None
    source_note = None

    if isinstance(incoming_products, list) and incoming_products:
        source_mode = "Request Payload"
        raw_items = incoming_products
    else:
        page = max(1, int(params.get("start_page") or params.get("page") or params.get("cpage") or 1))
        default_page_size = 60 if import_all else 20
        page_size = min(60, max(1, int(params.get("page_size") or params.get("pageSize") or default_page_size)))
        search_query = params.get("q") or params.get("query") or ""
        product_id_filter = params.get("product_id") or params.get("productId")

        raw_response_data = None
        source_mode = "Documentation Catalog & Examples"

        if access_token:
            try:
                raw_response_data = _fetch_yiwugo_live_page(
                    access_token=access_token,
                    page=page,
                    page_size=page_size,
                    search_query=search_query,
                    is_oauth_token=is_oauth_token,
                )
                source_mode = "Live Gateway"
            except Exception as e:
                return JsonResponse(
                    {
                        "status": "error",
                        "source_mode": "Live Gateway",
                        "message": str(e),
                    },
                    status=401 if "501" in str(e) else 502,
                    json_dumps_params={"indent": 2},
                )

            total_found = raw_response_data.get("numfound") or len(raw_response_data.get("prslist") or [])
            if isinstance(total_found, str) and total_found.isdigit():
                total_found = int(total_found)
            elif not isinstance(total_found, int):
                total_found = len(raw_response_data.get("prslist") or [])
            total_pages = max(1, math.ceil(total_found / page_size))

            if import_all and total_pages > page:
                end_page = total_pages
                if params.get("end_page"):
                    end_page = min(end_page, max(page, int(params.get("end_page"))))
                if params.get("max_pages"):
                    end_page = min(end_page, page + max(1, int(params.get("max_pages"))) - 1)

                run_background = str(params.get("background", "true")).lower() not in ["false", "0", "no"]
                if run_background and end_page > page:
                    job_id = uuid.uuid4().hex[:12]
                    with YUWI_GO_JOBS_LOCK:
                        YUWI_GO_IMPORT_JOBS[job_id] = {
                            "job_id": job_id,
                            "job_status": "running",
                            "source_mode": "Live Gateway",
                            "exchange_rate": f"{cny_rate} CNY = 1 USD",
                            "start_page": page,
                            "end_page": end_page,
                            "current_page": page - 1,
                            "total_pages_available": total_pages,
                            "total_products_available": total_found,
                            "pages_processed": 0,
                            "total_received": 0,
                            "created_count": 0,
                            "skipped_count": 0,
                            "failed_count": 0,
                            "last_error": None,
                        }
                    worker = threading.Thread(
                        target=_run_yuwi_go_bulk_job,
                        kwargs={
                            "job_id": job_id,
                            "access_token": access_token,
                            "first_page_data": raw_response_data,
                            "start_page": page,
                            "end_page": end_page,
                            "page_size": page_size,
                            "search_query": search_query,
                            "product_id_filter": product_id_filter,
                            "cny_rate": cny_rate,
                            "default_category_id": default_category_id,
                            "default_subcategory_id": default_subcategory_id,
                            "default_vendor_id": default_vendor_id,
                            "available_country_ids": available_country_ids,
                            "translate_enabled": translate_enabled,
                            "download_images": download_images,
                            "is_oauth_token": is_oauth_token,
                        },
                        daemon=True,
                    )
                    worker.start()
                    return JsonResponse(
                        {
                            "status": "started",
                            "source_mode": "Live Gateway",
                            "job_id": job_id,
                            "status_check_url": f"/api/import_yuwi_go_products/?job_id={job_id}",
                            "start_page": page,
                            "end_page": end_page,
                            "page_size": page_size,
                            "total_products_available": total_found,
                            "total_pages_available": total_pages,
                            "exchange_rate": f"{cny_rate} CNY = 1 USD",
                        },
                        status=202,
                        json_dumps_params={"indent": 2},
                    )

                # Synchronous multi-page import (when background=false)
                all_created, all_skipped, all_failed = [], [], []
                total_received = 0
                pages_processed = 0
                for cur_page in range(page, end_page + 1):
                    active_token = (cache.get(YIWUGO_TOKEN_CACHE_KEY) or access_token) if is_oauth_token else access_token
                    p_data = raw_response_data if cur_page == page else _fetch_yiwugo_live_page(
                        access_token=active_token,
                        page=cur_page,
                        page_size=page_size,
                        search_query=search_query,
                        is_oauth_token=is_oauth_token,
                    )
                    p_items = list((p_data or {}).get("prslist") or [])
                    if product_id_filter:
                        p_items = [x for x in p_items if str(x.get("id")) == str(product_id_filter)]
                    if not p_items and cur_page > page:
                        break
                    total_received += len(p_items)
                    pages_processed += 1
                    active_token = (cache.get(YIWUGO_TOKEN_CACHE_KEY) or active_token) if is_oauth_token else active_token
                    c_list, s_list, f_list = _process_yuwi_go_items(
                        raw_items=p_items,
                        access_token=active_token,
                        is_oauth_token=is_oauth_token,
                        cny_rate=cny_rate,
                        default_category_id=default_category_id,
                        default_subcategory_id=default_subcategory_id,
                        default_vendor_id=default_vendor_id,
                        available_country_ids=available_country_ids,
                        translate_enabled=translate_enabled,
                        download_images=download_images,
                    )
                    all_created.extend(c_list)
                    all_skipped.extend(s_list)
                    all_failed.extend(f_list)

                return JsonResponse(
                    {
                        "status": "success",
                        "source_mode": source_mode,
                        "exchange_rate": f"{cny_rate} CNY = 1 USD",
                        "pagination": {
                            "start_page": page,
                            "end_page": end_page,
                            "pages_processed": pages_processed,
                            "page_size": page_size,
                            "total_products_available": total_found,
                            "total_pages": total_pages,
                        },
                        "summary": {
                            "total_received": total_received,
                            "created_count": len(all_created),
                            "skipped_count": len(all_skipped),
                            "failed_count": len(all_failed),
                        },
                        "created_products": all_created,
                        "skipped_products": all_skipped,
                        "failed_products": all_failed,
                    },
                    status=200,
                    json_dumps_params={"indent": 2},
                )

        if raw_response_data is None:
            try:
                doc_data = _fetch_apipost_docs(target_ids=[TARGET_PRODUCT_LIST, TARGET_PRODUCT_DETAIL])
                raw_response_data = doc_data.get(TARGET_PRODUCT_LIST, {}).get("example_response", {}).get("data", {})
                doc_detail_example = doc_data.get(TARGET_PRODUCT_DETAIL, {}).get("example_response", {}).get("data")
                source_note = (
                    "No live access_token or products payload was provided, so Apipost documentation examples were used. "
                    "The 'numfound: 31648' value in Apipost is only static snapshot metadata—the doc payload only includes 2 sample items. "
                    "Set settings.YIWUGO_ACCESS_TOKEN or pass a valid access_token (with import_all=true) to import all live products."
                )
            except Exception as e:
                return JsonResponse(
                    {"status": "error", "message": f"Failed to fetch Yiwugo products: {str(e)}"},
                    status=502,
                    json_dumps_params={"indent": 2},
                )

        raw_items = list((raw_response_data or {}).get("prslist", []))
        if doc_detail_example and isinstance(doc_detail_example, dict):
            doc_vo_id = (doc_detail_example.get("detail") or {}).get("productDetailVO", {}).get("id")
            existing_ids = {str(x.get("id")) for x in raw_items if isinstance(x, dict) and x.get("id") is not None}
            if doc_vo_id and str(doc_vo_id) not in existing_ids:
                raw_items.append(doc_detail_example)

        if product_id_filter:
            raw_items = [
                item for item in raw_items
                if str(
                    item.get("id")
                    or ((item.get("detail") or {}).get("productDetailVO", {}).get("id"))
                ) == str(product_id_filter)
            ]

    created_products, skipped_products, failed_products = _process_yuwi_go_items(
        raw_items=raw_items,
        access_token=access_token if source_mode == "Live Gateway" else None,
        is_oauth_token=is_oauth_token,
        doc_detail_example=doc_detail_example,
        cny_rate=cny_rate,
        default_category_id=default_category_id,
        default_subcategory_id=default_subcategory_id,
        default_vendor_id=default_vendor_id,
        available_country_ids=available_country_ids,
        translate_enabled=translate_enabled,
        download_images=download_images,
    )

    response_payload = {
        "status": "success",
        "source_mode": source_mode,
        "exchange_rate": f"{cny_rate} CNY = 1 USD",
        "summary": {
            "total_received": len(raw_items),
            "created_count": len(created_products),
            "skipped_count": len(skipped_products),
            "failed_count": len(failed_products),
        },
        "created_products": created_products,
        "skipped_products": skipped_products,
        "failed_products": failed_products,
    }
    if source_note:
        response_payload["note"] = source_note

    return JsonResponse(
        response_payload,
        status=200,
        json_dumps_params={"indent": 2},
    )


@csrf_exempt
@api_view(["GET", "POST"])
@permission_classes([AllowAny])
def sync_third_party_products(request):
    """
    Create/import ProductDetail records by calling the fetch_third_party_products flow.
    - Reads products returned by fetch_third_party_products (supports page, page_size, q,
      product_id, access_token, or optional fetch_api_url, plus import_all / max_pages).
    - Converts CNY prices to USD at 7 CNY = 1 USD (overridable via cny_rate).
    - Sets status='yuwi_go' and product_added_from='yuwi_go'.
    - Skips any product whose product_name already exists under product_added_from='yuwi_go'.
    """
    params = _parse_request_params(request)

    try:
        cny_rate = float(params.get("cny_rate") or YIWUGO_CNY_TO_USD_RATE)
        if cny_rate <= 0:
            cny_rate = YIWUGO_CNY_TO_USD_RATE
    except (ValueError, TypeError):
        cny_rate = YIWUGO_CNY_TO_USD_RATE

    default_category_id = params.get("category_id")
    default_subcategory_id = params.get("subcategory_id")
    default_vendor_id = params.get("vendor_id")
    available_country_ids = params.get("available_country_ids")
    if isinstance(available_country_ids, str):
        available_country_ids = [int(x.strip()) for x in available_country_ids.split(",") if x.strip().isdigit()]
    translate_enabled = str(params.get("translate", "true")).lower() not in ["false", "0", "no"]
    download_images = str(params.get("download_images", "true")).lower() not in ["false", "0", "no"]
    import_all = str(params.get("import_all", "false")).lower() in ["true", "1", "yes"]
    max_pages = int(params["max_pages"]) if str(params.get("max_pages", "")).isdigit() else None
    fetch_api_url = (params.get("fetch_api_url") or "").strip()

    explicit_token = params.get("access_token") or request.headers.get("X-Access-Token")
    access_token, is_oauth_token = _get_yiwugo_access_token(explicit_token)

    job_id_query = params.get("job_id")
    if job_id_query:
        with YUWI_GO_JOBS_LOCK:
            job = YUWI_GO_IMPORT_JOBS.get(job_id_query)
            snapshot = dict(job) if job else None
        if not snapshot:
            return JsonResponse(
                {"status": "error", "message": f"Sync job '{job_id_query}' not found."},
                status=404,
                json_dumps_params={"indent": 2},
            )
        return JsonResponse(
            {"status": "success", "job": snapshot},
            status=200,
            json_dumps_params={"indent": 2},
        )

    request_headers = dict(request.headers)
    if import_all and not params.get("page_size") and not params.get("pageSize"):
        params = dict(params)
        params["page_size"] = 60

    def _fetch_page_via_third_party_api(page_num):
        page_params = dict(params)
        page_params["page"] = page_num
        if fetch_api_url:
            resp = requests.post(fetch_api_url, json=page_params, timeout=30, verify=False)
            return resp.json(), resp.status_code
        return _fetch_third_party_products_data(page_params, headers=request_headers)

    start_page = max(1, int(params.get("start_page") or params.get("page") or params.get("cpage") or 1))
    first_payload, first_status = _fetch_page_via_third_party_api(start_page)
    if first_status != 200 or first_payload.get("status") != "success":
        return JsonResponse(first_payload, status=first_status, json_dumps_params={"indent": 2})

    api_source = first_payload.get("api_source") or {}
    pagination = first_payload.get("pagination") or {}
    total_pages = int(pagination.get("total_pages") or 1)
    total_found = int(pagination.get("total_products_available") or len(first_payload.get("products") or []))
    page_size = int(pagination.get("page_size") or params.get("page_size") or 20)
    is_live_mode = api_source.get("mode") == "Live Gateway"

    end_page = start_page
    if import_all and (is_live_mode or fetch_api_url):
        end_page = total_pages
        if params.get("end_page") and str(params.get("end_page")).isdigit():
            end_page = min(end_page, max(start_page, int(params["end_page"])))
        if max_pages:
            end_page = min(end_page, start_page + max(1, max_pages) - 1)

    run_background = str(params.get("background", "true")).lower() not in ["false", "0", "no"]
    if import_all and (is_live_mode or fetch_api_url) and end_page > start_page and run_background:
        job_id = uuid.uuid4().hex[:12]
        with YUWI_GO_JOBS_LOCK:
            YUWI_GO_IMPORT_JOBS[job_id] = {
                "job_id": job_id,
                "job_status": "running",
                "source_mode": api_source.get("mode") or "Fetch API",
                "exchange_rate": f"{cny_rate} CNY = 1 USD",
                "start_page": start_page,
                "end_page": end_page,
                "current_page": start_page - 1,
                "total_pages_available": total_pages,
                "total_products_available": total_found,
                "pages_processed": 0,
                "total_received": 0,
                "created_count": 0,
                "skipped_count": 0,
                "failed_count": 0,
                "last_error": None,
            }

        def _background_page_fetcher(page_num):
            p_payload, p_status = _fetch_page_via_third_party_api(page_num)
            if p_status != 200 or p_payload.get("status") != "success":
                raise ValueError(p_payload.get("message") or f"Upstream fetch failed with status {p_status}")
            return p_payload.get("products") or []

        worker = threading.Thread(
            target=_run_yuwi_go_bulk_job,
            kwargs={
                "job_id": job_id,
                "access_token": access_token if is_live_mode else None,
                "first_page_data": None,
                "start_page": start_page,
                "end_page": end_page,
                "page_size": page_size,
                "search_query": params.get("q") or params.get("query") or "",
                "product_id_filter": params.get("product_id") or params.get("productId"),
                "cny_rate": cny_rate,
                "default_category_id": default_category_id,
                "default_subcategory_id": default_subcategory_id,
                "default_vendor_id": default_vendor_id,
                "available_country_ids": available_country_ids,
                "translate_enabled": translate_enabled,
                "download_images": download_images,
                "is_oauth_token": is_oauth_token if is_live_mode else False,
                "first_page_items": first_payload.get("products") or [],
                "page_fetcher": _background_page_fetcher,
            },
            daemon=True,
        )
        worker.start()
        return JsonResponse(
            {
                "status": "started",
                "api_source": api_source,
                "job_id": job_id,
                "status_check_url": f"/api/sync_third_party_products/?job_id={job_id}",
                "start_page": start_page,
                "end_page": end_page,
                "page_size": page_size,
                "total_products_available": total_found,
                "total_pages_available": total_pages,
                "exchange_rate": f"{cny_rate} CNY = 1 USD",
            },
            status=202,
            json_dumps_params={"indent": 2},
        )

    all_created, all_skipped, all_failed = [], [], []
    total_received = 0
    pages_processed = 0

    for current_page in range(start_page, end_page + 1):
        if current_page == start_page:
            page_payload = first_payload
        else:
            page_payload, page_status = _fetch_page_via_third_party_api(current_page)
            if page_status != 200 or page_payload.get("status") != "success":
                break

        page_products = page_payload.get("products") or []
        if not page_products and current_page > start_page:
            break

        total_received += len(page_products)
        pages_processed += 1

        active_token = (
            (cache.get(YIWUGO_TOKEN_CACHE_KEY) or access_token)
            if (is_live_mode and is_oauth_token)
            else (access_token if is_live_mode else None)
        )
        created, skipped, failed = _process_yuwi_go_items(
            raw_items=page_products,
            access_token=active_token,
            is_oauth_token=is_oauth_token if is_live_mode else False,
            cny_rate=cny_rate,
            default_category_id=default_category_id,
            default_subcategory_id=default_subcategory_id,
            default_vendor_id=default_vendor_id,
            available_country_ids=available_country_ids,
            translate_enabled=translate_enabled,
            download_images=download_images,
        )
        all_created.extend(created)
        all_skipped.extend(skipped)
        all_failed.extend(failed)

    response_data = {
        "status": "success",
        "api_source": api_source,
        "fetch_pagination": pagination,
        "pages_processed": pages_processed,
        "exchange_rate": f"{cny_rate} CNY = 1 USD",
        "summary": {
            "total_received": total_received,
            "created_count": len(all_created),
            "skipped_count": len(all_skipped),
            "failed_count": len(all_failed),
        },
        "created_products": all_created,
        "skipped_products": all_skipped,
        "failed_products": all_failed,
    }
    if not is_live_mode and not fetch_api_url:
        response_data["note"] = (
            "fetch_third_party_products is running in Documentation Catalog & Examples mode "
            "(only 1 static sample item in prslist). Provide a live access_token or settings.YIWUGO_ACCESS_TOKEN "
            "to fetch and add live products."
        )

    return JsonResponse(response_data, status=200, json_dumps_params={"indent": 2})



