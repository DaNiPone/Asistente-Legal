# Asistente Legal Inmobiliario para Cataluña

Sistema de Recuperación Aumentada por Generación (RAG) especializado en información legal inmobiliaria para Cataluña.

## Características

- Interfaz web intuitiva para consultar información legal
- Base de datos vectorial para búsqueda semántica
- Soporte para múltiples modelos de IA (OpenAI y Anthropic)
- Procesador de documentos PDF optimizado
- Sistema de referencia a fuentes consultadas

## Requisitos

- Python 3.8 o superior
- Claves API de OpenAI y Anthropic
- Dependencias listadas en `requirements.txt`

## Instalación

1. Clone el repositorio:
   ```
   git clone https://github.com/tu-usuario/mi-sistema-rag.git
   cd mi-sistema-rag
   ```

2. Cree un entorno virtual:
   ```
   python -m venv .venv
   ```

3. Active el entorno virtual:
   - Windows:
     ```
     .venv\Scripts\activate
     ```
   - Linux/Mac:
     ```
     source .venv/bin/activate
     ```

4. Instale las dependencias:
   ```
   pip install -r requirements.txt
   ```

5. Configure las variables de entorno con sus claves API:
   ```
   $env:OPENAI_API_KEY="su-clave-api-openai"
   $env:ANTHROPIC_API_KEY="su-clave-api-anthropic"
   ```

## Uso

1. Para procesar documentos nuevos:
   ```
   python ingestador.py
   ```

2. Para iniciar la aplicación web:
   ```
   python app.py
   ```

3. Acceda a la interfaz web:
   http://127.0.0.1:5000/

## Estructura de carpetas

- `app.py`: Aplicación web principal
- `ingestador.py`: Procesador de documentos
- `documentos/`: Carpeta para almacenar los PDFs legales
- `base_datos/`: Contiene la base de datos vectorial
- `requirements.txt`: Lista de dependencias

## Solución de problemas

Si encuentra errores de codificación con caracteres especiales, asegúrese de:
1. Configurar correctamente las variables de entorno:
   ```
   $env:PYTHONIOENCODING="utf-8"
   ```
2. Utilizar codificación UTF-8 en todos los archivos

## Licencia

Este proyecto está licenciado bajo la licencia MIT - vea el archivo LICENSE para más detalles. 