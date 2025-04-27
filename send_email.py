# send_email.py 最強修正版！

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
    df = yf.download(ticker, period="6mo", interval="1d")
    if df.empty:
        raise ValueError("無法取得資料")
    df = df[-50:].copy()

    # 計算技術指標
    df['EMA12'] = df['Close'].ewm(span=12, adjust=False).mean()
    df['EMA26'] = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = df['EMA12'] - df['EMA26']
    df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()

    delta = df['Close'].diff()
    gain = delta.clip(lower=0).rolling(window=14).mean()
    loss = -delta.clip(upper=0).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))

    latest = df.iloc[-1]

    close_price = float(latest['Close'])
    rsi_value = float(latest['RSI'])
    macd_status = "金叉" if float(latest['MACD']) > float(latest['Signal']) else "死叉"
    sma50 = df['Close'].rolling(window=50).mean().iloc[-1]
    sma200 = df['Close'].rolling(window=200).mean().iloc[-1]
    sma50_status = "Above SMA50" if close_price > sma50 else "Below SMA50"
    sma200_status = "Above SMA200" if close_price > sma200 else "Below SMA200"
    adx_strength = float(df['Close'].diff().abs().rolling(window=14).mean().iloc[-1])

    return {
        'Close': round(close_price, 2),
        'RSI': round(rsi_value, 1),
        'MACD': macd_status,
        'SMA50 Trend': sma50_status,
        'SMA200 Trend': sma200_status,
        'ADX': round(adx_strength, 1)
    }

# 集中所有資產的資料
report = ""
for asset in assets:
    try:
        info = get_asset_info(asset)
        asset_report = (
            f"{asset}:\n"
            f"  - Close: {info['Close']}\n"
            f"  - RSI: {info['RSI']}\n"
            f"  - MACD: {info['MACD']}\n"
            f"  - SMA50 Trend: {info['SMA50 Trend']}\n"
            f"  - SMA200 Trend: {info['SMA200 Trend']}\n"
            f"  - ADX (Trend Strength): {info['ADX']}\n\n"
        )
        report += asset_report
    except Exception as e:
        error_report = (
            f"{asset}:\n"
            f"  - ⚠️ 資料取得失敗，錯誤原因：{e}\n\n"
        )
        report += error_report

# Email 設定
email_user = "roverpoonhkg@gmail.com"
email_pass = "bkws mgrr kmpy cpqv"  # App Password
email_send = "klauspoon@gmail.com"

subject = "Roverman 技術分析更新"

msg = MIMEMultipart()
msg['From'] = email_user
msg['To'] = email_send
msg['Subject'] = subject

body = report if report.strip() else "⚠️ 今日未能取得任何資產資料，請稍後再試。"
msg.attach(MIMEText(body, 'plain'))

# 發送 Email
server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
server.login(email_user, email_pass)
text = msg.as_string()
server.sendmail(email_user, email_send, text)
server.quit()

print("✅ Email Sent Successfully!")
