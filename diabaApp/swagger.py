import os
import re
import ast
import json
import logging
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

logger = logging.getLogger(__name__)

# Cached OpenAPI Spec in memory
_CACHED_SPEC = None

# Security classifications based on client app specification
TOKEN_REQUIRED_PATHS = {
    # User Account & Profile
    '/api/customer_detail/',
    '/api/customer_profile_update/',
    '/api/customer_logout/',
    '/api/customer_delete/',
    '/api/mobile_number_update/',
    '/api/mobile_number_update_verify/',
    # Addresses
    '/api/customer_address_create/',
    '/api/customer_address_update/',
    # Cart & Wishlist (Server Sync)
    '/api/add_to_cart/',
    '/api/add_to_wishlist/',
    '/api/product_remove_from_cart/',
    '/api/customer_cart_check/',
    # Orders & Payments
    '/api/order_create/',
    '/api/order_create_wave_orange/',
    '/api/customer_order_list/',
    '/api/payment_callback/',
    '/api/create_wave_checkout/',
    '/api/get_wave_checkout_session/',
    '/api/create_payment_paydunya/',
    '/api/initiate_bictorys_payment/',
    '/api/payment_status/',
    '/api/initiate_stripe_payment/',
    # Inquiries & Container Requests
    '/api/inquiry_order_create/',
    '/api/all_order_inquiry_list_app/',
    '/api/product_inquiry_form/',
    '/api/customer_inquiry_list/',
    '/api/initiate_bictorys_payment_for_inquiry/',
    '/api/container_request_create/',
    '/api/customer_container_request_list/',
    # Customer Support & Reviews
    '/api/chat_history/',
    '/api/create_message/',
    '/api/user_new_message_count/',
    '/api/review_create/',
    '/api/recently_view_product_list/',
    # Delivery Days Configuration (Admin)
    '/api/delivery_day_detail_list_admin/',
    '/api/delivery_day_detail_add_admin/',
    '/api/delivery_day_detail_update_admin/',
    '/api/delivery_day_detail_delete_admin/',
    '/api/delivery_days_update/',
    # App Version Management (Admin)
    '/api/v1/admin/app-versions/',
    '/api/v1/admin/app-versions',
    '/api/admin_app_versions/',
}

DUAL_MODE_PATHS = {
    '/api/app_dashboard/': 'Guest: Default public home feed. Authenticated (with Bearer Token): Enriches feed with country-specific context and personalized deals.',
    '/api/product_detail_app/': 'Guest: Standard public product details. Authenticated (with Bearer Token): Includes customer status flags (is_in_wishlist, is_in_cart).',
    '/api/customer_wishlist_cart_list/': 'Guest: Uses local storage on client. Authenticated (with Bearer Token): Synchronizes and returns server-persisted user cart and wishlist.',
}

PUBLIC_PATHS = {
    # Authentication & Registration
    '/api/customer_login/',
    '/api/customer_register/',
    '/api/social_login/',
    '/api/customer_verify/',
    '/api/otp_send/',
    '/api/otp_verify/',
    '/api/token_refresh/',
    # Catalog, Search & Products
    '/api/app_dashboard_category/',
    '/api/category_with_subcategory_data/',
    '/api/subcategory_wise_product_list/',
    '/api/product_filter_data/',
    '/api/product_list_tag_result/',
    '/api/recommend_products/',
    '/api/product_search_by_tag/',
    '/api/product_review_list_admin/',
    '/api/get_shipping_cost/',
    '/api/all_product_country/',
    '/api/all_delivery_days_list/',
    '/api/delivery_day_available_countries_admin/',
    '/api/available_countries_for_delivery_day_admin/',
    # Logistics & App Settings
    '/api/cargo_list_app/',
    '/api/banner_list_app/',
    '/api/intro_banner_data/',
    '/api/countrywithcurrency_list_admin/',
    '/api/container_terms_list_app/',
    '/api/container_booking_fees_list/',
    '/api/money_network_list/',
    '/api/promocode_list/',
    '/api/app_setting/',
    '/api/inquiry_setting/',
    '/api/inquiry_amount/',
    '/api/v1/app/version-check/',
    '/api/v1/app/version-check',
    '/api/app_version_check/',
    '/api/container_status_view/',
    '/api/about_us_list/',
    '/api/terms_and_condition_list/',
    '/api/privacy_policy_list/',
    '/api/refund_policy_list/',
    # Portal Auth
    '/api/admin_login/',
    '/api/vendor_login/',
    '/api/vendor_register/',
    '/api/vendor_credentials_resend/',
}

MODULE_MAPPING = {
    'auth_views.py': 'Authentication & Accounts',
    'admin_views.py': 'Admin Management',
    'vendor_views.py': 'Vendor Management',
    'category_views.py': 'Category & Subcategory',
    'product_views.py': 'Product Management',
    'product_request_views.py': 'Product Requests',
    'customer_views.py': 'Customer & Profile',
    'wishlist_views.py': 'Wishlist & Cart',
    'order_views.py': 'Order Management',
    'payment_views.py': 'Payment & Transactions',
    'shipping_views.py': 'Shipping & Delivery',
    'cargo_views.py': 'Cargo & Logistics',
    'influencer_views.py': 'Influencer & Promocodes',
    'chat_views.py': 'Chat & Support',
    'container_views.py': 'Containers & Freight',
    'analytics_views.py': 'Analytics & Dashboard',
    'graph_views.py': 'Graphs & Statistics',
    'inquiry_views.py': 'Inquiry & Terms',
    'banner_views.py': 'Banners & Marketing',
    'activity_views.py': 'User Activity & Tracking',
    'third_party_product_views.py': 'Third Party & Yiwugo Products',
    'transaction_views.py': 'Vendor Transactions',
    'utility_views.py': 'Utility & Helpers',
    'currency_views.py': 'Currency & Exchange',
    'settings_views.py': 'System Settings',
    'review_views.py': 'Reviews & Ratings',
    'warehouse_views.py': 'Warehouse Management',
    'report_views.py': 'Reports & Export',
    'testing_views.py': 'Testing & Debugging',
    'money_network_views.py': 'Money Network',
}

MODULE_DESCRIPTIONS = {
    'Authentication & Accounts': 'Authentication, login, registration, OTP, and user credentials for admin, vendors, customers, and chat agents.',
    'Admin Management': 'Superadmin controls, admin users, permissions, and administrative operations.',
    'Vendor Management': 'Vendor onboarding, verification, profile updates, and vendor product catalogues.',
    'Category & Subcategory': 'Hierarchical category, subcategory, and super-subcategory definitions.',
    'Product Management': 'Product catalog, details, search, variants, pricing, tags, and recommendations.',
    'Product Requests': 'Customer and vendor customized product sourcing requests and quotations.',
    'Customer & Profile': 'Customer profiles, delivery addresses, and customer account configurations.',
    'Wishlist & Cart': 'Customer cart items, wishlist, pricing breakdowns, and promotional discounts.',
    'Order Management': 'Checkout, order lifecycle, tracking, multi-promocode calculation, and invoice management.',
    'Payment & Transactions': 'Payment gateway integrations (Bictorys, Wave, Orange Money, Stripe, Moov) and transaction verification.',
    'Shipping & Delivery': 'Shipping costs, express delivery calculation, logistics fees, and address validations.',
    'Cargo & Logistics': 'Air cargo, sea cargo, container bookings, and customs logistics.',
    'Influencer & Promocodes': 'Influencer management, product-wise promo codes (1:1), storewide promo codes, and commission calculations.',
    'Chat & Support': 'Real-time customer-vendor and customer-agent chat messaging and attachments.',
    'Containers & Freight': 'International freight container requests, tracking, and management.',
    'Analytics & Dashboard': 'Business metrics, analytics summaries, sales trends, and administrative KPIs.',
    'Graphs & Statistics': 'Data visualization and statistical charts for admin and vendor portals.',
    'Inquiry & Terms': 'Customer inquiries, vendor quotations, custom pricing, and terms & conditions.',
    'Banners & Marketing': 'Promotional banners, homepage sliders, and marketing placements.',
    'User Activity & Tracking': 'User tracking, page visits, search telemetry, and user audit logs.',
    'Third Party & Yiwugo Products': 'Third-party e-commerce synchronization, Yiwugo bulk product ingestion, and mapping.',
    'Vendor Transactions': 'Vendor balances, payout requests, withdrawals, and financial history.',
    'Utility & Helpers': 'Translations, system utilities, image handling, and diagnostic endpoints.',
    'Currency & Exchange': 'Currency rates (XOF, USD, CNY, EUR) and real-time conversions.',
    'System Settings': 'Application dynamic settings, operational constants, and system configurations.',
    'Reviews & Ratings': 'Customer reviews, star ratings, and review management.',
    'Warehouse Management': 'Warehouse locations, inventory points, and logistics checkpoints.',
    'Reports & Export': 'Data exports in Excel and CSV formats for orders, inventory, and users.',
    'Testing & Debugging': 'Internal testing tools, sandbox endpoints, and mock triggers.',
    'Money Network': 'Mobile money network operators, fees, and routing configurations.',
}

