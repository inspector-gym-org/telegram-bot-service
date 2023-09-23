# mypy: disable-error-code="union-attr"

# pyright: reportOptionalMemberAccess=false

from telegram import Update
from telegram.ext import ContextTypes

from ..types import Translate
from .constants import MenuState
from .helpers import log_update_data, send_typing_action


@log_update_data
@send_typing_action
async def send_music_playlists(
    update: Update, context: ContextTypes.DEFAULT_TYPE, translate: Translate
) -> MenuState:
    await update.effective_message.reply_text(translate("music_playlists_description"))

    return MenuState.MAIN_MENU
