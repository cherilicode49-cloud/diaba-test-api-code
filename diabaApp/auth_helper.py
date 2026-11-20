import jwt
import datetime
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer
from django.http import HttpResponse
import io
from diabaApp import models

JWT_ALGORITHM = 'HS256'
ACCESS_TOKEN_LIFETIME_DAYS = 30
REFRESH_TOKEN_LIFETIME_DAYS = 90

def generate_tokens_for_customer(customer):
    """Generates an access token and refresh token pair for a customer."""
    now = datetime.datetime.now(datetime.timezone.utc)
    
    access_payload = {
        'customer_id': customer.id,
        'mobileNumber': str(customer.mobileNumber),
        'countryCode': str(customer.countryCode),
        'token_type': 'access',
        'iat': now,
        'exp': now + datetime.timedelta(days=ACCESS_TOKEN_LIFETIME_DAYS)
    }
    
    refresh_payload = {
        'customer_id': customer.id,
        'token_type': 'refresh',
        'iat': now,
        'exp': now + datetime.timedelta(days=REFRESH_TOKEN_LIFETIME_DAYS)
    }
    
    access_token = jwt.encode(access_payload, settings.SECRET_KEY, algorithm=JWT_ALGORITHM)
    refresh_token = jwt.encode(refresh_payload, settings.SECRET_KEY, algorithm=JWT_ALGORITHM)
    
    return {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'expires_in': ACCESS_TOKEN_LIFETIME_DAYS * 86400
    }

def decode_token(token):
    """Decodes and validates a JWT token."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return {'error': 'token_expired', 'message': 'Token has expired'}
    except jwt.InvalidTokenError:
        return {'error': 'invalid_token', 'message': 'Invalid token signature'}

def get_token_from_request(request):
    """Extracts Bearer token from request Authorization header or GET/POST params."""
    auth_header = request.META.get('HTTP_AUTHORIZATION', '')
    if not auth_header:
        auth_header = request.headers.get('Authorization', '')
        
    if auth_header and auth_header.startswith('Bearer '):
        return auth_header[7:].strip()
    elif auth_header and auth_header.startswith('Token '):
        return auth_header[6:].strip()
    
    # Fallback to query parameter or body if needed
    if request.method == 'GET':
        return request.GET.get('token')
    return None

def get_authenticated_customer(request):
    """
    Returns (customer, error_dict)
    - If valid Bearer token provided, returns (customer, None)
    - If token invalid/expired, returns (None, error_info)
    - If no token provided, checks fallback 'customer' id in request data
    """
    token = get_token_from_request(request)
    if token:
        decoded = decode_token(token)
        if 'error' in decoded:
            return None, decoded
        
        customer_id = decoded.get('customer_id')
        try:
            customer = models.CustomerDetail.objects.filter(id=customer_id).first()
            if customer:
                return customer, None
            return None, {'error': 'customer_not_found', 'message': 'Customer account not found'}
        except Exception as e:
            return None, {'error': 'db_error', 'message': str(e)}
            
    # Check backwards compatible customer ID
    cust_id = None
    if request.method == 'GET':
        cust_id = request.GET.get('customer') or request.GET.get('customer_id')
    else:
        try:
            body = request.body
            if body:
                import json
                try:
                    data = json.loads(body)
                    cust_id = data.get('customer') or data.get('customer_id')
                except Exception:
                    cust_id = request.POST.get('customer') or request.POST.get('customer_id')
        except Exception:
            pass

    if cust_id:
        try:
            customer = models.CustomerDetail.objects.filter(id=cust_id).first()
            if customer:
                return customer, None
        except Exception:
            pass
            
    return None, None

def customer_token_required(view_func):
    """Decorator to enforce that the caller has a valid Bearer token or authenticated customer."""
    def wrapped(request, *args, **kwargs):
        customer, err = get_authenticated_customer(request)
        if err:
            return JsonResponse({
                'status': False,
                'message': err.get('message', 'Authentication failed'),
                'code': err.get('error', 'unauthorized')
            }, status=401)
            
        if not customer:
            return JsonResponse({
                'status': False,
                'message': 'Authentication required. Please include Authorization: Bearer <access_token>',
                'code': 'missing_token'
            }, status=401)
            
        request.customer = customer
        request.customer_id = customer.id
        return view_func(request, *args, **kwargs)
    wrapped.__name__ = view_func.__name__
    wrapped.__doc__ = view_func.__doc__
    return wrapped

def optional_customer_token(view_func):
    """Decorator for Dual-Mode endpoints: populates request.customer if token provided, else None."""
    def wrapped(request, *args, **kwargs):
        customer, err = get_authenticated_customer(request)
        request.customer = customer
        request.customer_id = customer.id if customer else None
        return view_func(request, *args, **kwargs)
    wrapped.__name__ = view_func.__name__
    wrapped.__doc__ = view_func.__doc__
    return wrapped

@csrf_exempt
def token_refresh_api(request):
    """
    POST /api/token_refresh/
    Body: {"refresh_token": "<refresh_token>"}
    Returns a new access_token and refresh_token pair.
    """
    if request.method != 'POST':
        return JsonResponse({'status': False, 'message': 'POST method required'}, status=405)
        
    try:
        data = JSONParser().parse(io.BytesIO(request.body))
    except Exception:
        data = request.POST
        
    refresh_token = data.get('refresh_token')
    if not refresh_token:
        # Check header
        refresh_token = get_token_from_request(request)
        
    if not refresh_token:
        return JsonResponse({
            'status': False,
            'message': 'refresh_token parameter is required in request body.',
            'code': 'missing_refresh_token'
        }, status=400)
        
    decoded = decode_token(refresh_token)
    if 'error' in decoded:
        return JsonResponse({
            'status': False,
            'message': decoded.get('message', 'Invalid refresh token'),
            'code': decoded.get('error', 'invalid_refresh_token')
        }, status=401)
        
    if decoded.get('token_type') != 'refresh':
        return JsonResponse({
            'status': False,
            'message': 'Provided token is not a refresh token.',
            'code': 'invalid_token_type'
        }, status=400)
        
    customer_id = decoded.get('customer_id')
    customer = models.CustomerDetail.objects.filter(id=customer_id).first()
    if not customer:
        return JsonResponse({
            'status': False,
            'message': 'Customer associated with refresh token not found.',
            'code': 'customer_not_found'
        }, status=404)
        
    tokens = generate_tokens_for_customer(customer)
    return JsonResponse({
        'status': True,
        'message': 'Access token refreshed successfully.',
        'data': tokens
    }, status=200)
