# mypy: disable-error-code="union-attr"

# pyright: reportOptionalMemberAccess=false

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from ..types import Translate
from .constants import MenuState
from .helpers import log_update_data, send_typing_action


def get_social_networks_keyboard(translate: Translate) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text=translate("social_networks_url_button"),
                    url=translate("social_networks_url"),
                )
            ]
        ]
    )


@log_update_data
@send_typing_action
async def send_social_network_links(
    update: Update, context: ContextTypes.DEFAULT_TYPE, translate: Translate
) -> MenuState:
    await update.effective_message.reply_text(
        translate("social_networks_description"),
        reply_markup=get_social_networks_keyboard(translate),
    )

    return MenuState.MAIN_MENU
