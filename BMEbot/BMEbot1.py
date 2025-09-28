import logging

from telegram import Update, ForceReply, InlineKeyboardMarkup, InlineKeyboardButton, ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler

logger = logging.getLogger(__name__)

# Store bot debug status
debug = False

# Pre-assign menu text
FIRST_MENU = """
الأدوات المتوفرة حاليا:

1- حاسبة منتصف الليل
2- تحميل ملف من رابط جوجل درايف
_________________________
"""
SECOND_MENU = """<b>🌙 حاسبة منتصف الليل</b>
<b>الأمر:</b>
<code>/mn [الفجر] [المغرب]</code>
<b>مثال:</b> 
<code>/mn 6:09 6:34</code>
"""
GET_PDF_MENU = """
فقط ارسل رابط المشاركة من جوجل درايف وسيصلك الملف 
(حاليا مدعوم pdf فقط)
"""

# Pre-assign button text
NEXT_BUTTON = "التالي"
BACK_BUTTON = "رجوع"
DETAILS_BUTTON = "للتفاصيل"
GET_PDF_BUTTON = "التالي 2"

# Build keyboards
FIRST_MENU_MARKUP = InlineKeyboardMarkup([[
    InlineKeyboardButton(DETAILS_BUTTON, callback_data=DETAILS_BUTTON)
]])
SECOND_MENU_MARKUP = InlineKeyboardMarkup([
    [InlineKeyboardButton(BACK_BUTTON, callback_data=BACK_BUTTON)],
    [InlineKeyboardButton(GET_PDF_BUTTON, callback_data=GET_PDF_BUTTON)]
])
GET_PDF_MENU_MARKUP = InlineKeyboardMarkup([
    [InlineKeyboardButton(BACK_BUTTON, callback_data=BACK_BUTTON)],
])

def start(update: Update, context: CallbackContext) -> None:
    """
    This handler sends a menu with the inline buttons we pre-assigned above
    """

    context.bot.send_message(
        update.message.from_user.id,
        FIRST_MENU,
        parse_mode=ParseMode.HTML,
        reply_markup=FIRST_MENU_MARKUP
    )


def button_tap(update: Update, context: CallbackContext) -> None:
    """
    This handler processes the inline buttons on the menu
    """

    data = update.callback_query.data
    text = ''
    markup = None

    if data == DETAILS_BUTTON:
        text = SECOND_MENU
        markup = SECOND_MENU_MARKUP
    elif data == NEXT_BUTTON:
        text = SECOND_MENU
        markup = SECOND_MENU_MARKUP
    elif data == BACK_BUTTON:
        text = FIRST_MENU
        markup = FIRST_MENU_MARKUP
    elif data == GET_PDF_BUTTON:
        text = GET_PDF_MENU
        markup = GET_PDF_MENU_MARKUP

    # Close the query to end the client-side loading animation
    update.callback_query.answer()

    # Update message content with corresponding menu section
    update.callback_query.message.edit_text(
        text,
        ParseMode.HTML,
        reply_markup=markup
    )

