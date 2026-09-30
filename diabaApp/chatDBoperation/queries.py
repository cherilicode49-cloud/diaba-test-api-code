from datetime import timedelta
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
    message_text = "This message was deleted" if getattr(recent_message, 'is_deleted', False) else recent_message.message
    return {
        "message": message_text,
        "send_by": recent_message.send_by,
        "is_deleted": getattr(recent_message, 'is_deleted', False),
        "last_message_send_date": recent_message.create_at.strftime('%Y-%m-%d %H:%M:%S') if recent_message.create_at else ""
    }


@sync_to_async
def soft_delete_chat_message(conversation_id, sender_type, sender_id=None):
    """
    Soft deletes a message if requested within 24 hours of creation.
    Sender can be 'user', 'agent', or 'admin'.
    Admin can view deleted messages for audit purposes.
    """
    try:
        message = ChatConversion.objects.filter(id=conversation_id).first()
        if not message:
            return {"success": False, "error": "Message not found"}

        if message.is_deleted:
            return {"success": False, "error": "Message is already deleted"}

        # 24-hour limit check
        if message.create_at:
            time_diff = timezone.now() - message.create_at
            if time_diff > timedelta(hours=24):
                return {"success": False, "error": "Message cannot be deleted after 24 hours"}

        sender_type_clean = str(sender_type).strip().lower()

        # Authorization check
        if sender_type_clean in ["user", "customer"]:
            if str(message.send_by).strip().lower() not in ["user", "customer"]:
                return {"success": False, "error": "You can only delete messages sent by you"}
            if sender_id and str(message.user_id) != str(sender_id):
                return {"success": False, "error": "Unauthorized to delete this message"}

        elif sender_type_clean in ["agent", "chat_agent"]:
            if str(message.send_by).strip().lower() not in ["agent", "chat_agent"]:
                return {"success": False, "error": "You can only delete messages sent by you"}
            if sender_id and str(message.chat_agent_id) != str(sender_id):
                return {"success": False, "error": "Unauthorized to delete this message"}

        elif sender_type_clean in ["admin", "administrator"]:
            pass  # Admin is authorized to delete/manage any message

        else:
            return {"success": False, "error": f"Invalid sender type: {sender_type}"}

        # Apply soft delete
        now = timezone.now()
        message.is_deleted = True
        message.deleted_at = now
        message.deleted_by = sender_type
        message.save()

        room_str = message.room.room if message.room else None

        return {
            "success": True,
            "message": message,
            "room": room_str,
            "agent_id": message.chat_agent_id,
            "user_id": message.user_id,
            "deleted_at": now.strftime('%Y-%m-%d %H:%M:%S'),
        }

    except Exception as e:
        return {"success": False, "error": str(e)}
