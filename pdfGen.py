"""
editar_campos_pdf.py
====================
Script para listar y rellenar los campos AcroForm (campos rellenables)
de un archivo PDF usando pypdf.
"""
import sys
import json
import argparse
from pathlib import Path
from pypdf import PdfReader, PdfWriter
from io import BytesIO 
import base64

with open("json_map_options.json", "r") as f:
    map_to_options: dict[str:dict[str:int]] = json.load(f)

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
        print(f"{name:<35} {tipo:<15} {valor}")

    print(f"{'─'*60}")
    print(f"Total: {len(fields)} campo(s)\n")


def make_pdf(pdf_path_input: str, valores: dict) -> bytes:

    """
    Rellena los campos del PDF con los valores proporcionados y
    guarda el resultado en output_path.

    Parámetros
    ----------
    valores : dict
        { "nombre_de_la_pregunta": { "answer": "valor", "type": "texto | opcion" } }
    """

    reader = PdfReader(pdf_path_input)
    writer = PdfWriter()
    writer.append(reader)

    # Construir dict compatible con pypdf:
    # checkboxes → "/Yes" o "/Off", texto → string normal
    fields = reader.get_fields() or {}
    actualizaciones = {}
    map_valor_campo: dict[str, str] = {field.get("/V", "(vacío)"):name for name, field in fields.items()}
    for pregunta, info in valores.items():
        valor = info.get("answer", "")
        tipo = info.get("type", "no existe")

        if tipo == "no existe":
            print(f"'tipo' de la pregunta '{pregunta}' no existe.")
            continue
        
        
        if tipo == "texto":
            campo_name = map_valor_campo.get(pregunta)
            actualizaciones[campo_name] = str(valor)

        elif tipo == "opcion":
            continue
            campo = get_campo_opcion(pregunta, valor)
            actualizaciones[campo] = '/Sí'
        else:
            raise Exception(f"Tipo de campo no reconocido: {tipo}")

    if not actualizaciones:
        print("  ⚠  No hay campos válidos para actualizar.")
        return

    # Para PDFs con campos en varias páginas, actualizar todas
    for page in writer.pages:
        try:
            writer.update_page_form_field_values(
                page, actualizaciones, auto_regenerate=False
            )
        except Exception:
            pass
    print(f"   Campos actualizados: {list(actualizaciones.keys())}\n")


# ══════════════════════════════════════════════
# UTILIDADES
# ══════════════════════════════════════════════

def get_campo_opcion(pregunta: str, valor: str) -> str:
    
    pass

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
    return "/Yes"



def main():
    


    pass
if __name__ == "__main__":
    listar_campos(sys.argv[1])