def mn(update: Update, context: CallbackContext) -> None:
    # Print to console
    print(f'{update.message.from_user.first_name} wrote {update.message.text}')

    # Show help if just "mn" is sent
    text = update.message.text.strip()
    if text.lower() == "mn":
        context.bot.send_message(
            update.message.chat_id,
            """
                🌙 حاسبة منتصف الليل

                طريقة الاستخدام:
                `/mn [وقت الشروق] [وقت المغرب]`

                مثال:
                `/mn 6:09 6:34`

                ملاحظات:
                - استخدم صيغة 12 ساعة
                - ضع مسافة بين الأوقات
            """,
            entities=update.message.entities
                        )
        return
    
    try:
        text =  update.message.text
        text = text.replace("/mn ", "").split(" ")
        
        # Check if we have enough arguments
        if len(text) < 2 or not text[0].strip() or not text[1].strip():
           context.bot.send_message(
            update.message.chat_id,
            f"""
                ❌ خطأ في الإدخال

                الصيغة الصحيحة:
                `/mn [وقت الشروق] [وقت المغرب]`

                مثال: `/mn 6:09 6:34`
                
                والمشكلة هي: {e}

                والنص المدخل هو: {text}
            """)
           return
            
        fajr = int(text[0].split(":")[1]) / 60 + int(text[0].split(":")[0])
        maghrib =  int(text[1].split(":")[1]) / 60 + int(text[1].split(":")[0])
        middle_night = (fajr + 12 - maghrib) / 2 + maghrib 
        minutes = (middle_night - int(middle_night)) * 60
    
        # Respond whenever someone says "mn" and something else
        context.bot.send_message(
            update.message.chat_id,
            f"""
                ✅ حساب منتصف الليل

                🌅 وقت الشروق: {text[0]}
                🌆 وقت المغرب: {text[1]}
                🌙 منتصف الليل: {int(middle_night)}:{round(minutes)}

                ━━━━━━━━━━━━━━━━━━━━
                💡 طريقة الاستخدام: `\mn 6:09 6:34`
            """)
        if debug:
            context.bot.send_message(
                update.message.chat_id,
                f"""
                    decimal_fajr = {fajr}
                    decimal_maghrib =  {maghrib}
                    decimal_middle_night = {middle_night}
                    time_format_minutes = {minutes}
                """)
                    
    except (IndexError, ValueError, AttributeError) as e:
       context.bot.send_message(
            update.message.chat_id,
            f"""
                ❌ خطأ في صيغة الوقت
                
                تأكد من:
                - استخدام صيغة ساعة:دقيقة (مثل 6:09)
                - وضع مسافة بين الوقتين
                - عدم وجود أحرف غير صحيحة

                مثال صحيح: `mn 6:09 6:34`

                والمشكلة هي: {e}

                والنص المدخل هو: {text}
            """)

    except Exception as e:
       context.bot.send_message(
            update.message.chat_id,
            f"""
                ❌ حدث خطأ غير متوقع

                يرجى التجربة مرة أخرى بالصيغة الصحيحة:
                `mn 6:09 6:34`

                والمشكلة هي: {e}

                والنص المدخل هو: {text}
            """)

def debug(update: Update, context: CallbackContext) -> None:
    """
    This function handles /debug command
    """

    global debug
    debug = not debug

    context.bot.send_message(
        update.message.chat_id,
        f"debug mode: {debug}",
    )

def get_pdf(update: Update, context: CallbackContext):
        import requests
        import io

        context.bot.send_message(
        update.message.chat_id,
        "يتم تحميل ...الملف"
        )

        text = update.message.text
        id = text.split('/file/d/')[1].split('/')[0] if '/file/d/' in text else text.split('id=')[1].split('&')[0]

        direct_link = f"https://drive.google.com/uc?export=download&id={id}"
        response = requests.get(direct_link, stream=True)
        response.raise_for_status()

        file_buffer = io.BytesIO(response.content)
        file_buffer.name = f"{id}.pdf"

        context.bot.send_document(
        chat_id=update.message.chat_id,
        document=file_buffer
        )

def main() -> None:
    from dotenv import load_dotenv
    import os
    load_dotenv()

    updater = Updater(f"{os.getenv('TELEGRAM_BMEEBOT_TOKEN')}")

    # Get the dispatcher to register handlers
    # Then, we register each handler and the conditions the update must meet to trigger it
    dispatcher = updater.dispatcher

    # Register commands
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("mn", mn))
    dispatcher.add_handler(CommandHandler("debug", debug))

    # Register handler for inline buttons
    dispatcher.add_handler(CallbackQueryHandler(button_tap))

    # Echo any message that is not a command
    dispatcher.add_handler(MessageHandler(Filters.regex(r'.*drive.*'), get_pdf))
    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C
    updater.idle()

if __name__ == '__main__':
    main()