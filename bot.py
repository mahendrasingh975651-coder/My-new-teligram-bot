import os
import asyncio
import yfinance as yf
from telegram import Bot
import pandas as pd
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

# अपना असली टोकन और चैट आईडी यहाँ डालें
TOKEN = "8859992598:AAF8ZRS3xt1vavbtLvVWhBGkuKEEx-YJ_M0"
CHAT_ID ='5994059280'


# रेंडर के पोर्ट एरर को ठीक करने के लिए नकली वेब सर्वर
class DummyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"Bot is running alive!")

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), DummyServer)
    print(f"वेब सर्वर पोर्ट {port} पर शुरू हो गया है...")
    server.serve_forever()

async def check_strategy():
    bot = Bot(token=TOKEN)
    print("ऑटोमैटिक एंट्री-टारगेट बोट शुरू हो गया है...")
    last_signal = None 

    while True:
        try:
            ticker = yf.Ticker("^NSEI")
            df = ticker.history(period="2d", interval="5m")
            
            if len(df) > 30:
                df['EMA_9'] = df['Close'].ewm(span=9, adjust=False).mean()
                df['EMA_21'] = df['Close'].ewm(span=21, adjust=False).mean()
                
                prev_row = df.iloc[-3]
                last_row = df.iloc[-2]
                current_price = df['Close'].iloc[-1]
                
                if prev_row['EMA_9'] <= prev_row['EMA_21'] and last_row['EMA_9'] > last_row['EMA_21']:
                    if last_signal != "BUY":
                        entry = round(current_price, 2)
                        target = round(entry + 60, 2)
                        sl = round(entry - 30, 2)
                        
                        msg = f"🟢 **NIFTY CALL ENTRY (BUY)** 🟢\n\n📈 एंट्री प्राइस: {entry}\n🎯 टारगेट (Target): {target} (+60 Pts)\n⚠️ स्टॉपलॉस (SL): {sl} (-30 Pts)"
                        await bot.send_message(chat_id=CHAT_ID, text=msg)
                        last_signal = "BUY"
                
                elif prev_row['EMA_9'] >= prev_row['EMA_21'] and last_row['EMA_9'] < last_row['EMA_21']:
                    if last_signal != "SELL":
                        entry = round(current_price, 2)
                        target = round(entry - 60, 2)
                        sl = round(entry + 30, 2)
                        
                        msg = f"🔴 **NIFTY PUT ENTRY (SELL)** 🔴\n\n📉 एंट्री प्राइस: {entry}\n🎯 टारगेट (Target): {target} (-60 Pts)\n⚠️ स्टॉपलॉस (SL): {sl} (+30 Pts)"
                        await bot.send_message(chat_id=CHAT_ID, text=msg)
                        last_signal = "SELL"
                        
        except Exception as e:
            print(f"कैलकुलेशन में एरर: {e}")
            
        await asyncio.sleep(300)

if __name__ == "__main__":
    # वेब सर्वर को बैकग्राउंड थ्रेड में चलाना
    threading.Thread(target=run_web_server, daemon=True).start()
    # बोट की मुख्य स्ट्रेटजी शुरू करना
    asyncio.run(check_strategy())
