import html
import json
import traceback
from logging import getLogger

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from ..config import settings

logger = getLogger("service")


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error("Exception while handling an update:", exc_info=context.error)

    tb_list = traceback.format_exception(
        None, context.error, context.error.__traceback__  # type: ignore[union-attr]
    )
    tb_string = "".join(tb_list)

    update_str = json.dumps(
        update.to_dict() if isinstance(update, Update) else str(update),
        indent=2,
        ensure_ascii=False,
    )

    message = (
        f"An exception was raised while handling an update\n"
        f"<pre>update = {html.escape(update_str)}</pre>\n\n"
        f"<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n"
        f"<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n"
        f"<pre>{html.escape(tb_string)}</pre>"
    )

    for chat_id in settings.bot_developer_chat_ids:
        await context.bot.send_message(
            chat_id=chat_id, text=message, parse_mode=ParseMode.HTML
        )
