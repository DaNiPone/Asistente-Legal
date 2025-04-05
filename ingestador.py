import os
import sys
import time
import glob
import logging
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
import httpx

# Corregir el problema de codificación de caracteres en httpx para OpenAI
httpx._models._SENTINEL_DEFAULT_HEADERS = None
httpx.Headers.__init__.__defaults__ = (httpx.Headers(), 'utf-8')

# Configurar codificación
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
os.environ["PYTHONIOENCODING"] = "utf-8"

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Obtener la clave API desde la variable de entorno
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# Verificar que la clave API esté disponible
if not OPENAI_API_KEY:
    logger.error("⚠️ ERROR: OPENAI_API_KEY no está configurada.")
    print("\n" + "="*50)
    print("ERROR: OPENAI_API_KEY no configurada")
    print("="*50)
    print("Para configurar la clave API, ejecuta:")
    print('$env:OPENAI_API_KEY="tu-clave-api-de-openai"')
    print("="*50 + "\n")
    sys.exit(1)

# Inicializar el modelo de embeddings de OpenAI
embeddings = OpenAIEmbeddings(
    openai_api_key=OPENAI_API_KEY,
    disallowed_special=()  # Permitir caracteres especiales
)

# Constantes para los chunks
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
MAX_BATCH_SIZE = 500  # Tamaño máximo de lote para enviar a OpenAI 