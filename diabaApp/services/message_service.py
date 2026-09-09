from django.utils import timezone
from diabaApp.chatDBoperation.queries import create_message, update_room, get_user_details,get_message_detail

import firebase_config
from firebase_admin import messaging


async def save_message(data):

    room = data["room"]
    print("DATA SAVE=====>",data)
    print("Saving message for room:", room.chat_agent_id)
    print("Saving message for room:", room.id)

    if data.get("message_type") == "resolved":
        await update_room(room, {"is_resolved": True})
    else:
        await update_room(room, {"is_resolved": False})

    if (data.get("file_type") in ["Audio", "audio","photo","Photo","dbImg"] and data.get("conversation_id") or data.get("message_type")=="resolved"):
        get_message = await get_message_detail(data.get("conversation_id"))
        
        # msg = {
        #     "user_id": data.get("user_id"),
        #     "admin_id": data.get("admin_id"),
        #     "chat_agent_id": room.chat_agent_id,
        #     "room_id": room.id,
        #     "message": data.get("message"),
        #     "message_french": data.get("message_french"),
        #     "message_type": data.get("message_type"),
        #     "send_by": data.get("send_by"),
        #     "product_id": data.get("product_id"),
        #     "file": data.get("file"),
        #     "file_type": data.get("file_type"),
        #     "create_at": timezone.now(),
        # }

        msg = get_message

    else:
        msg = await create_message({
            "user_id": data.get("user_id"),
            "admin_id": data.get("admin_id"),
            "chat_agent_id": room.chat_agent_id,
            "room_id": room.id,
            "message": data.get("message"),
            "message_french": data.get("message_french"),
            "message_type": data.get("message_type"),
            "send_by": data.get("send_by"),
            "product_id": data.get("product_id"),
            "create_at": timezone.now(),
        })
    return msg


async def send_notification_to_customer(send_by,userID,message_body,room):
    print("send_by=-==---->",send_by)
    if send_by in ["admin","Admin","agent","Agent"]: 
        get_user = await get_user_details(userID)

        FCMToken = get_user["FCMToken"]

        print(" Sending FCM notification to user with token:", FCMToken)

        notification_title = "Diaba Support"
        try:
            message = messaging.Message(
            notification=messaging.Notification(
                    title = notification_title,
                    body = message_body,
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