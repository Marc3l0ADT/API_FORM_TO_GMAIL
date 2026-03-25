from flask import Flask, request 
import json 
import base64
from pdfGen import make_pdf
from emails import enviar_correo


app = Flask(__name__)

@app.get('/')
def home():
    return "¡Bienvenido a la API de generación de PDFs y envío de correos!"

@app.post('/generate-pdf')
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
            pdf_base64= make_pdf(data)
        )
        return json.dumps({"message": "PDF generado y correo enviado exitosamente."}), 200
    
    except Exception as e:

        print("Error (web_py):", str(e))
        return json.dumps({"error": str(e)}), 500


if __name__ == '__main__':
    app.run()