"""BEETLE ALARM: watches your Beetle cooldowns through the official RemiliaNET API
and pings you on Telegram when an action is available again. It never catches or claims anything itself.

python bot.py          - run the bot
python bot.py --dump   - print raw API responses (to check field names)
"""
import json, sys, time

import requests

ISSUER = "https://www.remilia.net/oidc/realms/remilia"
TOKEN_URL = ISSUER + "/protocol/openid-connect/token"
API = "https://www.remilia.net/api/v1"

LABELS = {
    "catchBeetle": "catch a beetle 🪲",
    "beetleHunt": "go hunting 🔍",
    "claimUBC": "claim UBC 💰",
    "junkFaucet": "spin the faucet 🧀",
}

with open("config.json", encoding="utf-8") as f:
    cfg = json.load(f)


def load_tokens():
    with open("tokens.json", encoding="utf-8") as f:
        return json.load(f)


def save_tokens(t):
    with open("tokens.json", "w", encoding="utf-8") as f:
        json.dump(t, f, indent=2)


def refresh(t):
    r = requests.post(TOKEN_URL, data={
        "grant_type": "refresh_token",
        "refresh_token": t["refresh_token"],
        "client_id": cfg["client_id"],
    }, timeout=30)
    if r.status_code != 200:
        tg("♡ your RemiliaNET session expired, run python login.py and come back ♡")
        raise SystemExit(f"Token refresh failed: {r.status_code} {r.text}")
    new = r.json()
    new["obtained_at"] = time.time()
    save_tokens(new)  # refresh tokens may rotate, always keep the newest one
    return new


def access_token(force=False):
    t = load_tokens()
    if force or time.time() > t["obtained_at"] + t.get("expires_in", 300) - 60:
        t = refresh(t)
    return t["access_token"]


def api(path):
    for attempt in (0, 1):
        r = requests.get(API + path, timeout=30,
                         headers={"Authorization": "Bearer " + access_token(force=attempt == 1)})
        if r.status_code == 401 and attempt == 0:
            continue
        r.raise_for_status()
        body = r.json()
        return body.get("data", body) if isinstance(body, dict) else body


def tg(text):
    try:
        requests.post(f"https://api.telegram.org/bot{cfg['telegram_bot_token']}/sendMessage",
                      json={"chat_id": cfg["telegram_chat_id"], "text": text}, timeout=30)
    except requests.RequestException as e:
        print("Telegram unreachable:", e)


def main():
    if "--dump" in sys.argv:
        for path in ("/me/beetle", "/me/beetle/cooldowns"):
            print(path)
            print(json.dumps(api(path), indent=2, ensure_ascii=False))
        return

    prev_ready = None
    print("☆ BEETLE ALARM is running ♡  (Ctrl+C to stop)")
    tg("☆ BEETLE ALARM is online, watching your cooldowns ♡")
    while True:
        try:
            cds = api("/me/beetle/cooldowns") or {}
        except requests.RequestException as e:
            print("API error:", e)
            time.sleep(60)
            continue

        ready = {k for k in LABELS if not cds.get(k)}  # missing or 0 = available
        new = ready if prev_ready is None else ready - prev_ready
        if new:
            tg("☆ it's time! ☆\n" + "\n".join("· " + LABELS[k] for k in LABELS if k in new)
               + "\n\nhttps://www.remilia.net ♡")
        prev_ready = ready

        waits = [cds[k] / 1000 for k in LABELS if cds.get(k)]
        time.sleep(max(15, min([60] + [w + 2 for w in waits])))


if __name__ == "__main__":
    main()
