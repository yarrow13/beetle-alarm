"""One-time RemiliaNET login (Authorization Code + PKCE).

Run: python login.py -> your browser opens, sign in, tokens are saved to tokens.json
"""
import base64, hashlib, json, secrets, time, urllib.parse, webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer

import requests

ISSUER = "https://www.remilia.net/oidc/realms/remilia"
AUTH_URL = ISSUER + "/protocol/openid-connect/auth"
TOKEN_URL = ISSUER + "/protocol/openid-connect/token"
REDIRECT_URI = "http://127.0.0.1:3000/callback"  # register exactly this in the developer portal

with open("config.json", encoding="utf-8") as f:
    cfg = json.load(f)

verifier = secrets.token_urlsafe(64)
challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()
state = secrets.token_urlsafe(16)
nonce = secrets.token_urlsafe(16)

url = AUTH_URL + "?" + urllib.parse.urlencode({
    "client_id": cfg["client_id"],
    "redirect_uri": REDIRECT_URI,
    "response_type": "code",
    "scope": "openid",
    "state": state,
    "nonce": nonce,
    "code_challenge": challenge,
    "code_challenge_method": "S256",
})

result = {}


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path != "/callback":
            self.send_response(404)
            self.end_headers()
            return
        result.update({k: v[0] for k, v in urllib.parse.parse_qs(parsed.query).items()})
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write("☆ all done, you can close this tab ♡".encode("utf-8"))

    def log_message(self, *args):
        pass


server = HTTPServer(("127.0.0.1", 3000), Handler)
print("Opening your browser. If it doesn't open, go to:\n" + url)
webbrowser.open(url)
while not result:
    server.handle_request()

if "error" in result:
    raise SystemExit(f"Login failed: {result['error']} {result.get('error_description', '')}")
if result.get("state") != state:
    raise SystemExit("State mismatch, please try again")

r = requests.post(TOKEN_URL, data={
    "grant_type": "authorization_code",
    "code": result["code"],
    "redirect_uri": REDIRECT_URI,
    "client_id": cfg["client_id"],
    "code_verifier": verifier,
}, timeout=30)
if r.status_code != 200:
    raise SystemExit(f"Code exchange failed: {r.status_code} {r.text}")

tokens = r.json()
tokens["obtained_at"] = time.time()
with open("tokens.json", "w", encoding="utf-8") as f:
    json.dump(tokens, f, indent=2)
print("☆ logged in ♡  granted scopes:", tokens.get("scope"))
if "remilia:beetle.read" not in (tokens.get("scope") or ""):
    print("Heads up: remilia:beetle.read is missing. Add it to your client in the developer portal and log in again.")
