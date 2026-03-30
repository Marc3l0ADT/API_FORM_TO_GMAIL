from flask import Flask, request, jsonify
import json
import base64
import os, dotenv
import requests
from pdfGen import make_pdf
from emails import enviar_correo
import create_accesT
from urllib.parse import urlencode

SCOPES_GMAIL = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
]
AUTHORIZE_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
app = Flask("Generador de PDFs y Envío de Correos")


@app.get("/")
def home():
    return "¡Bienvenido a la API de generación de PDFs y envío de correos!"


@app.post("/pdf/make")  
def generate_pdf():
    payload = request.get_json()
    print("payload recibido:", payload)
    email = payload.get("email")
    data = payload.get("data")

    try:
        enviar_correo(
            asunto="Resultados de la Encuesta",
            direccion_destino=email,
            body_text="Hola,\n\nAdjunto encontrarás el PDF con los resultados de la encuesta.\n\nSaludos.",
            pdf_base64=make_pdf(
                pdf_path_input="formulario.pdf",
                valores=data,
                map_options_path="json_map_options.json",
            ),
        )
        return json.dumps(
            {"message": "PDF generado y correo enviado exitosamente."}
        ), 200

    except create_accesT.invalid_grant:
        dotenv.load_dotenv()
        params = {"client_id": os.getenv("CLIENT_ID"),
        "redirect_uri": f'localhost:{os.getenv("PORT")}/oauth/callback',
        "response_type": "code",
        "scope": " ".join(SCOPES_GMAIL),
        "access_type": "offline"}
        print("Refresh token caducado: Visita la siguiene pagina para restaurarlo:")
        print(f"{AUTHORIZE_URL}?{urlencode(params)}")


@app.get("/oauth/callback")
def oauth_callback():
    code = request.args.get("code")
    if not code:
        return jsonify({"error": "No se proporciono codigo de autorizacion"}), 400

    token_url = "https://oauth2.googleapis.com/token"
    client_id = os.getenv("")
    client_secret = os.getenv("SECRET")
    PORT = int(os.getenv("PORT"))

    data = {
        "code": code,
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": f'localhost:{PORT}',
        "grant_type": "authorization_code",
    }

    response = requests.post(token_url, data=data)
    token_data = response.json()

    

    return jsonify(token_data), 200


if __name__ == "__main__":
    dotenv.load_dotenv()
    puerto = int(os.getenv("PORT"))
    app.run(port=puerto)
