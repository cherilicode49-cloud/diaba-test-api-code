from os import name

from rest_framework import serializers
from diabaApp import models
from django.conf import settings
from django.db.models import Q
from datetime import datetime
import random, math




class AppDynamicSettingSerializer(serializers.ModelSerializer):   
    class Meta:
        model = models.AppDynamicSetting
        fields = '__all__'

class AdminDetailSerializer(serializers.ModelSerializer):   
    role = serializers.ReadOnlyField(source='userType.roleName')

    class Meta:
        model = models.AdminDetail
        fields = '__all__'



class ChatAgentDetailSerializer(serializers.ModelSerializer):   
    role = serializers.ReadOnlyField(source='userType.roleName')
    class Meta:
        model = models.ChatAgentDetail
        fields = ['id','email','countryCode','mobileNumber','userType','name','lastLoginDate','OTP','password','status','created_at','role','agent_type','is_verified']

class VendorDetailSerializer(serializers.ModelSerializer):   
    category_name = serializers.ReadOnlyField(source='category.category')
    category_id = serializers.ReadOnlyField(source='category.id')
    subcategory_name = serializers.ReadOnlyField(source='subcategory.subcategory')
    subcategory_id = serializers.ReadOnlyField(source='subcategory.id')

    class Meta:
        model = models.VendorDetail
        # fields = '__all__'
        exclude = ['password']


class VendorDataSerializer(serializers.ModelSerializer):   
    # category_name = serializers.ReadOnlyField(source='category.category')
    # category_id = serializers.ReadOnlyField(source='category.id')
    # subcategory_name = serializers.ReadOnlyField(source='subcategory.subcategory')
    # subcategory_id = serializers.ReadOnlyField(source='subcategory.id')
    
    class Meta:
        model = models.VendorDetail
        fields = ['id', 'vendor_name','phone_number','email']
        # exclude = ['password']



class CategoryDetailSerializer(serializers.ModelSerializer):   

    class Meta:
        model = models.CategoryDetail
        fields = '__all__'



class SubCategoryDetailSerializer(serializers.ModelSerializer):   
    category_name = serializers.ReadOnlyField(source='category.category')
    category_id = serializers.ReadOnlyField(source='category.id')

    class Meta:
        model = models.SubCategoryDetail
        fields = '__all__'

class SubCategoryListSerializer(serializers.ModelSerializer):   
    class Meta:
        model = models.SubCategoryDetail
        fields = ['id', 'subcategory', 'image']
     

class SuperSubCategoryDetailSerializer(serializers.ModelSerializer):   
    category_name = serializers.ReadOnlyField(source='category.category')
    category_id = serializers.ReadOnlyField(source='category.id')
    subcategory_name = serializers.ReadOnlyField(source='subcategory.subcategory')
    subcategory_id = serializers.ReadOnlyField(source='subcategory.id')

    class Meta:
        model = models.SuperSubCategoryDetail
        fields = '__all__'


class ProductDetailSerializer(serializers.ModelSerializer):   
    category_name = serializers.ReadOnlyField(source='category.category')
    category_id = serializers.ReadOnlyField(source='category.id')
    subcategory_name = serializers.ReadOnlyField(source='subcategory.subcategory')
    subcategory_id = serializers.ReadOnlyField(source='subcategory.id')
    # super_subcategory_name = serializers.ReadOnlyField(source='super_subcategory.super_subcategory')
    # super_subcategory_id = serializers.ReadOnlyField(source='super_subcategory.id')
    vendor_name = serializers.ReadOnlyField(source='vendor.vendor_name')
    phone_number = serializers.ReadOnlyField(source='vendor.phone_number')
    email = serializers.ReadOnlyField(source='vendor.email')
    vendor_country = serializers.ReadOnlyField(source='vendor.country')
    


    class Meta:
        model = models.ProductDetail
        # fields = '__all__'
        exclude = ['product_image_1_vector','product_image_2_vector','product_image_3_vector','product_image_4_vector','product_image_5_vector','product_image_6_vector','product_image_7_vector','product_image_8_vector']


class ChatAgentProductDetailSerializer(serializers.ModelSerializer):   
    product_id = serializers.ReadOnlyField(source='id')
    product_image = serializers.SerializerMethodField()

    class Meta:
        model = models.ProductDetail
        fields = ['product_id','product_name_french','product_code','product_image','status']

    def get_product_image(self, obj):
        if obj.product_image_1:
            return obj.product_image_1.url
        elif obj.product_image_2:
            return obj.product_image_2.url
        elif obj.product_image_3:
            return obj.product_image_3.url
        elif obj.product_image_4:
            return obj.product_image_4.url
        elif obj.product_image_5:
            return obj.product_image_5.url
        elif obj.product_image_6:
            return obj.product_image_6.url
        elif obj.product_image_7:
            return obj.product_image_7.url
        elif obj.product_image_8:
            return obj.product_image_8.url
        else:
            return None
        


