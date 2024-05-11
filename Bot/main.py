import asyncio
import telebot.types as tt

from loader import bot, user_contexts
from handlers import UserContext, StartState


@bot.message_handler(content_types=["text"])
async def get_msg(message: tt.Message) -> None:
    user_id = message.from_user.id
    if user_id not in user_contexts:
        cur_user_context = UserContext(user_id, StartState())
        user_contexts[user_id] = cur_user_context
    else:
        cur_user_context = user_contexts.get(user_id)
    await cur_user_context.text_request(message)


@bot.callback_query_handler(func=lambda call: True)
async def get_call(call: tt.CallbackQuery) -> None:
    user_id = call.from_user.id
    if user_id not in user_contexts:
        cur_user_context = UserContext(user_id, StartState())
        user_contexts[user_id] = cur_user_context
    else:
        cur_user_context = user_contexts.get(user_id)
    await cur_user_context.callback_request(call)


if __name__ == "__main__":
    asyncio.run(bot.polling(none_stop=True, interval=0, timeout=50))
