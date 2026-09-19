from django.views.static import serve
from django.conf.urls.static import static
from django.urls import path
# from diabaApp import views 

from django.conf import settings

from diabaApp.apis.admin_views import *
from diabaApp.apis.analytics_views import *
from diabaApp.apis.auth_views import *
from diabaApp.apis.cargo_views import *
from diabaApp.apis.category_views import *
from diabaApp.apis.chat_views import *
from diabaApp.apis.currency_views import *
from diabaApp.apis.customer_views import *
from diabaApp.apis.graph_views import *
from diabaApp.apis.influencer_views import *
from diabaApp.apis.inquiry_views import *
from diabaApp.apis.money_network_views import *
from diabaApp.apis.order_views import *
from diabaApp.apis.payment_views import *
from diabaApp.apis.product_request_views import *
from diabaApp.apis.product_views import *
from diabaApp.apis.report_views import *
from diabaApp.apis.review_views import *
from diabaApp.apis.settings_views import *
from diabaApp.apis.shipping_views import *
from diabaApp.apis.testing_views import *
from diabaApp.apis.transaction_views import *
from diabaApp.apis.utility_views import *
from diabaApp.apis.vendor_views import *
from diabaApp.apis.warehouse_views import *
from diabaApp.apis.wishlist_views import *
from diabaApp.apis.banner_views import *
from diabaApp.apis.container_views import *

