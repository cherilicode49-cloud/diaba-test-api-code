# """
# ASGI config for diaba project.
# """

# import os, time
# import uuid
# import socketio
# from django.core.asgi import get_asgi_application
# import django
# from datetime import datetime
# from django.utils import timezone
# from asgiref.sync import sync_to_async
# from django.db.models import Q, F, Count

# import firebase_config
# from firebase_admin import messaging

# django.setup()


# import asyncio


# # =========================
# # MAIN SOCKET HANDLER
# # =========================


# from diabaApp.models import ChatRoom, ChatConversion, CustomerDetail, ChatAgentDetail, AgentInChatRoomHistory

# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "diaba.settings")

# # FIXED: Get allowed origins based on your actual domains
# def get_allowed_origins():
#     debug_mode = os.environ.get('DEBUG', 'True').lower() == 'true'
    
#     if debug_mode:
#         # Development origins
#         # return [
#         #     "http://localhost:3000",
#         #     "http://localhost:8080", 
#         #     "http://127.0.0.1:3000",
#         #     "http://192.168.0.104:8080",
#         #     # Add your development IP if needed
#         #     "http://41.82.206.106:3000",
#         # ]
#         return "*"
#     else:
#         # Production origins - EXACT MATCH from your error logs
#         return "*"
#         # return [
#         #     "https://admin.diaba.store",          # From your error log
#         #     "https://diaba.store",                # Main domain
#         #     "https://www.diaba.store",            # WWW version  
#         #     "http://41.82.206.106:3000",         # IP from your error log
#         #     # Add any other origins you need
#         # ]

# # Create Socket.IO server with FIXED CORS configuration
# sio = socketio.AsyncServer(
#     async_mode="asgi",
#     cors_allowed_origins=get_allowed_origins(),
#     # Alternative: Allow all origins for testing (NOT recommended for production)
#     # cors_allowed_origins="*",
#     ping_interval=25,
#     ping_timeout=60,
#     max_http_buffer_size=100000,
#     logger=True,  # Keep logging enabled to debug
#     engineio_logger=True,
#     transports=['websocket', 'polling'],
# )

# # Rest of your code remains the same...
# django_app = get_asgi_application()
# application = socketio.ASGIApp(sio, django_app)

# # Track active rooms (users)
# active_rooms = {}
# # AGENT ROOM
# agent_rooms = {}

# @sio.event
# async def connect(sid, environ):
#     origin = environ.get('HTTP_ORIGIN', 'Unknown')
#     user_agent = environ.get('HTTP_USER_AGENT', 'Unknown')
#     print(f"🔌 Client connected: {sid}")
#     print(f"   Origin: {origin}")
#     print(f"   User Agent: {user_agent}")
#     print(f"   Allowed origins: {get_allowed_origins()}")
    
#     try:
#         await sio.emit("server_message", {
#             "data": f"Welcome to Diaba Chat!{origin}", 
#             "status": f"connected {user_agent}",
#             "server_time": datetime.now().isoformat()
#         }, to=sid)
#         print(f" Welcome message sent to {sid}")
#     except Exception as e:
#         print(f" Error sending welcome message: {e}")

# @sio.event  
# async def disconnect(sid):
#     print(f" Client disconnected: {sid}")

# @sio.event
# async def connect_error(sid, data):
#     print(f" Connection error for {sid}: {data}")

# # Your existing sync_to_async functions remain exactly the same...
# @sync_to_async
# def get_or_create_chat_room(user_id, admin_id, room):
#     if user_id not in [None, '', 'null']:
#         if ChatRoom.objects.filter(room=room).exists():
#             chat_room = ChatRoom.objects.get(room=room)
#             if chat_room.chat_agent not in [None,'','null']:
#                 agent_rooms[room] = chat_room.chat_agent.id
#                 print("ROOM AGENT FOUND", chat_room.chat_agent.id)
#                 return chat_room, False
#             else:
#                 all_agent = ChatAgentDetail.objects.filter(status="Active")
#                 unassigned_agent_found = False
                
#                 for check_already_assigned_agent in all_agent:
#                     if ChatRoom.objects.filter(chat_agent=check_already_assigned_agent.id).exists():
#                         pass
#                     else:
#                         agent_id = check_already_assigned_agent.id
#                         unassigned_agent_found = True
#                         break

#                 if not unassigned_agent_found:
#                     chat_room_agent = (
#                         ChatAgentDetail.objects.annotate(
#                         assigned_rooms=Count('chatroom', filter=Q(chatroom__status="Active"))
#                         ).order_by('assigned_rooms').first()
#                     )
#                     agent_id = chat_room_agent.id
                
#                 chat_room.chat_agent_id = agent_id
#                 chat_room.save()
           
#             return chat_room, False
#         else:
#             agent_id = None
#             if ChatAgentDetail.objects.filter(status="Active").exists():
#                 all_agent = ChatAgentDetail.objects.filter(status="Active")
#                 unassigned_agent_found = False
                
#                 for check_already_assigned_agent in all_agent:
#                     if ChatRoom.objects.filter(chat_agent=check_already_assigned_agent.id).exists():
#                         pass
#                     else:
#                         agent_id = check_already_assigned_agent.id
#                         unassigned_agent_found = True
#                         break

