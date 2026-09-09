from diabaApp.chatDBoperation.queries import get_available_agent, create_agent_history, update_room


async def assign_agent_to_room(room):

    agent = await get_available_agent()

    if not agent:
        return None

    await update_room(room, {"chat_agent_id": agent.id})

    await create_agent_history(room.id, agent.id)

    return agent