class ProductDetailAppSerializer(serializers.ModelSerializer):   
    category_name = serializers.ReadOnlyField(source='category.category')
    category_name_french = serializers.ReadOnlyField(source='category.category_french')
    subcategory_name = serializers.ReadOnlyField(source='subcategory.subcategory')
    
    country_of_origin_name = serializers.ReadOnlyField(source='country_of_origin.country')
    country_of_origin_image = serializers.ReadOnlyField(source='country_of_origin.image.url')
    vendor_name = serializers.ReadOnlyField(source='vendor.vendor_name')
    product_type = serializers.ReadOnlyField(source='product_type.product_type')
    product_packaging = serializers.ReadOnlyField(source='product_packaging.product_packaging')
    
    currency = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()

    dollar = serializers.SerializerMethodField()
    xaf = serializers.SerializerMethodField()
    xof = serializers.SerializerMethodField()
    cdf = serializers.SerializerMethodField()
    delivery_price_by = serializers.SerializerMethodField()


    class Meta:
        model = models.ProductDetail
        fields = ['id','product_name', 'product_name_french', 'product_code',
                    'country_of_origin', 'description', 'description_french',
                    'unit_of_measure', 'material', 'length', 'height', 'width', 'weight', 'color',
                    'carton_length', 'carton_width', 'carton_height', 'carton_weight',
                    'min_order_quantity', 'max_order_quantity','product_image_1', 
                    'product_image_2', 'product_image_3', 'product_image_4','product_image_5', 
                    'product_image_6', 'product_image_7', 'product_image_8','price', 'discount',
                    'final_price','shipping_via', 'refpro', 'reuser','currency','product_video',
                    'category_name','category_name_french','subcategory_name','country_of_origin_name',
                    'country_of_origin_image','vendor_name','dollar','xaf','xof','cdf','delivery_price_by',
                    'delay_days_air','delay_days_ship','delay_days_express', 'product_type','product_packaging', 'product_packaging_value'
                ]
        # exclude = ['available_quantity', 'quantity', 'product_verification', 'vendor', 'category', 'subcategory',
        # 'product_image_1_vector','product_image_2_vector','product_image_3_vector','product_image_4_vector', 
        # 'product_image_5_vector', 'product_image_6_vector', 'product_image_7_vector', 'product_image_8_vector']


    def get_dollar(self, obj):
        return 1
    def get_xaf(self, obj):
        return models.CurrencyConverter.objects.get(currency_code = "XAF").system_rate
    def get_xof(self, obj):
        return models.CurrencyConverter.objects.get(currency_code = "XOF").system_rate
    def get_cdf(self, obj):
        return models.CurrencyConverter.objects.get(currency_code = "CDF").system_rate
    

    def get_currency(self, obj):
        country = self.context.get('country','Egypt')
        if models.CountryWithCurrency.objects.filter(country_name = country).exists():
            try:
                return models.CountryWithCurrency.objects.filter(country_name = country).first().currency_symbol
            except:
                return "$"
        else:
            return "$"



    def get_price(self, obj):
        country = self.context.get('country','Egypt')
        if not models.CountryWithCurrency.objects.filter(country_name = country).exists():
            country = 'Egypt'

        # try:
        #     # print("country=-=-==-->",country)
        #     get_country = models.CountryWithCurrency.objects.get(country_name = country)
        #     if get_country.currency_code == "USD":
        #         currency = models.CurrencyConverter.objects.get(currency_code = "XOF")
        #         calculate_us_price = float(obj.price) / float(currency.system_rate)
                
        #     else:
        #         currency = models.CurrencyConverter.objects.get(currency_code = get_country.currency_code)
        #         to_convert_us_currency = models.CurrencyConverter.objects.get(currency_code = "XOF")
        #         calculate_us_price = float(obj.price) / float(to_convert_us_currency.system_rate)

        #         print("calculate_us_price======>",calculate_us_price)

        #     if calculate_us_price < 1:
        #         calculate_us_price = 1

        #     # print(calculate_us_price, 'calculate_us_price')

        #     if currency.currency_code == "XOF" and not get_country.currency_code == "USD":
        #         # # print("currency.system_rate=====>",currency.system_rate)    
        #         print("XOF jdfsjkfh=====>",obj.price)    
        #         # print("here-=----1")
        #         value = math.ceil(float(obj.price))
        #         return f"{value:,}".replace(",", " ")
                
                
        #     elif currency.currency_code == "XAF":
        #         value = math.ceil(float(calculate_us_price) * float(currency.system_rate)) 
        #         return f"{value:,}".replace(",", " ")
            
        #     elif currency.currency_code == "CDF":
        #         # # print("currency.system_rate=====>",currency.system_rate)    
        #         print("calculate_us_price=====>",calculate_us_price)    
        #         value = math.ceil(float(calculate_us_price) * float(currency.system_rate))       
        #         print("valuues---222-->",value)
        #         return f"{value:,}".replace(",", " ")
            
        #     else:
        #         value = math.ceil(float(calculate_us_price))
        #         print("valuues----->",value)
        #         return f"{value:,}".replace(",", " ")

        try:
            # print("Variant country=-=-==-->",country)
            get_country = models.CountryWithCurrency.objects.get(country_name = country)
            # print("Country-=----1--->",get_country.currency_code)
            if get_country.currency_code == "USD":
                # print("currency-=----1")
                currency = get_country

                to_convert_us_currency = models.CurrencyConverter.objects.get(currency_code = "XOF")
                calculate_us_price = float(obj.price) / float(to_convert_us_currency.system_rate)

                # print("currency-=-=-==-==-=--3---->",currency)
                # print("currency.currency_code-=-=-==-==-=--3---->",currency.currency_code)
                # print("calculate_us_price-=-=-==-==-=--3---->",calculate_us_price)

            else:
                # print("currency-=----2")
                currency = models.CurrencyConverter.objects.get(currency_code = get_country.currency_code)
                # print("cprint("Country-=----2--->",currency)
                to_convert_us_currency = models.CurrencyConverter.objects.get(currency_code = "XOF")
                calculate_us_price = float(obj.price) / float(to_convert_us_currency.system_rate)

            if calculate_us_price < 1:
                calculate_us_price = 1

            # print(calculate_us_price, 'calculate_us_price')

            if currency.currency_code == "XOF" and not get_country.currency_code == "USD":
                value = math.ceil(float(obj.price))
                return f"{value:,}".replace(",", " ")
            
            # elif currency.currency_code == "XAF":
                # value = math.ceil(float(calculate_us_price) * float(currency.system_rate))   
                # return f"{value:,}".replace(",", " ")
                # # # print("currency.system_rate=====>",currency.system_rate)    
                # value = math.ceil(float(calculate_us_price) * float(currency.system_rate))         
                # return f"{value:,}".replace(",", " ")

            elif currency.currency_code == "USD":  
                # # print("currency.system_rate=====>",currency.system_rate)    
                # value = math.ceil(float(calculate_us_price) * float(currency.system_rate))         
                # return f"{value:,}".replace(",", " ")
                value = math.ceil(float(calculate_us_price))
                # print("value===USDDDD==>",value)    
                return f"{value:,}".replace(",", " ")

            else:
                # # print("currency.system_rate=====>",currency.system_rate)    
                value = math.ceil(float(calculate_us_price) * float(currency.system_rate))         
                return f"{value:,}".replace(",", " ")
            

        except Exception as e:
            print("error----->",e)
            value = math.ceil(float(obj.price))
            return f"{value:,}".replace(",", " ")



    def get_delivery_price_by(self, obj):
        delivery_country = self.context.get('delivery_country',None)
        selected_country = self.context.get('country',None)

        # print("self.context-=-=---->",self.context)
        
        if delivery_country not in [None,'','null']:
            try:
                country = models.CountryWithCurrency.objects.get(country_name = delivery_country)
            except:
                country = models.CountryWithCurrency.objects.get(country_name = selected_country)
            price_by_air = country.price_by_air
            price_by_ship = country.price_by_ship
            price_by_express = country.express_shipping
            
            # print(country.currency_code, price_by_air , 'air', price_by_ship, 'country')
            # print("models.CountryWithCurrency.objects.filter(country_name = country----->)",models.CountryWithCurrency.objects.filter(country_name = selected_country).count())
            currency_country = models.CountryWithCurrency.objects.get(country_name = selected_country)

            if country.currency_code == currency_country.currency_code:
                # print(price_by_air, price_by_ship,"HERE--------1")
                return {
                    'price_by_air' : round(float(price_by_air), 2),
                    'price_by_ship' : round(float(price_by_ship), 2),
                    'price_by_express' : round(float(price_by_express), 2)
                }
            else:

                # print("HERE--------2")
                if country.currency_code != "USD" and currency_country.currency_code != "USD":
                    # print("HERE--------3", country.currency_code)
                    deliver_currency_value = models.CurrencyConverter.objects.get(currency_code = country.currency_code)
                    # print(deliver_currency_value, 'deliver_currency_value')
                    if country.price_by_air not in [None,'','null']:
                        usd_price_by_air = float(country.price_by_air) / float(deliver_currency_value.system_rate)
                        usd_price_by_ship = float(country.price_by_ship) / float(deliver_currency_value.system_rate)
                        actual_currency_value = models.CurrencyConverter.objects.get(currency_code = currency_country.currency_code)
                        price_by_air = float(usd_price_by_air) * float(actual_currency_value.system_rate)
                        price_by_ship = float(usd_price_by_ship) * float(actual_currency_value.system_rate)
                    else:
                        print("HERE--------3")
                        
                        price_by_air = currency_country.price_by_air
                        price_by_ship = currency_country.price_by_ship
                        price_by_express = currency_country.express_shipping


                elif country.currency_code == "USD" and currency_country.currency_code != "USD" :
                    # print("HERE--------4")
                    actual_currency_value = models.CurrencyConverter.objects.get(currency_code = currency_country.currency_code)

                    if country.price_by_air not in [None,'','null'] and country.price_by_ship not in [None,'','null']:
                        price_by_air = float( country.price_by_air) * float(actual_currency_value.system_rate)
                        price_by_express = float( country.express_shipping) * float(actual_currency_value.system_rate)
                        price_by_ship = float(country.price_by_ship) * float(actual_currency_value.system_rate)
                    else:
                        price_by_air = float(currency_country.price_by_air)
                        price_by_ship = float(currency_country.price_by_ship)
                        price_by_express = float(currency_country.express_shipping)


                elif country.currency_code != "USD" and currency_country.currency_code == "USD" :
                    # print("HERE--------5")
                    deliver_currency_value = models.CurrencyConverter.objects.get(currency_code = country.currency_code)

                    if country.price_by_air not in [None,'','null'] and country.price_by_ship not in [None,'','null']:
                        price_by_air = float(country.price_by_air) / float(deliver_currency_value.system_rate)
                        price_by_express = float(country.express_shipping) / float(deliver_currency_value.system_rate)
                        price_by_ship = float(country.price_by_ship) / float(deliver_currency_value.system_rate)
                    else:
                        price_by_air = float(currency_country.price_by_air)
                        price_by_ship = float(currency_country.price_by_ship)
                        price_by_express = float(currency_country.express_shipping)

                else:
                    # print("HERE--------6")
                    if country.price_by_air not in [None,'','null'] and country.price_by_ship not in [None,'','null']:
                        price_by_air = float(currency_country.price_by_air)
                        price_by_ship = float(currency_country.price_by_ship)
                        price_by_express = float(currency_country.express_shipping)
                
                print(price_by_express, 'dddddd')
                return {
                    'price_by_air' : round(int(price_by_air), 2),
                    'price_by_ship' : round(int(price_by_ship), 2),
                    'price_by_express' : round(int(price_by_express), 2)
                }
        else:
            # print("HERE--------7")
            currency_country = models.CountryWithCurrency.objects.get(country_name = selected_country)
            return {
                'price_by_air' : round(float(currency_country.price_by_air),2),
                'price_by_ship' : round(float(currency_country.price_by_ship),2),
                'price_by_express' : round(float(currency_country.express_shipping),2),

            }


class ProductImageSerializer(serializers.ModelSerializer):   

    class Meta:
        model = models.ProductImage
        fields = '__all__'

class ProductOtherSpecificationSerializer(serializers.ModelSerializer):   

    class Meta:
        model = models.ProductOtherSpecification
        fields = '__all__'


class ProductModelVariantSerializerAdmin(serializers.ModelSerializer):
    variant_name_french = serializers.ReadOnlyField(source = 'name_french')

    class Meta:
        model = models.ProductModelVariant
        fields = ['id','product','model','name','name_french','variant_name_french',
                  'image','price','variant_verification','status','price']
        