urlpatterns = [

    path('api/app_dyanmic_setting_update/',app_dyanmic_setting_update, name='app_dyanmic_setting_update'), #done
    path('api/app_setting/',app_setting, name='app_setting'), #done
    path('api/admin_app_dynamic_setting/',admin_app_dynamic_setting, name='admin_app_dynamic_setting'), #done

    path('api/admin_login/',admin_login, name='admin_login'), #done
    
    ## Vendor Details
    path('api/vendor_register/',vendor_register, name='vendor_register'),  #done
    path('api/vendor_login/',vendor_login, name='vendor_login'), #done
    path('api/vendor_update/',vendor_update, name='vendor_update'),  #done
    path('api/all_vendor_list/',all_vendor_list, name='all_vendor_list'),  #done
    path('api/vendor_approve_reject/',vendor_approve_reject, name='vendor_approve_reject'),  #done
    path('api/vendor_list_category_subcategory/',vendor_list_category_subcategory, name='vendor_list_category_subcategory'),  #done
    path('api/vendor_name_list/',vendor_name_list, name='vendor_name_list'),  #done
    path('api/variant_vendor_list/',variant_vendor_list, name='variant_vendor_list'),#done
    path('api/vendor_detail_admin/',vendor_detail_admin, name='vendor_detail_admin'), #done
    path('api/vendor_product_admin/',vendor_product_admin, name='vendor_product_admin'), #done
    path('api/pending_order_vendor_count/',pending_order_vendor_count, name='pending_order_vendor_count'),  #done
    
    path('api/vendor_credentials_resend/',vendor_credentials_resend, name='vendor_credentials_resend'),  #done

    ## Category 
    path('api/category_create/',category_create, name='category_create'),  #done
    path('api/all_category_list/',all_category_list, name='all_category_list'),  #done
    path('api/category_with_subcategory_data/',category_with_subcategory_data, name='category_with_subcategory_data'),  #done
    path('api/category_update/',category_update, name='category_update'), #done
    path('api/category_delete/',category_delete, name='category_delete'), #done
    path('api/category_status_update/',category_status_update, name='category_status_update'),  #done
    



    ### Subcategory
    path('api/subcategory_create/',subcategory_create, name='subcategory_create'), #done
    path('api/all_subcategory_list/',all_subcategory_list, name='all_subcategory_list'), #done
    path('api/subcategory_update/',subcategory_update, name='subcategory_update'), #done
    path('api/subcategory_delete/',subcategory_delete, name='subcategory_delete'), #done
    path('api/subcategory_status_update/',subcategory_status_update, name='subcategory_status_update'),  #done
    

    ### Super subcategory
    path('api/super_subcategory_create/',super_subcategory_create, name='super_subcategory_create'), #done
    path('api/all_super_subcategory_list/',all_super_subcategory_list, name='all_super_subcategory_list'), #done
    
    ### Product 
    # path('api/product_create/',product_create, name='product_create'),
    path('api/all_product_list/',all_product_list, name='all_product_list'), #done
    path('api/chat_agent_product_list/',chat_agent_product_list, name='chat_agent_product_list'), #done
    path('api/vendor_search_product/',vendor_search_product, name='vendor_search_product'), #done
    path('api/vendor_product_price_create/',vendor_product_price_create, name='vendor_product_price_create'), #done
    path('api/vendor_apply_product_price/',vendor_apply_product_price, name='vendor_apply_product_price'), #done
    
    path('api/product_detail_admin/',product_detail_admin, name='product_detail_admin'), #done
    path('api/product_list_admin/',product_list_admin, name='product_list_admin'), #done
    path('api/product_detail_vendor/',product_detail_vendor, name='product_detail_vendor'), #done
    path('api/vendor_product_search/',vendor_product_search, name='vendor_product_search'), #done
    path('api/product_verification_update/',product_verification_update, name='product_verification_update'), #done
    path('api/pending_product_verification_list_admin/',pending_product_verification_list_admin, name='pending_product_verification_list_admin'), #done
    path('api/vendor_detail/',vendor_detail, name='vendor_detail'), #done
    path('api/product_model_status_update/',product_model_status_update, name='product_model_status_update'), #done
    path('api/product_variant_status_update/',product_variant_status_update, name='product_variant_status_update'), #done
    path('api/product_vendor_status_update/',product_vendor_status_update, name='product_vendor_status_update'), #done
    path('api/product_detail_app/',product_detail_app, name='product_detail_app'), #done
    path('api/subcategory_wise_product_list/',subcategory_wise_product_list, name='subcategory_wise_product_list'), #done
    path('api/product_search/',product_search, name='product_search'), #done
    path('api/product_search_suggestion/',product_search_suggestion, name='product_search_suggestion'), #done
    path('api/product_search_by_tag/',product_search_by_tag, name='product_search_by_tag'), #done
    path('api/product_list_tag_result/',product_list_tag_result, name='product_list_tag_result'), #done
    

    path('api/model_update/',model_update, name='model_update'), #done
    path('api/variant_update/',variant_update, name='variant_update'), #done
    path('api/vendor_variant_update/',vendor_variant_update, name='vendor_variant_update'), #done
    path('api/product_delete/',product_delete, name='product_delete'), #done
    path('api/product_status_update/',product_status_update, name='product_status_update'), #done


    


    ### Product Request
    path('api/product_request_create/',product_request_create, name='product_request_create'), #done
    path('api/vendor_product_request_list/',vendor_product_request_list, name='vendor_product_request_list'), #done
    path('api/all_product_request_list/',all_product_request_list, name='all_product_request_list'), #done
    path('api/product_request_status_update/',product_request_status_update, name='product_request_status_update'), #done

    
    ### TEST
    path('api/google_transalate/',google_transalate, name='google_transalate'), #done


    ### PRODUCT CREATE
    path('api/product_model_variant_create/',product_model_variant_create, name='product_model_variant_create'), #done
    path('api/all_product_model_variant_list_admin/',all_product_model_variant_list_admin, name='all_product_model_variant_list_admin'), #done
    path('api/product_model_variant_update/',product_model_variant_update, name='product_model_variant_update'), #done
    path('api/product_delete/',product_delete, name='product_delete'), #done


    ### Customer 
    path('api/customer_register/',customer_register, name='customer_register'), #done
    path('api/customer_login/',customer_login, name='customer_login'),  #done
    path('api/customer_verify/',customer_verify, name='customer_verify'), #done
    path('api/customer_update_password/',customer_update_password, name='customer_update_password'), #done
    path('api/customer_address_create/',customer_address_create, name='customer_address_create'), #done
    path('api/customer_address_update/',customer_address_update, name='customer_address_update'), #done
    path('api/customer_list_admin/',customer_list_admin, name='customer_list_admin'), #done
    path('api/customer_detail/',customer_detail, name='customer_detail'), #done
    path('api/customer_profile_update/',customer_profile_update, name='customer_profile_update'), #done
    path('api/customer_logout/',customer_logout, name='customer_logout'), #done
    path('api/customer_wishlist_cart_list/',customer_wishlist_cart_list, name='customer_wishlist_cart_list'), #done
    path('api/social_login/',social_login, name='social_login'), #done
    path('api/customer_delete/',customer_delete, name='customer_delete'), #done
    
    path('api/country_list_customer_filter/',country_list_customer_filter, name='country_list_customer_filter'), #done

    ### APP 
    path('api/app_dashboard/',app_dashboard, name='app_dashboard'), #done
    path('api/app_dashboard_category/',app_dashboard_category, name='app_dashboard_category'), #done

    
    #### Wishlist & Cart
    path('api/add_to_wishlist/',add_to_wishlist, name='add_to_wishlist'), #done
    path('api/add_to_cart/',add_to_cart, name='add_to_cart'), #done
    path('api/product_remove_from_cart/',product_remove_from_cart, name='product_remove_from_cart'), #done
    path('api/customer_wishlist/',customer_wishlist, name='customer_wishlist'), #done
    path('api/customer_detail_admin/',customer_detail_admin, name='customer_detail_admin'), #done
    
    ### Order 
    path('api/order_create/',order_create, name='order_create'), #done
    path('api/order_create_wave_orange/',order_create_wave_orange, name='order_create_wave_orange'), #done
    path('api/inquiry_order_create/',inquiry_order_create, name='inquiry_order_create'), #done


    path('api/cash_status_update/',cash_status_update, name='cash_status_update'), #done
    
    path('api/all_order_list_admin/',all_order_list_admin, name='all_order_list_admin'), #done
    path('api/all_order_list_admin_inquiry/',all_order_list_admin_inquiry, name='all_order_list_admin_inquiry'), #done
    path('api/all_order_inquiry_list_app/',all_order_inquiry_list_app, name='all_order_inquiry_list_app'), #done
    
    path('api/customer_order_list/',customer_order_list, name='customer_order_list'), #done
    path('api/order_detail_admin/',order_detail_admin, name='order_detail_admin'), #done
    path('api/vendor_order_assign/',vendor_order_assign, name='vendor_order_assign'), #done
    path('api/vendor_order_list/',vendor_order_list, name='vendor_order_list'), #done
    path('api/vendor_order_list_vendor/',vendor_order_list_vendor, name='vendor_order_list_vendor'), #done
    path('api/order_delete_admin/',order_delete_admin, name='order_delete_admin'), #done
    
    path('api/variant_order_status_update/',variant_order_status_update, name='variant_order_status_update'), #done
    path('api/order_status_update/',order_status_update, name='order_status_update'), #done
    path('api/product_order_list/',product_order_list, name='product_order_list'), #done
    path('api/vendor_transaction_list_admin/',vendor_transaction_list_admin, name='vendor_transaction_list_admin'), #done
    path('api/container_added_in_order/',container_added_in_order, name='container_added_in_order'), #done

    ###
    path('api/translator_check/',translator_check, name='translator_check'), #done
    path('api/convert_product_french/',convert_product_french, name='convert_product_french'), #done

    ### Vendor Transactions
    path('api/vendor_transaction_create/',vendor_transaction_create, name='vendor_transaction_create'), #done
    path('api/all_vendor_transaction_list/',all_vendor_transaction_list, name='all_vendor_transaction_list'), #done
    path('api/vendor_transaction_list/',vendor_transaction_list, name='vendor_transaction_list'), #done
    

    #CHAT SYSTEM
    path('api/chat_history/',chat_history, name='chat_history'), #done
    path('api/chat_room_list/',chat_room_list, name='chat_room_list'), #done
    path('api/create_message/',create_message, name='create_message'), #done
    path('api/agent_chat_room_list/',agent_chat_room_list, name='agent_chat_room_list'), #done
    path('api/chat_room_update/',chat_room_update, name='chat_room_update'), #done
    path('api/user_new_message_count/',user_new_message_count, name='user_new_message_count'), #done


    path('api/daily_price_update/',daily_price_update, name='daily_price_update'), #done
    path('api/daily_price/',daily_price, name='daily_price'), #done

    ## Chat Agent
    path('api/chat_agent_register/',chat_agent_register, name='chat_agent_register'), #done
    path('api/chat_agent_login/',chat_agent_login, name='chat_agent_login'), #done
    path('api/chat_agent_update/',chat_agent_update, name='chat_agent_update'), #done
    path('api/chat_agent_list/',chat_agent_list, name='chat_agent_list'), #done
    path('api/chat_agent_status_update/',chat_agent_status_update, name='chat_agent_status_update'), #done
    path('api/user_assigned_agent_list/',user_assigned_agent_list, name='user_assigned_agent_list'), #done
    path('api/chat_assign_to_agent/',chat_assign_to_agent, name='chat_assign_to_agent'), #done
    path('api/chat_room_and_agent_history/',chat_room_and_agent_history, name='chat_room_and_agent_history'), #done
    path('api/senior_chat_agent_list/',senior_chat_agent_list, name='senior_chat_agent_list'), #done
    path('api/chat_agent_password_change/',chat_agent_password_change, name='chat_agent_password_change'), #done

    path('api/chat_agent_credentials_resend/',chat_agent_credentials_resend, name='chat_agent_credentials_resend'), #done

    # BULK IMPORT
    path('api/download_image/',download_image, name='download_image'), #done
    path('api/bulk_import/',bulk_import, name='bulk_import'), #done
    path('api/send_sms_api/',send_sms_api, name='send_sms_api'), #done


    # SETTINGS
    path('api/about_us_list/',about_us_list, name='about_us_list'), #done
    path('api/about_us_update/',about_us_update, name='about_us_update'), #done
    path('api/privacy_policy_list/',privacy_policy_list, name='privacy_policy_list'), #done
    path('api/privacy_policy_update/',privacy_policy_update, name='privacy_policy_update'), #done
    path('api/refund_policy_list/',refund_policy_list, name='refund_policy_list'),#done
    path('api/refund_policy_update/',refund_policy_update, name='refund_policy_update'), #done
    path('api/terms_and_condition_list/',terms_and_condition_list, name='terms_and_condition_list'), #done
    path('api/terms_and_condition_update/',terms_and_condition_update, name='terms_and_condition_update'), #done
    path('api/recommend_products/',recommend_products, name='recommend_products'), #done
    
    
    path('api/recently_view_product_list/',recently_view_product_list, name='recently_view_product_list'), #done
    path('api/product_filter_data/',product_filter_data, name='product_filter_data'), #done
    path('api/get_product_data_update/',get_product_data_update, name='get_product_data_update'), #done

    ### Sub admin
    path('api/sub_admin_register/',sub_admin_register, name='sub_admin_register'), #done
    path('api/sub_admin_update/',sub_admin_update, name='sub_admin_update'), #done
    path('api/sub_admin_list/',sub_admin_list, name='sub_admin_list'), #done
    path('api/sub_admin_module_rights_update/',sub_admin_module_rights_update, name='sub_admin_module_rights_update'), #done
    path('api/sub_admin_status_update/',sub_admin_status_update, name='sub_admin_status_update'), #done
    path('api/sub_admin_module_rights_list/',sub_admin_module_rights_list, name='sub_admin_module_rights_list'), #done
    path('api/sub_admin_module_rights/',sub_admin_module_rights, name='sub_admin_module_rights'), #done
    
    path('api/sub_admin_delete/',sub_admin_delete, name='sub_admin_delete'), #done
    path('api/subadmin_credentials_resend/',subadmin_credentials_resend, name='subadmin_credentials_resend'), #done

    # path('api/app_dashboard_dummy/',app_dashboard_dummy, name='app_dashboard_dummy'),
    

    ## EXPORT 
    path('api/export_product_list/',export_product_list, name='export_product_list'), #done


    ### Payment Gateway
    path('api/cash_in_view/',cash_in_view, name='cash_in_view'), #done

    path("api/payment_callback/", payment_callback,name='payment_callback'),#done
    path("api/status/<str:txn_id>/", status_view,name='status_view'), #done

    path("api/initiate_bictorys_payment/", initiate_bictorys_payment,name='initiate_bictorys_payment'),#done
    path("api/initiate_bictorys_payment_for_inquiry/", initiate_bictorys_payment_for_inquiry,name='initiate_bictorys_payment_for_inquiry'),#done
    
    # path("api/bictorys_webhook/", bictorys_webhook,name='bictorys_webhook'),#done
    path("webhook/bictorys/",bictorys_webhook,name="bictorys_webhook"),
    path("api/payment_status/",bictorys_payment_status,name="bictorys-payment-status"),
    # path("shipsgo/container-status/",shipsgo_container_status,name="shipsgo-container-status"),
    path("api/container_status_view/",container_status_view,name="container-status"),

    ### Transaction 
    
    path('api/all_transaction_list_admin/',all_transaction_list_admin, name='all_transaction_list_admin'), #done
    path('api/send_otp_whatsapp/',send_otp_whatsapp, name='send_otp_whatsapp'), #done

    #### Ware house 
    path('api/warehouse_create/',warehouse_create, name='warehouse_create'), #done
    path('api/warehouse_update/',warehouse_update, name='warehouse_update'), #done
    path('api/warehouse_list/',warehouse_list, name='warehouse_list'), #done
    path('api/warehouse_status_update/',warehouse_status_update, name='warehouse_status_update'), #done
    
    ### vendor order tracking
    path('api/vendor_variant_order_status_update/',vendor_variant_order_status_update, name='vendor_variant_order_status_update'), #done
    path('api/warehouse_order_assign/',warehouse_order_assign, name='warehouse_order_assign'), #done
    
    #Country With Currency
    path('api/create_countrywithcurrency/',create_countrywithcurrency, name='create_countrywithcurrency'), #done
    path('api/countrywithcurrency_list_admin/',countrywithcurrency_list_admin, name='countrywithcurrency_list_admin'), #done
    path('api/update_countrywithcurrency/',update_countrywithcurrency, name='update_countrywithcurrency'), #done
    path('api/delete_countrywithcurrency/',delete_countrywithcurrency, name='delete_countrywithcurrency'), #done
    path('api/update_countrywithcurrency_price_by/',update_countrywithcurrency_price_by, name='update_countrywithcurrency_price_by'), #done

    path('api/currency_coversion/',currency_coversion, name='currency_coversion'), #done

    path('api/currency_rates_update/',currency_rates_update, name='currency_rates_update'), #done
    path('api/currency_rates/',currency_rates, name='currency_rates'), #done
     
    path('api/calculate_shipping_cost/',calculate_shipping_cost, name='calculate_shipping_cost'), #done
    path('api/get_shipping_cost/',get_shipping_cost, name='get_shipping_cost'), #done


    path('api/intro_banner_update/',intro_banner_update, name='intro_banner_update'), #done
    path('api/intro_banner_data/',intro_banner_data, name='intro_banner_data'), #done

    # Influencer and Promocode

    path('api/influencer_register/',influencer_register, name='influencer_register'), #done
    path('api/influencer_login/',influencer_login, name='influencer_login'),#done


    
    path('api/file_update_test/',file_update_test, name='file_update_test'), #done
    path('api/model_file_update_test/',model_file_update_test, name='model_file_update_test'), #done
    path('api/variant_file_update_test/',variant_file_update_test, name='variant_file_update_test'), #done

    path('api/mobile_number_update/',mobile_number_update, name='mobile_number_update'), #done
    path('api/mobile_number_update_verify/',mobile_number_update_verify, name='mobile_number_update_verify'), #done

    path('api/all_influencer_list/',all_influencer_list, name='all_influencer_list'), #done
    path('api/influencer_login/',influencer_login, name='influencer_login'), #done
    path('api/influencer_update/',influencer_update, name='influencer_update'), #done
    path('api/influencer_status_update/',influencer_status_update, name='influencer_status_update'), #done
    path('api/influencer_detail/',influencer_detail, name='influencer_detail'), #done
    
    
    path('api/promocode_create/',promocode_create, name='promocode_create'), #done
    path('api/all_promocode_list/',all_promocode_list, name='all_promocode_list'), #done
    path('api/promocode_list/',promocode_list, name='promocode_list'), #done
    
    path('api/promocode_list_influencer/',promocode_list_influencer, name='promocode_list_influencer'), #done
    path('api/promocode_status_update/',promocode_status_update, name='promocode_status_update'), #done

    ### Cargo 
    path('api/cargo_create/',cargo_create, name='cargo_create'), #done
    path('api/all_cargo_list/',all_cargo_list, name='all_cargo_list'), #done
    path('api/cargo_update/',cargo_update, name='cargo_update'),#done
    path('api/cargo_status_update/',cargo_status_update, name='cargo_status_update'), #done
    path('api/country_list_admin/',country_list_admin, name='country_list_admin'), #done
    path('api/cargo_list_app/',cargo_list_app, name='cargo_list_app'), #done
    
    
    ### ADmin REview
    path('api/review_create_admin/',review_create_admin, name='review_create_admin'), #done
    path('api/product_review_list_admin/',product_review_list_admin, name='product_review_list_admin'), #done
    path('api/review_create/',review_create, name='review_create'), #done
    

    path('api/all_money_network_list/',all_money_network_list, name='all_money_network_list'), #done
    path('api/money_network_list/',money_network_list, name='money_network_list'), #done
    
    path('api/customer_cart_check/',customer_cart_check, name='customer_cart_check'), #done
 
    path('api/check_user/',check_user, name='check_user'), #done
    path('api/success_url/',success_url, name='success_url'), #done
    path('api/error_url/',error_url, name='error_url'), #done
    path('api/pay_pix_test/',pay_pix_test, name='pay_pix_test'), #done

    ### payment & cargo 
    path('api/payment_cargo_banner_create/',payment_cargo_banner_create, name='payment_cargo_banner_create'), #done
    path('api/all_payment_cargo_banner_list/',all_payment_cargo_banner_list, name='all_payment_cargo_banner_list'), #done
    path('api/payment_cargo_banner_update/',payment_cargo_banner_update, name='payment_cargo_banner_update'), #done
    path('api/payment_cargo_banner_status_update/',payment_cargo_banner_status_update, name='payment_cargo_banner_status_update'), #done
    
    ## tags
    path('api/product_tag_list/',product_tag_list, name='product_tag_list'), #done
    path('api/product_tag_create/',product_tag_create, name='product_tag_create'),#done
    path('api/product_tag_delete/',product_tag_delete, name='product_tag_delete'), #done
    path('api/product_tag_update/',product_tag_update, name='product_tag_update'), #done
    path('api/all_product_tag_list/',all_product_tag_list, name='all_product_tag_list'), #done
    
    ## Delivery Days 
    path('api/all_delivery_days_list/',all_delivery_days_list, name='all_delivery_days_list'), #done
    path('api/delivery_days_update/',delivery_days_update, name='delivery_days_update'), #done
    

    # path('api/price_exchange/',price_exchange, name='price_exchange'),
    path('api/vendor_revenue/',vendor_revenue, name='vendor_revenue'), #done
    

    path('api/product_value_update_test/',product_value_update_test, name='product_value_update_test'), #done
    path('api/all_product_country/',all_product_country, name='all_product_country'), #done
    path('api/product_country_update/',product_country_update, name='product_country_update'), #done

    # Export List
    path('api/export_customer_list/',export_customer_list, name='export_customer_list'), #done
    path('api/export_order_list_admin/',export_order_list_admin, name='export_order_list_admin'), #done
    path('api/export_vendor_list/',export_vendor_list, name='export_vendor_list'), #done

    # Graph
    path('api/graph_product_verification_data/',graph_product_verification_data, name='graph_product_verification_data'), #done
    path('api/graph_order_status/',graph_order_status, name='graph_order_status'), #done
    path('api/graph_top_products/',graph_top_products, name='graph_top_products'), #done
    path('api/graph_top_variants/',graph_top_variants, name='graph_top_variants'), #done
    path('api/graph_recent_orders/',graph_recent_orders, name='graph_recent_orders'), #done
    path('api/graph_last_twelve_months_performance/',graph_last_twelve_months_performance, name='graph_last_twelve_months_performance'), #done
    path('api/vendor_total_income/',vendor_total_income, name='vendor_total_income'),#done
    path('api/vendor_total_payout/',vendor_total_payout, name='vendor_total_payout'), #done
    path('api/vendor_pending_payment/',vendor_pending_payment, name='vendor_pending_payment'), #done


    
    path('api/fix_created_at_format/',fix_created_at_format, name='fix_created_at_format'), #done

    # Vendor Payment Tracker
    path('api/vendor_payment_track_create/',vendor_payment_track_create, name='vendor_payment_track_create'), #done
    path('api/vendor_payment_track_list/',vendor_payment_track_list, name='vendor_payment_track_list'), #done
    path('api/vendor_payment_track_delete/',vendor_payment_track_delete, name='vendor_payment_track_delete'), #done



    path('api/important_note_update/',important_note_update, name='important_note_update'), #done
    path('api/important_note_list/',important_note_list, name='important_note_list'),  #done


    # Inquiry Module 
    path('api/product_inquiry_form/',product_inquiry_form, name='product_inquiry_form'), #done
    path('api/product_inquiry_list/',product_inquiry_list, name='product_inquiry_list'), #done
    path('api/export_product_inquiry_list/',export_product_inquiry_list, name='export_product_inquiry_list'), #done
    path('api/product_inquiry_status_update/',product_inquiry_status_update, name='product_inquiry_status_update'), #done
    path('api/customer_inquiry_list/',customer_inquiry_list, name='customer_inquiry_list'), #done


    # Delay Note Module 
    path('api/delay_note_create/',delay_note_create, name='delay_note_create'), #done
    path('api/delay_note_list/',delay_note_list, name='delay_note_list'), #done
    path('api/vendor_list_with_delay_note/',vendor_list_with_delay_note, name='vendor_list_with_delay_note'), #done
    path('api/delay_note_update/',delay_note_update, name='delay_note_update'), #done
    path('api/delay_note_status_update/',delay_note_status_update, name='delay_note_status_update'), #done

### Testing
    path('api/create_wave_checkout/',create_wave_checkout, name='create_wave_checkout'), #done
    path('api/get_wave_checkout_session/',get_wave_checkout_session, name='get_wave_checkout_session'), #done

### bulk upload 
    path('api/bulk_upload/',bulk_upload, name='bulk_upload'), #done
    path('api/bulk_upload_submit/',bulk_upload_submit, name='bulk_upload_submit'), #done
    path('api/all_bulk_product_list/',all_bulk_product_list, name='all_bulk_product_list'), #done

### Product Type
    path('api/product_type_create/',product_type_create, name='product_type_create'), #done
    path('api/product_type_update/',product_type_update, name='product_type_update'), #done
    path('api/product_type_list/',product_type_list, name='product_type_list'), #done

### Product Type
    path('api/product_packaging_create/',product_packaging_create, name='product_packaging_create'), #done
    path('api/product_packaging_update/',product_packaging_update, name='product_packaging_update'), #done
    path('api/product_packaging_list/',product_packaging_list, name='product_packaging_list'), #done

    #  Product Vector Image
    path('api/update_vector/',update_vector, name='update_vector'), #done

### Orange money 
    path('api/initiate_payment/',initiate_payment, name='initiate_payment'), #done

# Analytics Admin Apis
    # App Api
    path('api/app_admin_counts/',app_admin_counts, name='app_admin_counts'), #done

    # VENDOR Analytics API
    path('api/vendor_analytics_count/',vendor_analytics_count, name='vendor_analytics_count'), #done
    path('api/vendor_monthly_user/',vendor_monthly_user, name='vendor_monthly_user'), #done
    path('api/top_vendor_net_profit/',top_vendor_net_profit, name='top_vendor_net_profit'), #done
    path('api/categories_wise_vendor/',categories_wise_vendor, name='categories_wise_vendor'), #done
    path('api/vendor_list_analyse/',vendor_list_analyse, name='vendor_list_analyse'), #done

    # Product Analytics API
    path('api/product_analytics_count/',product_analytics_count, name='product_analytics_count'), #done
    path('api/product_monthly_addition_graph/',product_monthly_addition_graph, name='product_monthly_addition_graph'), #done
    path('api/product_category_based_analysis/',product_category_based_analysis, name='product_category_based_analysis'), #done
    path('api/product_top_selling_variants/',product_top_selling_variants, name='product_top_selling_variants'), #done
    path('api/product_top_add_to_cart_analysis/',product_top_add_to_cart_analysis, name='product_top_add_to_cart_analysis'), #done
    path('api/product_wishlist_analysis/',product_wishlist_analysis, name='product_wishlist_analysis'), #done
    path('api/product_recent_inquiry_list_analysis/',product_recent_inquiry_list_analysis, name='product_recent_inquiry_list_analysis'), #done

    # Order Analytics API
    path('api/order_status_analytics_count/',order_status_analytics_count, name='order_status_analytics_count'), #done
    path('api/order_monthly_analysis/',order_monthly_analysis, name='order_monthly_analysis'), #done
    path('api/top_orders_analysis/',top_orders_analysis, name='top_orders_analysis'), #done
    path('api/order_source_and_ship_by/',order_source_and_ship_by, name='order_source_and_ship_by'), #done
    path('api/top_order_category_based_analysis/',top_order_category_based_analysis, name='top_order_category_based_analysis'), #done
    path('api/order_recent_list_analysis/',order_recent_list_analysis, name='order_recent_list_analysis'), #done

    # Customer Analytics API
    path('api/customer_analytics_count/',customer_analytics_count, name='customer_analytics_count'), #done
    path('api/monthly_customer_analysis/',monthly_customer_analysis, name='monthly_customer_analysis'), #done
    path('api/customer_by_country_analysis/',customer_by_country_analysis, name='customer_by_country_analysis'), #done
    path('api/customer_top_spenders_analysis/',customer_top_spenders_analysis, name='customer_top_spenders_analysis'), #done
    path('api/customer_order_frequency_distribution_analysis/',customer_order_frequency_distribution_analysis, name='customer_order_frequency_distribution_analysis'), #done
    path('api/customer_recent_registered_list_analysis/',customer_recent_registered_list_analysis, name='customer_recent_registered_list_analysis'), #done

    # Dashboard Analytics API
    path('api/dashboard_overview/',dashboard_overview, name='dashboard_overview'), #done
    path('api/dashboard_order_status_graph/',dashboard_order_status_graph, name='dashboard_order_status_graph'), #done
    path('api/monthly_dashboard_revenue_graph/',monthly_dashboard_revenue_graph, name='monthly_dashboard_revenue_graph'), #done
    path('api/dashboard_platform_module_count/',dashboard_platform_module_count, name='dashboard_platform_module_count'), #done
    path('api/dashboard_currencry_exchange_rate_base/',dashboard_currencry_exchange_rate_base, name='dashboard_currencry_exchange_rate_base'), #done
    
    ## home screen banner 
    path('api/banner_create_update/',banner_create_update, name='banner_create_update'), #done
    path('api/banner_list_admin/',banner_list_admin, name='banner_list_admin'), #done
    path('api/banner_list_app/',banner_list_app, name='banner_list_app'), #done
    
    ## Container Request  
    path('api/container_request_create/',container_request_create, name='container_request_create'), #done
    path('api/container_request_status_update/',container_request_status_update, name='container_request_status_update'), #done
    path('api/all_container_request_list/',all_container_request_list, name='all_container_request_list'), #done
    path('api/customer_container_request_list/',customer_container_request_list, name='customer_container_request_list'), #done
    






# Extra Apis
    path('api/convert_string_date_to_datetime/',convert_string_date_to_datetime, name='convert_string_date_to_datetime'), #done
    path('api/product_remove_add_to_cart/',product_remove_add_to_cart, name='product_remove_add_to_cart'), #done
    path('api/need_to_change/',need_to_change, name='need_to_change'), #done



]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
if not settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
