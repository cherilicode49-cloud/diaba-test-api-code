import socketio
from diabaApp.models import ChatRoom, ChatConversion
from django.utils import timezone

from datetime import datetime
from diabaApp.services.room_service import get_or_create_room
from diabaApp.services.message_service import save_message, send_notification_to_customer
from diabaApp.chatDBoperation.queries import get_user_details,get_admin_agent_detail,unseen_message,get_user_data, get_room_by_room_id, get_recent_message


sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins="*",
    ping_interval=25,
    ping_timeout=60,
)

active_users = {}

@sio.event
async def connect(sid, environ):
    print(f"Connected: {sid}")

    await sio.emit("connected", {
        "status": "ok",
        "time": datetime.now().isoformat()
    }, to=sid)

@sio.event
async def disconnect(sid):
    print(f"Disconnected: {sid}")

    print("active user:",active_users)
    # REMOVE USER
    for user_id, user_sid in list(active_users.items()):
        if user_sid == sid:
            room = f"room_{user_id}"
            del active_users[user_id]
            print(f"User {user_id} went offline")
            
            try:
                room_data = await get_room_by_room_id(room)

                user_detail = await get_user_data(room)
                user_mobileNumber = user_detail["mobileNumber"]
                user_countryCode = user_detail["countryCode"]
                user_name = user_detail["name"]
                user_email = user_detail["email"]

                admin_agent_data = await get_admin_agent_detail(room_data.chat_agent_id)
                agent_id = room_data.chat_agent_id
                name = admin_agent_data["name"]
                email = admin_agent_data["email"]
                mobileNumber = admin_agent_data["mobileNumber"]
                agent_type = admin_agent_data["agent_type"]

                last_message = await get_recent_message(room)
                message = last_message["message"] if last_message else None
                send_by = last_message["send_by"] if last_message else None
                last_message_send_date = last_message["last_message_send_date"]

                sender_name = user_name if send_by in ["user","User"] else name if send_by in ["agent","Agent"] else "admin"

                unseen_message_count = await unseen_message(room_data.id)

                await sio.emit(
                    "update_user_list",
                    {
                        "room": room,
                        "last_message": message if message else "📎 File",
                        "new_room": False,
                        'last_sender': send_by,
                        'sender_name': sender_name,
                        'id': room_data.id,
                        'user_name': user_name,
                        'user_email': user_email,
                        'user_country_code':user_countryCode,
                        'user_mobile_number':user_mobileNumber,
                        'last_message_detail': {
                            'message': message if message else "📎 File",
                            'send_by': send_by
                        },
                        'agent_detail': {
                            'agent_type': agent_type,
                            'id': agent_id,
                            'name': name,
                            'email': email,
                            'mobileNumber': mobileNumber,
                        },
                        'is_resolved': room_data.is_resolved,
                        'last_message_send_date': last_message_send_date,
                        'unseen_count': unseen_message_count,
                        'is_online': room_data.user_id in active_users, 
                    },
                    room="admins",
                )
            except Exception as e:
                print("Error in fetching last_data:",e)
        
            break

    print("ACTIVE USERS:", active_users)


@sio.on("join_room")
async def join_room(sid, data):
    try:
        room = data["room"]
        user_id = data.get("user_id")

        print("room------->",room)

        await sio.enter_room(sid, room)

        # STORE ONLINE USER
        if user_id:
            active_users[user_id] = sid

        print("ACTIVE USERS:", active_users)

        await sio.emit("room_joined", {"room": room}, to=sid)
        try:
            room_data = await get_room_by_room_id(room)

            user_detail = await get_user_data(room)
            user_mobileNumber = user_detail["mobileNumber"]
            user_countryCode = user_detail["countryCode"]
            user_name = user_detail["name"]
            user_email = user_detail["email"]

            admin_agent_data = await get_admin_agent_detail(room_data.chat_agent_id)
            agent_id = room_data.chat_agent_id
            name = admin_agent_data["name"]
            email = admin_agent_data["email"]
            mobileNumber = admin_agent_data["mobileNumber"]
            agent_type = admin_agent_data["agent_type"]

            last_message = await get_recent_message(room)
            message = last_message["message"] if last_message else None
            send_by = last_message["send_by"] if last_message else None
            last_message_send_date = last_message["last_message_send_date"]

            sender_name = user_name if send_by in ["user","User"] else name if send_by in ["agent","Agent"] else "admin"

            unseen_message_count = await unseen_message(room_data.id)

            await sio.emit(
                "update_user_list",
                {
                    "room": room,
                    "last_message": message if message else "📎 File",
                    "new_room": False,
                    'last_sender': send_by,
                    'sender_name': sender_name,
                    'id': room_data.id,
                    'user_name': user_name,
                    'user_email': user_email,
                    'user_country_code':user_countryCode,
                    'user_mobile_number':user_mobileNumber,
                    'last_message_detail': {
                        'message': message if message else "📎 File",
                        'send_by': send_by
                    },
                    'agent_detail': {
                        'agent_type': agent_type,
                        'id': agent_id,
                        'name': name,
                        'email': email,
                        'mobileNumber': mobileNumber,
                    },
                    'is_resolved': room_data.is_resolved,
                    'last_message_send_date': last_message_send_date,
                    'unseen_count': unseen_message_count,
                    'is_online': room_data.user_id in active_users, 
                },
                room="admins",
            )
        except Exception as e:
            print("Error in fetching last_data:",e)


    except Exception as e:
        print("Error:", str(e))

