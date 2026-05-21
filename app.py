from flask import Flask, request, jsonify
import os, json, requests, hmac, hashlib, base64

app = Flask(__name__)

CHANNEL_SECRET = os.environ["LINE_CHANNEL_SECRET"]
GITHUB_TOKEN   = os.environ["GITHUB_TOKEN"]
GIST_ID        = os.environ["GIST_ID"]
GIST_FILE      = "groups.json"

# ── 驗證 LINE 簽章 ──────────────────────────────────────
def verify(body, sig):
    h = hmac.new(CHANNEL_SECRET.encode(), body, hashlib.sha256).digest()
    return hmac.compare_digest(base64.b64encode(h).decode(), sig)

# ── 讀取群組清單 ────────────────────────────────────────
def get_groups():
    r = requests.get(
        f"https://api.github.com/gists/{GIST_ID}",
        headers={"Authorization": f"token {GITHUB_TOKEN}"}
    )
    return json.loads(r.json()["files"][GIST_FILE]["content"])

# ── 儲存群組清單 ────────────────────────────────────────
def save_groups(groups):
    requests.patch(
        f"https://api.github.com/gists/{GIST_ID}",
        headers={"Authorization": f"token {GITHUB_TOKEN}"},
        json={"files": {GIST_FILE: {"content": json.dumps(groups, indent=2)}}}
    )

# ── Webhook 端點 ────────────────────────────────────────
@app.route("/webhook", methods=["POST"])
def webhook():
    sig  = request.headers.get("X-Line-Signature", "")
    body = request.get_data()

    if not verify(body, sig):
        return jsonify({"error": "Invalid signature"}), 403

    for event in request.json.get("events", []):
        source   = event.get("source", {})
        etype    = event.get("type")
        group_id = source.get("groupId")

        if source.get("type") != "group" or not group_id:
            continue

        groups = get_groups()

        if etype == "join" and group_id not in groups:
            groups.append(group_id)
            save_groups(groups)
            print(f"[加入] {group_id}")

        elif etype == "leave" and group_id in groups:
            groups.remove(group_id)
            save_groups(groups)
            print(f"[離開] {group_id}")

    return jsonify({"status": "ok"})

# ── 健康檢查 ────────────────────────────────────────────
@app.route("/", methods=["GET"])
def health():
    return jsonify({"status": "running"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
