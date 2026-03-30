#!/usr/bin/env python3
"""
Script para autenticar con Google OAuth 2.0
Requiere: pip install requests python-dotenv
"""

import os
import requests
import webbrowser
from urllib.parse import urlencode
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
from dotenv import load_dotenv
import time

# Cargar .env
load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI", 
                         "http://localhost:8080")

AUTHORIZE_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"


auth_code = None
server = None

class CallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global auth_code
        if "code=" in self.path:
            auth_code = self.path.split("code=")[1].split("&")[0]
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            html = """<html><body style='text-align:center;padding:50px'>
            <h1 style='color:#4285f4'>✓ ¡Autorizado!</h1>
            <p>Puedes cerrar esta ventana.</p>
            </body></html>"""
            self.wfile.write(html.encode())
    def log_message(self, *args): pass

def start_server():
    global server
    server = HTTPServer(("localhost", 8080), 
                       CallbackHandler)
    Thread(target=server.serve_forever, 
           daemon=True).start()

def exchange_code(code):
    payload = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": REDIRECT_URI,
    }
    r = requests.post(TOKEN_URL, data=payload)
    return r.json() if r.status_code == 200 else None

def get_consent_url():
    params = {
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": " ".join(SCOPES),
        "access_type": "offline",
    }
    return f"{AUTHORIZE_URL}?{urlencode(params)}"

def save_env(tokens):
    with open(".env", "r") as f:
        content = f.read()
    
    token = tokens.get("refresh_token")
    if "REFRESH_TOKEN=" in content:
        content = "\n".join(
            f'REFRESH_TOKEN="{token}"' 
            if l.startswith("REFRESH_TOKEN=") else l
            for l in content.split("\n")
        )
    else:
        content += f'\nREFRESH_TOKEN="{token}"\n'
    
    with open(".env", "w") as f:
        f.write(content)
    print(f"✓ Guardado en .env")

def main():
    print("=" * 60)
    print("GOOGLE OAUTH 2.0")
    print("=" * 60)
    
    if not CLIENT_ID or not CLIENT_SECRET:
        print("❌ Falta CLIENT_ID o CLIENT_SECRET en .env")
        return
    
    url = get_consent_url()
    print(f"\n📍 REDIRECT_URI: {REDIRECT_URI}")
    print(f"\nURL de consentimiento:")
    print(url)
    print("\n▶ Abriendo navegador...")
    
    start_server()
    webbrowser.open(url)
    
    timeout = 0
    while auth_code is None and timeout < 120:
        time.sleep(1)
        timeout += 1
    
    if not auth_code:
        print("❌ Timeout")
        return
    
    print(f"✓ Código: {auth_code[:20]}...")
    
    if server:
        server.shutdown()
    
    print("\n▶ Obteniendo tokens...")
    tokens = exchange_code(auth_code)
    
    if not tokens:
        print("❌ Error")
        return
    
    print(f"\n📌 ACCESS_TOKEN: {tokens.get('access_token')[:30]}...")
    print(f"📌 REFRESH_TOKEN: {tokens.get('refresh_token')}")
    
    save_env(tokens)
    print("\n✓ ¡Listo!")

if __name__ == "__main__":
    main()