#                 if not unassigned_agent_found:
#                     chat_room_agent = (
#                         ChatAgentDetail.objects.annotate(
#                         assigned_rooms=Count('chatroom', filter=Q(chatroom__status="Active"))
#                         ).order_by('assigned_rooms').first()
#                     )
#                     agent_id = chat_room_agent.id
           
#             agent_rooms[room] = agent_id

#             chat_room, created = ChatRoom.objects.get_or_create(
#                 user_id=user_id,
#                 admin_id=admin_id,
#                 chat_agent_id=agent_id,
#                 room=room,
#                 defaults={"created_at": timezone.now()},
#             )
           
#             AgentInChatRoomHistory.objects.create(
#                 room_id=chat_room.id,
#                 agent_id=agent_id,
#                 assigned_date=datetime.now(),
#             )

#             return chat_room, created
#     else:
#         chat_room = ChatRoom.objects.get(room=room)
#         return chat_room, False

# @sync_to_async
# def save_chat_message(user_id, admin_id, agent_id, room_id, msg, message_french, message_type, send_by, conversation_id):
#     get_room = ChatRoom.objects.get(id=room_id)
#     if message_type == "resolved":
#         get_room.is_resolved = True
#     else:
#         get_room.is_resolved = False

#     get_room.save()

#     if conversation_id not in [None, '', 'null']:
#         return ChatConversion.objects.get(id=conversation_id)
   
#     return ChatConversion.objects.create(
#         user_id=user_id,
#         admin_id=admin_id,
#         chat_agent_id=agent_id,
#         room_id=room_id,
#         message=msg,
#         message_french=message_french,
#         message_type=message_type,
#         send_by=send_by,
#         create_at=timezone.now(),
#     )

# @sync_to_async
# def get_user_data(user_id, room):
#     if user_id not in [None, '', 'null']:
#         return CustomerDetail.objects.get(id=user_id)
#     return CustomerDetail.objects.get(id=room.user.id)

# @sync_to_async
# def get_unseen_message_count(room_id):
#     return ChatConversion.objects.filter(user__isnull=False, room=room_id, status="Unseen").count()

# @sync_to_async
# def get_agent_name(room):
#     if ChatRoom.objects.filter(room=room).exists():
#         return ChatRoom.objects.get(room=room).chat_agent.name if ChatRoom.objects.get(room=room).chat_agent not in [None, '', 'null'] else 'Agent'
#     return "Agent"

# # Your existing event handlers remain exactly the same...
# @sio.on("join_room")
# async def join_room(sid, data):
#     room = data["room"]
#     user_id = data.get("user_id")
#     role = data.get("role", "user")
    
#     try:
#         await sio.leave_room(sid, room)
#         await sio.enter_room(sid, room)
#         print(f" User {user_id} ({sid}) joined room {room} as {role}")
        
#         await sio.emit("room_joined", {"room": room, "status": "success"}, to=sid)
#     except Exception as e:
#         print(f" Error joining room {room}: {e}")
#         await sio.emit("room_error", {"room": room, "error": str(e)}, to=sid)




# # @sio.on("send_message")
# # async def handle_send_message(sid, data):

# #     print("Strating of message send")
# #     try:
# #         room = data.get("room", None)
# #         sender = data.get("sender", None)
# #         msg = data.get("message", None)
# #         message_french = data.get("message_french", None)
# #         message_type = data.get("message_type", None)
# #         user_id = data.get("user_id", None)
# #         adminID = data.get("adminID", None)
# #         agent_id = data.get("agent_id", None)
# #         conversation_id = data.get("conversation_id", None)
# #         file = data.get("file", None)
# #         file_type = data.get("file_type", None)
# #         agent_type = data.get("agent_type", None)

# #         print(" Send message data received:", data)

# #         agent_name = "Agent"
# #         if room not in [None, '', 'null']:
# #             agent_name = await get_agent_name(room)

# #         message = {
# #             "id": str(uuid.uuid4()),
# #             "room": room,
# #             "sender": sender,
# #             "message": msg,
# #             "message_french": message_french,
# #             "message_type": message_type,
# #             "agent_name": agent_name,
# #             "agent_type": agent_type,
# #             'file': file,
# #             'file_type': file_type,
# #             'send_time': timezone.now().strftime('%Y-%m-%d %H:%M:%S'),
# #         }

# #         # safe chat room lookup
# #         chat_room, created = await get_or_create_chat_room(user_id, adminID, room)

# #         # sender type
# #         send_by = "User" if user_id not in [None, "", "null"] else "Admin" if adminID not in [None, '', 'null'] else "Agent"
       
# #         # safe message save
# #         if conversation_id in [None, '', 'null']:
# #             new_message = await save_chat_message(user_id, adminID, agent_id, chat_room.id, msg, message_french, message_type, send_by, conversation_id)
# #         else:
# #             new_message = await save_chat_message(user_id, adminID, agent_id, chat_room.id, msg, message_french, message_type, send_by, conversation_id)

# #         # USER DATA
# #         get_user = await get_user_data(user_id, chat_room)
# #         print("CHECKing here ----1>")

        
# #         # Unseen Count
# #         unseen_message_count = await get_unseen_message_count(chat_room.id)

# #         # Emit to user and admin
# #         assigned_agent_id = agent_rooms.get(room)

