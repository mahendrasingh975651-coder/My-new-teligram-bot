
import os
import asyncio
import yfinance as yf
from telegram import Bot
import pandas as pd
import pandas_ta as ta
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

# अपना असली टोकन और चैट आईडी यहाँ डालें
TOKEN = "8859992598:AAF8ZRS3xt1vavbtLvVWhBGkuKEEx-YJ_M0"

CHAT_ID = '5994059280'

class DummyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"Advanced Strategy Bot is Running!")

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), DummyServer)
    server.serve_forever()

async def check_advanced_strategy():
    bot = Bot(token=TOKEN_REAL)
    print("एडवांस 15-डे प्रॉफिट स्ट्रेटजी बोट शुरू हो गया है...")
    last_signal = None 

    while True:
        try:
            ticker = yf.Ticker("^NSEI")
            df = ticker.history(period="3d", interval="5m")
            
            if len(df) > 35:
                # 1. EMA कैलकुलेशन
                df['EMA_9'] = df['Close'].ewm(span=9, adjust=False).mean()
                df['EMA_21'] = df['Close'].ewm(span=21, adjust=False).mean()
                
                # 2. RSI कैलकुलेशन
                df['RSI'] = ta.rsi(df['Close'], length=14)
                
                # 3. Supertrend कैलकुलेशन (7, 3)
                sti = ta.supertrend(df['High'], df['Low'], df['Close'], length=7, multiplier=3)
                df['ST_Direction'] = sti['SUPERTd_7_3.0'] # 1 मतलब Buy, -1 मतलब Sell
                
                # आखिरी कैंडल्स का डेटा
                prev_row = df.iloc[-3]
                last_row = df.iloc[-2] # क्लोज कैंडल
                current_price = df['Close'].iloc[-1]
                
                # 🔴 CALL ENTRY FILTER (EMA Crossover + Supertrend GREEN + RSI > 50)
                if prev_row['EMA_9'] <= prev_row['EMA_21'] and last_row['EMA_9'] > last_row['EMA_21']:
                    if last_row['ST_Direction'] == 1 and last_row['RSI'] > 50:
                        if last_signal != "BUY":
                            entry = round(current_price, 2)
                            target = round(entry + 70, 2)
                            sl = round(entry - 35, 2)
                            
                            msg = f"🔥 **HIGH ACCURACY NIFTY CALL (BUY)** 🔥\n\n" \
                                  f"📈 एंट्री प्राइस: {entry}\n" \
                                  f"🎯 टारगेट (Target): {target} (+70 Pts)\n" \
                                  f"⚠️ स्टॉपलॉस (SL): {sl} (-35 Pts)\n" \
                                  f"📊 RSI: {round(last_row['RSI'], 2)} (मजबूत बुल्स)"
                            await bot.send_message(chat_id=CHAT_ID, text=msg)
                            last_signal = "BUY"
                
                # 🟢 PUT ENTRY FILTER (EMA Crossover + Supertrend RED + RSI < 50)
                elif prev_row['EMA_9'] >= prev_row['EMA_21'] and last_row['EMA_9'] < last_row['EMA_21']:
                    if last_row['ST_Direction'] == -1 and last_row['RSI'] < 48:
                        if last_signal != "SELL":
                            entry = round(current_price, 2)
                            target = round(entry - 70, 2)
                            sl = round(entry + 35, 2)
                            
                            msg = f"💥 **HIGH ACCURACY NIFTY PUT (SELL)** 💥\n\n" \
                                  f"📉 एंट्री प्राइस: {entry}\n" \
                                  f"🎯 टारगेट (Target): {target} (-70 Pts)\n" \
                                  f"⚠️ स्टॉपलॉस (SL): {sl} (+35 Pts)\n" \
                                  f"📊 RSI: {round(last_row['RSI'], 2)} (मजबूत बीयर्स)"
                            await bot.send_message(chat_id=CHAT_ID, text=msg)
                            last_signal = "SELL"
                            
        except Exception as e:
            print(f"स्ट्रेटजी एरर: {e}")
            
        await asyncio.sleep(300) # हर 5 मिनट में चेक करेगा

if __name__ == "__main__":
    threading.Thread(target=run_web_server, daemon=True).start()
    asyncio.run(check_advanced_strategy())
