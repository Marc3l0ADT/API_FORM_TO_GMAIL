"""
editar_campos_pdf.py
====================
Script para listar y rellenar los campos AcroForm (campos rellenables)
de un archivo PDF usando pypdf.
"""
import sys
import json
from pathlib import Path
from pypdf import PdfReader, PdfWriter
from io import BytesIO 
import base64



def listar_campos(pdf_path_input: str) -> None:
    """Imprime todos los campos rellenables del PDF con su tipo y valor actual."""
    reader = PdfReader(pdf_path_input)

    if "/AcroForm" not in reader.trailer.get("/Root", {}):
        print(f"\n⚠  El archivo '{pdf_path_input}' NO tiene campos AcroForm rellenables.")
        return

    fields = reader.get_fields()
    if not fields:
        print(f"\n⚠  No se encontraron campos en '{pdf_path_input}'.")
        return

    print(f"\n📄  Campos encontrados en: {pdf_path_input}")
    print(f"{'─'*60}")
    print(f"{'Nombre del campo':<35} {'Tipo':<15} {'Valor actual'}")
    print(f"{'─'*60}")

    for name, field in fields.items():
        tipo   = _tipo_campo(field)
        valor  = field.get("/V", "(vacío)")
        print(f"{name:<35} {tipo:<15} {valor}") if tipo == "checkbox" else print(end="")

    print(f"{'─'*60}")
    print(f"Total: {len(fields)} campo(s)\n")


def make_pdf(pdf_path_input: str, valores: dict, map_options_path: str) -> bytes:

    """
    Rellena los campos del PDF con los valores proporcionados y
    guarda el resultado en output_path.

    Parámetros
    ----------
    valores : dict
        { "nombre_de_la_pregunta": { "answer": "valor", "type": "texto | opcion" } }
    map_options_path : str
        Ruta al archivo JSON que contiene el mapeo de todas las preguntas y respuestas posibles a nombres de campos checkbox.
    pdf_path_input : str
        Ruta al PDF de entrada con campos AcroForm. Nota: Los campos de texto deben tener como valor
        predeterminado el nombre de sus preguntas y todos los checkboxes con el visto.
    """

    reader = PdfReader(pdf_path_input)
    writer = PdfWriter()
    writer.append(reader)

    # Construir dict compatible con pypdf:
    # checkboxes → "/Yes" o "/Off", texto → string normal

    fields = reader.get_fields() or {}
    actualizaciones = {name: '' if _tipo_campo(field) == "texto" else '' for name, field in fields.items()}
    map_valor_campo: dict[str, str] = {field.get("/V", "(vacío)"):name for name, field in fields.items() if _tipo_campo(field) == "texto"}

    for pregunta, info in valores.items():
        
        valor = info.get("answer", "")
        tipo = info.get("type", "no existe")

        if tipo == "no existe":
            continue
        
        
        if tipo == "texto" or tipo == "DATE":
            campo_name = map_valor_campo.get(pregunta)
            actualizaciones[campo_name] = str(valor)
        elif tipo == "opcion":
            
            campo_name = get_campo_opcion(pregunta, valor, map_options_path)
            actualizaciones[campo_name] = _checked_value(fields[campo_name])
        else:
            raise Exception(f"Tipo de campo no reconocido: {tipo}")

    if not actualizaciones:
        raise Exception("No hay campos válidos para actualizar.")

    # Para PDFs con campos en varias páginas, actualizar todas
    for page in writer.pages:
        try:
            writer.update_page_form_field_values(
                page, actualizaciones, auto_regenerate=False
            )
        except Exception:
            pass
    buffer = BytesIO()
    writer.write(buffer)
    pdf_base64 = base64.b64encode(buffer.getvalue())
    return pdf_base64
# ══════════════════════════════════════════════
# UTILIDADES
# ══════════════════════════════════════════════

def get_campo_opcion(pregunta: str, valor: str, json_map_options_path: str) -> str:
    """
    Devuelve el nombre del campo correspondiente a la pregunta y la respuesta dada por el usuario, usando el mapeo definido en map_to_options.
    Si no se encuentra una coincidencia, devuelve None.
    
    Args:
        pregunta (str): El nombre de la pregunta que se definio en el formulario.
        valor (str): Una de las respuestas posibles que el usuario decidio responder.
        json_map_options_path (str): La ruta al archivo JSON que contiene el mapeo de preguntas, respuestas y campos checkbox.

    Returns:
        tipo: Un string que contiene el nombre del campo "checkbox" relacionado a la pregunta y respuesta dada.

    Raises:
        NoneFieldCheckbox: No se encontro ningun campo que corresponda a la pregunta y respuesta dadas.
    """
    with open(json_map_options_path, 'r') as f:
        json_map_to_options = json.load(f)
    opciones = json_map_to_options.get(pregunta)
    NoneFieldCheckbox = Exception(f"No se encontró un campo checkbox para la pregunta '{pregunta}' con la respuesta '{valor}' en el mapeo.")
    if not opciones:
        raise NoneFieldCheckbox
    
    campo = opciones.get(valor)
    if not campo:
        raise NoneFieldCheckbox
    
    return campo

def _tipo_campo(field) -> str:
    """Devuelve el tipo legible del campo PDF."""
    ft = field.get("/FT", "")
    if ft == "/Tx":
        return "texto"
    if ft == "/Btn":
        ff = field.get("/Ff", 0)
        if isinstance(ff, int) and (ff >> 16) & 1:
            return "radio"
        return "checkbox"
    if ft == "/Ch":
        return "lista/combo"
    if ft == "/Sig":
        return "firma"
    return str(ft) if ft else "desconocido"


def _checked_value(field) -> str:
    """Obtiene el valor 'marcado' de un checkbox (puede ser /Yes, /On, etc.)."""
    ap = field.get("/AP")
    if ap:
        n = ap.get("/N")
        if n:
            keys = list(n.keys()) if hasattr(n, "keys") else []
            for k in keys:
                if k not in ("/Off", "/off"):
                    return k
    return "/Sí"



if __name__ == "__main__":
    listar_campos("C:/Users/Usuario/Downloads/ACOSTA PEREZ MARIA JAZMINA.pdf")