# #         # Emit to user room
# #         await sio.emit("receive_message", message, room=room)
# #         print("CHECKing here ----fsdkjfhskjdhfskh>")

# #         # Emit to admins
# #         await sio.emit("receive_message", message, room="admins")

# #         # Emit to assigned agent (if any)
# #         if assigned_agent_id:
# #             await sio.emit("receive_message", message, room=f"agent_{assigned_agent_id}")

# #         # Track last message for sidebar
# #         active_rooms[room] = {"last_message": msg, "last_sender": sender}

# #         chat_agent = await sync_to_async(lambda: chat_room.chat_agent)()
# #         if chat_agent not in [None, '', 'null']:
# #             agent_type = chat_agent.agent_type
# #             agent_id = chat_agent.id
# #             name = chat_agent.name
# #             email = chat_agent.email
# #             mobileNumber = chat_agent.mobileNumber
# #         else:
# #             agent_type = None
# #             agent_id = None
# #             name = None
# #             email = None
# #             mobileNumber = None

# #         await sio.emit(
# #             "update_user_list",
# #             {
# #                 "room": chat_room.room,
# #                 "last_message": msg if msg else "📎 File",
# #                 "new_room": created,
# #                 'last_sender': sender,
# #                 'sender_name': get_user.name,
# #                 'room_id': chat_room.id,
# #                 'user_name': get_user.name,
# #                 'user_email': get_user.email,
# #                 'last_message_detail': {
# #                     'message': msg if msg else "📎 File",
# #                     'send_by': send_by
# #                 },
# #                 'agent_detail': {
# #                     'agent_type': agent_type,
# #                     'id': agent_id,
# #                     'name': name,
# #                     'email': email,
# #                     'mobileNumber': mobileNumber,
# #                 },
# #                 'note': chat_room.note,
# #                 'priority': chat_room.priority,
# #                 'is_resolved': chat_room.is_resolved,
# #                 'last_message_send_date': new_message.create_at.strftime('%Y-%m-%d %H:%M:%S'),
# #                 'unseen_count': unseen_message_count
# #             },
# #             room="admins",
# #         )

# #         if assigned_agent_id:
# #             await sio.emit(
# #                 "update_user_list",
# #                 {
# #                     "room": chat_room.room,
# #                     "last_message": msg if msg else "📎 File",
# #                     "new_room": created,
# #                     "last_sender": sender,
# #                     "sender_name": get_user.name,
# #                     "user_name": get_user.name,
# #                     "user_email": get_user.email,
# #                     "last_message_detail": {
# #                         "message": msg if msg else "📎 File",
# #                         "message_french": message_french,
# #                         "send_by": send_by,
# #                     },
# #                     'agent_detail': {
# #                         'agent_type': agent_type,
# #                         'id': agent_id,
# #                         'name': name,
# #                         'email': email,
# #                         'mobileNumber': mobileNumber,
# #                     },
# #                     'note': chat_room.note,
# #                     'priority': chat_room.priority,
# #                     'is_resolved': chat_room.is_resolved,
# #                     "last_message_send_date": new_message.create_at.strftime('%Y-%m-%d %H:%M:%S'),
# #                     "unseen_count": unseen_message_count,
# #                 },
# #                 room=f"agent_{assigned_agent_id}",
# #             )

# #         print(f" Message processed in {room}: {message}")

# #         print(f" Messagesend_bysend_by: {send_by}")
# #         if send_by in ["Admin", "Agent"]:

# #             print(" Sending FCM notification to user with token:", get_user.FCMToken)

# #             notification_title = "Diaba Support"
# #             try:
# #                 message = messaging.Message(
# #                 notification=messaging.Notification(
# #                         title=notification_title,
# #                         body=msg,
# #                     ),
# #                     data={
# #                         "notification_type": "support",
# #                         "room": chat_room.room,
# #                         "sender": "admin"
# #                     },
# #                     token=get_user.FCMToken
# #                     # tokens=token_chunk,
# #                 )
# #                 try:
# #                     response = messaging.send(message)

# #                     print("Notification Sent Successfully")

# #                     # Process the response
# #                     # print(f'{response.success_count} messages were sent successfully')
# #                     # print(f'{response.failure_count} messages failed')

# #                     # if response.failed_tokens:
# #                     #     print("------5------")
# #                     #     print('List of failed tokens and their errors:')
# #                     #     for error in response.failed_tokens:
# #                     #         print(f'  Token: {error.token}, Error: {error.exception}')

# #                     # print("------6------")
# #                 except Exception as e:
# #                     print(f"An error occurred while sending multicast message: {e}")
# #             except Exception as e:
# #                 print('Error---->',e)


# #     except Exception as e:
# #         print(f" Error handling message: {e}")
# #         await sio.emit("message_error", {"error": str(e)}, to=sid)




# @sio.on("send_message")
# async def handle_send_message(sid, data):
#     try:
#         print(" Send message start===>", data)
#         print(" sid===>", sid)

#         # =========================
#         # EXTRACT DATA
#         # =========================
#         room = data.get("room")
#         sender = data.get("sender")
#         msg = data.get("message")
#         message_french = data.get("message_french")
#         message_type = data.get("message_type")
#         user_id = data.get("user_id")
#         adminID = data.get("adminID")
#         agent_id = data.get("agent_id")
#         conversation_id = data.get("conversation_id")
#         file = data.get("file")
#         file_type = data.get("file_type")
#         agent_type = data.get("agent_type")

