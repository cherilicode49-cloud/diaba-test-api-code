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
    return ChatConversion.objects.filter(user__isnull=False, room=room_id, status="Unseen").count()

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
    return {
        "message":recent_message.message,
        "send_by":recent_message.send_by,
        "last_message_send_date": recent_message.create_at.strftime('%Y-%m-%d %H:%M:%S')
    }
