import os
import sys
import requests
import tempfile
from datetime import datetime
import subprocess
import hashlib
import json
import logging
from urllib.parse import urlparse
from pathlib import Path

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("actualizador.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Directorios y archivos importantes
DOCUMENTOS_DIR = "documentos"
REGISTRO_DOCS = "registro_documentos.json"
URLS_VIGILADAS = "urls_vigiladas.json"

def crear_directorios():
    """Crea los directorios necesarios si no existen"""
    os.makedirs(DOCUMENTOS_DIR, exist_ok=True)

def cargar_registro():
    """Carga el registro de documentos procesados"""
    if os.path.exists(REGISTRO_DOCS):
        with open(REGISTRO_DOCS, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def guardar_registro(registro):
    """Guarda el registro de documentos procesados"""
    with open(REGISTRO_DOCS, 'w', encoding='utf-8') as f:
        json.dump(registro, f, indent=2)

def cargar_urls_vigiladas():
    """Carga la lista de URLs que se deben vigilar"""
    if os.path.exists(URLS_VIGILADAS):
        with open(URLS_VIGILADAS, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def guardar_urls_vigiladas(urls):
    """Guarda la lista de URLs que se deben vigilar"""
    with open(URLS_VIGILADAS, 'w', encoding='utf-8') as f:
        json.dump(urls, f, indent=2)

def generar_hash_archivo(ruta_archivo):
    """Genera un hash MD5 del contenido del archivo"""
    hash_md5 = hashlib.md5()
    with open(ruta_archivo, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def descargar_documento(url):
    """Descarga un documento desde una URL"""
    try:
        logger.info(f"Descargando documento desde: {url}")
        response = requests.get(url, stream=True, timeout=60)
        response.raise_for_status()
        
        # Obtener el nombre del archivo de la URL o de las cabeceras
        nombre_archivo = None
        if "Content-Disposition" in response.headers:
            import re
            cd = response.headers["Content-Disposition"]
            if re.findall("filename=(.+)", cd):
                nombre_archivo = re.findall("filename=(.+)", cd)[0].strip('"')
        
        if not nombre_archivo:
            nombre_archivo = os.path.basename(urlparse(url).path)
            if not nombre_archivo:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                extension = ".pdf"  # Por defecto asumimos PDF
                nombre_archivo = f"documento_{timestamp}{extension}"
        
        # Guardar el archivo temporalmente
        with tempfile.NamedTemporaryFile(suffix=os.path.splitext(nombre_archivo)[1], delete=False) as tmp:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    tmp.write(chunk)
            temp_path = tmp.name
        
        # Determinar la ruta definitiva
        ruta_destino = os.path.join(DOCUMENTOS_DIR, nombre_archivo)
        
        # Si ya existe un archivo con el mismo nombre, añadir timestamp
        if os.path.exists(ruta_destino):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base, ext = os.path.splitext(nombre_archivo)
            nombre_archivo = f"{base}_{timestamp}{ext}"
            ruta_destino = os.path.join(DOCUMENTOS_DIR, nombre_archivo)
        
        # Mover el archivo a la carpeta de documentos
        os.rename(temp_path, ruta_destino)
        logger.info(f"Documento guardado en: {ruta_destino}")
        
        return ruta_destino
    
    except Exception as e:
        logger.error(f"Error al descargar documento desde {url}: {str(e)}")
        if 'temp_path' in locals() and os.path.exists(temp_path):
            os.remove(temp_path)
        return None

def actualizar_base_conocimiento():
    """Ejecuta el ingestador para actualizar la base de conocimiento"""
    try:
        logger.info("Actualizando base de conocimiento...")
        resultado = subprocess.run(["python", "ingestador.py"], 
                                  capture_output=True, text=True, check=True)
        logger.info(f"Base de conocimiento actualizada exitosamente:\n{resultado.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Error al actualizar la base de conocimiento: {str(e)}\n{e.stderr}")
        return False

def agregar_url(url, descripcion=""):
    """Agrega una URL a la lista de vigiladas"""
    urls = cargar_urls_vigiladas()
    
    # Comprobar si la URL ya existe
    for item in urls:
        if item.get("url") == url:
            logger.info(f"La URL {url} ya está en la lista de vigiladas")
            return False
    
    # Agregar la nueva URL
    urls.append({
        "url": url,
        "descripcion": descripcion,
        "fecha_agregada": datetime.now().isoformat(),
        "ultima_actualizacion": None
    })
    
    guardar_urls_vigiladas(urls)
    logger.info(f"URL agregada correctamente: {url}")
    return True

def actualizar_desde_urls():
    """Descarga documentos desde las URLs vigiladas y actualiza la base de conocimiento"""
    urls = cargar_urls_vigiladas()
    registro = cargar_registro()
    actualizaciones = False
    
    for item in urls:
        url = item.get("url")
        try:
            ruta_archivo = descargar_documento(url)
            if ruta_archivo:
                # Calcular hash del archivo descargado
                hash_archivo = generar_hash_archivo(ruta_archivo)
                
                # Comprobar si el archivo ha cambiado
                if url in registro and registro[url]["hash"] == hash_archivo:
                    logger.info(f"El documento de {url} no ha cambiado, no es necesario actualizar")
                    os.remove(ruta_archivo)  # Eliminar archivo duplicado
                else:
                    # Registrar el nuevo documento
                    registro[url] = {
                        "ruta": ruta_archivo,
                        "hash": hash_archivo,
                        "fecha_descarga": datetime.now().isoformat()
                    }
                    
                    # Actualizar fecha de última actualización en la lista de URLs
                    for u in urls:
                        if u.get("url") == url:
                            u["ultima_actualizacion"] = datetime.now().isoformat()
                    
                    actualizaciones = True
                    logger.info(f"Documento actualizado: {ruta_archivo}")
        except Exception as e:
            logger.error(f"Error procesando {url}: {str(e)}")
    
    # Guardar el registro actualizado
    guardar_registro(registro)
    guardar_urls_vigiladas(urls)
    
    # Si hubo actualizaciones, reindexar la base de conocimiento
    if actualizaciones:
        actualizar_base_conocimiento()
        return True
    
    return False

def listar_urls_vigiladas():
    """Muestra la lista de URLs vigiladas"""
    urls = cargar_urls_vigiladas()
    if not urls:
        print("No hay URLs configuradas para vigilar.")
        return
    
    print("\n=== URLs vigiladas ===")
    for i, item in enumerate(urls, 1):
        ultima_act = item.get("ultima_actualizacion", "Nunca")
        if ultima_act and ultima_act != "Nunca":
            try:
                ultima_act = datetime.fromisoformat(ultima_act).strftime("%d/%m/%Y %H:%M")
            except (TypeError, ValueError):
                ultima_act = "Formato inválido"
        
        print(f"{i}. {item.get('url')}")
        print(f"   Descripción: {item.get('descripcion', 'Sin descripción')}")
        print(f"   Última actualización: {ultima_act}")
        print()

def main():
    """Función principal"""
    crear_directorios()
    
    if len(sys.argv) < 2:
        print("Uso: python actualizador.py [actualizar|agregar|listar]")
        return
    
    comando = sys.argv[1].lower()
    
    if comando == "actualizar":
        print("Actualizando documentos desde URLs vigiladas...")
        if actualizar_desde_urls():
            print("Base de conocimiento actualizada correctamente.")
        else:
            print("No hubo cambios para actualizar.")
    
    elif comando == "agregar":
        if len(sys.argv) < 3:
            print("Por favor, especifica la URL para agregar.")
            return
        
        url = sys.argv[2]
        descripcion = sys.argv[3] if len(sys.argv) > 3 else ""
        
        if agregar_url(url, descripcion):
            print(f"URL agregada correctamente: {url}")
        else:
            print("La URL ya estaba en la lista de vigiladas.")
    
    elif comando == "listar":
        listar_urls_vigiladas()
    
    else:
        print(f"Comando desconocido: {comando}")
        print("Uso: python actualizador.py [actualizar|agregar|listar]")

if __name__ == "__main__":
    main() 