class ProductModelVariantSerializer(serializers.ModelSerializer):
    variant_name_french = serializers.ReadOnlyField(source = 'name_french')

    currency = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    class Meta:
        model = models.ProductModelVariant
        fields = ['id','product','model','name','name_french','variant_name_french',
                  'image','price','variant_verification','status','currency','price']

    def get_currency(self, obj):
        country = self.context.get('country','Egypt')
        if models.CountryWithCurrency.objects.filter(country_name = country).exists():
            try:
                return models.CountryWithCurrency.objects.filter(country_name = country).first().currency_symbol
            except:
                return "$"
        else:
            return "$"
        
    
    def get_image(self, obj):
        if obj.image:
            return obj.image.url
        elif obj.product.product_image_1:
            return obj.product.product_image_1.url
        return None



    def get_price(self, obj):
        country = self.context.get('country','Egypt')
        if not models.CountryWithCurrency.objects.filter(country_name = country).exists():
            country = 'Egypt'

        try:
            # print("Variant country=-=-==-->",country)
            get_country = models.CountryWithCurrency.objects.get(country_name = country)
            # print("Country-=----1--->",get_country.currency_code)
            if get_country.currency_code == "USD":
                # print("currency-=----1")
                currency = get_country

                to_convert_us_currency = models.CurrencyConverter.objects.get(currency_code = "XOF")
                calculate_us_price = float(obj.price) / float(to_convert_us_currency.system_rate)

                # print("currency-=-=-==-==-=--3---->",currency)
                # print("currency.currency_code-=-=-==-==-=--3---->",currency.currency_code)
                # print("calculate_us_price-=-=-==-==-=--3---->",calculate_us_price)

            else:
                # print("currency-=----2")
                currency = models.CurrencyConverter.objects.get(currency_code = get_country.currency_code)
                # print("cprint("Country-=----2--->",currency)
                to_convert_us_currency = models.CurrencyConverter.objects.get(currency_code = "XOF")
                calculate_us_price = float(obj.price) / float(to_convert_us_currency.system_rate)

            if calculate_us_price < 1:
                calculate_us_price = 1

            # print(calculate_us_price, 'calculate_us_price')

            if currency.currency_code == "XOF" and not get_country.currency_code == "USD":
                value = math.ceil(float(obj.price))
                return f"{value:,}".replace(",", " ")
            
            # elif currency.currency_code == "XAF":
                # value = math.ceil(float(calculate_us_price) * float(currency.system_rate))   
                # return f"{value:,}".replace(",", " ")
                # # # print("currency.system_rate=====>",currency.system_rate)    
                # value = math.ceil(float(calculate_us_price) * float(currency.system_rate))         
                # return f"{value:,}".replace(",", " ")

            elif currency.currency_code == "USD":  
                # # print("currency.system_rate=====>",currency.system_rate)    
                # value = math.ceil(float(calculate_us_price) * float(currency.system_rate))         
                # return f"{value:,}".replace(",", " ")
                value = math.ceil(float(calculate_us_price))
                # print("value===USDDDD==>",value)    
                return f"{value:,}".replace(",", " ")

            else:
                # # print("currency.system_rate=====>",currency.system_rate)    
                value = math.ceil(float(calculate_us_price) * float(currency.system_rate))         
                return f"{value:,}".replace(",", " ")
            

        
        except Exception as e:
            print("error----->",e)
            value = math.ceil(float(obj.price))
            return f"{value:,}".replace(",", " ")



# class ProductSearchSerializer(serializers.ModelSerializer):   
#     category_name = serializers.ReadOnlyField(source='category.category')
#     category_id = serializers.ReadOnlyField(source='category.id')
#     subcategory_name = serializers.ReadOnlyField(source='subcategory.subcategory')
#     subcategory_id = serializers.ReadOnlyField(source='subcategory.id')
#     # super_subcategory_name = serializers.ReadOnlyField(source='super_subcategory.super_subcategory')
#     # super_subcategory_id = serializers.ReadOnlyField(source='super_subcategory.id')

#     price = serializers.SerializerMethodField()
#     currency = serializers.SerializerMethodField()

#     class Meta:
#         model = models.ProductDetail
#         fields = ['id', 'category_name', 'category_id', 'subcategory_name', 'subcategory_id', \
#         'product_name','product_name_french', 'product_code', 'product_image_1', 'price', 'discount', 'final_price','currency']
    
#     def get_currency(self, obj):
#         country = self.context.get('country','Egypt')
#         if models.CountryWithCurrency.objects.filter(country_name = country).exists():
#             try:
#                 return models.CountryWithCurrency.objects.filter(country_name = country).first().currency_symbol
#             except:
#                 return "$"
#         else:
#             return "$"



#     def get_price(self, obj):
#         country = self.context.get('country','Egypt')
#         if not models.CountryWithCurrency.objects.filter(country_name = country).exists():
#             country = 'Egypt'

#         try:
#             # print("Variant country=-=-==-->",country)
#             get_country = models.CountryWithCurrency.objects.get(country_name = country)
#             # print("Country-=----1--->",get_country.currency_code)
#             if get_country.currency_code == "USD":
#                 # print("currency-=----1")
#                 currency = get_country

#                 to_convert_us_currency = models.CurrencyConverter.objects.get(currency_code = "XOF")
#                 calculate_us_price = float(obj.price) / float(to_convert_us_currency.system_rate)

#                 # print("currency-=-=-==-==-=--3---->",currency)
#                 # print("currency.currency_code-=-=-==-==-=--3---->",currency.currency_code)
#                 # print("calculate_us_price-=-=-==-==-=--3---->",calculate_us_price)

#             else:
#                 # print("currency-=----2")
#                 currency = models.CurrencyConverter.objects.get(currency_code = get_country.currency_code)
#                 # print("cprint("Country-=----2--->",currency)
#                 to_convert_us_currency = models.CurrencyConverter.objects.get(currency_code = "XOF")
#                 calculate_us_price = float(obj.price) / float(to_convert_us_currency.system_rate)

#             if calculate_us_price < 1:
#                 calculate_us_price = 1

#             # print(calculate_us_price, 'calculate_us_price')

#             if currency.currency_code == "XOF" and not get_country.currency_code == "USD":
#                 value = math.ceil(float(obj.price))
#                 return f"{value:,}".replace(",", " ")
            
#             # elif currency.currency_code == "XAF":
#                 # value = math.ceil(float(calculate_us_price) * float(currency.system_rate))   
#                 # return f"{value:,}".replace(",", " ")
#                 # # # print("currency.system_rate=====>",currency.system_rate)    
#                 # value = math.ceil(float(calculate_us_price) * float(currency.system_rate))         
#                 # return f"{value:,}".replace(",", " ")

#             elif currency.currency_code == "USD":  
#                 # # print("currency.system_rate=====>",currency.system_rate)    
#                 # value = math.ceil(float(calculate_us_price) * float(currency.system_rate))         
#                 # return f"{value:,}".replace(",", " ")
#                 value = math.ceil(float(calculate_us_price))
#                 # print("value===USDDDD==>",value)    
#                 return f"{value:,}".replace(",", " ")

#             else:
#                 # # print("currency.system_rate=====>",currency.system_rate)    
#                 value = math.ceil(float(calculate_us_price) * float(currency.system_rate))         
#                 return f"{value:,}".replace(",", " ")
            

        
#         except Exception as e:
#             print("error----->",e)
#             value = math.ceil(float(obj.price))
#             return f"{value:,}".replace(",", " ")



class ProductSearchSerializer(serializers.ModelSerializer):

    category_name = serializers.ReadOnlyField(
        source='category.category'
    )

    category_id = serializers.ReadOnlyField(
        source='category.id'
    )

    subcategory_name = serializers.ReadOnlyField(
        source='subcategory.subcategory'
    )

    subcategory_id = serializers.ReadOnlyField(
        source='subcategory.id'
    )

    price = serializers.SerializerMethodField()
    currency = serializers.SerializerMethodField()

    class Meta:
        model = models.ProductDetail
        fields = [
            'id',
            'category_name',
            'category_id',
            'subcategory_name',
            'subcategory_id',
            'product_name',
            'product_name_french',
            'product_code',
            'product_image_1',
            'price',
            'discount',
            'final_price',
            'currency'
        ]

    def get_currency(self, obj):

        country = self.context.get(
            'country',
            'Egypt'
        )

        country_currency = (
            models.CountryWithCurrency.objects
            .filter(country_name=country)
            .first()
        )

        if country_currency:
            return country_currency.currency_symbol or "$"

        return "$"

    def get_price(self, obj):

        country = self.context.get(
            'country',
            'Egypt'
        )

        # SAFE PRICE
        price = float(obj.price or 0)

        country_obj = (
            models.CountryWithCurrency.objects
            .filter(country_name=country)
            .first()
        )

        if not country_obj:
            country_obj = (
                models.CountryWithCurrency.objects
                .filter(country_name='Egypt')
                .first()
            )

        try:

            xof_currency = (
                models.CurrencyConverter.objects
                .filter(currency_code="XOF")
                .first()
            )

            if not xof_currency or not xof_currency.system_rate:
                return 0

            calculate_us_price = (
                price /
                float(xof_currency.system_rate)
            )

            if calculate_us_price < 1:
                calculate_us_price = 1

            # USD
            if country_obj.currency_code == "USD":

                value = math.ceil(
                    float(calculate_us_price)
                )

                return (
                    f"{value:,}"
                    .replace(",", " ")
                )

            # XOF
            elif country_obj.currency_code == "XOF":

                value = math.ceil(price)

                return (
                    f"{value:,}"
                    .replace(",", " ")
                )

            # OTHER CURRENCY
            else:

                currency = (
                    models.CurrencyConverter.objects
                    .filter(
                        currency_code=country_obj.currency_code
                    )
                    .first()
                )

                if not currency:
                    value = math.ceil(price)

                    return (
                        f"{value:,}"
                        .replace(",", " ")
                    )

                value = math.ceil(
                    float(calculate_us_price) *
                    float(currency.system_rate or 1)
                )

                return (
                    f"{value:,}"
                    .replace(",", " ")
                )

        except Exception as e:

            print("error----->", e)

            value = math.ceil(price)

            return (
                f"{value:,}"
                .replace(",", " ")
            )



