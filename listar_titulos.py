import os
import re
import csv
import sys
import json
from datetime import datetime
from pypdf import PdfReader
from tabulate import tabulate

# Directorio de documentos
DOCUMENTOS_DIR = "documentos"
OUTPUT_FILE_CSV = "catalogo_documentos.csv"
OUTPUT_FILE_JSON = "catalogo_documentos.json"

def extraer_metadatos_pdf(ruta_pdf):
    """Extrae metadatos y título del documento PDF"""
    try:
        reader = PdfReader(ruta_pdf)
        
        # Extraer metadatos básicos
        metadatos = reader.metadata
        
        # Información básica
        info = {
            "nombre_archivo": os.path.basename(ruta_pdf),
            "ruta": ruta_pdf,
            "paginas": len(reader.pages),
            "tamaño_kb": round(os.path.getsize(ruta_pdf) / 1024, 2),
            "fecha_modificacion": datetime.fromtimestamp(os.path.getmtime(ruta_pdf)).strftime('%Y-%m-%d'),
        }
        
        # Extraer metadatos estándar si están disponibles
        if metadatos:
            info["titulo"] = metadatos.title if metadatos.title else ""
            info["autor"] = metadatos.author if metadatos.author else ""
            info["creador"] = metadatos.creator if metadatos.creator else ""
            info["productor"] = metadatos.producer if metadatos.producer else ""
            info["fecha_creacion"] = metadatos.creation_date if metadatos.creation_date else ""
            info["fecha_modificacion_pdf"] = metadatos.modification_date if metadatos.modification_date else ""
        
        # Si no hay título en los metadatos, intentar extraerlo del contenido
        if not info.get("titulo") or info["titulo"] == "":
            # Intentar extraer del primer párrafo de la primera página
            primera_pagina = reader.pages[0].extract_text()
            # División en líneas
            lineas = primera_pagina.split('\n')
            
            # Buscar posibles títulos (primeras líneas no vacías, en mayúsculas o con formato destacado)
            posibles_titulos = []
            for linea in lineas[:10]:  # Considerar solo las primeras 10 líneas
                linea = linea.strip()
                if linea and len(linea) > 10:  # Líneas no vacías y con cierta longitud
                    posibles_titulos.append(linea)
            
            if posibles_titulos:
                # Preferir líneas en mayúsculas o que contengan "LEY", "DECRETO", "CÓDIGO", etc.
                for linea in posibles_titulos:
                    if (linea.isupper() or 
                        any(palabra in linea.upper() for palabra in ["LEY", "DECRETO", "CÓDIGO", "REAL DECRETO", "ORDEN"])):
                        info["titulo"] = linea
                        break
                
                # Si no se encontró un título con las condiciones anteriores, usar el primer posible título
                if not info.get("titulo") or info["titulo"] == "":
                    info["titulo"] = posibles_titulos[0]
        
        # Extraer el tipo de documento basado en el nombre o contenido
        tipo_documento = "Desconocido"
        nombre_archivo = info["nombre_archivo"].upper()
        
        if "LEY" in nombre_archivo or "LEY" in info.get("titulo", "").upper():
            tipo_documento = "Ley"
        elif "DECRETO" in nombre_archivo or "DECRETO" in info.get("titulo", "").upper():
            tipo_documento = "Decreto"
        elif "CÓDIGO" in nombre_archivo or "CODIGO" in nombre_archivo:
            tipo_documento = "Código"
        elif "ORDEN" in nombre_archivo or "ORDEN" in info.get("titulo", "").upper():
            tipo_documento = "Orden"
        elif "INSTRUCCIÓN" in nombre_archivo or "INSTRUCCION" in nombre_archivo:
            tipo_documento = "Instrucción"
        elif "GUIA" in nombre_archivo:
            tipo_documento = "Guía"
        elif "BOE" in nombre_archivo:
            tipo_documento = "Boletín Oficial"
        
        info["tipo_documento"] = tipo_documento
        
        # Normalizar el título si está en blanco
        if not info.get("titulo") or info["titulo"] == "":
            # Generar un título basado en el nombre del archivo
            nombre_sin_extension = os.path.splitext(info["nombre_archivo"])[0]
            nombre_formateado = nombre_sin_extension.replace("-", " ").replace("_", " ")
            info["titulo"] = f"{tipo_documento}: {nombre_formateado}"
        
        return info
    
    except Exception as e:
        return {
            "nombre_archivo": os.path.basename(ruta_pdf),
            "ruta": ruta_pdf,
            "error": str(e),
            "titulo": os.path.basename(ruta_pdf),
            "tipo_documento": "Error"
        }

