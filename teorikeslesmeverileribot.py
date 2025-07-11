import logging
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup,
    ReplyKeyboardMarkup, KeyboardButton
)
from telegram.ext import (
    Application, MessageHandler, filters, ContextTypes,
    CallbackQueryHandler, CommandHandler
)

# ----------------------
TOKEN = "7983646134:AAGm9bdC1g_hU-aA4m_L0FZSAeSIUMpg0gA"

PUBLIC_GROUP_USERNAMES = [
    "teorikeslesme1",
    "teorikeslesme2",
    "teorikeslesme3",
    "teorikeslesme4",
    "megaphissesii",
    "sdttrhissesi",
    "borsaanketleri",
    "analisthedefleri",
    "ekonomikitaplari",
    "tavandabekleyenlot",
    "thyaoteorik",
    "crfsateorik",
    "astorteorik",
    "dgnmoteorik",
    "ulufateorik",
    "eliteteorik",
    "bimasteorik",
    "vakbnteorik"
]
# ----------------------

logging.basicConfig(level=logging.INFO)

user_points = {}
user_message_points = {}

# --- /start komutu ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = ReplyKeyboardMarkup(
        [
            [KeyboardButton("Puanımı gör")],
            [KeyboardButton("Canlı veri grubuna git")]
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )
    await update.message.reply_text(
        "Hoş geldin! Aşağıdaki butonları kullanabilirsin:",
        reply_markup=keyboard
    )

# --- Grup mesajlarında mention ve butonlar ---

async def mention_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    chat = update.effective_chat

    if not message.text:
        return

    # Mesaj bot tarafından mı atılmış? (Mesaj gönderenin username'si @MagfiAds_Bot ise)
    sender_username = message.from_user.username if message.from_user else None
    if sender_username != "MagfiAds_Bot":
        return  # Sadece @MagfiAds_Bot tarafından gönderilen mesajlara cevap ver

    # Mesaj grubun adı "Magfi Ads- #sponsorlu" mu?
    if chat.title != "Magfi Ads- #sponsorlu":
        return  # Sadece o grup

    msg_id = message.message_id
    group_username = chat.username

    if group_username not in PUBLIC_GROUP_USERNAMES:
        logging.info(f"Bilinmeyen grup: {group_username}")
        return

    group_link = f"https://t.me/{group_username}/{msg_id}"

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Görüntüle", url=group_link)],
        [InlineKeyboardButton("Görüntüledim", callback_data=f"seen_{chat.id}_{msg_id}")],
        [InlineKeyboardButton("Bota dön", url="https://t.me/teorikeslesmeverileribot")]
    ])

    await message.reply_text(
        "Görüntüle, görüntüledim butonuna bas, 1 günlük canlı veri kazan!",
        reply_markup=keyboard
    )

# --- Inline buton callback ---

async def callback_query_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    data = query.data

    if data.startswith("seen_"):
        _, chat_id_str, message_id_str = data.split("_")
        chat_id = int(chat_id_str)
        message_id = int(message_id_str)

        key = (user.id, chat_id, message_id)

        if user_message_points.get(key):
            await query.answer("Bu mesaj için puanını zaten aldın.", show_alert=True)
            return

        # Puan arttır
        user_points[user.id] = user_points.get(user.id, 0) + 1
        user_message_points[key] = True

        await query.answer("Puanın 1 arttı! Tebrikler 🎉", show_alert=True)

        # Kullanıcıya özel mesaj gönder, reply keyboard olmadan
        try:
            await context.bot.send_message(
                chat_id=user.id,
                text=f"Merhaba {user.first_name}, puanın 1 arttı! Kaç puana ihtiyacın olduğunu görmek için /start'a bas. Toplam puanın: {user_points[user.id]}"
            )
        except Exception as e:
            logging.warning(f"Özel mesaj gönderilemedi: {e}")

# --- ReplyKeyboard ile gelen mesajları yönet ---

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user = update.message.from_user

    if text == "Puanımı gör":
        puan = user_points.get(user.id, 0)
        await update.message.reply_text(f"Puanın: {puan}")

    elif text == "Canlı veri grubuna git":
        puan = user_points.get(user.id, 0)
        if puan < 25:
            eksik = 25 - puan
            await update.message.reply_text(f"Puanın {puan}. Canlı veri grubuna katılmak için {eksik} puan daha kazanmalısın.")
        else:
            user_points[user.id] = 0
            await update.message.reply_text(
                "Tebrikler! Puanın 25'e ulaştı ve sıfırlandı.\n"
                "Canlı veri grubuna katılmak için lütfen @turgute ile iletişime geç."
            )

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    # Reply keyboard mesajları sadece özel sohbetlerde işlenecek (grup değil)
    app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE, button_handler))

    app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.GROUPS, mention_handler))
    app.add_handler(CallbackQueryHandler(callback_query_handler))

    app.run_polling()

if __name__ == '__main__':
    main()
