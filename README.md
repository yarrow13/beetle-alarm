<div align="center">

# ☆ BEETLE ALARM ♡

*a tiny bot that whispers to you on Telegram when you can catch beetles on [RemiliaNET](https://www.remilia.net) again*

🪲 · 🔍 · 💰 · 🧀

</div>

---

## ✶ what it does

Once a minute the bot checks your Beetle cooldowns through the **official RemiliaNET API** and pings you on Telegram when you can:

| | action |
|---|---|
| 🪲 | catch a beetle |
| 🔍 | go hunting |
| 💰 | claim UBC |
| 🧀 | spin the faucet |

```
☆ it's time! ☆
· catch a beetle 🪲
· spin the faucet 🧀

https://www.remilia.net ♡
```

> **you do the catching yourself, by hand, on the site.** the bot only reminds you. it never clicks, catches or claims anything.
> it only uses what the [RemiliaNET docs](https://docs.remilia.net/) allow, so your account stays safe ♡

---

## ✶ setup

### 1 · Telegram bot

1. message [@BotFather](https://t.me/BotFather) → `/newbot` → save the token
2. send your new bot any message
3. open `https://api.telegram.org/bot<TOKEN>/getUpdates` and find `"chat":{"id": ...}` — that's your `chat_id`

### 2 · RemiliaNET app

1. [remilia.net](https://www.remilia.net) → profile menu → **Developer portal**
2. create an app of type **Login (public)**
3. redirect URI, exactly: `http://127.0.0.1:3000/callback`
4. scope: `remilia:beetle.read`
5. wait for approval and copy the **client ID**

### 3 · run it

```bash
pip install -r requirements.txt
cp config.example.json config.json   # fill in client_id, bot token and chat_id
python login.py                      # once: log in through your browser
python bot.py --dump                 # check that the API answers
python bot.py                        # ☆ let's go ☆
```

---

## ✶ good to know

- your computer needs to stay on while the bot runs
- if your session expires, the bot tells you on Telegram — just run `python login.py` again
- `config.json` and `tokens.json` are your secrets. they're already in `.gitignore`, never share them
- if `--dump` shows different cooldown field names, edit the `LABELS` dict in `bot.py`

---

<div align="center">

☆ made with love by Remilia Russia ✶ CIS · [@MiladyRussia](https://x.com/MiladyRussia) ♡

<sub>fan project, not an official Remilia product</sub>

</div>