def generar_catalogo():
    """Genera un catálogo de todos los documentos en la carpeta"""
    if not os.path.exists(DOCUMENTOS_DIR):
        print(f"Error: No se encontró la carpeta {DOCUMENTOS_DIR}")
        return []
    
    archivos_pdf = []
    for archivo in os.listdir(DOCUMENTOS_DIR):
        if archivo.lower().endswith('.pdf'):
            ruta_completa = os.path.join(DOCUMENTOS_DIR, archivo)
            archivos_pdf.append(ruta_completa)
    
    catalogo = []
    total = len(archivos_pdf)
    
    print(f"Procesando {total} documentos PDF...")
    
    for i, pdf in enumerate(archivos_pdf, 1):
        print(f"[{i}/{total}] Procesando: {os.path.basename(pdf)}")
        metadatos = extraer_metadatos_pdf(pdf)
        catalogo.append(metadatos)
    
    return catalogo

def guardar_csv(catalogo, ruta_salida=OUTPUT_FILE_CSV):
    """Guarda el catálogo en formato CSV"""
    with open(ruta_salida, 'w', newline='', encoding='utf-8') as f:
        if not catalogo:
            print("No hay documentos para guardar.")
            return
        
        # Recopilar todos los campos posibles de todos los documentos
        campos = set()
        for doc in catalogo:
            campos.update(doc.keys())
        
        campos = list(campos)
        
        writer = csv.DictWriter(f, fieldnames=campos, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(catalogo)
    
    print(f"Catálogo guardado en {ruta_salida}")

def guardar_json(catalogo, ruta_salida=OUTPUT_FILE_JSON):
    """Guarda el catálogo en formato JSON"""
    # Convertir objetos datetime a string
    catalogo_serializable = []
    for doc in catalogo:
        doc_serializable = {}
        for key, value in doc.items():
            if isinstance(value, datetime):
                doc_serializable[key] = value.isoformat()
            else:
                doc_serializable[key] = value
        catalogo_serializable.append(doc_serializable)
    
    with open(ruta_salida, 'w', encoding='utf-8') as f:
        json.dump(catalogo_serializable, f, indent=2, ensure_ascii=False)
    
    print(f"Catálogo guardado en {ruta_salida}")

def mostrar_catalogo(catalogo):
    """Muestra el catálogo en la consola en formato de tabla"""
    if not catalogo:
        print("No hay documentos para mostrar.")
        return
    
    # Crear una versión simplificada para mostrar
    catalogo_simplificado = []
    for doc in catalogo:
        catalogo_simplificado.append({
            "Tipo": doc.get("tipo_documento", ""),
            "Título": doc.get("titulo", "")[:80] + ("..." if len(doc.get("titulo", "")) > 80 else ""),
            "Archivo": doc.get("nombre_archivo", ""),
            "Páginas": doc.get("paginas", ""),
            "Tamaño (KB)": doc.get("tamaño_kb", ""),
            "Fecha Mod.": doc.get("fecha_modificacion", "")
        })
    
    print(tabulate(catalogo_simplificado, headers="keys", tablefmt="grid"))

def main():
    print("Generando catálogo de documentos legales...")
    catalogo = generar_catalogo()
    
    if not catalogo:
        print("No se encontraron documentos PDF.")
        return
    
    print(f"\nSe encontraron {len(catalogo)} documentos.")
    
    # Guardar catálogo
    guardar_csv(catalogo)
    guardar_json(catalogo)
    
    # Mostrar catálogo
    print("\nCatálogo de documentos:")
    mostrar_catalogo(catalogo)
    
    # Mostrar información sobre tipos de documentos
    tipos = {}
    for doc in catalogo:
        tipo = doc.get("tipo_documento", "Desconocido")
        tipos[tipo] = tipos.get(tipo, 0) + 1
    
    print("\nResumen por tipo de documento:")
    for tipo, cantidad in tipos.items():
        print(f"- {tipo}: {cantidad} documentos")

if __name__ == "__main__":
    main() 