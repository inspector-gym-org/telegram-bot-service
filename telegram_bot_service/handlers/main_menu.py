# mypy: disable-error-code="union-attr"

# pyright: reportOptionalMemberAccess=false

from telegram import KeyboardButton, ReplyKeyboardMarkup, Update
from telegram.ext import ContextTypes

from ..types import Translate
from ..user import User
from .constants import MenuState
from .helpers import (
    authenticate_user,
    get_reply_keyboard,
    get_translations,
    log_update_data,
)


def get_main_menu(translate: Translate) -> ReplyKeyboardMarkup:
    return get_reply_keyboard(
        [
            KeyboardButton(translate("individual_training_plan_button")),
            KeyboardButton(translate("ready_made_plans_button")),
            KeyboardButton(translate("educational_plan_button")),
            KeyboardButton(translate("equipment_shop_button")),
        ],
        placeholder=translate("main_menu_placeholder"),
        one_time=False,
        keys_per_row=1,
    )


@log_update_data
@authenticate_user
@get_translations
async def send_main_menu(
    update: Update, context: ContextTypes.DEFAULT_TYPE, user: User, translate: Translate
) -> MenuState:
    await update.effective_message.reply_text(
        translate("main_menu"), reply_markup=get_main_menu(translate)
    )

    context.user_data.clear()
    return MenuState.MAIN_MENU