@sio.on("admin_join")
async def admin_join(sid, data):
    try:
        admin_id = data["admin_id"]
        user_room = data.get("room")

        # Always join global admins room
        await sio.enter_room(sid, "admins")
        print(f" Admin {admin_id} joined admins room")

        # Optionally also join a specific user room
        if user_room:
            await sio.leave_room(sid, user_room)
            await sio.enter_room(sid, user_room)
            print(f" Admin {admin_id} also joined {user_room}")

        # Send current active user list only to THIS admin
        # if active_rooms:
        #     for room, info in active_rooms.items():
        #         await sio.emit(
        #             "update_user_list",
        #             {"room": room, "last_message": info.get("last_message", "")},
        #             to=sid,
        #         )
        #     print(f" Sent active rooms to Admin {admin_id}")
        
        await sio.emit("admin_joined", {"admin_id": admin_id, "status": "success"}, to=sid)
        
    except Exception as e:
        print(f" Error in admin_join: {e}")
        await sio.emit("admin_join_error", {"error": str(e)}, to=sid)



@sio.on("chat_agent_join_room")
async def agent_join(sid, data):
    try:
        agent_id = data["agent_id"]

        room_name = f"agent_{agent_id}"

        await sio.enter_room(sid, room_name)

        print(f"Agent {agent_id} joined {room_name}")

        await sio.emit("agent_joined", {
            "agent_id": agent_id,
            "room": room_name
        }, to=sid)

    except Exception as e:
        print("agent_join error:", str(e))



@sio.on("init_chat")
async def init_chat(sid, data):
    try:
        room, created = await get_or_create_room(
            data.get("user_id"),
            data.get("admin_id"),
            data.get("room")
        )

        await sio.emit("chat_initialized", {
            "room": room.room,
            "agent_id": room.chat_agent_id
        }, to=sid)
    except Exception as e:
        print("Error:", str(e))

