from asgiref.sync import sync_to_async
from django.utils import timezone
from django.db.models import Count, Q

from diabaApp.models import ChatRoom, ChatConversion, ChatAgentDetail, AgentInChatRoomHistory,CustomerDetail


@sync_to_async
def get_room_by_room_id(room):
    return ChatRoom.objects.filter(room=room).first()


@sync_to_async
def create_room(data):
    return ChatRoom.objects.create(**data)


@sync_to_async
def update_room(room, data):
    for key, value in data.items():
        setattr(room, key, value)
    room.save()
    return room


@sync_to_async
def create_message(data):
    message = ChatConversion.objects.create(**data)
    return message

@sync_to_async
def get_message_detail(conversation_id):
    message = ChatConversion.objects.get(id = conversation_id)
    return message

@sync_to_async
def get_available_agent():
    agents = ChatAgentDetail.objects.filter(status="Active")

    for agent in agents:
        if not ChatRoom.objects.filter(chat_agent=agent.id).exists():
            return agent

    return (
        ChatAgentDetail.objects.annotate(
            assigned_rooms=Count('chatroom', filter=Q(chatroom__status="Active"))
        ).order_by('assigned_rooms').first()
    )



@sync_to_async
def create_agent_history(room_id, agent_id):
    return AgentInChatRoomHistory.objects.create(
        room_id=room_id,
        agent_id=agent_id,
        assigned_date=timezone.now()
    )

@sync_to_async
def unseen_message(room_id):
    return ChatConversion.objects.filter(user__isnull=False, room=room_id, status="Unseen", is_deleted=False).count()

@sync_to_async
def get_user_details(user_id):
    user = CustomerDetail.objects.get(id=user_id)
    return {
        "name": user.name,
        "email": user.email,
        "FCMToken": user.FCMToken,
        "mobileNumber": user.mobileNumber,
        "countryCode": user.countryCode,
    }

@sync_to_async
def get_admin_agent_detail(agent_id):
    agent = ChatAgentDetail.objects.get(id=agent_id)
    return {
        "name": agent.name,
        "email": agent.email,
        "mobileNumber": agent.mobileNumber,
        "agent_type": agent.agent_type,
    }



@sync_to_async
def get_user_data(room):
    room_data =  ChatRoom.objects.filter(room=room).first()
    user = CustomerDetail.objects.get(id=room_data.user_id)
    
    return{
        "name": user.name,
        "email": user.email,
        "mobileNumber": user.mobileNumber,
        "countryCode": user.countryCode,
    }

@sync_to_async
def get_recent_message(room):
    recent_message = ChatConversion.objects.filter(room__room = room).order_by('-id').first()
    if not recent_message:
        return None
    message_text = "This message was deleted" if recent_message.is_deleted else recent_message.message
    return {
        "message": message_text,
        "original_message": recent_message.message,
        "is_deleted": recent_message.is_deleted,
        "send_by": recent_message.send_by,
        "deleted_by": recent_message.deleted_by,
        "last_message_send_date": recent_message.create_at.strftime('%Y-%m-%d %H:%M:%S') if recent_message.create_at else ""
    }

@sync_to_async
def soft_delete_message(message_id, sender_role=None, sender_id=None):
    try:
        msg = ChatConversion.objects.select_related('room').filter(id=message_id).first()
        if not msg:
            return {"success": False, "error": "Message not found", "data": None}

        if msg.is_deleted:
            return {"success": False, "error": "Message is already deleted", "data": None}

        # Check 24 hours window (86400 seconds)
        if msg.create_at:
            time_diff = timezone.now() - msg.create_at
            if time_diff.total_seconds() > 24 * 3600:
                return {"success": False, "error": "Message cannot be deleted after 24 hours.", "data": None}

        # Permission check
        role_lower = str(sender_role).lower() if sender_role else ""
        msg_sender_lower = str(msg.send_by).lower() if msg.send_by else ""

        if role_lower in ["user", "customer"]:
            if msg_sender_lower not in ["user", "customer"]:
                return {"success": False, "error": "You can only delete your own messages.", "data": None}
            if sender_id and str(msg.user_id) != str(sender_id):
                return {"success": False, "error": "Unauthorized to delete this message.", "data": None}
        elif role_lower in ["agent", "chat_agent"]:
            if msg_sender_lower not in ["agent", "chat_agent"]:
                return {"success": False, "error": "You can only delete messages sent by agent.", "data": None}
            if sender_id and str(msg.chat_agent_id) != str(sender_id):
                return {"success": False, "error": "Unauthorized to delete this message.", "data": None}

        msg.is_deleted = True
        msg.deleted_at = timezone.now()
        msg.deleted_by = sender_role if sender_role else msg.send_by
        msg.save()

        return {
            "success": True,
            "error": None,
            "data": {
                "id": msg.id,
                "room": msg.room.room if msg.room else None,
                "room_id": msg.room_id,
                "agent_id": msg.chat_agent_id,
                "user_id": msg.user_id,
                "original_message": msg.message,
                "deleted_by": msg.deleted_by,
                "deleted_at": msg.deleted_at.strftime('%Y-%m-%d %H:%M:%S') if msg.deleted_at else "",
                "is_deleted": True
            }
        }
    except Exception as e:
        return {"success": False, "error": str(e), "data": None}