#         # =========================
#         # PREPARE SOCKET MESSAGE
#         # =========================
#         agent_name = "Agent"
#         if room and room != "null":
#             try:
#                 agent_name = await get_agent_name(room)
#             except:
#                 pass

#         socket_message = {
#             "id": str(uuid.uuid4()),
#             "room": room,
#             "sender": sender,
#             "message": msg,
#             "message_french": message_french,
#             "message_type": message_type,
#             "agent_name": agent_name,
#             "agent_type": agent_type,
#             "file": file,
#             "file_type": file_type,
#             "send_time": timezone.now().strftime('%Y-%m-%d %H:%M:%S'),
#         }

#         # =========================
#         #  INSTANT EMIT
#         # =========================
#         print(socket_message,"------------> Emitting message instantly to room and admins----->",room)
#         print(" SID =-=-=> Emitting message instantly to room and admins----->",sid)


#         await sio.enter_room(sid, room)

#         # time.sleep(1)  # Simulate short delay before emitting
#         # if room and room != "null":
#         #     await sio.emit("receive_message", socket_message, room=room)
#         # else:
#         await sio.emit("receive_message", socket_message, to=sid)

#         await sio.emit("receive_message", socket_message, room="admins")

#         print(" Message emitted instantly")

#         # time.sleep(5)  # Simulate short processing delay

#         # =========================
#         # BACKGROUND TASK
#         # =========================
#         asyncio.create_task(process_message_background(data, socket_message))

#     except Exception as e:
#         print(f"❌ Error: {e}")
#         await sio.emit("message_error", {"error": str(e)}, to=sid)


# # =========================
# # BACKGROUND PROCESSOR
# # =========================
# async def process_message_background(data, socket_message):
#     try:
#         room = data.get("room")
#         msg = data.get("message")
#         message_french = data.get("message_french")
#         message_type = data.get("message_type")
#         user_id = data.get("user_id")
#         adminID = data.get("adminID")
#         agent_id = data.get("agent_id")
#         conversation_id = data.get("conversation_id")

#         # =========================
#         # CHAT ROOM
#         # =========================
#         chat_room, created = await get_or_create_chat_room(user_id, adminID, room)

#         send_by = (
#             "User" if user_id not in [None, "", "null"]
#             else "Admin" if adminID not in [None, "", "null"]
#             else "Agent"
#         )

#         # =========================
#         # SAVE MESSAGE
#         # =========================
#         new_message = await save_chat_message(
#             user_id,
#             adminID,
#             agent_id,
#             chat_room.id,
#             msg,
#             message_french,
#             message_type,
#             send_by,
#             conversation_id,
#         )

#         # =========================
#         # PARALLEL DATA FETCH
#         # =========================
#         get_user_task = asyncio.create_task(get_user_data(user_id, chat_room))
#         unseen_task = asyncio.create_task(get_unseen_message_count(chat_room.id))

#         get_user = await get_user_task
#         unseen_message_count = await unseen_task

#         # =========================
#         # AGENT DETAILS
#         # =========================
#         chat_agent = await sync_to_async(lambda: chat_room.chat_agent)()

#         if chat_agent:
#             agent_data = {
#                 "agent_type": chat_agent.agent_type,
#                 "id": chat_agent.id,
#                 "name": chat_agent.name,
#                 "email": chat_agent.email,
#                 "mobileNumber": chat_agent.mobileNumber,
#             }
#         else:
#             agent_data = None

#         # =========================
#         # UPDATE USER LIST (ADMIN)
#         # =========================
#         update_payload = {
#             "room": chat_room.room,
#             "last_message": msg if msg else "📎 File",
#             "new_room": created,
#             "last_sender": socket_message["sender"],
#             "sender_name": get_user.name,
#             "room_id": chat_room.id,
#             "user_name": get_user.name,
#             "user_email": get_user.email,
#             "last_message_detail": {
#                 "message": msg if msg else "📎 File",
#                 "send_by": send_by,
#             },
#             "agent_detail": agent_data,
#             "note": chat_room.note,
#             "priority": chat_room.priority,
#             "is_resolved": chat_room.is_resolved,
#             "last_message_send_date": new_message.create_at.strftime('%Y-%m-%d %H:%M:%S'),
#             "unseen_count": unseen_message_count,
#         }

#         await sio.emit("update_user_list", update_payload, room="admins")

#         # =========================
#         # AGENT ROOM EMIT
#         # =========================
#         assigned_agent_id = agent_rooms.get(room)

#         if assigned_agent_id:
#             await sio.emit(
#                 "update_user_list",
#                 update_payload,
#                 room=f"agent_{assigned_agent_id}",
#             )

#         # =========================
#         #  FCM NOTIFICATION (NON-BLOCKING)
#         # =========================
#         if send_by in ["Admin", "Agent"] and get_user.FCMToken:
#             asyncio.create_task(
#                 send_fcm_notification(get_user.FCMToken, msg, chat_room.room)
#             )
#         print("Background processing complete")

#     except Exception as e:
#         print(" Background error:", e)


