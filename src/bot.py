import secrets
import string
import re

from telegram import Update
from telegram.ext import (
    Application,
    PicklePersistence,
    CommandHandler,
    ContextTypes,
    filters
)

UUID_CHARS = string.ascii_letters + string.digits + '-_'
UUID_LEN = 8
application: Application

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_html('Hello, type /help to view available commands')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_html('This place is a bit empty :(')


def gen_uuid(data: dict[str, dict]): # We could do this better, but honestly, no one will use this bot enough to make this function slow
    while True:
        uuid = ''.join(secrets.choice(UUID_CHARS) for _ in range(UUID_LEN))
        if uuid not in data:
            return uuid

async def shortify_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if len(context.args) == 0:
        await update.message.reply_html("We're sorry, but some content is needed after /shortify")
        return
    
    uuid = gen_uuid(context.bot_data)
    context.bot_data[uuid] = {
        'url': ' '.join(context.args), 
        'user': update.effective_user.id, 
        'lifespan': 0
    }

    await update.message.reply_html(f"Here's your shortified link: t.me/{context.bot.username}?start={uuid}")

async def get_url_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args[0] in context.bot_data:
        await update.message.reply_html(f"Here's the unshorted-link:\n{context.bot_data[context.args[0]]['url']}")
        return
    await update.message.reply_html(f'No url has been found.')

def setup(token: str, store_path: str) -> None:
    global application
    persistence = PicklePersistence(filepath = store_path)

    application = Application.builder() \
        .token(token) \
        .persistence(persistence) \
        .build()

    reg_ex = f'[{re.escape(UUID_CHARS)}]{{{UUID_LEN}}}'
    application.add_handler(CommandHandler('start', get_url_command, filters.Regex(reg_ex)))

    application.add_handler(CommandHandler('start', start_command))
    application.add_handler(CommandHandler('help', help_command))

    application.add_handler(CommandHandler('shortify', shortify_command))


def start() -> None:
    global application
    application.run_polling()

