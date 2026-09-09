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
from django.db.models import Max, Min
from django.db.models.functions import Replace, Lower, Greatest
from django.db.models import Value
from django.utils import timezone

import numpy as np
from django.contrib.postgres.search import TrigramSimilarity

from django.template.loader import get_template
from django.core.mail import send_mail
from diabaApp.serializer import ChatConversionSerializer, ChatRoomSerializer, AgentInChatRoomHistorySerializer, ChatCustomerDetailSerializer, \
    AdminChatAgentDetailSerializer, ChatAgentProductDetailSerializer

BASE_URL = settings.BASE_URL
IMAGE_URL = settings.IMAGE_URL


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



