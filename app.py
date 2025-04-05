import os
import sys
from flask import Flask, render_template_string, request, send_file, make_response, session, redirect, url_for
from markupsafe import Markup
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_chroma import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate
import markdown
import logging
import httpx
import time
from dotenv import load_dotenv
import re
import uuid
import io
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, ListFlowable, ListItem
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from bs4 import BeautifulSoup
import html

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

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Configuración
CARPETA_BD = "base_datos"
NUM_RESULTADOS = 10

# Cargar variables de entorno
load_dotenv()

# Obtener API keys de variables de entorno
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

# Verificar y mostrar información sobre la configuración de API keys
if OPENAI_API_KEY:
    logger.info("OpenAI API Key configurada correctamente")
else:
    logger.warning("OpenAI API Key no configurada. Algunas funcionalidades pueden no estar disponibles.")

if ANTHROPIC_API_KEY:
    logger.info("Anthropic API Key configurada correctamente")
else:
    logger.warning("Anthropic API Key no configurada. Los modelos de Claude no estarán disponibles.") 