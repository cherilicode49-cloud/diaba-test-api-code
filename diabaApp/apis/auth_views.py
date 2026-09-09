from django.views.decorators.csrf import csrf_exempt
from diabaApp import models
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from django.http import HttpResponse
import io
import math, random 
from datetime import datetime, timedelta
from django.template.loader import get_template
from django.core.mail import send_mail
from django.conf import settings
import json
from django.http import JsonResponse

import  requests
from diabaApp.serializer import AdminDetailSerializer, AdminModuleRightsDetailSerializer, CustomerDetailSerializer, VendorDetailSerializer, \
    ChatAgentDetailSerializer


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

