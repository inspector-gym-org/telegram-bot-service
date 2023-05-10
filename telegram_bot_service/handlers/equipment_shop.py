# mypy: disable-error-code="union-attr"

# pyright: reportOptionalMemberAccess=false

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from ..types import Translate
from .constants import MenuState
from .helpers import log_update_data, send_typing_action


def get_equipment_shop_keyboard(translate: Translate) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text=translate("equipment_shop_url_button"),
                    url=translate("equipment_shop_url"),
                )
            ]
        ]
    )


@log_update_data
@send_typing_action
async def send_equipment_shop_data(
    update: Update, context: ContextTypes.DEFAULT_TYPE, translate: Translate
) -> MenuState:
    await update.effective_message.reply_text(
        translate("equipment_shop_description"),
        reply_markup=get_equipment_shop_keyboard(translate),
    )

    return MenuState.MAIN_MENU
