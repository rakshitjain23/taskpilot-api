from app.services.deepseek_client import deepseek_chat
from app.services.ai_context_service import build_user_context
from app.services.prompt_templates import SYSTEM_PROMPT


async def chat(messages: list, user_id: int, db):
    # 1) Load user's project/task/workspace data
    context = await build_user_context(user_id, db)

    # 2) Inject guardrails + database context
    system_message = SYSTEM_PROMPT.replace("{context}", str(context))

    # Prepend to user messages
    final_messages = [{"role": "system", "content": system_message}] + messages

    # 3) DeepSeek call
    result = await deepseek_chat(final_messages, max_tokens=500)
    return result
