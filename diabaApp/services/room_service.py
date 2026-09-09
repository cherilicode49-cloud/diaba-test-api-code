from datetime import datetime
from diabaApp.chatDBoperation.queries import get_room_by_room_id, create_room, update_room
from diabaApp.services.agent_service import assign_agent_to_room


async def get_or_create_room(user_id, admin_id, room_name):

    room = await get_room_by_room_id(room_name)

    if room:
        await update_room(room, {"updated_at": datetime.now()})

        # 🔥 FIXED HERE
        if not room.chat_agent_id:
            await assign_agent_to_room(room)

        return room, False

    room = await create_room({
        "user_id": user_id,
        "admin_id": admin_id,
        "room": room_name,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    })

    await assign_agent_to_room(room)

    return room, True