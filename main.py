import json
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
KONGJI_TOKEN = os.environ["KONGJI_TELEGRAM_TOKEN"]
KONGJI_CHAT_ID = os.environ["KONGJI_TELEGRAM_CHAT_ID"]
STATE_FILE = "state.json"


def load_state():
    try:
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    except:
        return {}


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def check_cross(df, ma_col, name, ticker, state, band=0.02):
    curr_price = df["Close"].iloc[-1].item()
    curr_ma = df[ma_col].iloc[-1].item()

    # ma가 넘으면 매수, 98 이격도 미만이면 매도
    upper = curr_ma
    lower = curr_ma * (1 - band)

    key = f"{ticker}_{ma_col}"

    prev_state = state.get(key)

    # 현재 상태 판단
    if curr_price > upper:
        curr_state = "UP"
    elif curr_price < lower:
        curr_state = "DOWN"
    else:
        curr_state = prev_state

    # 상태 변화 있을 때만 알림
    if prev_state != curr_state:
        state[key] = curr_state

        if curr_state == "UP":
            return f"{name} UP 전환 (MA 돌파)"
        elif curr_state == "DOWN":
            return f"{name} DOWN 전환 ({100 - int(band * 100)}% 이격도 미만)"

    return None


def process(ticker, state):
    df = yf.download(ticker, period="1y", auto_adjust=True, progress=False)

    df["MA60"] = df["Close"].rolling(60).mean()
    df["MA120"] = df["Close"].rolling(120).mean()
    df["MA200"] = df["Close"].rolling(200).mean()

    signals = []

    for ma, label in [
        ("MA60", "60일"),
        ("MA120", "120일"),
        ("MA200", "200일"),
    ]:
        result = check_cross(df, ma, label, ticker, state, band=0.02)
        if result:
            signals.append(result)

    return signals


def send_telegram(msg):
    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        data={"chat_id": CHAT_ID, "text": msg},
    )
    requests.post(
        f"https://api.telegram.org/bot{KONGJI_TOKEN}/sendMessage",
        data={"chat_id": KONGJI_CHAT_ID, "text": msg},
    )


def main():
    messages = []

    state = load_state()

    for ticker, name in TICKERS.items():
        signals = process(ticker, state)

        if signals:
            msg = f"[{name}]\n" + "\n".join(signals)
            messages.append(msg)

    if messages:
        final_msg = "\n\n".join(messages)
        send_telegram(final_msg)

    save_state(state)


if __name__ == "__main__":
    main()
