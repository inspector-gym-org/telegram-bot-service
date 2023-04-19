from typing import Callable

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from .constants import MenuState
from .helpers import log_update_data, send_typing_action


@log_update_data
@send_typing_action
async def send_equipment_shop_data(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    translate: Callable,
) -> MenuState:
    await update.effective_message.reply_text(  # type: ignore[union-attr]
        translate("equipment_shop_description"),
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text=translate("equipment_shop_url_button"),
                        url=translate("equipment_shop_url"),
                    )
                ],
            ]
        ),
    )

    return MenuState.MAIN_MENU