class ProductDataSerializer(serializers.ModelSerializer):   
    category_name = serializers.ReadOnlyField(source='category.category')
    category_name_french = serializers.ReadOnlyField(source='category.category_french')
    subcategory_name = serializers.ReadOnlyField(source='subcategory.subcategory')
    
    # super_subcategory_name = serializers.ReadOnlyField(source='super_subcategory.super_subcategory')
    # super_subcategory_id = serializers.ReadOnlyField(source='super_subcategory.id')
    country_of_origin_name = serializers.ReadOnlyField(source='country_of_origin.country')
    country_of_origin_image = serializers.ReadOnlyField(source='country_of_origin.image.url')

    price = serializers.SerializerMethodField()
    currency = serializers.SerializerMethodField()

    class Meta:
        model = models.ProductDetail
        fields = ['id', 'category_name', 'subcategory_name', 'product_name_french', 'category_name_french', 'price', \
         'product_name', 'product_code', 'product_image_1', 'country_of_origin_name', 'country_of_origin_image','currency']

    def get_currency(self, obj):
        country = self.context.get('country','Egypt')
        if models.CountryWithCurrency.objects.filter(country_name = country).exists():
            try:
                return models.CountryWithCurrency.objects.filter(country_name = country).first().currency_symbol
            except:
                return "$"
        else:
            return "$"



    def get_price(self, obj):
        country = self.context.get('country','Egypt')
        if not models.CountryWithCurrency.objects.filter(country_name = country).exists():
            country = 'Egypt'

        try:
            # print("Variant country=-=-==-->",country)
            get_country = models.CountryWithCurrency.objects.get(country_name = country)
            # print("Country-=----1--->",get_country.currency_code)
            if get_country.currency_code == "USD":
                # print("currency-=----1")
                currency = get_country

                to_convert_us_currency = models.CurrencyConverter.objects.get(currency_code = "XOF")
                calculate_us_price = float(obj.price) / float(to_convert_us_currency.system_rate)

                # print("currency-=-=-==-==-=--3---->",currency)
                # print("currency.currency_code-=-=-==-==-=--3---->",currency.currency_code)
                # print("calculate_us_price-=-=-==-==-=--3---->",calculate_us_price)

            else:
                # print("currency-=----2")
                currency = models.CurrencyConverter.objects.get(currency_code = get_country.currency_code)
                # print("cprint("Country-=----2--->",currency)
                to_convert_us_currency = models.CurrencyConverter.objects.get(currency_code = "XOF")
                calculate_us_price = float(obj.price) / float(to_convert_us_currency.system_rate)

            if calculate_us_price < 1:
                calculate_us_price = 1

            # print(calculate_us_price, 'calculate_us_price')

            if currency.currency_code == "XOF" and not get_country.currency_code == "USD":
                value = math.ceil(float(obj.price))
                return f"{value:,}".replace(",", " ")
            
            # elif currency.currency_code == "XAF":
                # value = math.ceil(float(calculate_us_price) * float(currency.system_rate))   
                # return f"{value:,}".replace(",", " ")
                # # # print("currency.system_rate=====>",currency.system_rate)    
                # value = math.ceil(float(calculate_us_price) * float(currency.system_rate))         
                # return f"{value:,}".replace(",", " ")

            elif currency.currency_code == "USD":  
                # # print("currency.system_rate=====>",currency.system_rate)    
                # value = math.ceil(float(calculate_us_price) * float(currency.system_rate))         
                # return f"{value:,}".replace(",", " ")
                value = math.ceil(float(calculate_us_price))
                # print("value===USDDDD==>",value)    
                return f"{value:,}".replace(",", " ")

            else:
                # # print("currency.system_rate=====>",currency.system_rate)    
                value = math.ceil(float(calculate_us_price) * float(currency.system_rate))         
                return f"{value:,}".replace(",", " ")
            

        
        except Exception as e:
            print("error----->",e)
            value = math.ceil(float(obj.price))
            return f"{value:,}".replace(",", " ")



class ProductNameSerializer(serializers.ModelSerializer):   
    
    class Meta:
        model = models.ProductDetail
        fields = ['product_name', 'product_name_french' ]



class ProductRequestSerializer(serializers.ModelSerializer):   
    
    class Meta:
        model = models.ProductRequest
        fields = '__all__'

    def to_representation(self, instance):
        self.fields['vendor'] =  VendorDetailSerializer(read_only=True)
        return super(ProductRequestSerializer, self).to_representation(instance)



class VendorProductPriceSerializer(serializers.ModelSerializer):   
    
    class Meta:
        model = models.VendorProductPrice
        fields = '__all__'

    def to_representation(self, instance):
        self.fields['vendor'] =  VendorDataSerializer(read_only=True)
        return super(VendorProductPriceSerializer, self).to_representation(instance)


class VendorProductDataSerializer(serializers.ModelSerializer):   
    vendor_id = serializers.ReadOnlyField(source='vendor.id')
    vendor_name = serializers.ReadOnlyField(source='vendor.vendor_name')
    phone_number = serializers.ReadOnlyField(source='vendor.phone_number')
    category_name = serializers.ReadOnlyField(source='vendor.category.category')
    
    class Meta:
        model = models.VendorProductPrice
        fields = ['vendor', 'vendor_id','vendor_name', 'phone_number', 'category_name', 'price']

    # def to_representation(self, instance):
    #     self.fields['vendor'] =  VendorDataSerializer(read_only=True)
    #     return super(VendorProductDataSerializer, self).to_representation(instance)


class AdminProductModelVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ProductModelVariant
        fields = ['id','model','name','image','price','status']

class AdminProductModelSerializer(serializers.ModelSerializer):
    variants = serializers.SerializerMethodField()
    name = serializers.ReadOnlyField(source='model_name')
    image = serializers.ReadOnlyField(source='model_image.url')

    class Meta:
        model = models.ProductModel
        fields = ['id','product','name','image','variants']

    def get_variants(self, obj):
        variant_list = models.ProductModelVariant.objects.filter(model_id = obj.id)
        variant_list_serializer = AdminProductModelVariantSerializer(variant_list, many=True).data

        return variant_list_serializer


class AdminProductDetailSerializer(serializers.ModelSerializer):   
    category_name = serializers.ReadOnlyField(source='category.category')
    # category_id = serializers.ReadOnlyField(source='category.id')
    subcategory_name = serializers.ReadOnlyField(source='subcategory.subcategory')
    # subcategory_id = serializers.ReadOnlyField(source='subcategory.id')
    # super_subcategory_name = serializers.ReadOnlyField(source='super_subcategory.super_subcategory')
    # super_subcategory_id = serializers.ReadOnlyField(source='super_subcategory.id')

    list_model = serializers.SerializerMethodField()

    class Meta:
        model = models.ProductDetail
        fields = ["id", "product_name", "product_code", "vendor", "category", "category_name", "subcategory", "subcategory_name", "description", "unit_of_measure", "material", "length", "height", "width", "weight", "color", "min_order_quantity", "max_order_quantity", "product_image_1", "product_image_2", "product_image_3", "product_image_4", "price", "discount", "final_price", "product_verification", "status", "list_model"]

    
    def get_list_model(self, obj):
        model_list = models.ProductModel.objects.filter(product_id = obj.id)
        model_list_serilizer = AdminProductModelSerializer(model_list, many=True).data

        return model_list_serilizer

class ProductModelSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(source='model_name')
    image = serializers.SerializerMethodField()

    class Meta:
        model = models.ProductModel
        fields = ['id','product','model_name','name','model_name_french','model_image','image','status']

    def get_image(self, obj):
        if obj.model_image not in [None,'','null']:
            return obj.model_image.url
        elif obj.product.product_image_1:
            return obj.product.product_image_1.url
        return None



class CustomerDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.CustomerDetail
        fields = '__all__'

class CustomerAddressDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.CustomerAddressDetail
        fields = '__all__'


class WishlistDetailSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source='product.product_name')
    product_image_1 = serializers.ReadOnlyField(source='product.product_image_1.url')
    category_name = serializers.ReadOnlyField(source='product.category.category')
    shipping_via = serializers.ReadOnlyField(source='product.shipping_via')

    carton_length = serializers.ReadOnlyField(source = 'product.carton_length')
    carton_width = serializers.ReadOnlyField(source = 'product.carton_width')
    carton_height = serializers.ReadOnlyField(source = 'product.carton_height')
    carton_weight = serializers.ReadOnlyField(source = 'product.carton_weight')

    

    class Meta:
        model = models.WishlistDetail
        fields = ['id','customer','product','created_at','product_name','product_image_1',
                  'category_name','shipping_via','carton_length','carton_width','carton_height',
                  'carton_weight']

    



class CartDetailSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source='product.product_name')
    min_order_quantity = serializers.ReadOnlyField(source='product.min_order_quantity')
    max_order_quantity = serializers.ReadOnlyField(source='product.max_order_quantity')
    
    carton_length = serializers.ReadOnlyField(source = 'product.carton_length')
    carton_width = serializers.ReadOnlyField(source = 'product.carton_width')
    carton_height = serializers.ReadOnlyField(source = 'product.carton_height')
    carton_weight = serializers.ReadOnlyField(source = 'product.carton_weight')

    variant_name = serializers.ReadOnlyField(source='variant.name')
    image = serializers.SerializerMethodField()
    # price = serializers.ReadOnlyField(source='variant.price')

    price = serializers.SerializerMethodField()
    currency = serializers.SerializerMethodField()

    class Meta:
        model = models.CartDetail
        fields = '__all__'

    
    def get_currency(self, obj):
        country = self.context.get('country','Egypt')
        # print("country--get_currency--->",country)
        if models.CountryWithCurrency.objects.filter(country_name = country).exists():
            try:
                return models.CountryWithCurrency.objects.filter(country_name = country).first().currency_symbol
            except:
                return "$"
        else:
            return "$"

    def get_image(self, obj):
        if obj.variant.image not in [None,'','null']:
            return obj.variant.image.url
        elif obj.variant.model.model_image:
            return obj.variant.model.model_image.url
        elif obj.product.product_image_1:
            return obj.product.product_image_1.url
        return None



    def get_price(self, obj):
        country = self.context.get('country','Egypt')
        # print("country=-first __get_price=-==-->",country)
        if not models.CountryWithCurrency.objects.filter(country_name = country).exists():
            country = 'Egypt'

        try:
            # print("Variant country=-=-==-->",country)
            get_country = models.CountryWithCurrency.objects.get(country_name = country)
            # print("Country-=----1--->",get_country.currency_code)
            if get_country.currency_code == "USD":
                # print("currency-=----1")
                currency = get_country
                to_convert_us_currency = models.CurrencyConverter.objects.get(currency_code = "XOF")
                calculate_us_price = float(obj.variant.price) / float(to_convert_us_currency.system_rate)

                # print("currency-=-=-==-==-=--3---->",currency)
                # print("currency.currency_code-=-=-==-==-=--3---->",currency.currency_code)
                # print("calculate_us_price-=-=-==-==-=--3---->",calculate_us_price)

            else:
                # print("currency-=----2")
                currency = models.CurrencyConverter.objects.get(currency_code = get_country.currency_code)
                # print("cprint("Country-=----2--->",currency)
                to_convert_us_currency = models.CurrencyConverter.objects.get(currency_code = "XOF")
                calculate_us_price = float(obj.variant.price) / float(to_convert_us_currency.system_rate)

            if calculate_us_price < 1:
                calculate_us_price = 1

            # print(calculate_us_price, 'calculate_us_price')

            if currency.currency_code == "XOF" and not get_country.currency_code == "USD":
                value = math.ceil(float(obj.variant.price))
                
                # return f"{value:,}".replace(",", " ")
                return value
            
            # elif currency.currency_code == "XAF":
                # value = math.ceil(float(calculate_us_price) * float(currency.system_rate))   
                # return f"{value:,}".replace(",", " ")
                # # # print("currency.system_rate=====>",currency.system_rate)    
                # value = math.ceil(float(calculate_us_price) * float(currency.system_rate))         
                # return f"{value:,}".replace(",", " ")

            elif currency.currency_code == "USD":  
                # # print("currency.system_rate=====>",currency.system_rate)    
                # value = math.ceil(float(calculate_us_price) * float(currency.system_rate))         
                # return f"{value:,}".replace(",", " ")
                value = math.ceil(float(calculate_us_price))
                # print("value===USDDDD==>",value)    
                # return f"{value:,}".replace(",", " ")
                return value

            else:
                # # print("currency.system_rate=====>",currency.system_rate)    
                value = math.ceil(float(calculate_us_price) * float(currency.system_rate))         
                # return f"{value:,}".replace(",", " ")
                return value
            

        
        except Exception as e:
            print("error----->",e)
            value = math.ceil(float(obj.variant.price))
            # return f"{value:,}".replace(",", " ")
            return value



class CargoDetailSerializer(serializers.ModelSerializer):
    country_name = serializers.ReadOnlyField(source='country.country_name')
    
    class Meta:
        model = models.CargoDetail
        fields = '__all__'
    

class OrderDetailSerializer(serializers.ModelSerializer):
    # status = serializers.ReadOnlyField(source='order_status')
    bank_detail = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()

    class Meta:
        model = models.OrderDetail
        fields = '__all__'

    def to_representation(self, instance):
        self.fields['customer'] =  CustomerDetailSerializer(read_only=True)
        self.fields['customer_address'] =  CustomerAddressDetailSerializer(read_only=True)
        self.fields['cargo'] =  CargoDetailSerializer(read_only=True)
        return super(OrderDetailSerializer, self).to_representation(instance)
    
    def get_bank_detail(self, obj):
        bank = models.OrderPaymentReceivingBankDetail.objects.filter(order = obj.id).first()
        if bank:
            return {
                "holder_name":bank.holder_name,
                "bank_name":bank.bank_name,
                "account_number":bank.account_number,
                "branch_name":bank.branch_name,
                "branch_code":bank.branch_code,
            }
        else:
            return None
    def get_images(self, obj):
        all_products = models.ProductOrderDetail.objects.filter(
            Q(variant__image__isnull = False),
            # Q(product__product_image_1__isnull = False)|
            # Q(product__product_image_2__isnull = False)|
            # Q(product__product_image_3__isnull = False)|
            # Q(product__product_image_4__isnull = False)|
            # Q(product__product_image_5__isnull = False)|
            # Q(product__product_image_6__isnull = False)|
            # Q(product__product_image_7__isnull = False)|
            # Q(product__product_image_8__isnull = False),
            order = obj.id,
            )
        image = []

        for get_product_image in all_products:
            if get_product_image.variant.image not in [None,'','null']:
                image.append(get_product_image.variant.image.url)
            # elif get_product_image.product.product_image_2 not in [None,'','null']:
            #     image.append(get_product_image.product.product_image_2.url)
            # elif get_product_image.product.product_image_3 not in [None,'','null']:
            #     image.append(get_product_image.product.product_image_3.url)
            # elif get_product_image.product.product_image_4 not in [None,'','null']:
            #     image.append(get_product_image.product.product_image_4.url)
            # elif get_product_image.product.product_image_5 not in [None,'','null']:
            #     image.append(get_product_image.product.product_image_5.url)
            # elif get_product_image.product.product_image_6 not in [None,'','null']:
            #     image.append(get_product_image.product.product_image_6.url)
            # elif get_product_image.product.product_image_7 not in [None,'','null']:
            #     image.append(get_product_image.product.product_image_7.url)
            # elif get_product_image.product.product_image_8 not in [None,'','null']:
            #     image.append(get_product_image.product.product_image_8.url)
        print("image======>",image)
        return image

class OrderInquiryDataSerializer(serializers.ModelSerializer):
    # cargo_name = serializers.ReadOnlyField(source='cargo.cargo_name')
    
    total_price = serializers.SerializerMethodField()
    bank_detail = serializers.SerializerMethodField()
    
    class Meta:
        model = models.OrderDetail
        fields = '__all__'

    # def to_representation(self, instance):
    #     self.fields['customer_address'] =  CustomerAddressDetailSerializer(read_only=True)
    #     return super(OrderDetailDataSerializer, self).to_representation(instance)

    def get_bank_detail(self, obj):
        bank = models.OrderPaymentReceivingBankDetail.objects.filter(order = obj.id).first()
        if bank:
            return {
                "holder_name":bank.holder_name,
                "bank_name":bank.bank_name,
                "account_number":bank.account_number,
                "branch_name":bank.branch_name,
                "branch_code":bank.branch_code,
            }
        else:
            return None
    
    def get_total_price(self, obj):
        return int(float(obj.total_price))
    # def get_air_shipping_price(self, obj):
    #     return int(float(obj.air_shipping_price))
    # def get_ship_shipping_price(self, obj):
    #     return int(float(obj.ship_shipping_price))

class OrderDetailDataSerializer(serializers.ModelSerializer):
    cargo_name = serializers.ReadOnlyField(source='cargo.cargo_name')
    
    total_price = serializers.SerializerMethodField()
    bank_detail = serializers.SerializerMethodField()
    
    class Meta:
        model = models.OrderDetail
        fields = '__all__'

    def to_representation(self, instance):
        self.fields['customer_address'] =  CustomerAddressDetailSerializer(read_only=True)
        return super(OrderDetailDataSerializer, self).to_representation(instance)

    def get_bank_detail(self, obj):
        bank = models.OrderPaymentReceivingBankDetail.objects.filter(order = obj.id).first()
        if bank:
            return {
                "holder_name":bank.holder_name,
                "bank_name":bank.bank_name,
                "account_number":bank.account_number,
                "branch_name":bank.branch_name,
                "branch_code":bank.branch_code,
            }
        else:
            return None
    
    def get_total_price(self, obj):
        return int(float(obj.total_price))
    # def get_air_shipping_price(self, obj):
    #     return int(float(obj.air_shipping_price))
    # def get_ship_shipping_price(self, obj):
    #     return int(float(obj.ship_shipping_price))


