# MA Signal Bot

한국 상장 ETF의 **이동평균선(Moving Average) 돌파 여부를 추적하고, 상태가 변경되면 Telegram으로 알림을 보내는 자동화 봇**입니다.

`yfinance`를 통해 ETF 가격을 가져오고 **60일 / 120일 / 200일 이동평균선**을 계산합니다.
GitHub Actions를 이용해 평일마다 자동 실행되며, 이전 상태는 `state.json`에 저장하여 **실제 상태 변화가 발생했을 때만 알림**을 전송합니다.

## Strategy

각 ETF에 대해 다음 이동평균선을 추적합니다.

* MA60
* MA120
* MA200

단순히 이동평균선을 한 번 넘나들 때마다 신호를 발생시키지 않고, **2% band를 둔 상태 기반 방식**을 사용합니다.

```text
Price >= MA
    → UP

Price <= MA × 0.98
    → DOWN

MA × 0.98 < Price < MA
    → Previous State 유지
```

예를 들어 MA200이 `10,000원`이라면:

```text
Price >= 10,000
    → UP

Price <= 9,800
    → DOWN

9,800 < Price < 10,000
    → 기존 상태 유지
```

이 방식은 이동평균선 부근에서 가격이 반복적으로 움직일 때 발생하는 불필요한 신호를 줄이기 위한 것입니다.

## Signal

상태가 실제로 변경된 경우에만 Telegram 알림을 전송합니다.

### UP

가격이 이동평균선을 상향 돌파한 경우입니다.

```text
[KODEX 미국S&P500]
60일 UP 전환 (MA 돌파)
```

### DOWN

가격이 이동평균선의 98% 이하로 내려간 경우입니다.

```text
[KODEX 미국S&P500]
60일 DOWN 전환 (98% 이격도 미만)
```

## Monitored ETFs

| Ticker      | ETF                    |
| ----------- | ---------------------- |
| `379800.KS` | KODEX 미국S&P500         |
| `294400.KS` | KIWOOM 200TR           |
| `283580.KS` | KODEX 차이나 CSI300       |
| `453810.KS` | KODEX 인도 NIFTY50       |
| `308620.KS` | KODEX 미국10년국채선물        |
| `453850.KS` | ACE 미국30년국채액티브(H)      |
| `385560.KS` | RISE KIS국고채30년Enhanced |
| `411060.KS` | ACE KRX금현물             |

ETF 목록은 `main.py`의 `TICKERS`에서 변경할 수 있습니다.

```python
TICKERS = {
    "379800.KS": "KODEX 미국S&P500",
    ...
}
```

## How It Works

```text
GitHub Actions
      │
      ▼
   main.py
      │
      ├── yfinance에서 ETF 가격 조회
      │
      ├── MA60 / MA120 / MA200 계산
      │
      ├── state.json의 이전 상태 확인
      │
      ├── 현재 UP / DOWN 상태 판단
      │
      └── 상태 변경 발생
                │
                ▼
          Telegram Alert
                │
                ▼
          state.json 갱신
```

## Installation

Repository를 clone합니다.

```bash
git clone https://github.com/pderer/ma_signal.git
cd ma_signal
```

Python dependencies를 설치합니다.

```bash
pip install -r requirements.txt
```

## Telegram Setup

실행을 위해 다음 환경 변수가 필요합니다.

```text
TELEGRAM_TOKEN
TELEGRAM_CHAT_ID
KONGJI_TELEGRAM_TOKEN
KONGJI_TELEGRAM_CHAT_ID
```

현재 구현은 동일한 신호를 **두 개의 Telegram destination**으로 전송합니다.

로컬에서 실행하려면 환경 변수를 설정합니다.

```bash
export TELEGRAM_TOKEN="your_token"
export TELEGRAM_CHAT_ID="your_chat_id"

export KONGJI_TELEGRAM_TOKEN="your_second_token"
export KONGJI_TELEGRAM_CHAT_ID="your_second_chat_id"
```

그 후 실행합니다.

```bash
python main.py
```

## GitHub Actions

`.github/workflows/cron.yml`을 통해 자동 실행됩니다.

현재 schedule은 다음과 같습니다.

```yaml
schedule:
  - cron: '0 7 * * 1-5'
```

GitHub Actions cron은 UTC 기준이므로 다음 시간에 실행됩니다.

```text
UTC 07:00
KST 16:00
Monday - Friday
```

수동 실행(`workflow_dispatch`)도 지원합니다.

## GitHub Secrets

GitHub Actions를 사용하려면 repository의

**Settings → Secrets and variables → Actions**

에서 다음 Secrets를 추가해야 합니다.

```text
TELEGRAM_TOKEN
TELEGRAM_CHAT_ID
KONGJI_TELEGRAM_TOKEN
KONGJI_TELEGRAM_CHAT_ID
```

## State Management

`state.json`에는 각 ETF와 이동평균선의 현재 상태가 저장됩니다.

예:

```json
{
  "379800.KS_MA60": "DOWN",
  "379800.KS_MA120": "UP",
  "379800.KS_MA200": "UP"
}
```

이를 통해 프로그램이 매번 같은 신호를 보내지 않고 다음과 같은 **상태 전환만 감지**할 수 있습니다.

```text
DOWN → UP
UP   → DOWN
```

GitHub Actions 실행 후 `state.json`에 변화가 있으면 자동으로 commit/push됩니다.

## Tech Stack

* Python
* yfinance
* pandas
* requests
* Telegram Bot API
* GitHub Actions

## Disclaimer

이 프로젝트는 개인적인 투자 지표 모니터링 및 자동화 목적으로 작성되었습니다.

생성되는 신호는 투자 권유 또는 매수·매도 추천이 아니며, 실제 투자 판단에 대한 책임은 사용자에게 있습니다.