@sio.on("send_message")
async def send_message(sid, data):

    print("DATA------>", data)
    try:
        room_obj, created = await get_or_create_room(
            data.get("user_id"),
            data.get("admin_id"),
            data.get("room")
        )

        userID = room_obj.user_id
        roomID = room_obj.room

        await sio.enter_room(sid, data["room"])

        msg = await save_message({
            "room": room_obj,
            "user_id": data.get("user_id"),
            "admin_id": data.get("admin_id"),

            "message": data.get("message"),
            "message_french": data.get("message_french"),

            "message_type": data.get("message_type"),
            "send_by": data.get("sender"),

            #  FILE SUPPORT
            "file": data.get("file"),
            "file_type": data.get("file_type"),

            "conversation_id": data.get("conversation_id"),
            #  PRODUCT SUPPORT
            "product_id": data.get("product_id"),
        })

        room = data.get("room")
        sender = data.get("sender")        

        message = msg.message
        message_type = msg.message_type
        send_by = msg.send_by
        chat_agent_id = msg.chat_agent_id
        file = msg.file.url if msg.file else None
        file_type = msg.file_type
        product_id = msg.product_id
        create_at = str(msg.create_at)


        admin_agent_data = await get_admin_agent_detail(msg.chat_agent_id)
        user_detail = await get_user_data(room)
        user_mobileNumber = user_detail["mobileNumber"]
        user_countryCode = user_detail["countryCode"]
        user_name = user_detail["name"]
        user_email = user_detail["email"]

        if send_by in ["user","User"]:
            user_data = await get_user_details(msg.user_id)

            sender_name = user_data["name"]
            sender_email = user_data["email"]
            user_mobileNumber = user_data["mobileNumber"]
            user_countryCode = user_data["countryCode"]
        elif send_by in ["agent","Agent"]:
            sender_name = admin_agent_data["name"]
            sender_email = admin_agent_data["email"]

        else:
            sender_name = "admin"
            sender_email = "admin"

    
      
        # agent_type = msg.chat_agent.agent_type
        agent_id = msg.chat_agent_id
        name = admin_agent_data["name"]
        email = admin_agent_data["email"]
        mobileNumber = admin_agent_data["mobileNumber"]
        agent_type = admin_agent_data["agent_type"]
    
        await sio.emit("receive_message", {
            "id": msg.id,
            "room":room,
            "sender":sender,

            "message": message,
            "message_type": message_type,
            "send_by": send_by,
            "agent_name": name,

            #  FILE RETURN
            "file": file,
            "file_type": file_type,

            #  PRODUCT RETURN
            "product_id": product_id,

            "send_time": timezone.now().strftime('%Y-%m-%d %H:%M:%S'),
            "created_at": create_at,
        }, room=data["room"])

        print("")

        await sio.emit("receive_message", {
            "id": msg.id,
            "room":room,
            "sender":sender,

            "message": message,
            "message_type": message_type,
            "send_by": send_by,
            "agent_name": name,

            #  FILE RETURN
            "file": file,
            "file_type": file_type,

            #  PRODUCT RETURN
            "product_id": product_id,

            "send_time": timezone.now().strftime('%Y-%m-%d %H:%M:%S'),
            "created_at": create_at,
        }, room="admins")

        await sio.emit("receive_message", {
            "id": msg.id,
            "room":room,
            "sender":sender,

            "message": message,
            "message_type": message_type,
            "send_by": send_by,
            "agent_name": chat_agent_id,

            #  FILE RETURN
            "file": file,
            "file_type": file_type,

            #  PRODUCT RETURN
            "product_id": product_id,

            "send_time": timezone.now().strftime('%Y-%m-%d %H:%M:%S'),
            "created_at": create_at,
        }, room=f"agent_{agent_id}")

        unseen_message_count = await unseen_message(room_obj.id)
        print("unseen_message_count", unseen_message_count)

        await sio.emit(
            "update_user_list",
            {
                "room": room,
                "last_message": message if message else "📎 File",
                "new_room": created,
                'last_sender': sender,
                'sender_name': sender_name,
                'id': room_obj.id,
                'user_name': user_name,
                'user_email': user_email,
                'user_country_code':user_countryCode,
                'user_mobile_number':user_mobileNumber,
                'last_message_detail': {
                    'message': message if message else "📎 File",
                    'send_by': send_by
                },
                'agent_detail': {
                    'agent_type': agent_type,
                    'id': agent_id,
                    'name': name,
                    'email': email,
                    'mobileNumber': mobileNumber,
                },
                'is_resolved': room_obj.is_resolved,
                'last_message_send_date': msg.create_at.strftime('%Y-%m-%d %H:%M:%S'),
                'unseen_count': unseen_message_count,
                'is_online': room_obj.user_id in active_users, 
            },
            room="admins",
        )

        print("MESSAGE TO AGENT")
        await sio.emit(
            "update_user_list",
            {
                "room": room,
                "last_message": message if message else "📎 File",
                "new_room": created,
                'last_sender': sender,
                'sender_name': sender_name,
                'id': room_obj.id,
                'user_name': user_name,
                'user_email': user_email,
                # 'user_mobile_number':user_mobileNumber,
                'last_message_detail': {
                    'message': message if message else "📎 File",
                    'send_by': send_by
                },
                'agent_detail': {
                    'agent_type': agent_type,
                    'id': agent_id,
                    'name': name,
                    'email': email,
                    'mobileNumber': mobileNumber,
                },
                'is_resolved': room_obj.is_resolved,
                'last_message_send_date': msg.create_at.strftime('%Y-%m-%d %H:%M:%S'),
                'unseen_count': unseen_message_count,
                'is_online': room_obj.user_id in active_users, 
            },
            room=f"agent_{agent_id}",
        )
        print("MESSAGE TO AGENT---- DOne")

        # SEND NOTIFICATION
        if send_by not in ["user","User"]:
            print("NOTIFICATION TRIGGERED")
            await send_notification_to_customer(send_by, userID, message, roomID)


    except Exception as e:
        print("send_message error:", str(e))