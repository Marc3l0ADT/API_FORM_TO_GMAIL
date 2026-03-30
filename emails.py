import base64
import requests
import os
from datetime import datetime
from dotenv import load_dotenv
from create_accesT import accessTokenGen

load_dotenv()

# ==============================
# CONFIGURACIÓN
# ==============================

REFRESH_TOKEN = os.getenv("REFRESH_TOKEN")  # Obtener un nuevo access token usando el refresh token
FROM_EMAIL = os.getenv("CORREO")
TO_EMAIL = os.getenv("CORREO_DESTINO")

# ==============================
# LEER Y CODIFICAR IMAGEN
# ==============================


def enviar_correo(asunto, direccion_destino, body_text, pdf_base64, gmailTokenGen: accessTokenGen = None):
    # ==============================
    # CREAR MIME MANUALMENTE
    # ==============================

    boundary = "boundary_" + datetime.now().strftime("%Y%m%d%H%M%S")

    mime_message = f"""From: {FROM_EMAIL}
To: {direccion_destino}
Subject: {asunto}
MIME-Version: 1.0
Content-Type: multipart/mixed; boundary="{boundary}"

--{boundary}
Content-Type: text/plain; charset="UTF-8"
Content-Transfer-Encoding: 7bit

{body_text} 

--{boundary}
Content-Type: application/pdf; name="documento.pdf"
Content-Transfer-Encoding: base64
Content-Disposition: attachment; filename="documento.pdf"

{pdf_base64}

--{boundary}--
"""
    print(mime_message[0:700])
    print("========")
    # ==============================
    # CODIFICAR TODO EN BASE64URL
    # ==============================

    message_bytes = mime_message.encode("utf-8")
    encoded_message = base64.urlsafe_b64encode(message_bytes).decode("utf-8")

    # ==============================
    # ENVIAR A GMAIL API
    # ==============================

    url = "https://gmail.googleapis.com/gmail/v1/users/me/messages/send"

    headers = {
        "Authorization": f"Bearer {gmailTokenGen.get_access()}",
        "Content-Type": "application/json"
        }

    body = {
        "raw": encoded_message
    }

    response = requests.post(url, headers=headers, json=body)

    print('==========EMAIL==========')

    print("Status Code:", response.status_code)
    print("Response:", response.text)

    print('==========END EMAIL==========')
    
if __name__ == "__main__":
    # Ejemplo de uso
    import pdfGen
    import json
    
    with open('json.json', 'r') as f:
        resultados = json.load(f)["data"]
    
    pdf_base64 = pdfGen.make_pdf('pdfBase.pdf', resultados, 'json_map_options.json')

    
    enviar_correo(
        asunto="Resultados de la Encuesta",
        direccion_destino='moreiraibarramarcelo@gmail.com',
        body_text="Hola,\n\nAdjunto encontrarás el PDF con los resultados de la encuesta.\n\nSaludos.",
        pdf_base64= pdf_base64.decode('utf-8')
    )

    with open('output.pdf', 'wb') as f:
        f.write(base64.b64decode(pdf_base64))