IGNORE_PARAMS = {
    'REMOTE_ADDR', 'HTTP_AUTHORIZATION', 'CSRF_COOKIE', 'CONTENT_TYPE', 'HTTP_USER_AGENT',
    'SERVER_NAME', 'SERVER_PORT', 'PATH_INFO', 'QUERY_STRING', 'error', 'csrf_token',
    'request', 'self', 'args', 'kwargs', 'HTTP_HOST', 'HTTP_ACCEPT', 'CONTENT_LENGTH',
    'message', 'status_code'
}

def clean_param_name(name):
    if not isinstance(name, str):
        return None
    name = name.strip("'\" \t\r\n")
    if not name or name in IGNORE_PARAMS:
        return None
    if name.startswith('HTTP_') or name.startswith('wsgi.') or name.startswith('django.'):
        return None
    return name

def guess_type_and_schema(pname):
    lower = pname.lower()
    if any(k in lower for k in ['image', 'file', 'photo', 'avatar', 'doc', 'pdf', 'excel', 'receipt']):
        return {'type': 'string', 'format': 'binary', 'description': f'File upload for {pname}'}
    if any(k in lower for k in ['_delivery', 'delivery_day', 'delay_day']) or lower in ['express_delivery', 'air_delivery', 'ship_delivery', 'express_delivery_days', 'air_delivery_days', 'ship_delivery_days']:
        example_val = 10 if 'express' in lower else (25 if 'air' in lower else (90 if 'ship' in lower else 7))
        return {'type': 'integer', 'example': example_val, 'description': f'Number of delivery days ({pname})'}
    if lower in ['country', 'country_id', 'country_name', 'countryname']:
        return {'type': 'string', 'example': '1', 'description': 'Country identifier (Country ID or country name)'}
    if lower in ['search', 'q', 'keyword']:
        return {'type': 'string', 'example': 'Egypt', 'description': 'Search keyword for filtering'}
    if lower.endswith('_id') or lower in ['id', 'user_id', 'product_id', 'order_id', 'category_id', 'subcategory_id', 'vendor_id', 'page_number', 'row_data', 'count', 'quantity', 'total_employee', 'days']:
        return {'type': 'integer', 'example': 1, 'description': f'Identifier or count ({pname})'}
    if lower in ['platform']:
        return {'type': 'string', 'enum': ['android', 'ios'], 'example': 'android', 'description': 'Target mobile platform (android or ios)'}
    if lower in ['app_version', 'latest_version', 'min_supported_version']:
        return {'type': 'string', 'example': '1.0.0', 'description': f'Semantic version string ({pname})'}
    if lower in ['store_url']:
        return {'type': 'string', 'format': 'uri', 'example': 'https://play.google.com/store/apps/details?id=com.diaba.ecommerce', 'description': 'App store download URL'}
    if lower in ['update_title']:
        return {'type': 'string', 'example': 'New Version Available', 'description': 'Update dialog title'}
    if lower in ['release_notes']:
        return {'type': 'string', 'example': 'Bug fixes and performance enhancements.', 'description': 'Changelog / release notes'}
    if lower in ['maintenance_message']:
        return {'type': 'string', 'example': 'Scheduled maintenance in progress. Please check back shortly.', 'description': 'Downtime message'}
    if any(k in lower for k in ['price', 'amount', 'discount', 'weight', 'length', 'width', 'height', 'rate', 'commission']):
        return {'type': 'number', 'format': 'float', 'example': 10.50, 'description': f'Numeric amount ({pname})'}
    if any(k in lower for k in ['is_', 'has_']) or lower in ['status_bool', 'active', 'coupon_verify']:
        return {'type': 'boolean', 'example': True, 'description': f'Boolean flag ({pname})'}
    if lower in ['products', 'promocodes', 'items', 'tags', 'variants', 'ids', 'categories', 'colors', 'sizes']:
        return {'type': 'array', 'items': {'type': 'string'}, 'example': [], 'description': f'List of {pname}'}
    if 'email' in lower:
        return {'type': 'string', 'format': 'email', 'example': 'user@example.com', 'description': 'Email address'}
    if 'phone' in lower or 'mobile' in lower:
        return {'type': 'string', 'example': '+221770000000', 'description': 'Phone / mobile number'}
    if 'date' in lower or 'time' in lower:
        return {'type': 'string', 'example': '2026-11-20', 'description': 'Date or timestamp string'}
    if 'password' in lower:
        return {'type': 'string', 'format': 'password', 'example': '••••••••', 'description': 'Password'}
    return {'type': 'string', 'example': f'value_{pname}', 'description': f'Field {pname}'}

def format_summary(func_name):
    words = func_name.replace('__', '_').split('_')
    return ' '.join(w.capitalize() for w in words if w)

# Detailed schemas and parameters for Product Model & Variant Creation
PRODUCT_MODEL_VARIANT_CREATE_DESCRIPTION = """### 📦 Product Creation with Models, Variants & Specifications

Creates a comprehensive product entry with multipart file uploads, JSON-encoded specifications, and hierarchical nested models and variants.

#### 📌 Key Requirements & Protocols:
1. **Content-Type**: Must be `multipart/form-data`.
2. **`other_specification`**: Required JSON string representing an array of specifications:
   ```json
   [
     {
       "key": "Battery Life",
       "key_french": "Autonomie",
       "value": "30 Hours",
       "value_french": "30 Heures"
     },
     {
       "key": "Bluetooth Version",
       "key_french": "Version Bluetooth",
       "value": "5.3",
       "value_french": "5.3"
     }
   ]
   ```
3. **Hierarchical Models & Variants Format**:
   Submitted as indexed form fields from index `0` up to `499`:
   - **Model `i`**:
     - `models[{i}][name]` *(Required)*: Model name in English (e.g., `models[0][name]=Pro Edition`)
     - `models[{i}][model_name_french]`: Model name in French (e.g., `models[0][model_name_french]=Édition Pro`)
     - `models[{i}][image]`: Binary file upload for the model image
   - **Variant `j` under Model `i`**:
     - `models[{i}][variants][{j}][name]` *(Required)*: Variant name (e.g., `models[0][variants][0][name]=Midnight Black / 64GB`)
     - `models[{i}][variants][{j}][variant_name_french]`: Variant French name
     - `models[{i}][variants][{j}][price]` *(Required)*: Selling price (e.g., `79.99`)
     - `models[{i}][variants][{j}][image]`: Binary file upload for variant
     - `models[{i}][variants][{j}][vendor]`: Vendor ID supplying this variant
     - `models[{i}][variants][{j}][vendor_price]`: Vendor cost/wholesale price
     - Dimensions: `length`, `width`, `height`, `weight`, `carton_length`, `carton_width`, `carton_height`, `carton_weight` (falls back to base product dimensions if omitted)
4. **Automatic Lowest Price Assignment**:
   The base product's `price` field is automatically set to the minimum price among all submitted variants.
5. **Image Vector Extraction**:
   Submitted product images (`product_image_1` to `product_image_8`) automatically have visual search vectors extracted and stored for image-based recommendations.
6. **Role Behavior (`login_flag`)**:
   - `'Admin'`: Automatically approves the product (`product_verification='Approved'`, `status='Approved'`).
   - `'Vendor'`: Keeps product in review (`product_verification='Pending'`, `status='Pending'`).
"""

