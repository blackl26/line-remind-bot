from flask import Flask, request, jsonify
import os, json, requests, hmac, hashlib, base64

app = Flask(__name__)

CHANNEL_SECRET = os.environ.get("LINE_CHANNEL_SECRET", "")
GITHUB_TOKEN   = os.environ.get("GITHUB_TOKEN", "")
GIST_ID        = os.environ.get("GIST_ID", "")
GIST_FILE      = "groups.json"

def verify(body, sig):
    try:
        h = hmac.new(CHANNEL_SECRET.encode("utf-8"), body, hashlib.sha256).digest()
        expected = base64.b64encode(h).decode("utf-8")
        return hmac.compare_digest(expected, sig)
    except Exception as e:
        print(f"[驗證錯誤] {e}")
        return False

def get_groups():
    try:
        r = requests.get(
            f"https://api.github.com/gists/{GIST_ID}",
            headers={"Authorization": f"token {GITHUB_TOKEN}"}
        )
        return json.loads(r.json()["files"][GIST_FILE]["content"])
    except:
        return []

def save_groups(groups):
    try:
        requests.patch(
            f"https://api.github.com/gists/{GIST_ID}",
            headers={"Authorization": f"token {GITHUB_TOKEN}"},
            json={"files": {GIST_FILE: {"content": json.dumps(groups, indent=2)}}}
        )
    except Exception as e:
        print(f"[儲存錯誤] {e}")

@app.route("/webhook", methods=["POST"])
def webhook():
    sig  = request.headers.get("X-Line-Signature", "")
    body = request.get_data()

    if not verify(body, sig):
        print(f"[簽章失敗] sig={sig}")
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

@app.route("/", methods=["GET"])
def health():
    return jsonify({"status": "running", "gist_id": GIST_ID[:8] + "..."})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