class OrderDetailExportSerializer(serializers.ModelSerializer):
    cargo_name = serializers.ReadOnlyField(source='cargo.cargo_name')
    customer_name = serializers.ReadOnlyField(source='customer.name')
    email = serializers.ReadOnlyField(source='customer.email')
    countryCode = serializers.ReadOnlyField(source='customer.countryCode')
    mobileNumber = serializers.ReadOnlyField(source='customer.mobileNumber')
    
    total_price = serializers.SerializerMethodField()
    
    class Meta:
        model = models.OrderDetail
        fields = '__all__'

    def get_total_price(self, obj):
        return int(float(obj.total_price))
    # def get_air_shipping_price(self, obj):
    #     return int(float(obj.air_shipping_price))
    # def get_ship_shipping_price(self, obj):
    #     return int(float(obj.ship_shipping_price))




class WarehouseDetailSerializer(serializers.ModelSerializer):   
    
    class Meta:
        model = models.WarehouseDetail
        fields = '__all__'



# class ProductOrderDetailSerializer(serializers.ModelSerializer):
#     variant_name = serializers.ReadOnlyField(source='variant.name')
#     variant_image = serializers.ReadOnlyField(source='variant.image.url')
#     order_id = serializers.ReadOnlyField(source='order.order_id')
#     order_status = serializers.ReadOnlyField(source='order.order_status')
#     product_code = serializers.ReadOnlyField(source='product.product_code')
#     product_name = serializers.ReadOnlyField(source='product.product_name')
#     model_name = serializers.ReadOnlyField(source='variant.model.model_name')
#     warehouse_name = serializers.ReadOnlyField(source='warehouse.name')
#     product_cfa_price = serializers.ReadOnlyField(source = 'variant.price')
    
#     # total_price = serializers.SerializerMethodField()
    


#     class Meta:
#         model = models.ProductOrderDetail
#         fields = '__all__'

#     # def get_total_price(self, obj):
#     #         return int(float(obj.total_price))


class ProductOrderDetailSerializer(serializers.ModelSerializer):
    variant_name = serializers.ReadOnlyField(source='variant.name')
    order_id = serializers.ReadOnlyField(source='order.order_id')
    order_status = serializers.ReadOnlyField(source='order.order_status')
    product_code = serializers.ReadOnlyField(source='product.product_code')
    product_name = serializers.ReadOnlyField(source='product.product_name')
    model_name = serializers.ReadOnlyField(source='variant.model.model_name')
    warehouse_name = serializers.ReadOnlyField(source='warehouse.name')
    product_cfa_price = serializers.ReadOnlyField(source='variant.price')

    variant_image = serializers.SerializerMethodField()

    def get_variant_image(self, obj):
        image = getattr(obj.variant, 'image', None)

        if image and image.name:
            try:
                return image.url
            except ValueError:
                return None

        return None

    class Meta:
        model = models.ProductOrderDetail
        fields = '__all__'




class ProductOrderDetailDataSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.ProductOrderDetail
        fields = '__all__'



class ProductOrderDataSerializer(serializers.ModelSerializer):
    variant_name = serializers.ReadOnlyField(source='variant.name')
    product_name = serializers.ReadOnlyField(source='product.product_name')
    product_code = serializers.ReadOnlyField(source='product.product_code')
    product_id = serializers.ReadOnlyField(source='product.id')
    model_name = serializers.ReadOnlyField(source='variant.model.model_name')
    warehouse_name = serializers.ReadOnlyField(source='warehouse.name')
    variant_image = serializers.SerializerMethodField()

    class Meta:
        model = models.ProductOrderDetail
        # fields = ['id', 'variant_name', 'product_name', 'model_name', 'product_id']
        fields = ['id', 'order','product','variant','warehouse','quantity',
                  'price','total_price','shipping_via','status','vendor_status',
                  'variant_name','product_name','product_code','product_id','model_name','warehouse_name',
                  'variant_image']
        # fields = '__all__'

    def get_variant_image(self, obj):
        if obj.variant.image:
            return obj.variant.image.url
        
        return None


class VendorOrderDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.VendorOrderDetail
        fields = '__all__'

    def to_representation(self, instance):
        self.fields['order'] =  OrderDetailSerializer(read_only=True)
        self.fields['variant'] =  ProductOrderDataSerializer(read_only=True)
        self.fields['warehouse'] =  WarehouseDetailSerializer(read_only=True)
        
        return super(VendorOrderDetailSerializer, self).to_representation(instance)


class VendorOrderDataSerializer(serializers.ModelSerializer):
    product_cfa_price = serializers.ReadOnlyField(source = 'variant.variant.price')
    vendor_cfa_price = serializers.SerializerMethodField()

    class Meta:
        model = models.VendorOrderDetail
        fields = '__all__'

    def get_vendor_cfa_price(self, obj):
        try:
            return models.VendorProductPrice.objects.filter(vendor = obj.vendor.id , variant = obj.variant.variant.id).first().price
        except:
            return models.VendorProductPrice.objects.filter(variant = obj.variant.variant.id).first().price

    def to_representation(self, instance):
        self.fields['vendor'] =  VendorDataSerializer(read_only=True)
        return super(VendorOrderDataSerializer, self).to_representation(instance)


class OrderTrackingSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.OrderTracking
        fields = '__all__'



class VendorOrderTrackingSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.VendorOrderTracking
        fields = '__all__'


class ProductDetailTransalteSerializer(serializers.ModelSerializer):   
   

    class Meta:
        model = models.ProductDetail
        fields = '__all__'



class VendorProductvariantSerializer(serializers.ModelSerializer):   
    
    class Meta:
        model = models.VendorProductPrice
        fields = '__all__'

    def to_representation(self, instance):
        self.fields['vendor'] =  VendorDataSerializer(read_only=True)
        return super(VendorProductvariantSerializer, self).to_representation(instance)



class AdminProductDataSerializer(serializers.ModelSerializer):   
    category_name = serializers.ReadOnlyField(source='category.category')
    category_id = serializers.ReadOnlyField(source='category.id')
    subcategory_name = serializers.ReadOnlyField(source='subcategory.subcategory')
    subcategory_id = serializers.ReadOnlyField(source='subcategory.id')

    class Meta:
        model = models.ProductDetail
        fields = ["id", "product_name", "product_code", "category_name", "category_id", "subcategory_name", "subcategory_id", 'available_quantity', \
        "min_order_quantity", "max_order_quantity", "product_image_1", "status", 'product_verification']

class AdminProductModelDataSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(source='model_name')
    image = serializers.SerializerMethodField()

    class Meta:
        model = models.ProductModel
        fields = ['id','product','name','image']
    
    def get_image(self, obj):
        if obj.model_image:
            return obj.model_image.url
        return None




class ChatConversionSerializer(serializers.ModelSerializer):
    sender = serializers.ReadOnlyField(source = 'send_by')
    send_time = serializers.SerializerMethodField()
    agent_type = serializers.SerializerMethodField()
    agent_name = serializers.SerializerMethodField()
    class Meta:
        model = models.ChatConversion
        fields = ['id','user','admin','room','message','message_type','send_by','file','file_type','create_at','status','sender','send_time','agent_type','agent_name','message_french','product_id']

    def get_send_time(self, obj):
        return obj.create_at.strftime('%Y-%m-%d %H:%M:%S')
    
    def get_agent_type(self, obj):
        if obj.chat_agent not in [None,'','null']:
            return obj.chat_agent.agent_type
        
        return None
    
    
    def get_agent_name(self, obj):
        if obj.chat_agent not in [None,'','null']:
            return obj.chat_agent.name
        
        return "Agent"
    

class ChatRoomChatAgentDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ChatAgentDetail
        fields = ['id','email','mobileNumber','name','agent_type']
    


class ChatRoomSerializer(serializers.ModelSerializer):
    user_name = serializers.ReadOnlyField(source = 'user.name')
    user_email = serializers.ReadOnlyField(source = 'user.email')
    user_country_code = serializers.ReadOnlyField(source = 'user.countryCode')
    user_mobile_number = serializers.ReadOnlyField(source = 'user.mobileNumber')

    unseen_count = serializers.SerializerMethodField()
    last_message_detail = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    last_message_send_date = serializers.SerializerMethodField()
    last_message_type = serializers.SerializerMethodField()

    agent_detail = serializers.SerializerMethodField()

    class Meta:
        model = models.ChatRoom
        fields = ['id','user','admin','room','created_at','user_name','user_email','user_country_code','user_mobile_number','unseen_count','last_message_detail','last_message','last_message_send_date','agent_detail','priority','is_resolved','note','last_message_type']

    def get_unseen_count(self, obj):
        return models.ChatConversion.objects.filter(user__isnull = False, room = obj.id,status = "Unseen").count()
    
    def get_last_message(self, obj):
        last_message = models.ChatConversion.objects.filter(room = obj.id).last()
        
        if last_message:
            message = last_message.message
        else:
            message = ""
        return message
    
    def get_last_message_send_date(self, obj):
        return obj.updated_at.strftime('%Y-%m-%d %H:%M:%S')
    
    def get_last_message_detail(self, obj):
        last_message = models.ChatConversion.objects.filter(room = obj.id).last()

        # print("Last message------>",last_message)

        if last_message:
            message = last_message.message
            send_by = last_message.send_by
        else:
            message = ""
            send_by = ""
        
        return {
            'message':message,
            'send_by':send_by
        }
    
    def get_agent_detail(self, obj):
        if obj.chat_agent not in [None, 'null','']:
            agent_detail = models.ChatAgentDetail.objects.get(id = obj.chat_agent.id)
            return ChatRoomChatAgentDetailSerializer(agent_detail).data
        return
    
    def get_last_message_type(self, obj):
        last_message = models.ChatConversion.objects.filter(room = obj.id).last()
        if last_message:
            # print("Last message type------>",last_message.message_type)
            # print("Last file_type type------>",last_message.file_type)
            # print("Last ------>",last_message)
            return last_message.file_type if last_message.file_type else "text"
        return ""
