
import os
import asyncio
import yfinance as yf
from telegram import Bot
import pandas as pd
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading


TOKEN = "8859992598:AAF8ZRS3xt1vavbtLvVWhBGkuKEEx-YJ_M0"
CHAT_ID = '5994059280'

class DummyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"Nifty RSI Strategy Bot is Running!")

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), DummyServer)
    server.serve_forever()

async def check_strategy():
    bot = Bot(token=TOKEN)
    print("9/21 EMA + RSI स्ट्रेटजी बोट शुरू हो गया है...")
    last_signal = None 

    while True:
        try:
            ticker = yf.Ticker("^NSEI")
            df = ticker.history(period="3d", interval="5m")
            
            if len(df) > 30:
                # 1. EMA कैलकुलेशन
                df['EMA_9'] = df['Close'].ewm(span=9, adjust=False).mean()
                df['EMA_21'] = df['Close'].ewm(span=21, adjust=False).mean()
                
                # 2. RSI मैन्युअल कैलकुलेशन (बिना किसी बाहरी लाइब्रेरी के)
                delta = df['Close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rs = gain / loss
                df['RSI'] = 100 - (100 / (1 + rs))
                
                # आखिरी कैंडल्स का डेटा
                prev_row = df.iloc[-3]
                last_row = df.iloc[-2] # क्लोज कैंडल
                current_price = df['Close'].iloc[-1]
                
                current_rsi = last_row['RSI']
                
                # 🔴 CALL ENTRY (EMA Cross Up + RSI > 55 मजबूत ट्रेंड के लिए)
                if prev_row['EMA_9'] <= prev_row['EMA_21'] and last_row['EMA_9'] > last_row['EMA_21']:
                    if current_rsi > 55:
                        if last_signal != "BUY":
                            entry = round(current_price, 2)
                            target = round(entry + 70, 2)
                            sl = round(entry - 35, 2)
                            
                            msg = f"🔥 **NIFTY CALL ENTRY (BUY)** 🔥\n\n" \
                                  f"📈 एंट्री प्राइस: {entry}\n" \
                                  f"🎯 टारगेट (Target): {target} (+70 Pts)\n" \
                                  f"⚠️ स्टॉपलॉस (SL): {sl} (-35 Pts)\n" \
                                  f"📊 RSI: {round(current_rsi, 2)} (मजबूत मोमेंटम)"
                            await bot.send_message(chat_id=CHAT_ID, text=msg)
                            last_signal = "BUY"
                
                # 🟢 PUT ENTRY (EMA Cross Down + RSI < 45 मजबूत मंदी के लिए)
                elif prev_row['EMA_9'] >= prev_row['EMA_21'] and last_row['EMA_9'] < last_row['EMA_21']:
                    if current_rsi < 45:
                        if last_signal != "SELL":
                            entry = round(current_price, 2)
                            target = round(entry - 70, 2)
                            sl = round(entry + 35, 2)
                            
                            msg = f"💥 **NIFTY PUT ENTRY (SELL)** 💥\n\n" \
                                  f"📉 एंट्री प्राइस: {entry}\n" \
                                  f"🎯 टारगेट (Target): {target} (-70 Pts)\n" \
                                  f"⚠️ स्टॉपलॉस (SL): {sl} (+35 Pts)\n" \
                                  f"📊 RSI: {round(current_rsi, 2)} (मजबूत मंदी)"
                            await bot.send_message(chat_id=CHAT_ID, text=msg)
                            last_signal = "SELL"
                            
        except Exception as e:
            print(f"रणनीति एरर: {e}")
            
        await asyncio.sleep(300)

if __name__ == "__main__":
    threading.Thread(target=run_web_server, daemon=True).start()
    asyncio.run(check_strategy())
