############################################################################
## Django ORM Standalone Python Template
############################################################################
"""Here we'll import the parts of Django we need. It's recommended to leave
these settings as is, and skip to START OF APPLICATION section below"""

# Turn off bytecode generation
import sys

sys.dont_write_bytecode = True

# Import settings
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

# setup django environment
import django

django.setup()

# Import your models for use in your script
from db.models import *
import os
from asgiref.sync import sync_to_async
from dotenv import load_dotenv
from telegram.constants import MessageEntityType
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
import re

load_dotenv()
NAME_REGEX = re.compile(r"^[A-Za-z\s]+$")
PHONE_REGEX = re.compile(r"^\+?\d{7,15}$")
TEXT_REGEX = re.compile(r'^[A-Za-z0-9 !"#$%&\'()*+,\-./:;<=>?@[\\\]^_`{|}~]+$')
MENU_STATE, FIRST_NAME_STATE, LAST_NAME_STATE, PHONE_STATE, FEEDBACK_STATE = range(5)


def menu_keyboard():
    return ReplyKeyboardMarkup(
        [[KeyboardButton("Yangi fikr")], [KeyboardButton("Mening fiklarim")]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def phone_keyboard():
    return ReplyKeyboardMarkup(
        [[KeyboardButton("Yuborish", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


# def not_only_numbers(message): TO DO
#     return message.text and not message.text.isnumeric()


# custom_filter = not_only_numbers
@sync_to_async
def get_feedback(update):
    return list(
        Feedback.objects.filter(user_id=update.effective_user.id)
        .order_by("-id")[:5]
        .values("feedback")
    )


async def start_handler(update, context):
    await update.message.reply_text("Salom!", reply_markup=menu_keyboard())
    return MENU_STATE


async def stop_handler(update, context):
    await update.message.reply_text("Hayr", reply_markup=ReplyKeyboardRemove())


async def menu_handler(update, context):
    await update.message.reply_text("Menu", reply_markup=menu_keyboard())
    # return MENU_STATE


async def new_feedback_handler(update, context):
    await update.message.reply_text("Ismingizni kiriting")
    return FIRST_NAME_STATE


async def all_feedback_handler(update, context):
    await update.message.reply_text("Mening fikrlarim")

    feedbacks = await get_feedback(update)

    if len(feedbacks) == 0:
        await update.message.reply_text("Sizda hech qanday fikr yoq")
    else:
        for feed in feedbacks:
            await update.message.reply_text(feed["feedback"])


async def name_handler(update, context):
    context.chat_data.update({"first_name": update.message.text})
    await update.message.reply_text("Endi Familyangizni kiriting")
    return LAST_NAME_STATE


async def name_resend_handler(update, context):
    await update.message.reply_text("Ismingizni kiriting")


async def last_name_handler(update, context):
    context.chat_data.update({"last_name": update.message.text})
    await update.message.reply_text(
        "Endi telefon raqamingizni kiriting yoki pastdagi tugmani bosing!",
        reply_markup=phone_keyboard(),
    )

    return PHONE_STATE


async def last_name_resend_handler(update, context):
    await update.message.reply_text("Familaygizni togri kiriting")


async def phone_handler(update, context):
    phone_number = update.message.contact.phone_number

    context.chat_data.update({"phone_number": phone_number})

    await update.message.reply_text(
        "Fikringizni qiriting", reply_markup=ReplyKeyboardRemove()
    )
    return FEEDBACK_STATE


async def phone_entity_handler(update, context):
    index = update.message.entities[0].offset
    index2 = update.message.entities[0].length
    pne = list(update.message.text)
    phone_number = "".join(pne[index : index + index2 + 1]).strip()

    context.chat_data.update({"phone_number": phone_number})
    await update.message.reply_text(
        "Fikringizni qiriting", reply_markup=ReplyKeyboardRemove()
    )
    return FEEDBACK_STATE


async def phone_resend_handler(update, context):
    await update.message.reply_text("Telefon raqam", reply_markup=phone_keyboard())


async def feedback_handler(update, context):
    context.chat_data.update({"feedback": update.message.text})
    await update.message.reply_text(
        "Fikringizni uchun rahmat. Menu ga qaytish uchun nimadur janoting"
    )

    await sync_to_async(Feedback.objects.create)(
        first_name=context.chat_data["first_name"],
        last_name=context.chat_data["last_name"],
        phone_number=context.chat_data["phone_number"],
        feedback=context.chat_data["feedback"],
        user_id=update.effective_user.id,
    )

    return MENU_STATE


async def feedback_resend_handler(update, context):
    await update.message.reply_text("Fikrigizni matn korinishida bildiring")


token = os.getenv("TELEGRAM_BOT_TOKEN")
app = ApplicationBuilder().token(str(token)).build()
app.add_handler(CommandHandler("stop", stop_handler))
app.add_handler(
    ConversationHandler(
        entry_points=[CommandHandler("start", start_handler)],
        states={
            MENU_STATE: [
                CommandHandler("stop", stop_handler),
                MessageHandler(filters.Regex("Yangi fikr"), new_feedback_handler),
                MessageHandler(filters.Regex("Mening fiklarim"), all_feedback_handler),
                MessageHandler(filters.ALL, menu_handler),
            ],
            FIRST_NAME_STATE: [
                MessageHandler(filters.Regex(NAME_REGEX), name_handler),
                MessageHandler(filters.ALL, new_feedback_handler),
            ],
            LAST_NAME_STATE: [
                MessageHandler(filters.Regex(NAME_REGEX), last_name_handler),
                MessageHandler(filters.ALL, last_name_resend_handler),
            ],
            PHONE_STATE: [
                MessageHandler(filters.CONTACT, phone_handler),
                MessageHandler(
                    filters.TEXT & filters.Entity(MessageEntityType.PHONE_NUMBER),
                    phone_entity_handler,
                ),
                MessageHandler(filters.ALL, phone_resend_handler),
            ],
            FEEDBACK_STATE: [
                MessageHandler(filters.TEXT, feedback_handler),
                MessageHandler(filters.ALL, feedback_resend_handler),
            ],
        },
        fallbacks=[CommandHandler("stop", stop_handler)],
    )
)

app.run_polling()