# # =========================
# # FCM NOTIFICATION (ASYNC SAFE)
# # =========================
# async def send_fcm_notification(token, msg, room):
#     try:
#         message = messaging.Message(
#             notification=messaging.Notification(
#                 title="Diaba Support",
#                 body=msg,
#             ),
#             data={
#                 "notification_type": "support",
#                 "room": room,
#             },
#             token=token,
#         )

#         # Run blocking call in separate thread
#         await asyncio.to_thread(messaging.send, message)

#         print("📲 FCM sent")

#     except Exception as e:
#         print("❌ FCM error:", e)




# @sio.on("typing")
# async def typing(sid, data):
#     room = data["room"]
#     await sio.emit("show_typing", data, room=room, skip_sid=sid)
#     print(f"⌨️ Typing event in {room}: {data}")

# @sio.on("admin_join")
# async def admin_join(sid, data):
#     try:
#         admin_id = data["admin_id"]
#         user_room = data.get("room")

#         # Always join global admins room
#         await sio.enter_room(sid, "admins")
#         print(f"✅ Admin {admin_id} joined admins room")

#         # Optionally also join a specific user room
#         if user_room:
#             await sio.leave_room(sid, user_room)
#             await sio.enter_room(sid, user_room)
#             print(f"✅ Admin {admin_id} also joined {user_room}")

#         # Send current active user list only to THIS admin
#         if active_rooms:
#             for room, info in active_rooms.items():
#                 await sio.emit(
#                     "update_user_list",
#                     {"room": room, "last_message": info.get("last_message", "")},
#                     to=sid,
#                 )
#             print(f"✅ Sent active rooms to Admin {admin_id}")
        
#         await sio.emit("admin_joined", {"admin_id": admin_id, "status": "success"}, to=sid)
        
#     except Exception as e:
#         print(f"🔴 Error in admin_join: {e}")
#         await sio.emit("admin_join_error", {"error": str(e)}, to=sid)

# @sio.on("chat_agent_join_room")
# async def chat_agent_join_room(sid, data):
#     agent_id = data.get("agent_id")
#     user_room = data.get("room")

#     # Join agent global room
#     await sio.enter_room(sid, f"agent_{agent_id}")
#     print(f"✅ Agent {agent_id} joined global agent room")

#     # Optionally join a specific user room (if provided)
#     if user_room:
#         await sio.leave_room(sid, user_room)
#         await sio.enter_room(sid, user_room)
#         print(f"✅ Agent {agent_id} also joined {user_room}")

#     # Send only rooms assigned to this agent
#     for room, assigned_agent in agent_rooms.items():
#         if assigned_agent == agent_id:
#             info = active_rooms.get(room, {})
#             await sio.emit(
#                 "update_user_list",
#                 {"room": room, "last_message": info.get("last_message", "")},
#                 to=sid,
#             )





###########################################################################################################
###########################################################################################################
###########################################################################################################
###########################################################################################################





# """
# ASGI config + Socket.IO production structured single file
# """

# import os
# import uuid
# import asyncio
# import socketio
# from datetime import datetime

# import django
# from django.core.asgi import get_asgi_application
# from django.utils import timezone
# from django.db.models import Q, Count
# from asgiref.sync import sync_to_async

# from firebase_admin import messaging

# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "diaba.settings")
# django.setup()

# # =========================
# # IMPORT MODELS
# # =========================

# from diabaApp.models import (
#     ChatRoom,
#     ChatConversion,
#     CustomerDetail,
#     ChatAgentDetail,
#     AgentInChatRoomHistory
# )

# # =========================
# # SOCKET INITIALIZATION
# # =========================

# def get_allowed_origins():
#     return "*"

# sio = socketio.AsyncServer(
#     async_mode="asgi",
#     cors_allowed_origins=get_allowed_origins(),
#     ping_interval=25,
#     ping_timeout=60,
#     max_http_buffer_size=100000,
#     logger=True,
#     engineio_logger=True,
# )

# django_app = get_asgi_application()
# application = socketio.ASGIApp(sio, django_app)

# # =========================
# # IN-MEMORY STATE (TEMPORARY)
# # =========================

# active_rooms = {}
# agent_rooms = {}

# # =========================
# # DATABASE SERVICES
# # =========================

# @sync_to_async
# def get_or_create_chat_room_service(user_id, admin_id, room):
#     if not room:
#         raise Exception("Room required")

#     if ChatRoom.objects.filter(room=room).exists():
#         chat_room = ChatRoom.objects.get(room=room)

#         if chat_room.chat_agent:
#             agent_rooms[room] = chat_room.chat_agent.id
#             return chat_room, False

#         agent_id = assign_agent_logic()

#         chat_room.chat_agent_id = agent_id
#         chat_room.save()

#         return chat_room, False

#     agent_id = assign_agent_logic()

#     chat_room = ChatRoom.objects.create(
#         user_id=user_id,
#         admin_id=admin_id,
#         chat_agent_id=agent_id,
#         room=room,
#         created_at=timezone.now(),
#     )

#     AgentInChatRoomHistory.objects.create(
#         room_id=chat_room.id,
#         agent_id=agent_id,
#         assigned_date=datetime.now(),
#     )

#     agent_rooms[room] = agent_id

