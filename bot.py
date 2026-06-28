import os
import asyncio
import yfinance as yf
from telegram import Bot

# लेटेस्ट वर्जन (v20+) के अनुसार सेटिंग्स
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# निफ्टी और सेंसेक्स के लेवल्स (इन्हें आप कभी भी बदल सकते हैं)
TARGETS = {
    "^NSEI": {"target": 24000, "sl": 23500},  # Nifty 50
    "^BSESN": {"target": 79000, "sl": 78000}  # Sensex
}

async def check_market():
    # लेटेस्ट v20+ में बोट ऑब्जेक्ट ऐसे बनता है
    bot = "8859992598:AAF8ZRS3xt1vavbtLvVWhBGkuKEEx-YJ_M0"
    print("लेटेस्ट बोट स्क्रिप्ट शुरू हो गई है...")
    
    while True:
        for ticker, levels in TARGETS.items():
            name = "NIFTY 50" if ticker == "^NSEI" else "SENSEX"
            try:
                # लाइव प्राइस फेच करना
                data = yf.Ticker(ticker)
                live_price = data.history(period="1d")["Close"].iloc[-1]
                print(f"{name} लाइव प्राइस: {live_price:.2f}")
                
                # टारगेट चेक और अलर्ट
                if live_price >= levels["target"]:
                    msg = f"🚀 ALERT: {name} ने टारगेट हिट किया! \nलाइव प्राइस: {live_price:.2f}\nटारगेट था: {levels['target']}"
                    await bot.send_message(chat_id=CHAT_ID, text=msg)
                
                # स्टॉपलॉस चेक और अलर्ट
                elif live_price <= levels["sl"]:
                    msg = f"⚠️ ALERT: {name} का Stoploss हिट हुआ! \nलाइव प्राइस: {live_price:.2f}\nSL था: {levels['sl']}"
                    await bot.send_message(chat_id=CHAT_ID, text=msg)
                    
            except Exception as e:
                print(f"डेटा निकालने में एरर आया: {e}")
                
        # हर 5 मिनट (300 सेकंड) में चेक करेगा
        await asyncio.sleep(300)

if __name__ == "__main__":
    # लेटेस्ट एसिंक्रोनस रनर
    asyncio.run(check_market())
