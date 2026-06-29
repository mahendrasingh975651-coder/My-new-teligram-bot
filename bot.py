
import os
import requests
import telebot
from flask import Flask, request

# ---- कॉन्फ़िगरेशन ----
BOT_TOKEN = "8859992598:AAF8ZRS3xt1vavbtLvVWhBGkuKEEx-YJ_M0"
RENDER_URL = "https://onrender.com"  # अपना रेंडर URL डालें

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# ---- बॉट कमांड्स और ट्रेडिंग सिग्नल्स लॉजिक ----

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = (
        "🤖 **ट्रेडिंग सिग्नल अलर्ट बॉट में आपका स्वागत है!**\n\n"
        "📈 **एक्यूरेसी:** 60% - 70%\n"
        "🎯 **टारगेट:** प्रीमियम चार्ट्स में 50 से 100 पॉइंट्स कैप्चर।\n\n"
        "सिग्नल प्राप्त करने के लिए चैनल/ग्रुप में अलर्ट्स चालू रखें।"
    )
    bot.reply_to(message, welcome_text, parse_mode="Markdown")

# उदाहरण: जब आपको कोई ट्रेडिंग अलर्ट भेजना हो, तो आप इस फ़ंक्शन का उपयोग कर सकते हैं
def send_trading_signal(chat_id, action, entry, target1, target2, sl):
    """
    मैन्युअल या ऑटोमैटिक सिग्नल भेजने के लिए फ़ंक्शन
    action: BUY_CALL, BUY_PUT
    """
    signal_text = (
        "🚨 **NEW TRADING SIGNAL** 🚨\n"
        f"➡️ **Action:** {action}\n"
        f"🎯 **Entry Point:** {entry}\n"
        f"✅ **Target 1:** {target1} (+50 Points)\n"
        f"✅ **Target 2:** {target2} (+100 Points)\n"
        f"❌ **Stop Loss (SL):** {sl}\n\n"
        "⚠️ *रिस्क मैनेजमेंट के साथ ट्रेड करें। एक्यूरेसी: 60-70%*"
    )
    bot.send_message(chat_id, signal_text, parse_mode="Markdown")


# ---- WEBHOOK & SERVER SETTINGS (Render के लिए अनिवार्य) ----

@app.route('/' + BOT_TOKEN, methods=['POST'])
def get_message():
    """टेलीग्राम से आने वाले अपडेट्स को प्रोसेस करने के लिए"""
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "OK", 200

@app.route('/')
def webhook_setup():
    """जब रेंडर सर्वर चालू होगा, यह वेबहुक एक्टिवेट करेगा"""
    bot.remove_webhook()
    # पुराने सभी पेंडिंग टेलीग्राम मैसेजेस (Conflicts) को साफ़ करने के लिए drop_pending_updates=True किया है
    bot.set_webhook(url=f"{RENDER_URL}/{BOT_TOKEN}", drop_pending_updates=True)
    return "<h3>Trading Bot Webhook Successfully Configured!</h3>", 200

if __name__ == "__main__":
    # Render स्वचालित रूप से PORT एन्वायरमेंट वेरिएबल प्रदान करता है
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
