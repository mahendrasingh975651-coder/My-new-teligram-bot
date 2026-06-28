
import os
import asyncio
import yfinance as yf
from telegram import Bot
from http.server import HTTPServer, BaseHTTPRequestHandler

# 🛠️ आपकी सेटिंग्स (पहले से सेट कर दी हैं)
TOKEN = "8859992598:AAF8ZRS3xt1vavbtLvVWhBG"
CHAT_ID = "5994059280"

port = int(os.getenv("PORT", 8000))

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive")

def run_server():
    server = HTTPServer(("0.0.0.0", port), SimpleHTTPRequestHandler)
    import threading
    threading.Thread(target=server.serve_forever, daemon=True).start()

async def check_strategy():
    bot = Bot(token=TOKEN)
    print("1-Minute Pre-Alert Trading Bot Started...")
    last_signal = None

    while True:
        try:
            ticker = yf.Ticker("^NSEI")
            df = ticker.history(period="1mo", interval="15m")
            
            if df.empty or len(df) < 30:
                await asyncio.sleep(10)
                continue

            # EMA Calculation
            df['EMA_9'] = df['Close'].ewm(span=9, adjust=False).mean()
            df['EMA_21'] = df['Close'].ewm(span=21, adjust=False).mean()

            # RSI Calculation
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / (loss + 1e-10)
            df['RSI'] = 100 - (100 / (1 + rs))

            current_price = round(df['Close'].iloc[-1], 2)
            ema9_now = df['EMA_9'].iloc[-1]
            ema21_now = df['EMA_21'].iloc[-1]
            rsi_now = df['RSI'].iloc[-1]

            # सिग्नल कंडीशन चेक करना
            if ema9_now > ema21_now and rsi_now > 58:
                current_signal = "BUY"
            elif ema9_now < ema21_now and rsi_now < 42:
                current_signal = "SELL"
            else:
                current_signal = "HOLD"

            # अगर कोई मजबूत कंडीशन बन रही है, तो टेलीग्राम पर मैसेज भेजना
            if current_signal != "HOLD" and current_signal != last_signal:
                last_signal = current_signal
                
                target_price = current_price + 120 if current_signal == "BUY" else current_price - 120
                sl_price = current_price - 40 if current_signal == "BUY" else current_price + 40
                option_type = "CE (Call Option)" if current_signal == "BUY" else "PE (Put Option)"

                message_text = (
                    f"⚠️ *🚨 UPCOMING SIGNAL ALERT (1 MIN LEFT) 🚨*\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"📝 *Action:* Prepare to {current_signal} {option_type}\n"
                    f"💰 *Expected Entry:* ₹{current_price}\n"
                    f"🎯 *Target (~100pt Premium):* ₹{round(target_price, 2)}\n"
                    f"🛑 *StopLoss:* ₹{round(sl_price, 2)}\n"
                    f"📊 *Current RSI:* {round(rsi_now, 2)}\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"⏳ _अगले 1 मिनट में कैंडल क्लोज होते ही ट्रेड एग्जीक्यूट करें।_"
                )
                
                await bot.send_message(chat_id=CHAT_ID, text=message_text, parse_mode='Markdown')
                print(f"एडवांस अलर्ट टेलीग्राम पर भेजा गया: {current_signal}")

        except Exception as e:
            print(f"Error: {e}")
        
        await asyncio.sleep(60)

if __name__ == "__main__":
    run_server()
    asyncio.run(check_strategy())