class DailyPriceSerializer(serializers.ModelSerializer):   
    
    class Meta:
        model = models.DailyPrice
        fields = '__all__'


class ChatCustomerDetailSerializer(serializers.ModelSerializer): 
    room_created_on = serializers.SerializerMethodField()  
    
    class Meta:
        model = models.CustomerDetail
        fields = ['id','email','mobileNumber','name','room_created_on']

    def get_room_created_on(self, obj):
        return models.ChatRoom.objects.get(user = obj.id).created_at


class AdminChatAgentDetailSerializer(serializers.ModelSerializer):   
    total_assigned_room = serializers.SerializerMethodField()
    
    class Meta:
        model = models.ChatAgentDetail
        fields = ['id','email','countryCode','mobileNumber','userType','agent_type','name','lastLoginDate','OTP','password','status','created_at','total_assigned_room']

    def get_total_assigned_room(self, obj):
        return models.ChatRoom.objects.filter(chat_agent = obj.id,is_resolved__in = [False, "false","False"]).count()

    
class AgentInChatRoomHistorySerializer(serializers.ModelSerializer):      
    agent_name = serializers.ReadOnlyField(source = 'agent.name')
    agent_type = serializers.ReadOnlyField(source = 'agent.agent_type')
    class Meta:
        model = models.AgentInChatRoomHistory
        fields = ['id','room','agent','agent_name','assigned_date','unassigned_date','agent_type']

class AboutUsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AboutUs
        fields = '__all__'


class PrivacyPolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PrivacyPolicy
        fields = '__all__'

class RefundPolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.RefundPolicy
        fields = '__all__'

class TermsAndConditionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.TermsAndCondition
        fields = '__all__'

 

class VendorTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.VendorTransaction
        fields = '__all__'

 

class ProductDetailCheckSerializer(serializers.ModelSerializer):
    # country_of_origin_image = serializers.ReadOnlyField(source = 'country_of_origin.image')
    country_of_origin_image = serializers.ReadOnlyField(source='country_of_origin.image.url')
    price = serializers.SerializerMethodField()
    currency = serializers.SerializerMethodField()


    class Meta:
        model = models.ProductDetail
        exclude = ['product_image_1_vector', 'description','description_french', 'product_image_2_vector', 'product_image_3_vector', 'product_image_4_vector',
        'product_image_5_vector', 'product_image_6_vector', 'product_image_7_vector', 'product_image_8_vector']

    
    def get_currency(self, obj):
        country = self.context.get('country','Egypt')
        if models.CountryWithCurrency.objects.filter(country_name = country).exists():
            try:
                return models.CountryWithCurrency.objects.filter(country_name = country).first().currency_symbol
            except:
                return "$"
        else:
            return "$"



    def get_price(self, obj):
        country = self.context.get('country','Egypt')
        if not models.CountryWithCurrency.objects.filter(country_name = country).exists():
            country = 'Egypt'

        try:
            # print("Variant country=-=-==-->",country)
            get_country = models.CountryWithCurrency.objects.get(country_name = country)
            # print("Country-=----1--->",get_country.currency_code)
            if get_country.currency_code == "USD":
                # print("currency-=----1")
                currency = get_country

                to_convert_us_currency = models.CurrencyConverter.objects.get(currency_code = "XOF")
                calculate_us_price = float(obj.price) / float(to_convert_us_currency.system_rate)

                # print("currency-=-=-==-==-=--3---->",currency)
                # print("currency.currency_code-=-=-==-==-=--3---->",currency.currency_code)
                # print("calculate_us_price-=-=-==-==-=--3---->",calculate_us_price)

            else:
                # print("currency-=----2")
                currency = models.CurrencyConverter.objects.get(currency_code = get_country.currency_code)
                # print("cprint("Country-=----2--->",currency)
                to_convert_us_currency = models.CurrencyConverter.objects.get(currency_code = "XOF")
                calculate_us_price = float(obj.price) / float(to_convert_us_currency.system_rate)

            if calculate_us_price < 1:
                calculate_us_price = 1

            # print(calculate_us_price, 'calculate_us_price')

            if currency.currency_code == "XOF" and not get_country.currency_code == "USD":
                value = math.ceil(float(obj.price))
                return f"{value:,}".replace(",", " ")
            
            # elif currency.currency_code == "XAF":
                # value = math.ceil(float(calculate_us_price) * float(currency.system_rate))   
                # return f"{value:,}".replace(",", " ")
                # # # print("currency.system_rate=====>",currency.system_rate)    
                # value = math.ceil(float(calculate_us_price) * float(currency.system_rate))         
                # return f"{value:,}".replace(",", " ")

            elif currency.currency_code == "USD":  
                # # print("currency.system_rate=====>",currency.system_rate)    
                # value = math.ceil(float(calculate_us_price) * float(currency.system_rate))         
                # return f"{value:,}".replace(",", " ")
                value = math.ceil(float(calculate_us_price))
                # print("value===USDDDD==>",value)    
                return f"{value:,}".replace(",", " ")

            else:
                # # print("currency.system_rate=====>",currency.system_rate)    
                value = math.ceil(float(calculate_us_price) * float(currency.system_rate))         
                return f"{value:,}".replace(",", " ")

        
        except Exception as e:
            print("error----->",e)
            value = math.ceil(float(obj.price))
            return f"{value:,}".replace(",", " ")




class RecentlyViewProductSerializer(serializers.ModelSerializer):
    price = serializers.SerializerMethodField()
    currency = serializers.SerializerMethodField()
    
    class Meta:
        model = models.RecentlyViewProduct
        fields = '__all__'

    def get_currency(self, obj):
        country = self.context.get('country','Egypt')
        if models.CountryWithCurrency.objects.filter(country_name = country).exists():
            try:
                return models.CountryWithCurrency.objects.filter(country_name = country).first().currency_symbol
            except:
                return "$"
        else:
            return "$"



    def get_price(self, obj):
        country = self.context.get('country','Egypt')
        if not models.CountryWithCurrency.objects.filter(country_name = country).exists():
            country = 'Egypt'

        try:
            # print("Variant country=-=-==-->",country)
            get_country = models.CountryWithCurrency.objects.get(country_name = country)
            # print("Country-=----1--->",get_country.currency_code)
            if get_country.currency_code == "USD":
                # print("currency-=----1")
                currency = get_country
                to_convert_us_currency = models.CurrencyConverter.objects.get(currency_code = "XOF")
                calculate_us_price = float(obj.product.price) / float(to_convert_us_currency.system_rate)

                # print("currency-=-=-==-==-=--3---->",currency)
                # print("currency.currency_code-=-=-==-==-=--3---->",currency.currency_code)
                # print("calculate_us_price-=-=-==-==-=--3---->",calculate_us_price)

            else:
                # print("currency-=----2")
                currency = models.CurrencyConverter.objects.get(currency_code = get_country.currency_code)
                # print("cprint("Country-=----2--->",currency)
                to_convert_us_currency = models.CurrencyConverter.objects.get(currency_code = "XOF")
                calculate_us_price = float(obj.product.price) / float(to_convert_us_currency.system_rate)

            if calculate_us_price < 1:
                calculate_us_price = 1

            # print(calculate_us_price, 'calculate_us_price')

            if currency.currency_code == "XOF" and not get_country.currency_code == "USD":
                value = math.ceil(float(obj.product.price))
                return f"{value:,}".replace(",", " ")
            
            # elif currency.currency_code == "XAF":
                # value = math.ceil(float(calculate_us_price) * float(currency.system_rate))   
                # return f"{value:,}".replace(",", " ")
                # # # print("currency.system_rate=====>",currency.system_rate)    
                # value = math.ceil(float(calculate_us_price) * float(currency.system_rate))         
                # return f"{value:,}".replace(",", " ")

            elif currency.currency_code == "USD":  
                # # print("currency.system_rate=====>",currency.system_rate)    
                # value = math.ceil(float(calculate_us_price) * float(currency.system_rate))         
                # return f"{value:,}".replace(",", " ")
                value = math.ceil(float(calculate_us_price))
                # print("value===USDDDD==>",value)    
                return f"{value:,}".replace(",", " ")

            else:
                # # print("currency.system_rate=====>",currency.system_rate)    
                value = math.ceil(float(calculate_us_price) * float(currency.system_rate))         
                return f"{value:,}".replace(",", " ")
            

        
        except Exception as e:
            print("error----->",e)
            value = math.ceil(float(obj.product.price))
            return f"{value:,}".replace(",", " ")
        

    def to_representation(self, instance):
        self.fields['product'] =  ProductDataSerializer(read_only=True)
        return super(RecentlyViewProductSerializer, self).to_representation(instance)