#     return chat_room, True


# def assign_agent_logic():
#     agents = ChatAgentDetail.objects.filter(status="Active")

#     for agent in agents:
#         if not ChatRoom.objects.filter(chat_agent=agent.id).exists():
#             return agent.id

#     agent = (
#         ChatAgentDetail.objects.annotate(
#             assigned_rooms=Count('chatroom', filter=Q(chatroom__status="Active"))
#         ).order_by('assigned_rooms').first()
#     )

#     return agent.id if agent else None


# @sync_to_async
# def save_message_service(data, chat_room, send_by):
#     if data.get("conversation_id"):
#         return ChatConversion.objects.get(id=data["conversation_id"])

#     return ChatConversion.objects.create(
#         user_id=data.get("user_id"),
#         admin_id=data.get("adminID"),
#         chat_agent_id=data.get("agent_id"),
#         room_id=chat_room.id,
#         message=data.get("message"),
#         message_french=data.get("message_french"),
#         message_type=data.get("message_type"),
#         send_by=send_by,
#         create_at=timezone.now(),
#     )


# @sync_to_async
# def get_user_service(user_id, chat_room):
#     if user_id:
#         return CustomerDetail.objects.get(id=user_id)
#     return chat_room.user


# @sync_to_async
# def get_unseen_count_service(room_id):
#     return ChatConversion.objects.filter(
#         user__isnull=False,
#         room=room_id,
#         status="Unseen"
#     ).count()

# # =========================
# # SOCKET EVENTS
# # =========================

# @sio.event
# async def connect(sid, environ):
#     print("Client connected", sid)

# @sio.event
# async def disconnect(sid):
#     print("Client disconnected", sid)

# # =========================
# # ROOM JOIN
# # =========================

# @sio.on("join_room")
# async def join_room(sid, data):
#     room = data.get("room")
#     await sio.enter_room(sid, room)
#     await sio.emit("room_joined", {"room": room}, to=sid)

# # =========================
# # SEND MESSAGE (LIGHTWEIGHT)
# # =========================

# @sio.on("send_message")
# async def send_message(sid, data):
#     # try:
#         room = data.get("room")

#         socket_payload = {
#             "id": str(uuid.uuid4()),
#             "room": room,
#             "sender": data.get("sender"),
#             "message": data.get("message"),
#             "message_type": data.get("message_type"),
#             "file": data.get("file"),
#             "file_type": data.get("file_type"),
#             "send_time": timezone.now().strftime('%Y-%m-%d %H:%M:%S'),
#         }

#         # instant emit
#         if room not in [None, '', 'null']:
#             await sio.emit("receive_message", socket_payload, room=room)
#         else:
#             await sio.emit("receive_message", socket_payload, room=room)
#         await sio.emit("receive_message", socket_payload, room="admins")

#         # background processing
#         asyncio.create_task(process_message_background(data, socket_payload))

#     # except Exception as e:
#     #     await sio.emit("error", {"error": str(e)}, to=sid)

# # =========================
# # BACKGROUND PROCESSOR
# # =========================

# async def process_message_background(data, socket_payload):
#     # try:
#         room = data.get("room")

#         send_by = (
#             "User" if data.get("user_id")
#             else "Admin" if data.get("adminID")
#             else "Agent"
#         )

#         chat_room, created = await get_or_create_chat_room_service(
#             data.get("user_id"),
#             data.get("adminID"),
#             room
#         )

#         message = await save_message_service(data, chat_room, send_by)

#         user_task = asyncio.create_task(
#             get_user_service(data.get("user_id"), chat_room)
#         )

#         unseen_task = asyncio.create_task(
#             get_unseen_count_service(chat_room.id)
#         )

#         user = await user_task
#         unseen_count = await unseen_task

#         agent = await sync_to_async(lambda: chat_room.chat_agent)()

#         agent_data = None
#         if agent:
#             agent_data = {
#                 "id": agent.id,
#                 "name": agent.name,
#                 "email": agent.email,
#                 "mobileNumber": agent.mobileNumber,
#                 "agent_type": agent.agent_type,
#             }

#         update_payload = {
#             "room": chat_room.room,
#             "last_message": data.get("message") or "File",
#             "new_room": created,
#             "last_sender": socket_payload["sender"],
#             "sender_name": user.name,
#             "room_id": chat_room.id,
#             "user_name": user.name,
#             "user_email": user.email,
#             "last_message_detail": {
#                 "message": data.get("message"),
#                 "send_by": send_by,
#             },
#             "agent_detail": agent_data,
#             "note": chat_room.note,
#             "priority": chat_room.priority,
#             "is_resolved": chat_room.is_resolved,
#             "last_message_send_date": message.create_at.strftime('%Y-%m-%d %H:%M:%S'),
#             "unseen_count": unseen_count,
#         }

#         await sio.emit("update_user_list", update_payload, room="admins")

#         assigned_agent_id = agent_rooms.get(room)

#         if assigned_agent_id:
#             await sio.emit(
#                 "update_user_list",
#                 update_payload,
#                 room=f"agent_{assigned_agent_id}",
#             )

#         # notification
#         if send_by in ["Admin", "Agent"] and user.FCMToken:
#             asyncio.create_task(send_notification(user.FCMToken, data.get("message"), room))

