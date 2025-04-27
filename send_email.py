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
data = yf.download(tickers, period="6mo", interval="1d", group_by='ticker', threads=True, auto_adjust=True)

# 整理結果
summary = []

for ticker in tickers:
    df = data[ticker].dropna()
    df['SMA50'] = df['Close'].rolling(window=50).mean()
    df['SMA200'] = df['Close'].rolling(window=200).mean()
    df['EMA12'] = df['Close'].ewm(span=12, adjust=False).mean()
    df['EMA26'] = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = df['EMA12'] - df['EMA26']
    df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    delta = df['Close'].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()
    rs = avg_gain / avg_loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    df['UpMove'] = df['High'].diff()
    df['DownMove'] = df['Low'].diff() * -1
    df['PlusDM'] = (df['UpMove'] > df['DownMove']) & (df['UpMove'] > 0) * df['UpMove']
    df['MinusDM'] = (df['DownMove'] > df['UpMove']) & (df['DownMove'] > 0) * df['DownMove']
    df['TR'] = df[['High', 'Close']].max(axis=1) - df[['Low', 'Close']].min(axis=1)
    df['ATR'] = df['TR'].rolling(window=14).mean()
    df['PlusDI'] = 100 * (df['PlusDM'].rolling(window=14).sum() / df['ATR'])
    df['MinusDI'] = 100 * (df['MinusDM'].rolling(window=14).sum() / df['ATR'])
    df['DX'] = (abs(df['PlusDI'] - df['MinusDI']) / (df['PlusDI'] + df['MinusDI'])) * 100
    df['ADX'] = df['DX'].rolling(window=14).mean()

    latest = df.iloc[-1]

    # 整理每隻資產的技術摘要
    summary.append(
        f"{ticker}:\n"
        f"  - Close: {latest['Close']:.2f}\n"
        f"  - RSI: {latest['RSI']:.1f}\n"
        f"  - MACD: {'金叉' if latest['MACD'] > latest['Signal'] else '死叉'}\n"
        f"  - SMA50 Trend: {'Above' if latest['Close'] > latest['SMA50'] else 'Below'} SMA50\n"
        f"  - SMA200 Trend: {'Above' if latest['Close'] > latest['SMA200'] else 'Below'} SMA200\n"
        f"  - ADX (Trend Strength): {latest['ADX']:.1f}\n"
    )

# 組成 email 內容
email_content = "\n\n".join(summary)

# Gmail 發送設定
email_user = os.environ['EMAIL_USER']
email_pass = os.environ['EMAIL_PASS']
email_to = "klauspoon@gmail.com"

msg = MIMEText(email_content)
msg['Subject'] = "📈 Roverman 每週技術指標分析（中長線版）"
msg['From'] = email_user
msg['To'] = email_to

server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
server.login(email_user, email_pass)
server.sendmail(email_user, [email_to], msg.as_string())
server.quit()
