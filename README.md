# 📋 LINE 收發文提醒機器人

每天 **16:00**（台灣時間）自動在 LINE 群組發送收發文提醒。
- ✅ 週末自動跳過
- ✅ 台灣國定假日自動跳過
- ✅ 免費，使用 GitHub Actions 執行

---

## 部署步驟

### Step 1 — 申請 LINE Bot

1. 前往 [LINE Developers](https://developers.line.biz/)，登入後建立 Provider
2. 建立 **Messaging API Channel**
3. 在 Channel 頁面取得 **Channel Access Token**（長期）
4. 將機器人加入目標群組

### Step 2 — 取得群組 Group ID

1. 前往 [Webhook.site](https://webhook.site)，複製頁面上的 URL
2. 到 LINE Developers → Messaging API → Webhook URL，貼上並啟用
3. 在群組中對機器人說任何一句話
4. 回到 Webhook.site，在 JSON 中找到 `groupId` 欄位，複製備用

### Step 3 — 上傳到 GitHub

1. 申請 [GitHub](https://github.com) 帳號
2. 建立新的 **Private Repository**，命名為 `line-remind-bot`
3. 將本專案所有檔案上傳至 Repo

### Step 4 — 設定 Secrets

進入 Repo → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

新增以下兩筆：

| Secret 名稱      | 值                          |
|------------------|-----------------------------|
| `LINE_TOKEN`     | LINE Channel Access Token   |
| `LINE_GROUP_ID`  | 群組的 groupId              |

### Step 5 — 測試

進入 Repo → **Actions** → **每日收發文提醒** → **Run workflow**

確認執行成功後，即會在每個工作日 16:00 自動發送。

---

## 檔案結構

```
line-remind-bot/
├── .github/
│   └── workflows/
│       └── remind.yml   ← GitHub Actions 排程設定
├── remind.py            ← 主程式（推播 + 假日判斷）
├── requirements.txt     ← Python 套件清單
└── README.md            ← 本說明文件
```

---

## 常見問題

**Q：發送時間可以改嗎？**
A：修改 `remind.yml` 中的 `cron: '0 8 * * 1-5'`，注意時間為 UTC（台灣時間 -8 小時）。

**Q：想改提醒訊息內容？**
A：修改 `remind.py` 中的 `message` 變數。

**Q：想推播到多個群組？**
A：在 `remind.py` 中將 `LINE_GROUP_ID` 改為清單並迴圈發送即可。
