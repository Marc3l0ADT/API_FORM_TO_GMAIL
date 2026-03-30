from click import prompt
from flask import Flask, request, jsonify
import os, dotenv,requests
from create_accesT import accessTokenGen, invalid_grant
from pdfGen import make_pdf
from emails import enviar_correo
import create_accesT
from urllib.parse import urlencode
dotenv.load_dotenv()

SCOPES_GMAIL = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
]
AUTHORIZE_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"

def recuperar_refresh():
    
    params = {"client_id": os.getenv("CLIENT_ID"),
    "redirect_uri": f'http://localhost:{os.getenv("PORT")}/oauth/callback',
    "response_type": "code",
    "scope": " ".join(SCOPES_GMAIL),
    "access_type": "offline",
    "prompt": "consent"}
    
    print("Refresh token caducado: Visita la siguiene pagina para restaurarlo:")
    print(f"{AUTHORIZE_URL}?{urlencode(params)}")

try:
    gmailTokenGen = accessTokenGen(os.getenv("EMAIL_REFRESH_TOKEN"))
except invalid_grant:
    recuperar_refresh()



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
                pdf_path_input="pdfBase.pdf",
                valores=data,
                map_options_path="json_map_options.json"),
            gmailTokenGen= gmailTokenGen)
        return jsonify(
            {"message": "PDF generado y correo enviado exitosamente."}
        ), 200

    except create_accesT.invalid_grant:
        recuperar_refresh()
        return jsonify({"error": "El token de acceso ha caducado. Se ha generado un nuevo token de acceso. Por favor, intenta nuevamente."}), 401

@app.get("/oauth/callback")
def oauth_callback():
    global gmailTokenGen

    code = request.args.get("code")
    if not code:
        return jsonify({"error": "No se proporciono codigo de autorizacion"}), 400

    token_url = "https://oauth2.googleapis.com/token"
    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("SECRET")
    PORT = int(os.getenv("PORT"))
    
    
    data = {
        "code": code,
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": f'http://localhost:{PORT}/oauth/callback',
        "grant_type": "authorization_code",
    }
    
    response = requests.post(token_url, data=data)
    token_data = response.json()
    print(token_data)

    if "error" in token_data.keys():
        return jsonify({"error": "Error al intercambiar el codigo por tokens", "details": token_data}), 400
    
    gmailTokenGen = accessTokenGen(refresh_token=token_data.get("refresh_token"))

    return jsonify(token_data), 200


if __name__ == "__main__":
    dotenv.load_dotenv()
    puerto = int(os.getenv("PORT"))
    app.run(port=puerto)