PRODUCT_MODEL_VARIANT_UPDATE_DESCRIPTION = """### 📦 Product Update with Models, Variants & Specifications

Updates an existing product entry including base details, JSON specifications, media gallery, and nested models/variants.

- **Content-Type**: Must be `multipart/form-data`.
- **`id`**: Product ID to update *(Required)*.
- **`other_specification`**: JSON array string of updated specifications.
- **Nested Models & Variants**: Accepts updated or new indexed entries (`models[0][name]`, `models[0][variants][0][name]`, etc.).
"""

PRODUCT_MODEL_VARIANT_CREATE_PROPERTIES = {
    # --- Base Product Info ---
    'product_name': {
        'type': 'string',
        'description': 'Product name in English (Required)',
        'example': 'Wireless Noise-Canceling Over-Ear Headphones'
    },
    'product_name_french': {
        'type': 'string',
        'description': 'Product name in French (Required)',
        'example': 'Casque circum-auriculaire sans fil antibruit'
    },
    'category': {
        'type': 'integer',
        'description': 'Category ID (Required)',
        'example': 1
    },
    'subcategory': {
        'type': 'integer',
        'description': 'SubCategory ID (Required)',
        'example': 4
    },
    'vendor': {
        'type': 'integer',
        'description': 'Vendor ID owning this product (Required)',
        'example': 2
    },
    'description': {
        'type': 'string',
        'description': 'Detailed product description in English',
        'example': 'Premium high-fidelity audio with active noise cancellation and 30-hour battery life.'
    },
    'description_french': {
        'type': 'string',
        'description': 'Detailed product description in French',
        'example': 'Audio haute fidélité haut de gamme avec réduction active du bruit et autonomie de 30 heures.'
    },
    'unit_of_measure': {
        'type': 'string',
        'description': 'Unit of measurement (e.g. piece, box, set, kg, pair)',
        'example': 'piece'
    },
    'material': {
        'type': 'string',
        'description': 'Product material / composition',
        'example': 'Aluminum & Memory Foam'
    },
    'color': {
        'type': 'string',
        'description': 'Default / primary product color',
        'example': 'Matte Black'
    },
    'country_of_origin': {
        'type': 'integer',
        'description': 'CountryWithCurrency ID for country of manufacture',
        'example': 1
    },

    # --- Pricing & Inventory ---
    'price': {
        'type': 'number',
        'format': 'float',
        'description': 'Base price. Note: The system will automatically overwrite product price with the lowest variant price upon creation.',
        'example': 89.99
    },
    'discount': {
        'type': 'number',
        'format': 'float',
        'description': 'Discount percentage or amount',
        'example': 10.00
    },
    'final_price': {
        'type': 'number',
        'format': 'float',
        'description': 'Final calculated price after discount',
        'example': 79.99
    },
    'price_currency': {
        'type': 'string',
        'enum': ['USD', 'XOF'],
        'description': "Currency code of submitted variant prices ('USD' or 'XOF'). If 'XOF', prices are converted to USD at system conversion rate.",
        'example': 'USD'
    },
    'quantity': {
        'type': 'integer',
        'description': 'Total inventory stock quantity',
        'example': 500
    },
    'available_quantity': {
        'type': 'integer',
        'description': 'Available inventory stock quantity for sale',
        'example': 500
    },
    'min_order_quantity': {
        'type': 'integer',
        'description': 'Minimum Order Quantity (MOQ)',
        'example': 1
    },
    'max_order_quantity': {
        'type': 'integer',
        'description': 'Maximum Order Quantity per purchase',
        'example': 50
    },

    # --- Product Dimensions & Shipping Carton ---
    'length': {
        'type': 'number',
        'format': 'float',
        'description': 'Product item length in cm',
        'example': 18.5
    },
    'width': {
        'type': 'number',
        'format': 'float',
        'description': 'Product item width in cm',
        'example': 15.0
    },
    'height': {
        'type': 'number',
        'format': 'float',
        'description': 'Product item height in cm',
        'example': 7.5
    },
    'weight': {
        'type': 'number',
        'format': 'float',
        'description': 'Product item weight in kg',
        'example': 0.35
    },
    'carton_length': {
        'type': 'number',
        'format': 'float',
        'description': 'Outer shipping carton length in cm',
        'example': 50.0
    },
    'carton_width': {
        'type': 'number',
        'format': 'float',
        'description': 'Outer shipping carton width in cm',
        'example': 40.0
    },
    'carton_height': {
        'type': 'number',
        'format': 'float',
        'description': 'Outer shipping carton height in cm',
        'example': 35.0
    },
    'carton_weight': {
        'type': 'number',
        'format': 'float',
        'description': 'Outer shipping carton gross weight in kg',
        'example': 12.5
    },

    # --- Logistics & Delays ---
    'shipping_via': {
        'type': 'string',
        'description': 'Default shipping mode (e.g. Air, Sea, Express)',
        'example': 'Air'
    },
    'delay_days_air': {
        'type': 'integer',
        'description': 'Estimated delivery duration in days for Air freight',
        'example': 15
    },
    'delay_days_ship': {
        'type': 'integer',
        'description': 'Estimated delivery duration in days for Sea freight',
        'example': 45
    },
    'delay_days_express': {
        'type': 'integer',
        'description': 'Estimated delivery duration in days for Express courier',
        'example': 7
    },
    'available_country': {
        'type': 'string',
        'description': 'Target countries for sale. Comma-separated Country IDs string (e.g. "1,2,3") or JSON array string "[1,2,3]".',
        'example': '1,2,3'
    },
    'tag': {
        'type': 'string',
        'description': 'Product tags. Comma-separated Tag IDs string (e.g. "1,4") or JSON array string "[1,4]".',
        'example': '1,4'
    },
    'product_type': {
        'type': 'integer',
        'description': 'ProductType ID',
        'example': 1
    },
    'product_packaging': {
        'type': 'integer',
        'description': 'ProductPackaging ID',
        'example': 1
    },
    'product_packaging_value': {
        'type': 'string',
        'description': 'Packaging description / packaging value',
        'example': 'Retail Color Box'
    },

    # --- Admin / Flags ---
    'login_flag': {
        'type': 'string',
        'enum': ['Admin', 'Vendor'],
        'description': "Role submitting the product. 'Admin' automatically marks product verification and status as 'Approved'; 'Vendor' marks it as 'Pending'.",
        'example': 'Admin'
    },
    'is_inquiry': {
        'type': 'integer',
        'enum': [0, 1],
        'description': '1 if this is a quotation/inquiry-only product; 0 for standard purchasable item.',
        'example': 0
    },
    'refpro': {
        'type': 'string',
        'description': 'External reference product code',
        'example': 'REF-WH-1000XM4'
    },
    'reuser': {
        'type': 'string',
        'description': 'Reference user code / creator tag',
        'example': 'USER-102'
    },

    # --- Specifications (JSON String) ---
    'other_specification': {
        'type': 'string',
        'description': (
            'Required JSON string representing an array of specification objects. '
            'Each object must contain: key, key_french, value, value_french.'
        ),
        'example': '[{"key": "Bluetooth Version", "key_french": "Version Bluetooth", "value": "5.3", "value_french": "5.3"}, {"key": "Battery Life", "key_french": "Autonomie de la batterie", "value": "30 Hours", "value_french": "30 Heures"}]'
    },

    # --- Image & Media File Uploads ---
    'product_image_1': {
        'type': 'string',
        'format': 'binary',
        'description': 'Primary main product image file (Required, JPEG/PNG/AVIF). Feature vector is extracted automatically.'
    },
    'product_image_2': {
        'type': 'string',
        'format': 'binary',
        'description': 'Gallery image #2 (JPEG/PNG/AVIF)'
    },
    'product_image_3': {
        'type': 'string',
        'format': 'binary',
        'description': 'Gallery image #3 (JPEG/PNG/AVIF)'
    },
    'product_image_4': {
        'type': 'string',
        'format': 'binary',
        'description': 'Gallery image #4 (JPEG/PNG/AVIF)'
    },
    'product_image_5': {
        'type': 'string',
        'format': 'binary',
        'description': 'Gallery image #5 (JPEG/PNG/AVIF)'
    },
    'product_image_6': {
        'type': 'string',
        'format': 'binary',
        'description': 'Gallery image #6 (JPEG/PNG/AVIF)'
    },
    'product_image_7': {
        'type': 'string',
        'format': 'binary',
        'description': 'Gallery image #7 (JPEG/PNG/AVIF)'
    },
    'product_image_8': {
        'type': 'string',
        'format': 'binary',
        'description': 'Gallery image #8 (JPEG/PNG/AVIF)'
    },
    'product_video': {
        'type': 'string',
        'format': 'binary',
        'description': 'Product demo video file (MP4) or video URL string'
    },

    # --- Dynamic Models & Variants (Indexed 0..499) ---
    # Model 0
    'models[0][name]': {
        'type': 'string',
        'description': 'Model 0 name in English (Required for Model 0)',
        'example': 'Pro Edition'
    },
    'models[0][model_name_french]': {
        'type': 'string',
        'description': 'Model 0 name in French',
        'example': 'Édition Pro'
    },
    'models[0][image]': {
        'type': 'string',
        'format': 'binary',
        'description': 'Model 0 image file upload'
    },

    # Model 0 -> Variant 0
    'models[0][variants][0][name]': {
        'type': 'string',
        'description': 'Model 0 Variant 0 name in English (Required for Variant 0)',
        'example': 'Midnight Black / 64GB'
    },
    'models[0][variants][0][variant_name_french]': {
        'type': 'string',
        'description': 'Model 0 Variant 0 name in French',
        'example': 'Noir Minuit / 64Go'
    },
    'models[0][variants][0][image]': {
        'type': 'string',
        'format': 'binary',
        'description': 'Model 0 Variant 0 image file upload'
    },
    'models[0][variants][0][price]': {
        'type': 'number',
        'format': 'float',
        'description': 'Model 0 Variant 0 selling price (Required)',
        'example': 79.99
    },
    'models[0][variants][0][vendor]': {
        'type': 'integer',
        'description': 'Vendor ID supplying Model 0 Variant 0',
        'example': 2
    },
    'models[0][variants][0][vendor_price]': {
        'type': 'number',
        'format': 'float',
        'description': 'Vendor cost price for Model 0 Variant 0',
        'example': 55.00
    },
    'models[0][variants][0][length]': {
        'type': 'number',
        'format': 'float',
        'description': 'Variant 0 specific length in cm (optional; falls back to product length)',
        'example': 18.5
    },
    'models[0][variants][0][width]': {
        'type': 'number',
        'format': 'float',
        'description': 'Variant 0 specific width in cm (optional; falls back to product width)',
        'example': 15.0
    },
    'models[0][variants][0][height]': {
        'type': 'number',
        'format': 'float',
        'description': 'Variant 0 specific height in cm (optional; falls back to product height)',
        'example': 7.5
    },
    'models[0][variants][0][weight]': {
        'type': 'number',
        'format': 'float',
        'description': 'Variant 0 specific weight in kg (optional; falls back to product weight)',
        'example': 0.35
    },
    'models[0][variants][0][carton_length]': {
        'type': 'number',
        'format': 'float',
        'description': 'Variant 0 carton length in cm',
        'example': 50.0
    },
    'models[0][variants][0][carton_width]': {
        'type': 'number',
        'format': 'float',
        'description': 'Variant 0 carton width in cm',
        'example': 40.0
    },
    'models[0][variants][0][carton_height]': {
        'type': 'number',
        'format': 'float',
        'description': 'Variant 0 carton height in cm',
        'example': 35.0
    },
    'models[0][variants][0][carton_weight]': {
        'type': 'number',
        'format': 'float',
        'description': 'Variant 0 carton weight in kg',
        'example': 12.5
    },

    # Model 0 -> Variant 1 (Example of 2nd variant)
    'models[0][variants][1][name]': {
        'type': 'string',
        'description': 'Model 0 Variant 1 name in English (Example of additional variant)',
        'example': 'Silver Platinum / 128GB'
    },
    'models[0][variants][1][variant_name_french]': {
        'type': 'string',
        'description': 'Model 0 Variant 1 name in French',
        'example': 'Argent Platine / 128Go'
    },
    'models[0][variants][1][price]': {
        'type': 'number',
        'format': 'float',
        'description': 'Model 0 Variant 1 selling price',
        'example': 89.99
    },
    'models[0][variants][1][vendor]': {
        'type': 'integer',
        'description': 'Vendor ID supplying Model 0 Variant 1',
        'example': 2
    },
    'models[0][variants][1][vendor_price]': {
        'type': 'number',
        'format': 'float',
        'description': 'Vendor cost price for Model 0 Variant 1',
        'example': 62.00
    },
}