class AdminModuleRightsDetailSerializer(serializers.ModelSerializer):   
    
    class Meta:
        model = models.AdminModuleRightsDetail
        fields = '__all__'

class OrderTransactionSerializer(serializers.ModelSerializer):   
    order_id = serializers.ReadOnlyField(source='order.order_id')
    id_order = serializers.ReadOnlyField(source='order.id')
    customer_email = serializers.ReadOnlyField(source='customer.email')
    customer_mobileNumber = serializers.ReadOnlyField(source='customer.mobileNumber')
    customer_countryCode = serializers.ReadOnlyField(source='customer.countryCode')
    customer_id = serializers.ReadOnlyField(source='customer.id')
    
    
    class Meta:
        model = models.OrderTransaction
        fields = '__all__'


class AdminCountryWithCurrencyListSerializer(serializers.ModelSerializer):

    holder_name = serializers.SerializerMethodField()
    bank_name = serializers.SerializerMethodField()
    account_number = serializers.SerializerMethodField()
    branch_name = serializers.SerializerMethodField()
    branch_code = serializers.SerializerMethodField()   
    cash_limit = serializers.SerializerMethodField()   
    
    class Meta:
        model = models.CountryWithCurrency
        fields = '__all__'


    def get_holder_name(self, obj):
        get_bank_detail = models.CountryWiseBankDetail.objects.filter(country = obj.id).first()
        return get_bank_detail.holder_name if get_bank_detail else None

    def get_bank_name(self, obj):
        get_bank_detail = models.CountryWiseBankDetail.objects.filter(country = obj.id).first()
        return get_bank_detail.bank_name if get_bank_detail else None

    def get_account_number(self, obj):
        get_bank_detail = models.CountryWiseBankDetail.objects.filter(country = obj.id).first()
        return get_bank_detail.account_number if get_bank_detail else None

    def get_branch_name(self, obj):
        get_bank_detail = models.CountryWiseBankDetail.objects.filter(country = obj.id).first()
        return get_bank_detail.branch_name if get_bank_detail else None

    def get_branch_code(self, obj):
        get_bank_detail = models.CountryWiseBankDetail.objects.filter(country = obj.id).first()
        return get_bank_detail.branch_code if get_bank_detail else None
    def get_cash_limit(self, obj):
        cash_limit_detail = models.CountryCashLimit.objects.filter(country = obj.id).first()
        return cash_limit_detail.cash_limit if cash_limit_detail else None


class AdminCountrySerializer(serializers.ModelSerializer):   
    
    class Meta:
        model = models.Country
        fields = '__all__'


class AdminCurrencyConverterSerializer(serializers.ModelSerializer):   
    
    class Meta:
        model = models.CurrencyConverter
        fields = '__all__'


class IntroBannerSerializer(serializers.ModelSerializer):  
 
    class Meta:
        model = models.IntroBanner
        fields =  '__all__'
 
class InfluencerDetailSerializer(serializers.ModelSerializer):  

    class Meta:
        model = models.InfluencerDetail
        fields =  '__all__'
 
  
class PromocodeDetailSerializer(serializers.ModelSerializer):  
    influencer_name = serializers.ReadOnlyField(source='influencer.name')

    class Meta:
        model = models.PromocodeDetail
        fields =  '__all__'


  
class MoneyNetworkSerializer(serializers.ModelSerializer):  
    # country_name = serializers.ReadOnlyField(source='country.country_name')
    # key = serializers.ReadOnlyField(source='country.key')

    class Meta:
        model = models.MoneyNetwork
        fields =  '__all__'
  
class CountryWiseBankDetailSerializer(serializers.ModelSerializer):  
    class Meta:
        model = models.CountryWiseBankDetail
        fields =  '__all__'



class ProductOrderDetailOrderSerializer(serializers.ModelSerializer):
    variant_name = serializers.ReadOnlyField(source='variant.name')
    order_id = serializers.ReadOnlyField(source='order.order_id')
    
    
    class Meta:
        model = models.ProductOrderDetail
        fields = ['order_id', 'variant_name', 'quantity', 'price', 'total_price', 'shipping_via']




class ProductReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ProductReview
        fields = '__all__'

class PaymentCargoSliderSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PaymentCargoSlider
        fields = '__all__'



class ImportantNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ImportantNote
        fields = '__all__'

class ProductCountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ProductCountry
        fields = '__all__'

class ProductTagSerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source='category.category')
    category_french = serializers.ReadOnlyField(source='category.category_french')
    
    class Meta:
        model = models.ProductTag
        fields = '__all__'

    # def to_representation(self, instance):
    #     self.fields['category'] =  CategoryDetailSerializer(read_only=True)
    #     return super(ProductTagSerializer, self).to_representation(instance)

class ProductTagSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ProductTag
        fields = ['id','tag']



class DummyTagProductNameEnglishSerializer(serializers.ModelSerializer):
    tag = serializers.ReadOnlyField(source='product_name')
    
    class Meta:
        model = models.ProductDetail
        fields = ['id','tag']


class DummyTagProductNameFrenchSerializer(serializers.ModelSerializer):
    tag = serializers.ReadOnlyField(source='product_name_french')
    
    class Meta:
        model = models.ProductDetail
        fields = ['id','tag']



class DeliveryDayDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DeliveryDayDetail
        fields = '__all__'

#  Vendor Payment Tracker Serializer
class VendorPaymentTrackerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.VendorPaymentTracker
        fields = '__all__'

class ProductRequestTransactionSerializer(serializers.ModelSerializer):
    class Meta:
            model = models.ProductRequestTransaction
            fields = '__all__'

class ProductInquirySerializer(serializers.ModelSerializer):

    customer_name = serializers.ReadOnlyField(source='customer.name')
    customer_email = serializers.ReadOnlyField(source='customer.email')
    customer_countryCode = serializers.ReadOnlyField(source='customer.countryCode')
    customer_mobileNumber = serializers.ReadOnlyField(source='customer.mobileNumber')
    payment_id = serializers.ReadOnlyField(source='transaction.payment_id')
    reference_id = serializers.ReadOnlyField(source='transaction.reference_id')
    total_amount = serializers.ReadOnlyField(source='transaction.total_amount')
    currency = serializers.ReadOnlyField(source='transaction.currency')
    
    transaction_details = ProductRequestTransactionSerializer(
        source='transaction',
        read_only=True
    )

    
    
    images = serializers.SerializerMethodField()

    class Meta:
        model = models.ProductInquiry
        fields = '__all__'

    def get_images(self, obj):
        images = models.ProductInquiryImages.objects.filter(inquiry=obj.id)

        return [
            img.image.url
            for img in images if img.image
        ]



#  Vendor Payment Tracker Serializer

class VendorDetailExistsInDelayNote(serializers.ModelSerializer):
    # is_included_in_delay_note = serializers.SerializerMethodField()
    class Meta:
        model = models.VendorDetail
        fields = ['id','vendor_name','company_name','phone_number','email']

    # def get_is_included_in_delay_note(self,obj):
    #     return models.VendorDelayNote.objects.filter(
    #         vendor=obj.id,
    #         start_at__lte=datetime.now(),
    #         end_at__gte=datetime.now(),
    #         status="Active"
    #     ).exists()

# class VendorDetailForDelayNote(serializers.ModelSerializer):
#     class Meta:
#         model = models.VendorDetail
#         fields = ['id']

class VendorDelayNoteSerializer(serializers.ModelSerializer):
    vendor_ids = serializers.SerializerMethodField()
    start_at = serializers.DateTimeField(format="%Y-%m-%d", read_only=True)
    end_at = serializers.DateTimeField(format="%Y-%m-%d", read_only=True)
    # vendor = VendorDetailForDelayNote(many=True, read_only=True)
    class Meta:
        model = models.VendorDelayNote
        fields = '__all__'
    
    def get_vendor_ids(self, obj):
        return list(models.VendorDelayNote.objects.filter(id=obj.id).values_list('vendor', flat=True))


class ProductTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ProductType
        fields = '__all__'


class ProductPackagingBySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ProductPackagingBy
        fields = '__all__'


class BannerContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.BannerContent
        fields = '__all__'


class ContainerRequestSerializer(serializers.ModelSerializer):
    customer_name = serializers.ReadOnlyField(source='customer.name')
    email = serializers.ReadOnlyField(source='customer.email')
    countryCode = serializers.ReadOnlyField(source='customer.countryCode')
    mobileNumber = serializers.ReadOnlyField(source='customer.mobileNumber')
    destination_country_name = serializers.ReadOnlyField(source='destination_country.country_name')


    class Meta:
        model = models.ContainerRequest
        fields = '__all__'