from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from pypdf import PdfWriter, PdfReader
import csv, json
from io import BytesIO 
import base64

def iterador_de_csv(n):
    for i in range(1,n):    
        with open(f'tablas/cords{i}.csv','r', newline='',encoding='utf-8') as f:
            reader = csv.reader(f)
            yield list(reader) 


def make_pdf(resultados_encuesta: dict) -> BytesIO:
    # Paso 1: Crear PDF base con reportlab
    pdf_buffer = BytesIO()
    pdf = canvas.Canvas(pdf_buffer, pagesize=A4, bottomup=1)
    width, height = A4

    for i, cordenadas in enumerate(iterador_de_csv(n = 3)):
        pdf.drawImage(f'Images/imagen{i+1}.jpg', 0, 0, width=width, height=height)
        pdf.showPage() 
    
    pdf.save()
    pdf_buffer.seek(0)

    # Paso 2: Añadir campos editables con PyPDF2
    pdf_buffer.seek(0)
    reader = PdfReader(pdf_buffer)
    writer = PdfWriter()

    page_num = 0
    for i, cordenadas in enumerate(iterador_de_csv(n = 3)):
        page = reader.pages[i]
        
        for respuesta, pregunta, x_float, y_float, limite in cordenadas:
            tipo = 'texto' if respuesta == '' else 'opcion'

            if resultados_encuesta.get(pregunta, None) == None:                
                continue
            elif tipo == 'opcion' and resultados_encuesta[pregunta]['answer'] != respuesta:
                continue

            y = corregidor(float(y_float) * height, height)
            x = int(float(x_float) * width)

            if tipo == 'texto':
                default_value = resultados_encuesta[pregunta]['answer']
                max_length = int(limite) if limite != 'no' else 0
                
                # Crear campo de texto editable
                writer.add_form_field(
                    page,
                    "text",
                    name=f"campo_{pregunta}_{i}",
                    value=default_value,
                    flags=0,
                    max_length=max_length if max_length > 0 else None,
                    coordinates=(x, y - 20, x + 200, y) 
                )

            elif tipo == 'opcion':
                # Crear checkbox editable
                writer.add_form_field(
                    page,
                    "checkbox",
                    name=f"opcion_{pregunta}_{i}",
                    value="Off",
                    flags=0,
                    coordinates=(x - 5, y - 15, x + 15, y + 5)
                )
        
        writer.add_page(page)

    # Paso 3: Guardar y codificar
    output_buffer = BytesIO()
    writer.write(output_buffer)
    output_buffer.seek(0)
    
    base_64_pdf = base64.b64encode(output_buffer.getvalue()).decode('utf-8')
    return base_64_pdf
             
def corregidor(c, h):
    return (c * -1) % h