#     # except Exception as e:
#     #     print("Background error", e)

# # =========================
# # NOTIFICATION
# # =========================

# async def send_notification(token, msg, room):
#     # try:
#         message = messaging.Message(
#             notification=messaging.Notification(
#                 title="Support",
#                 body=msg,
#             ),
#             data={
#                 "room": room,
#                 "notification_type": "support",
#                 "room": room,
#                 "sender": "admin"
#                 },
#             token=token,
            
#         )

#         await asyncio.to_thread(messaging.send, message)

#     # except Exception as e:
#     #     print("Notification error", e)

# # =========================
# # TYPING EVENT
# # =========================

# @sio.on("typing")
# async def typing(sid, data):
#     await sio.emit("show_typing", data, room=data.get("room"), skip_sid=sid)

# # =========================
# # ADMIN JOIN
# # =========================

# @sio.on("admin_join")
# async def admin_join(sid, data):
#     await sio.enter_room(sid, "admins")

# # =========================
# # AGENT JOIN
# # =========================

# @sio.on("chat_agent_join_room")
# async def agent_join(sid, data):
#     agent_id = data.get("agent_id")
#     await sio.enter_room(sid, f"agent_{agent_id}")





#######################################################################################################################################
#######################################################################################################################################
#######################################################################################################################################
#######################################################################################################################################




"""
ASGI + Socket.IO full production single file (debug safe)
"""

import os
import uuid
import asyncio
import socketio
from datetime import datetime

import django
from django.core.asgi import get_asgi_application
from django.utils import timezone
from django.db.models import Q, Count
from asgiref.sync import sync_to_async

from firebase_admin import messaging

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "diaba.settings")
django.setup()

from diabaApp.models import (
    ChatRoom,
    ChatConversion,
    CustomerDetail,
    ChatAgentDetail,
    AgentInChatRoomHistory
)

# =========================
# SOCKET SETUP
# =========================

sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins="*",
    logger=True,
    engineio_logger=True,
    ping_interval=25,
    ping_timeout=60,
)

django_app = get_asgi_application()
application = socketio.ASGIApp(sio, django_app)

# =========================
# TEMP MEMORY (NO REDIS)
# =========================

agent_rooms = {}

# =========================
# DATABASE SERVICES
# =========================

@sync_to_async
def get_or_create_chat_room_service(user_id, admin_id, room):
    print("DB: get_or_create_chat_room_service")

    if ChatRoom.objects.filter(room=room).exists():
        chat_room = ChatRoom.objects.get(room=room)
        chat_room.updated_at = datetime.now()
        chat_room.save()

        if chat_room.chat_agent:
            agent_rooms[room] = chat_room.chat_agent.id
            return chat_room, False

        agent_id = assign_agent_logic()

        chat_room.chat_agent_id = agent_id
        chat_room.save()

        return chat_room, False

    agent_id = assign_agent_logic()

    chat_room = ChatRoom.objects.create(
        user_id=user_id,
        admin_id=admin_id,
        chat_agent_id=agent_id,
        room=room,
        created_at=timezone.now(),
    )

    AgentInChatRoomHistory.objects.create(
        room_id=chat_room.id,
        agent_id=agent_id,
        assigned_date=datetime.now(),
    )

    agent_rooms[room] = agent_id

    return chat_room, True


def assign_agent_logic():
    agents = ChatAgentDetail.objects.filter(status="Active")

    for agent in agents:
        if not ChatRoom.objects.filter(chat_agent=agent.id).exists():
            return agent.id

    agent = (
        ChatAgentDetail.objects.annotate(
            assigned_rooms=Count('chatroom', filter=Q(chatroom__status="Active"))
        ).order_by('assigned_rooms').first()
    )

    return agent.id if agent else None


@sync_to_async
def save_message_service(data, chat_room, send_by):
    print("DB: save_message_service")

    if data.get("conversation_id"):
        return ChatConversion.objects.get(id=data["conversation_id"])

    return ChatConversion.objects.create(
        user_id=data.get("user_id"),
        admin_id=data.get("adminID"),
        chat_agent_id=data.get("agent_id"),
        room_id=chat_room.id,
        message=data.get("message"),
        message_french=data.get("message_french"),
        message_type=data.get("message_type"),
        send_by=send_by,
        create_at=timezone.now(),
    )


@sync_to_async
def get_user_service(user_id, chat_room):
    print("DB: get_user_service")
    if user_id:
        return CustomerDetail.objects.get(id=user_id)
    return chat_room.user


@sync_to_async
def get_unseen_count_service(room_id):
    print("DB: get_unseen_count_service")
    return ChatConversion.objects.filter(
        user__isnull=False,
        room=room_id,
        status="Unseen"
    ).count()

# =========================
# SOCKET EVENTS
# =========================

@sio.event
async def connect(sid, environ):
    print("CONNECT:", sid)
    print("All rooms:------1", sio.manager.rooms)

@sio.event
async def disconnect(sid):
    print("DISCONNECT:", sid)

# =========================
# JOIN ROOM
# =========================

