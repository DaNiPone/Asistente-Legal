# Sistema RAG para Consultas Inmobiliarias en Cataluña

Este proyecto implementa un sistema RAG (Retrieval Augmented Generation) para responder consultas sobre normativa inmobiliaria en Cataluña. Utiliza una base de conocimiento vectorial de documentos PDF y modelos de lenguaje para proporcionar respuestas precisas y contextualizadas.

## Características

- **Procesamiento de documentos PDF**: Ingesta automática de documentos legales, incluyendo PDFs protegidos.
- **Base de datos vectorial**: Almacenamiento eficiente de embeddings utilizando Chroma DB.
- **Interfaz web**: Aplicación Flask con diseño responsive para realizar consultas.
- **Múltiples modelos LLM**: Soporte para varios modelos de OpenAI y Anthropic.
- **Exportación de resultados**: Generación de PDFs y checklists a partir de las respuestas.
- **Preguntas sugeridas**: Organización por categorías de consultas frecuentes.

## Requisitos

- Python 3.8 o superior
- Claves API de OpenAI y/o Anthropic (configurable)
- Dependencias definidas en `requirements.txt`

## Instalación

1. Clonar el repositorio:
   ```
   git clone https://github.com/tu-usuario/mi-sistema-rag.git
   cd mi-sistema-rag
   ```

2. Crear un entorno virtual e instalar dependencias:
   ```
   python -m venv venv
   # En Windows
   venv\Scripts\activate
   # En Linux/Mac
   source venv/bin/activate
   
   pip install -r requirements.txt
   ```

3. Configurar las claves API:
   - Editar los archivos `app.py` e `ingestador.py` para añadir tus claves API de OpenAI y/o Anthropic.

## Uso

### Procesamiento de documentos

1. Coloca tus archivos PDF en la carpeta `documentos`.
2. Ejecuta el procesador de documentos:
   ```
   python ingestador.py
   ```
   Esto creará una base de datos vectorial en la carpeta `base_datos`.

### Aplicación web

1. Inicia la aplicación Flask:
   ```
   python app.py
   ```
2. Abre tu navegador y accede a `http://localhost:5000`
3. Realiza consultas sobre normativa inmobiliaria en Cataluña.

## Estructura del proyecto

- `app.py`: Aplicación web Flask.
- `ingestador.py`: Procesador de documentos PDF.
- `documentos/`: Carpeta para almacenar archivos PDF a procesar.
- `base_datos/`: Carpeta donde se guarda la base de datos vectorial.

## Personalización

- Puedes ajustar los parámetros de chunking en `ingestador.py`
- Modifica los prompts para los diferentes modelos en `app.py`
- Añade o elimina categorías de preguntas sugeridas en `app.py`

## Licencia

Este proyecto está disponible bajo licencia MIT.

## Contribuciones

Las contribuciones son bienvenidas. Por favor, crea un issue o pull request para proponer mejoras. 