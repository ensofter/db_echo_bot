import logging
from contextlib import suppress

from aiogram import Bot, F, Router
from aiogram.enums import BotCommandScopeType
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import BotCommandScopeChat, CallbackQuery, Message
from app.bot.filters.filters import LocaleFilter
from app.bot.keyboards.keyboards import get_lang_settings_kb
from app. bot.keyboards.meny_button import get_main_meny_commands
from app.bot.states.states import LangSG
from app.infrastructure.database.db import (
get_user_lang,
get_user_role,
update_user_lang
)

from psycopg import AsyncConnection

logger = logging.getLogger(__name__)

settings_router = Router()

# Этот хэндлер будет срабатывать на любые сообщения, кроме команды /startб в стостоянии `LangSG.lang`
@settings_router.message(StateFilter(LangSG.lang), ~CommandStart())
async def process_any_message_when_lang(
        message: Message,
        bot: Bot,
        i18n: dict[str, str],
        state: FSMContext,
        locales: list[str],
):
    user_id = message.from_user.id
    data = await state.get_data()
    user_lang = data.get("user_lang")

    with suppress(TelegramBadRequest):
        msg_id = data.get("lang_settings_msg_id")
        if msg_id:
            await bot.edit_message_reply_markup(chat_id=user_id, message_id=msg_id)

    msg = await message.answer(
        text=i18n.get("/lang"),
        reply_markup=get_lang_settings_kb(i18n=i18n, locales=locales, checked=user_lang),
    )

    await state.update_data(lang_settings_msg_id=msg.message_id)
