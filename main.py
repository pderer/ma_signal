import os

import requests
import yfinance as yf

TICKERS = {
    "379800.KS": "KODEX 미국S&P500",
    "294400.KS": "KIWOOM 200TR",
    "283580.KS": "KODEX 차이나 CSI300",
    "453810.KS": "KODEX 인도 NIFTY50",
    "308620.KS": "KODEX 미국10년국채선물",
    "453850.KS": "ACE 미국30년국채액티브(H)",
    "385560.KS": "RISE KIS국고채30년Enhanced",
    "411060.KS": "ACE KRX금현물",
}

TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]


def check_cross(df, ma_col, name, band=0.01):
    prev_price = df["Close"].iloc[-2].item()
    curr_price = df["Close"].iloc[-1].item()

    prev_ma = df[ma_col].iloc[-2].item()
    curr_ma = df[ma_col].iloc[-1].item()

    upper_prev = prev_ma * (1 + band)
    upper_curr = curr_ma * (1 + band)

    lower_prev = prev_ma * (1 - band)
    lower_curr = curr_ma * (1 - band)

    # 상향 돌파 (밴드 위로 진입)
    if prev_price <= upper_prev and curr_price > upper_curr:
        return f"{name} 상향 돌파 (+{int(band * 100)}% 밴드)"

    # 하향 돌파 (밴드 아래로 이탈)
    if prev_price >= lower_prev and curr_price < lower_curr:
        return f"{name} 하향 돌파 (-{int(band * 100)}% 밴드)"

    return None


def process(ticker, name):
    df = yf.download(ticker, period="1y", auto_adjust=True, progress=False)

    df["MA60"] = df["Close"].rolling(60).mean()
    df["MA120"] = df["Close"].rolling(120).mean()
    df["MA200"] = df["Close"].rolling(200).mean()

    signals = []

    for ma, label in [("MA60", "60일"), ("MA120", "120일"), ("MA200", "200일")]:
        result = check_cross(df, ma, label, band=0.01)
        if result:
            signals.append(result)

    return signals


def send_telegram(msg):
    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        data={"chat_id": CHAT_ID, "text": msg},
    )


def main():
    messages = []

    for ticker, name in TICKERS.items():
        signals = process(ticker, name)

        if signals:
            msg = f"[{name}]\n" + "\n".join(signals)
            messages.append(msg)

    if messages:
        final_msg = "\n\n".join(messages)
        send_telegram(final_msg)


if __name__ == "__main__":
    main()
