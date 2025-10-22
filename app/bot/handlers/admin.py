import logging

from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message
from app.bot.enums.roles import UserRole
from app.bot.filters.filters import UserRoleFilter
from app.infrastructure.database.db import (
    change_user_banned_status_by_id,
    change_user_banned_status_by_username,
    get_statistics,
    get_user_banned_status_by_id,
    get_user_banned_status_by_username,
)
from psycopg import AsyncConnection


logger = logging.getLogger(__name__)

admin_router = Router()

admin_router.message.filer(UserRoleFilter(UserRole.ADMIN))


# Этот хэндлер будет срабатывать на команду /help для пользователя с ролью `UserRole.ADMIN`
@admin_router.message(Command('help'))
async def process_admin_help_command(message: Message, i18n: dict):
    await message.answer(text=i18n.get('/help_admin'))


# Это хендлер будет срабатывать на команду /statistics для пользователя с ролью `UserRole.ADMIN`
@admin_router.message(Command('statstics'))
async def process_admin_statistics_command(message: Message, conn: AsyncConnection, i18n: dict[str, str]):
    statistics = await get_statistics(conn)
    await message.answer(
        text=i18n.get("statistics").format(
            "\n".join(
                f"{i}. <b>{stat[0]}</b>: {stat[1]}"
                for i, stat in enumerate(statistics, 1)
            )
        )
    )


# Этот хэндлер будет срабатывать на команду /ban для пользователя с ролью `UserRole.ADMIN`
@admin_router.message(Command('ban'))
async def process_ban_command(
        message: Message,
        command: CommandObject,
        conn: AsyncConnection,
        i18n: dict[str, str],
) -> None:
    args = command.args

    if not args:
        await message.reply(i18n.get('empty_ban_answer'))
        return

    arg_user = args.split()[0].strip()

    if arg_user.isdigit():
        banned_status = await get_user_banned_status_by_id(conn, user_id=int(arg_user))
    elif arg_user.startswith('@'):
        banned_status = await get_user_banned_status_by_username(conn, username=arg_user[1:])
    else:
        await message.reply(text=i18n.get('incorrect_ban_arg'))
        return

    if banned_status is None:
        await message.reply(i18n.get('no_user'))
