import os
import json
import secrets
import logging
import logging.config
from telegram import Update, helpers
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from sqlitedict import SqliteDict
from string import ascii_letters, digits


logger = logging.getLogger(__name__)
db = SqliteDict("database.sqlite", autocommit = True)
UUID_LEN, UUID_CHARS = 8, ascii_letters + digits + '-_'
formatted_regex = "[{}]{{{}}}".format(UUID_CHARS.replace('-', '\\-'), UUID_LEN) 

async def start_cmd(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_html(
        r"Start message."
    )


async def help_cmd(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_html(
        r"Help message.",
    )

def gen_uuid(): # We could do this better, but honestly, no one will use this bot enough to make this function slow
    while True:
        uuid = ''.join(secrets.choice(UUID_CHARS) for _ in range(UUID_LEN))
        if uuid in db:
            continue
        return uuid

async def shortify_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if len(context.args) == 0:
        await update.message.reply_html("We're sorry, but some content is needed after /shortify")
        return
    uuid = gen_uuid()
    db[uuid] = {"url": ' '.join(context.args), "user": update.effective_user.id, "lifespan": 0}
    await update.message.reply_html(f"Here's your shortified link: t.me/{context.bot.username}?start={uuid}")

async def get_url_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args[0] in db:
        await update.message.reply_html(f"Here's the unshorted-link:\n{db[context.args[0]]['url']}")
        return
    await update.message.reply_html(f"No url has been found.")

def setup_logging(path=''):
    """Setup logging configuration from a json file"""
    global logger
    with open(path) as f:
        config = json.load(f)
    logging.config.dictConfig(config)
    logger.info(f'Logger correctly initialized from {path}')


def main():
    setup_logging('logging.json')
    application = Application.builder().token(os.environ.get("SHRTURL_TOKEN")).build()

    application.add_handler(CommandHandler("help", help_cmd))
    application.add_handler(CommandHandler("shortify", shortify_cmd))
    
    application.add_handler(
        CommandHandler("start", get_url_cmd, filters.Regex(formatted_regex))
    )

    application.add_handler(CommandHandler("start", start_cmd))
    
    application.run_polling()
    db.close()


if __name__ == '__main__':
    main()