import os, json, requests, holidays
from datetime import date

LINE_TOKEN    = os.environ["LINE_TOKEN"]
GITHUB_TOKEN  = os.environ["GH_TOKEN"]
GIST_ID       = os.environ["GIST_ID"]
GIST_FILE     = "groups.json"

today = date.today()

# ── 1. 週末跳過 ─────────────────────────────────────────
if today.weekday() >= 5:
    print(f"[跳過] {today} 是週末")
    exit(0)

# ── 2. 國定假日跳過 ─────────────────────────────────────
tw = holidays.Taiwan(years=today.year)
if today in tw:
    print(f"[跳過] {today} 是國定假日（{tw[today]}）")
    exit(0)

# ── 3. 從 Gist 讀取所有群組 ─────────────────────────────
r = requests.get(
    f"https://api.github.com/gists/{GIST_ID}",
    headers={"Authorization": f"token {GITHUB_TOKEN}"}
)
groups = json.loads(r.json()["files"][GIST_FILE]["content"])

if not groups:
    print("[跳過] 目前沒有任何群組")
    exit(0)

# ── 4. 推播到每個群組 ───────────────────────────────────
headers = {
    "Authorization": f"Bearer {LINE_TOKEN}",
    "Content-Type": "application/json"
}

for gid in groups:
    res = requests.post(
        "https://api.line.me/v2/bot/message/push",
        headers=headers,
        json={"to": gid, "messages": [{"type": "text", "text": "📋 請記得處理收發文！"}]}
    )
    status = "✅ 成功" if res.status_code == 200 else f"❌ 失敗（{res.status_code}）"
    print(f"群組 {gid}：{status}")