PRODUCT_MODEL_VARIANT_UPDATE_PROPERTIES = {
    'id': {
        'type': 'integer',
        'description': 'Product ID to update (Required)',
        'example': 105
    },
    **PRODUCT_MODEL_VARIANT_CREATE_PROPERTIES,
}

class CodebaseInspector:
    def __init__(self, base_dir=None):
        if base_dir is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
        self.base_dir = base_dir
        self.apis_dir = os.path.join(base_dir, 'apis')
        self.urls_file = os.path.join(base_dir, 'urls.py')
        self.views_meta = {}
        self._index_all_views()

    def _index_all_views(self):
        if not os.path.exists(self.apis_dir):
            return

        for fname in os.listdir(self.apis_dir):
            if not fname.endswith('.py') or fname.startswith('__'):
                continue
            fpath = os.path.join(self.apis_dir, fname)
            try:
                with open(fpath, 'r', encoding='utf-8') as f:
                    content = f.read()
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        self.views_meta[node.name] = self._analyze_function(node, fname)
                    elif isinstance(node, ast.ClassDef):
                        self.views_meta[node.name] = self._analyze_class(node, fname)
            except Exception as e:
                logger.warning(f"Error parsing {fname} in swagger inspector: {e}")

    def _analyze_function(self, node, fname):
        methods = set()
        query_params = set()
        body_params = set()
        file_params = set()

        doc = ast.get_docstring(node) or ""
        payload_vars = {'python_data', 'data', 'payload', 'body_data', 'request_data', 'json_data', 'post_data'}

        for sub in ast.walk(node):
            if isinstance(sub, ast.Compare):
                try:
                    left_str = ast.unparse(sub.left)
                except Exception:
                    left_str = ""
                if 'request.method' in left_str or 'method' in left_str:
                    for comp in sub.comparators:
                        if isinstance(comp, ast.Constant) and isinstance(comp.value, str):
                            m = comp.value.upper()
                            if m in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS']:
                                methods.add(m)
                        elif isinstance(comp, (ast.List, ast.Tuple)):
                            for elt in comp.elts:
                                if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                                    m = elt.value.upper()
                                    if m in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS']:
                                        methods.add(m)

            if isinstance(sub, ast.Call):
                if isinstance(sub.func, ast.Attribute) and sub.func.attr == 'get':
                    try:
                        caller = ast.unparse(sub.func.value)
                    except Exception:
                        caller = ""

                    if sub.args and isinstance(sub.args[0], ast.Constant):
                        pname = clean_param_name(sub.args[0].value)
                        if pname:
                            if 'GET' in caller:
                                query_params.add(pname)
                            elif 'FILES' in caller:
                                file_params.add(pname)
                            elif 'POST' in caller:
                                body_params.add(pname)
                            elif any(v in caller for v in payload_vars):
                                body_params.add(pname)
                            elif 'request' in caller:
                                body_params.add(pname)

            if isinstance(sub, ast.Subscript):
                try:
                    caller = ast.unparse(sub.value)
                except Exception:
                    caller = ""
                slice_node = sub.slice
                if isinstance(slice_node, ast.Constant):
                    pname = clean_param_name(slice_node.value)
                    if pname:
                        if 'GET' in caller:
                            query_params.add(pname)
                        elif 'FILES' in caller:
                            file_params.add(pname)
                        elif 'POST' in caller or any(v in caller for v in payload_vars):
                            body_params.add(pname)

        if not methods:
            if file_params or body_params:
                methods.add('POST')
            elif query_params:
                methods.add('GET')
            else:
                methods.add('POST')

        module_name = MODULE_MAPPING.get(fname, fname.replace('_views.py', '').replace('_', ' ').title())

        return {
            'file': fname,
            'module': module_name,
            'methods': sorted(list(methods)),
            'query_params': sorted(list(query_params)),
            'body_params': sorted(list(body_params)),
            'file_params': sorted(list(file_params)),
            'doc': doc.strip()
        }

    def _analyze_class(self, node, fname):
        module_name = MODULE_MAPPING.get(fname, fname.replace('_views.py', '').replace('_', ' ').title())
        return {
            'file': fname,
            'module': module_name,
            'methods': ['GET', 'POST'],
            'query_params': [],
            'body_params': [],
            'file_params': [],
            'doc': (ast.get_docstring(node) or "").strip()
        }

    def get_endpoints(self):
        endpoints = []
        if not os.path.exists(self.urls_file):
            return endpoints

        with open(self.urls_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        for line in lines:
            line = line.strip()
            if line.startswith('#'):
                continue
            m = re.search(r"path\s*\(\s*['\"]([^'\"]+)['\"]\s*,\s*([a-zA-Z0-9_]+)", line)
            if m:
                raw_path = m.group(1)
                view_name = m.group(2)

                if any(x in raw_path for x in ['swagger', 'schema', 'redoc', 'docs']):
                    continue

                full_path = '/' + raw_path if not raw_path.startswith('/') else raw_path
                meta = self.views_meta.get(view_name)
                if not meta:
                    meta = {
                        'file': 'unknown',
                        'module': 'General APIs',
                        'methods': ['POST'],
                        'query_params': [],
                        'body_params': [],
                        'file_params': [],
                        'doc': ''
                    }

                endpoints.append({
                    'path': full_path,
                    'view_name': view_name,
                    'meta': meta
                })

        return endpoints


def classify_auth_tier(path, view_name, module):
    """
    Classifies endpoint into:
    - 'token_required': Requires Authorization: Bearer <access_token>
    - 'dual_mode': Works without token as Guest; enriched with token as User
    - 'public': Public / Guest access
    """
    if path in DUAL_MODE_PATHS:
        return 'dual_mode', DUAL_MODE_PATHS[path]

    if path in TOKEN_REQUIRED_PATHS:
        return 'token_required', 'This endpoint requires an active User Access Token in the Authorization header: `Authorization: Bearer <access_token>`.'

    if path in PUBLIC_PATHS:
        return 'public', 'Public API accessible without an access token.'

    # Fallback heuristics for admin / vendor endpoints
    if 'admin' in path or 'admin' in view_name or module == 'Admin Management':
        if 'login' in path:
            return 'public', 'Public Admin Login endpoint.'
        return 'token_required', 'Requires Admin Authentication Token.'

    if 'vendor' in path or 'vendor' in view_name or module == 'Vendor Management':
        if 'login' in path or 'register' in path or 'credentials' in path:
            return 'public', 'Public Vendor Login / Registration endpoint.'
        return 'token_required', 'Requires Vendor Authentication Token.'

    return 'public', 'Public endpoint.'


def build_openapi_spec(base_url=""):
    inspector = CodebaseInspector()
    endpoints = inspector.get_endpoints()

    tags_dict = {}
    for mod_name, desc in MODULE_DESCRIPTIONS.items():
        tags_dict[mod_name] = {'name': mod_name, 'description': desc}

    paths = {}
    total_token_required = 0
    total_dual_mode = 0
    total_public = 0

    for ep in endpoints:
        path = ep['path']
        view_name = ep['view_name']
        meta = ep['meta']
        mod_tag = meta['module']

        auth_tier, auth_note = classify_auth_tier(path, view_name, mod_tag)
        if auth_tier == 'token_required':
            total_token_required += 1
        elif auth_tier == 'dual_mode':
            total_dual_mode += 1
        else:
            total_public += 1

        if mod_tag not in tags_dict:
            tags_dict[mod_tag] = {'name': mod_tag, 'description': f'Endpoints in {mod_tag}'}

        base_summary = format_summary(view_name)
        if auth_tier == 'token_required':
            summary = f"🔒 {base_summary}"
        elif auth_tier == 'dual_mode':
            summary = f"🔀 {base_summary} [Dual-Mode]"
        else:
            summary = f"🔓 {base_summary}"

        description_lines = []
        if meta['doc']:
            description_lines.append(meta['doc'])
        else:
            description_lines.append(f"API endpoint for {base_summary} in {mod_tag}.")

        # Add clear security notice in description
        if auth_tier == 'token_required':
            description_lines.append(f"\n\n> 🔒 **Authentication Required**: `{auth_note}`")
        elif auth_tier == 'dual_mode':
            description_lines.append(f"\n\n> 🔀 **Dual-Mode API** (Guest & Authenticated):\n> {auth_note}")
        else:
            description_lines.append(f"\n\n> 🔓 **Public / Guest API**: `{auth_note}`")

        description = "\n".join(description_lines)

        if path not in paths:
            paths[path] = {}

        for method in meta['methods']:
            method_key = method.lower()
            operation = {
                'tags': [mod_tag],
                'summary': summary,
                'description': description,
                'operationId': f"{method_key}_{view_name}",
                'parameters': [],
                'responses': {
                    '200': {
                        'description': 'Successful response',
                        'content': {
                            'application/json': {
                                'schema': {
                                    'type': 'object',
                                    'properties': {
                                        'status': {'type': 'boolean', 'example': True},
                                        'message': {'type': 'string', 'example': 'Operation completed successfully'},
                                        'data': {'type': 'object'}
                                    }
                                }
                            }
                        }
                    },
                    '400': {
                        'description': 'Bad Request / Parameter Validation Error'
                    },
                    '500': {
                        'description': 'Internal Server Error'
                    }
                }
            }

            # Custom response schemas for Delivery Day Detail endpoints
            if path == '/api/delivery_day_detail_list_admin/':
                operation['responses']['200'] = {
                    'description': 'List of configured delivery days per country',
                    'content': {
                        'application/json': {
                            'schema': {
                                'type': 'object',
                                'properties': {
                                    'data': {
                                        'type': 'array',
                                        'items': {'$ref': '#/components/schemas/DeliveryDayDetail'}
                                    },
                                    'total_count': {'type': 'integer', 'example': 1},
                                    'message': {'type': 'string', 'example': 'Delivery day details fetched successfully.'}
                                }
                            }
                        }
                    }
                }
            elif path in ['/api/delivery_day_detail_add_admin/', '/api/delivery_day_detail_update_admin/', '/api/all_delivery_days_list/', '/api/delivery_days_update/']:
                operation['responses']['200'] = {
                    'description': 'Delivery day configuration record',
                    'content': {
                        'application/json': {
                            'schema': {
                                'type': 'object',
                                'properties': {
                                    'message': {'type': 'string', 'example': 'Delivery days updated successfully.'},
                                    'data': {'$ref': '#/components/schemas/DeliveryDayDetail'}
                                }
                            }
                        }
                    }
                }
            elif path in ['/api/delivery_day_available_countries_admin/', '/api/available_countries_for_delivery_day_admin/']:
                operation['responses']['200'] = {
                    'description': 'List of available countries (excluding countries that already have a delivery day configuration)',
                    'content': {
                        'application/json': {
                            'schema': {
                                'type': 'object',
                                'properties': {
                                    'data': {
                                        'type': 'array',
                                        'items': {'$ref': '#/components/schemas/AvailableCountryForDelivery'}
                                    },
                                    'total_count': {'type': 'integer', 'example': 50},
                                    'message': {'type': 'string', 'example': 'Available countries fetched successfully.'}
                                }
                            }
                        }
                    }
                }
            elif path == '/api/delivery_day_detail_delete_admin/':
                operation['responses']['200'] = {
                    'description': 'Deletion confirmation',
                    'content': {
                        'application/json': {
                            'schema': {
                                'type': 'object',
                                'properties': {
                                    'message': {'type': 'string', 'example': 'Delivery day detail deleted successfully.'}
                                }
                            }
                        }
                    }
                }
            elif path in ['/api/v1/app/version-check/', '/api/v1/app/version-check', '/api/app_version_check/']:
                operation['responses']['200'] = {
                    'description': 'SemVer version evaluation and update recommendations',
                    'content': {
                        'application/json': {
                            'schema': {
                                'type': 'object',
                                'properties': {
                                    'status': {'type': 'boolean', 'example': True},
                                    'message': {'type': 'string', 'example': 'Version check retrieved successfully'},
                                    'data': {'$ref': '#/components/schemas/AppVersionCheckData'}
                                }
                            }
                        }
                    }
                }
            elif path in ['/api/v1/admin/app-versions/', '/api/v1/admin/app-versions', '/api/admin_app_versions/']:
                if method_key == 'get':
                    operation['responses']['200'] = {
                        'description': 'Current version settings for Android and iOS platforms',
                        'content': {
                            'application/json': {
                                'schema': {
                                    'type': 'object',
                                    'properties': {
                                        'status': {'type': 'boolean', 'example': True},
                                        'message': {'type': 'string', 'example': 'App version settings fetched successfully'},
                                        'data': {
                                            'type': 'array',
                                            'items': {'$ref': '#/components/schemas/AppVersionSetting'}
                                        }
                                    }
                                }
                            }
                        }
                    }
                else:
                    operation['responses']['200'] = {
                        'description': 'Updated version setting for the specified platform',
                        'content': {
                            'application/json': {
                                'schema': {
                                    'type': 'object',
                                    'properties': {
                                        'status': {'type': 'boolean', 'example': True},
                                        'message': {'type': 'string', 'example': 'App version settings updated successfully'},
                                        'data': {'$ref': '#/components/schemas/AppVersionSetting'}
                                    }
                                }
                            }
                        }
                    }

            # Security requirement configuration
            if auth_tier == 'token_required':
                operation['security'] = [{'BearerAuth': []}]
                operation['responses']['401'] = {
                    'description': 'Unauthorized - Missing or invalid `Authorization: Bearer <access_token>` header.'
                }
            else:
                operation['security'] = []

            # Custom tags for filtering
            operation['x-auth-tier'] = auth_tier

            # Query parameters
            for qp in meta['query_params']:
                p_schema = guess_type_and_schema(qp)
                operation['parameters'].append({
                    'name': qp,
                    'in': 'query',
                    'required': False,
                    'description': p_schema.get('description', qp),
                    'schema': p_schema
                })

            # Request Body (POST / PUT / PATCH)
            if method_key in ['post', 'put', 'patch']:
                all_body = meta['body_params']
                files = meta['file_params']

                # Manual enrichments for specific endpoints
                if path == '/api/cart_list/':
                    if 'promocodes' not in all_body:
                        all_body.append('promocodes')
                if path == '/api/order_create/':
                    if 'promocodes' not in all_body:
                        all_body.append('promocodes')
                if path == '/api/token_refresh/':
                    all_body = ['refresh_token']
                if path == '/api/delivery_day_detail_add_admin/':
                    all_body = ['country', 'express_delivery', 'air_delivery', 'ship_delivery']
                if path in ['/api/delivery_day_detail_update_admin/', '/api/delivery_days_update/']:
                    all_body = ['id', 'country', 'express_delivery', 'air_delivery', 'ship_delivery']
                if path == '/api/delivery_day_detail_delete_admin/':
                    all_body = ['id']
                if path == '/api/delivery_day_detail_list_admin/':
                    all_body = ['search', 'country']
                if path == '/api/all_delivery_days_list/':
                    all_body = ['country']
                if path in ['/api/v1/app/version-check/', '/api/v1/app/version-check', '/api/app_version_check/']:
                    all_body = ['platform', 'app_version']
                if path in ['/api/v1/admin/app-versions/', '/api/v1/admin/app-versions', '/api/admin_app_versions/']:
                    if method_key in ['post', 'put']:
                        all_body = [
                            'platform', 'latest_version', 'min_supported_version',
                            'is_force_update', 'update_title', 'release_notes',
                            'store_url', 'is_maintenance_mode', 'maintenance_message'
                        ]
                    else:
                        all_body = []

                if path == '/api/product_model_variant_create/':
                    operation['summary'] = "📦 Create Product with Models, Variants & Specifications (Multipart)"
                    operation['description'] = PRODUCT_MODEL_VARIANT_CREATE_DESCRIPTION
                    operation['requestBody'] = {
                        'required': True,
                        'description': 'Product creation payload with multipart form-data including base details, JSON specifications, media files, and nested models/variants.',
                        'content': {
                            'multipart/form-data': {
                                'schema': {
                                    'type': 'object',
                                    'required': [
                                        'product_name',
                                        'product_name_french',
                                        'category',
                                        'subcategory',
                                        'vendor',
                                        'other_specification',
                                        'models[0][name]',
                                        'models[0][variants][0][name]',
                                        'models[0][variants][0][price]'
                                    ],
                                    'properties': PRODUCT_MODEL_VARIANT_CREATE_PROPERTIES
                                }
                            }
                        }
                    }
                    operation['responses']['200'] = {
                        'description': 'Product created successfully along with models, variants, specifications, and vector embeddings.',
                        'content': {
                            'application/json': {
                                'schema': {
                                    'type': 'object',
                                    'properties': {
                                        'message': {'type': 'string', 'example': 'Project create successfully.'}
                                    }
                                }
                            }
                        }
                    }
                elif path == '/api/product_model_variant_update/':
                    operation['summary'] = "📦 Update Product with Models, Variants & Specifications (Multipart)"
                    operation['description'] = PRODUCT_MODEL_VARIANT_UPDATE_DESCRIPTION
                    operation['requestBody'] = {
                        'required': True,
                        'description': 'Product update payload with multipart form-data including product ID, base details, JSON specifications, media files, and nested models/variants.',
                        'content': {
                            'multipart/form-data': {
                                'schema': {
                                    'type': 'object',
                                    'required': ['id', 'product_name', 'product_name_french', 'category', 'subcategory'],
                                    'properties': PRODUCT_MODEL_VARIANT_UPDATE_PROPERTIES
                                }
                            }
                        }
                    }
                    operation['responses']['200'] = {
                        'description': 'Product updated successfully',
                        'content': {
                            'application/json': {
                                'schema': {
                                    'type': 'object',
                                    'properties': {
                                        'message': {'type': 'string', 'example': 'Project update successfully.'}
                                    }
                                }
                            }
                        }
                    }
                elif files or all_body:
                    properties = {}
                    for bp in all_body:
                        properties[bp] = guess_type_and_schema(bp)
                    for fp in files:
                        properties[fp] = guess_type_and_schema(fp)

                    if files:
                        operation['requestBody'] = {
                            'required': True,
                            'content': {
                                'multipart/form-data': {
                                    'schema': {
                                        'type': 'object',
                                        'properties': properties
                                    }
                                }
                            }
                        }
                    else:
                        operation['requestBody'] = {
                            'required': True,
                            'content': {
                                'application/json': {
                                    'schema': {
                                        'type': 'object',
                                        'properties': properties
                                    }
                                },
                                'multipart/form-data': {
                                    'schema': {
                                        'type': 'object',
                                        'properties': properties
                                    }
                                }
                            }
                        }

            paths[path][method_key] = operation

    spec = {
        'openapi': '3.0.3',
        'info': {
            'title': 'Diaba E-Commerce REST API',
            'version': '1.0.0',
            'description': (
                'Comprehensive OpenAPI / Swagger documentation for the Diaba E-Commerce platform.\n\n'
                '### 🔐 Authentication Matrix:\n'
                f'- **🔒 Token Required ({total_token_required} APIs)**: Requires `Authorization: Bearer <access_token>`.\n'
                f'- **🔓 Public / Guest ({total_public} APIs)**: Accessible without an access token.\n'
                f'- **🔀 Dual-Mode ({total_dual_mode} APIs)**: Works for anonymous guests, and enriches data with personalized context when an access token is provided.\n\n'
                '### 🔄 Silent Refresh Flow:\n'
                'When any authenticated endpoint returns HTTP `401 Unauthorized`, send the stored `refresh_token` '
                'to `POST /api/token_refresh/` to receive a new `access_token` seamlessly without interrupting the user session.'
            ),
            'contact': {
                'name': 'Diaba Technical Support',
                'email': 'support@icode49solution.com'
            }
        },
        'servers': [
            {'url': '/', 'description': 'Current Environment Server'},
            {'url': 'https://api-diaba.icode49solution.com', 'description': 'Live Production API Server'}
        ],
        'tags': sorted(list(tags_dict.values()), key=lambda t: t['name']),
        'paths': paths,
        'components': {
            'schemas': {
                'DeliveryDayDetail': {
                    'type': 'object',
                    'properties': {
                        'id': {'type': 'integer', 'example': 1},
                        'country': {'type': 'integer', 'example': 1, 'description': 'CountryWithCurrency ID'},
                        'country_name': {'type': 'string', 'example': 'Egypt'},
                        'country_calling_code': {'type': 'string', 'example': '+20'},
                        'country_iso_alphaTwo_key': {'type': 'string', 'example': 'EG'},
                        'currency_code': {'type': 'string', 'example': 'EGP'},
                        'currency_symbol': {'type': 'string', 'example': 'E£'},
                        'express_delivery': {'type': 'integer', 'example': 10, 'description': 'Express delivery duration in days'},
                        'air_delivery': {'type': 'integer', 'example': 25, 'description': 'Air delivery duration in days'},
                        'ship_delivery': {'type': 'integer', 'example': 90, 'description': 'Ship delivery duration in days'}
                    }
                },
                'AvailableCountryForDelivery': {
                    'type': 'object',
                    'properties': {
                        'id': {'type': 'integer', 'example': 1},
                        'country_name': {'type': 'string', 'example': 'Senegal'},
                        'country_calling_code': {'type': 'string', 'example': '+221'},
                        'country_iso_alphaTwo_key': {'type': 'string', 'example': 'SN'},
                        'currency_code': {'type': 'string', 'example': 'XOF'},
                        'currency_symbol': {'type': 'string', 'example': 'CFA'},
                        'price_by_air': {'type': 'string', 'example': '0.00'},
                        'price_by_ship': {'type': 'string', 'example': '0.00'},
                        'express_shipping': {'type': 'string', 'example': '0.00'},
                        'status': {'type': 'string', 'example': 'Active'}
                    }
                },
                'AppVersionCheckData': {
                    'type': 'object',
                    'properties': {
                        'update_type': {
                            'type': 'string',
                            'enum': ['none', 'optional', 'force', 'maintenance'],
                            'example': 'force',
                            'description': 'Update urgency classification based on SemVer comparison'
                        },
                        'is_maintenance_mode': {'type': 'boolean', 'example': False},
                        'maintenance_message': {'type': 'string', 'example': ''},
                        'latest_version': {'type': 'string', 'example': '1.2.0'},
                        'min_supported_version': {'type': 'string', 'example': '1.1.0'},
                        'update_title': {'type': 'string', 'example': 'Update Available'},
                        'release_notes': {'type': 'string', 'example': 'We fixed critical payment issues and improved app speed.'},
                        'store_url': {'type': 'string', 'example': 'https://apps.apple.com/app/id6754025301'}
                    }
                },
                'AppVersionSetting': {
                    'type': 'object',
                    'properties': {
                        'id': {'type': 'integer', 'example': 1},
                        'platform': {'type': 'string', 'enum': ['android', 'ios'], 'example': 'android'},
                        'latest_version': {'type': 'string', 'example': '1.2.0'},
                        'min_supported_version': {'type': 'string', 'example': '1.1.0'},
                        'is_force_update': {'type': 'boolean', 'example': True},
                        'update_title': {'type': 'string', 'example': 'Mandatory Update'},
                        'release_notes': {'type': 'string', 'example': 'Please update to continue using the app.'},
                        'store_url': {'type': 'string', 'example': 'https://play.google.com/store/apps/details?id=com.diaba.ecommerce'},
                        'is_maintenance_mode': {'type': 'boolean', 'example': False},
                        'maintenance_message': {'type': 'string', 'example': ''},
                        'updated_at': {'type': 'string', 'format': 'date-time', 'example': '2026-11-24T15:00:00Z'}
                    }
                },
                'ProductSpecificationItem': {
                    'type': 'object',
                    'required': ['key', 'key_french', 'value', 'value_french'],
                    'properties': {
                        'key': {'type': 'string', 'example': 'Battery Life', 'description': 'Specification attribute in English'},
                        'key_french': {'type': 'string', 'example': 'Autonomie', 'description': 'Specification attribute in French'},
                        'value': {'type': 'string', 'example': '30 Hours', 'description': 'Specification value in English'},
                        'value_french': {'type': 'string', 'example': '30 Heures', 'description': 'Specification value in French'}
                    }
                },
                'ProductModelVariantCreateResponse': {
                    'type': 'object',
                    'properties': {
                        'message': {'type': 'string', 'example': 'Project create successfully.'}
                    }
                }
            },
            'securitySchemes': {
                'BearerAuth': {
                    'type': 'http',
                    'scheme': 'bearer',
                    'bearerFormat': 'JWT',
                    'description': 'Enter User JWT Access Token: Bearer <access_token>'
                },
                'ApiKeyAuth': {
                    'type': 'apiKey',
                    'in': 'header',
                    'name': 'Authorization',
                    'description': 'Custom Token or Authorization header'
                }
            }
        }
    }

    return spec


def get_cached_spec():
    global _CACHED_SPEC
    if _CACHED_SPEC is None:
        _CACHED_SPEC = build_openapi_spec()
    return _CACHED_SPEC


@csrf_exempt
def openapi_schema_json(request):
    """Returns the OpenAPI 3.0 specification in JSON format."""
    spec = get_cached_spec()
    return JsonResponse(spec, json_dumps_params={'indent': 2})


@csrf_exempt
def openapi_schema_refresh(request):
    """Force refreshes the OpenAPI cached specification."""
    global _CACHED_SPEC
    _CACHED_SPEC = build_openapi_spec()
    return JsonResponse({'message': 'Swagger OpenAPI schema refreshed successfully', 'endpoints_count': len(_CACHED_SPEC['paths'])})


@csrf_exempt
def swagger_ui_html(request):
    """Renders the interactive Swagger UI interface with auth filters and quick controls."""
    html = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Diaba API Documentation</title>
  <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5.11.0/swagger-ui.css" />
  <link rel="shortcut icon" href="https://fastapi.tiangolo.com/img/favicon.png" />
  <style>
    body {
      margin: 0;
      padding: 0;
      background: #f8fafc;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    }
    .topbar {
      background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%) !important;
      padding: 14px 28px !important;
      box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .topbar-wrapper {
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 16px;
    }
    .topbar-wrapper .link {
      display: flex;
      align-items: center;
      text-decoration: none;
      color: #38bdf8 !important;
      font-weight: 700;
      font-size: 1.25rem;
      letter-spacing: 0.5px;
    }
    .topbar-wrapper .link::before {
      content: "🛍️ ";
      font-size: 1.5rem;
      margin-right: 8px;
    }
    .topbar-tagline {
      color: #94a3b8;
      font-size: 0.875rem;
      font-weight: 400;
      margin-left: 12px;
    }
    .auth-filter-bar {
      display: flex;
      gap: 8px;
      align-items: center;
    }
    .auth-btn {
      background: rgba(255, 255, 255, 0.12);
      color: #f1f5f9;
      border: 1px solid rgba(255, 255, 255, 0.2);
      padding: 6px 14px;
      border-radius: 20px;
      cursor: pointer;
      font-size: 0.825rem;
      font-weight: 600;
      transition: all 0.2s ease;
    }
    .auth-btn:hover, .auth-btn.active {
      background: #0284c7;
      border-color: #38bdf8;
      color: #ffffff;
      box-shadow: 0 2px 4px rgba(2, 132, 199, 0.4);
    }
    .quick-links {
      display: flex;
      gap: 10px;
      align-items: center;
    }
    .quick-links a {
      color: #cbd5e1;
      text-decoration: none;
      font-size: 0.825rem;
      padding: 6px 12px;
      border-radius: 6px;
      background: rgba(255, 255, 255, 0.08);
      transition: background 0.2s;
    }
    .quick-links a:hover {
      background: rgba(255, 255, 255, 0.2);
      color: #ffffff;
    }
    .swagger-ui .info {
      margin: 24px 0 16px 0;
    }
    .swagger-ui .info .title {
      font-family: inherit;
      color: #0f172a;
      font-weight: 800;
    }
    .swagger-ui .scheme-container {
      background: #ffffff;
      padding: 16px 24px;
      margin-bottom: 24px;
      border-radius: 8px;
      box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05);
    }
    .swagger-ui .opblock {
      border-radius: 8px !important;
      box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
      margin-bottom: 12px !important;
      transition: all 0.15s ease-in-out;
    }
    .swagger-ui .opblock:hover {
      box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .swagger-ui .opblock-tag {
      font-size: 1.15rem !important;
      font-weight: 700 !important;
      color: #1e293b !important;
      border-bottom: 2px solid #e2e8f0 !important;
      padding: 14px 4px !important;
      margin-top: 24px !important;
    }
    .swagger-ui .btn.authorize {
      color: #0284c7;
      border-color: #0284c7;
    }
    .swagger-ui .btn.authorize svg {
      fill: #0284c7;
    }
  </style>
</head>
<body>
<div id="swagger-ui"></div>
<script src="https://unpkg.com/swagger-ui-dist@5.11.0/swagger-ui-bundle.js"></script>
<script src="https://unpkg.com/swagger-ui-dist@5.11.0/swagger-ui-standalone-preset.js"></script>
<script>
window.onload = function() {
  const ui = SwaggerUIBundle({
    url: "/api/schema.json",
    dom_id: '#swagger-ui',
    deepLinking: true,
    presets: [
      SwaggerUIBundle.presets.apis,
      SwaggerUIStandalonePreset
    ],
    plugins: [
      SwaggerUIBundle.plugins.DownloadUrl
    ],
    layout: "StandaloneLayout",
    docExpansion: "none",
    filter: true,
    showExtensions: true,
    showCommonExtensions: true,
    defaultModelsExpandDepth: 1,
    persistAuthorization: true,
    displayRequestDuration: true
  });

  setTimeout(() => {
    const topbar = document.querySelector('.topbar-wrapper');
    if (topbar) {
      topbar.innerHTML = `
        <div style="display:flex;align-items:center;">
          <a class="link" href="/swagger/">
            <span>Diaba API</span>
            <span class="topbar-tagline">| Module-Wise Documentation & Sandbox</span>
          </a>
        </div>
        <div class="auth-filter-bar">
          <button class="auth-btn active" onclick="filterAuth('all', this)">All APIs</button>
          <button class="auth-btn" onclick="filterAuth('token_required', this)">🔒 Token Required</button>
          <button class="auth-btn" onclick="filterAuth('public', this)">🔓 Public / Guest</button>
          <button class="auth-btn" onclick="filterAuth('dual_mode', this)">🔀 Dual-Mode</button>
        </div>
        <div class="quick-links">
          <a href="/redoc/" target="_blank">📖 ReDoc View</a>
          <a href="/api/schema.json" target="_blank">📄 OpenAPI JSON</a>
          <a href="/api/schema/refresh/" onclick="event.preventDefault(); fetch('/api/schema/refresh/').then(r=>r.json()).then(d=>{alert('Schema Refreshed! Total endpoints: ' + d.endpoints_count); location.reload();});">🔄 Refresh</a>
        </div>
      `;
    }
  }, 200);

  window.ui = ui;
};

function filterAuth(type, btn) {
  document.querySelectorAll('.auth-btn').forEach(b => b.classList.remove('active'));
  if (btn) btn.classList.add('active');

  const opblocks = document.querySelectorAll('.opblock');
  opblocks.forEach(block => {
    const summary = block.querySelector('.opblock-summary-description')?.innerText || 
                    block.querySelector('.opblock-summary-path')?.innerText || '';
    if (type === 'all') {
      block.style.display = '';
    } else if (type === 'token_required') {
      block.style.display = summary.includes('🔒') ? '' : 'none';
    } else if (type === 'public') {
      block.style.display = summary.includes('🔓') ? '' : 'none';
    } else if (type === 'dual_mode') {
      block.style.display = summary.includes('🔀') ? '' : 'none';
    }
  });
}
</script>
</body>
</html>
"""
    return HttpResponse(html, content_type='text/html')


@csrf_exempt
def redoc_ui_html(request):
    """Renders the ReDoc documentation interface."""
    html = """<!DOCTYPE html>
<html>
  <head>
    <title>Diaba API Documentation - ReDoc</title>
    <meta charset="utf-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://fonts.googleapis.com/css?family=Montserrat:300,400,700|Roboto:300,400,700" rel="stylesheet">
    <link rel="shortcut icon" href="https://fastapi.tiangolo.com/img/favicon.png" />
    <style>
      body {
        margin: 0;
        padding: 0;
      }
    </style>
  </head>
  <body>
    <redoc spec-url='/api/schema.json'></redoc>
    <script src="https://cdn.redoc.ly/redoc/latest/bundles/redoc.standalone.js"> </script>
  </body>
</html>
"""
    return HttpResponse(html, content_type='text/html')
