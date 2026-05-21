import os
import requests
import holidays
from datetime import date

# ── 從 GitHub Secrets 讀取 ──────────────────────────────
LINE_TOKEN    = os.environ["LINE_TOKEN"]
LINE_GROUP_ID = os.environ["LINE_GROUP_ID"]

# ── 今天日期 ────────────────────────────────────────────
today = date.today()

# ── 1. 判斷週末 ─────────────────────────────────────────
if today.weekday() >= 5:
    print(f"[跳過] {today} 是週末，不發送提醒。")
    exit(0)

# ── 2. 判斷台灣國定假日 ─────────────────────────────────
tw_holidays = holidays.Taiwan(years=today.year)
if today in tw_holidays:
    holiday_name = tw_holidays.get(today)
    print(f"[跳過] {today} 是國定假日（{holiday_name}），不發送提醒。")
    exit(0)

# ── 3. 發送 LINE 推播 ───────────────────────────────────
message = "📋 請記得處理收發文！"

headers = {
    "Authorization": f"Bearer {LINE_TOKEN}",
    "Content-Type": "application/json"
}

payload = {
    "to": LINE_GROUP_ID,
    "messages": [
        {
            "type": "text",
            "text": message
        }
    ]
}

response = requests.post(
    "https://api.line.me/v2/bot/message/push",
    headers=headers,
    json=payload
)

if response.status_code == 200:
    print(f"[成功] {today} 提醒已發送至群組。")
else:
    print(f"[失敗] 狀態碼：{response.status_code}，回應：{response.text}")
    exit(1)
