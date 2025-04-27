# 完整版 send_email.py

import yfinance as yf
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# 資產清單
assets = [
    "QQQ", "GLD", "TLT", "BND", "VT", "VNQ", "XLP", "BITO",
    "2800.HK", "2823.HK", "3033.HK", "3690.HK", "1810.HK",
    "XLE", "URA", "OXY", "MP", "BRK-B", "BIDU",
    "SMH", "SCHD", "FXI",
    "XLU", "VXUS", "VHT", "MTCH", "HSAI",
    "06618.HK", "03191.HK", "01137.HK", "MSFT", "JNJ"
]

# 抓取每個資產的資料
def get_asset_info(ticker):
    df = yf.download(ticker, period="3mo", interval="1d")
    df = df[-50:].copy()
    df['EMA12'] = df['Close'].ewm(span=12, adjust=False).mean()
    df['EMA26'] = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = df['EMA12'] - df['EMA26']
    df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    df['RSI'] = 100 - (100 / (1 + df['Close'].pct_change().rolling(window=14).mean()))
    latest = df.iloc[-1]

    macd_status = "金叉" if latest['MACD'] > latest['Signal'] else "死叉"
    sma50 = df['Close'].rolling(window=50).mean()
    sma200 = df['Close'].rolling(window=200).mean()
    sma50_status = "Above SMA50" if latest['Close'] > sma50.iloc[-1] else "Below SMA50"
    sma200_status = "Above SMA200" if latest['Close'] > sma200.iloc[-1] else "Below SMA200"

    adx = df['Close'].diff().abs().rolling(window=14).mean().iloc[-1]  # 簡易版ADX

    return {
        'Close': round(latest['Close'], 2),
        'RSI': round(latest['RSI'], 1),
        'MACD': macd_status,
        'SMA50 Trend': sma50_status,
        'SMA200 Trend': sma200_status,
        'ADX': round(adx, 1)
    }

# 集中所有資產的資料
report = ""
for asset in assets:
    try:
        info = get_asset_info(asset)
        asset_report = f"{asset}:\n  - Close: {info['Close']}\n  - RSI: {info['RSI']}\n  - MACD: {info['MACD']}\n  - SMA50 Trend: {info['SMA50 Trend']}\n  - SMA200 Trend: {info['SMA200 Trend']}\n  - ADX (Trend Strength): {info['ADX']}\n\n"
        report += asset_report
    except Exception as e:
        print(f"Error fetching {asset}: {e}")

# Email 設定
email_user = "roverpoonhkg@gmail.com"
email_pass = "bkws mgrr kmpy cpqv"  # 用 App Password
email_send = "klauspoon@gmail.com"

subject = "Roverman 技術分析更新"

msg = MIMEMultipart()
msg['From'] = email_user
msg['To'] = email_send
msg['Subject'] = subject

body = report
msg.attach(MIMEText(body, 'plain'))

# 發送 Email
server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
server.login(email_user, email_pass)
text = msg.as_string()
server.sendmail(email_user, email_send, text)
server.quit()

print("✅ Email Sent Successfully!")
