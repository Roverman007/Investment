import yfinance as yf
import pandas as pd
import smtplib
from email.mime.text import MIMEText
import os

# 追蹤資產清單
tickers = [
    "QQQ", "GLD", "TLT", "BND", "VT", "VNQ", "XLP", "BITO",
    "2800.HK", "2823.HK", "3033.HK", "3690.HK", "1810.HK", "XLE",
    "VHT", "URA", "OXY", "MP", "BRK-B", "BIDU", "SMH", "SCHD", "FXI"
]

# 下載數據
data = yf.download(tickers, period="15d", interval="1d", group_by='ticker', threads=True)

# 整理結果
summary = []

for ticker in tickers:
    df = data[ticker]
    df['EMA12'] = df['Close'].ewm(span=12, adjust=False).mean()
    df['EMA26'] = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = df['EMA12'] - df['EMA26']
    df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    df['RSI'] = 100 - (100 / (1 + df['Close'].pct_change().rolling(window=14).mean()))
    latest = df.iloc[-1]
    
    rsi_status = "超買 (>70)" if latest['RSI'] > 70 else "超賣 (<30)" if latest['RSI'] < 30 else "正常"
    macd_status = "金叉" if latest['MACD'] > latest['Signal'] else "死叉"
    
    summary.append(f"{ticker}: RSI={latest['RSI']:.1f} ({rsi_status}), MACD={macd_status}")

# 整理 email 內容
email_content = "\n".join(summary)

# 寄出 Email
email_user = os.environ['EMAIL_USER']
email_pass = os.environ['EMAIL_PASS']
email_to = "klauspoon@gmail.com"

msg = MIMEText(email_content)
msg['Subject'] = "📈 Roverman 每週技術指標分析"
msg['From'] = email_user
msg['To'] = email_to

server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
server.login(email_user, email_pass)
server.sendmail(email_user, email_to, msg.as_string())
server.quit()