@sio.on("join_room")
async def join_room(sid, data):
    room = data.get("room")
    user_id = data.get("user_id")
    print("JOIN ROOM:", room)

    try:
        await sio.leave_room(sid, room)
        await sio.enter_room(sid, room)
        print(f" User {user_id} ({sid}) joined room {room}")
        
        await sio.emit("room_joined", {"room": room, "status": "success"}, to=sid)
    except Exception as e:
        print(f" Error joining room {room}: {e}")
        await sio.emit("room_error", {"room": room, "error": str(e)}, to=sid)

# =========================
# SEND MESSAGE
# =========================

@sio.on("send_message")
async def send_message(sid, data):
    print("All rooms:------2", sio.manager.rooms)
    try:
        print("SEND MESSAGE EVENT:", data)

        room = data.get("room")

        socket_payload = {
            "id": str(uuid.uuid4()),
            "room": room,
            "sender": data.get("sender"),
            "message": data.get("message"),
            "message_type": data.get("message_type"),
            "file": data.get("file"),
            "file_type": data.get("file_type"),
            "send_time": timezone.now().strftime('%Y-%m-%d %H:%M:%S'),
        }

        print("EMIT MESSAGE TO ROOM:", room)

        await sio.emit("receive_message", socket_payload, room=room)
        await sio.emit("receive_message", socket_payload, room="admins")

        # run background safely
        asyncio.create_task(process_message_background(data, socket_payload))

    except Exception as e:
        print("SEND ERROR:", str(e))
        await sio.emit("error", {"error": str(e)}, to=sid)

# =========================
# BACKGROUND PROCESS
# =========================

async def process_message_background(data, socket_payload):
    print("BACKGROUND START")
    print("All rooms:------3", sio.manager.rooms)

    try:
        room = data.get("room")

        send_by = (
            "User" if data.get("user_id")
            else "Admin" if data.get("adminID")
            else "Agent"
        )

        print("STEP 1: ROOM LOGIC")

        chat_room, created = await get_or_create_chat_room_service(
            data.get("user_id"),
            data.get("adminID"),
            room
        )

        print("STEP 2: MESSAGE SAVE")

        message = await save_message_service(data, chat_room, send_by)

        print("STEP 3: USER + UNSEEN")

        user = await get_user_service(data.get("user_id"), chat_room)
        unseen_count = await get_unseen_count_service(chat_room.id)

        print("UNSEEN COUNT:", unseen_count)

        print("STEP 4: AGENT FETCH")

        agent = await sync_to_async(
            lambda: ChatRoom.objects.get(id=chat_room.id).chat_agent
        )()

        agent_data = None
        if agent:
            agent_data = {
                "id": agent.id,
                "name": agent.name,
                "email": agent.email,
                "mobileNumber": agent.mobileNumber,
                "agent_type": agent.agent_type,
            }

        print("STEP 5: PREPARE PAYLOAD")

        update_payload = {
            "room": chat_room.room,
            "last_message": data.get("message") or "File",
            "new_room": created,
            "last_sender": socket_payload["sender"],
            "sender_name": user.name,
            "room_id": chat_room.id,
            "user_name": user.name,
            "user_email": user.email,
            "last_message_detail": {
                "message": data.get("message"),
                "send_by": send_by,
            },
            "agent_detail": agent_data,
            "note": chat_room.note,
            "priority": chat_room.priority,
            "is_resolved": chat_room.is_resolved,
            "last_message_send_date": message.create_at.strftime('%Y-%m-%d %H:%M:%S'),
            "unseen_count": unseen_count,
        }

        print("STEP 6: EMIT ADMIN")

        await sio.emit("update_user_list", update_payload, room="admins")

        assigned_agent_id = agent_rooms.get(room)

        print("STEP 7: EMIT AGENT", assigned_agent_id)

        if assigned_agent_id:
            await sio.emit(
                "update_user_list",
                update_payload,
                room=f"agent_{assigned_agent_id}",
            )

        print("STEP 8: NOTIFICATION")

        if send_by in ["Admin", "Agent"] and user.FCMToken:
            asyncio.create_task(
                send_notification(user.FCMToken, data.get("message"), room)
            )

        print("BACKGROUND COMPLETE")

    except Exception as e:
        print("BACKGROUND ERROR:", str(e))

# =========================
# NOTIFICATION
# =========================

async def send_notification(token, msg, room):
    try:
        print("FCM START")

        message = messaging.Message(
            notification=messaging.Notification(
                title="Support",
                body=msg,
            ),
            data={
                "room": room,
                "notification_type": "support",
                "room": room,
                "sender": "admin"
            },
            token=token,
        )

        await asyncio.to_thread(messaging.send, message)

        print("FCM SENT")

    except Exception as e:
        print("FCM ERROR:", str(e))

# =========================
# TYPING
# =========================

@sio.on("typing")
async def typing(sid, data):
    print("TYPING:", data)
    await sio.emit("show_typing", data, room=data.get("room"), skip_sid=sid)

# =========================
# ADMIN JOIN
# =========================

@sio.on("admin_join")
async def admin_join(sid, data):
    print("ADMIN JOIN:", data)
    await sio.enter_room(sid, "admins")

# =========================
# AGENT JOIN
# =========================

@sio.on("chat_agent_join_room")
async def agent_join(sid, data):
    agent_id = data.get("agent_id")
    print("AGENT JOIN:", agent_id)
    await sio.enter_room(sid, f"agent_{agent_id}")




