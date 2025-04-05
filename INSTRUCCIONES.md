# Instrucciones detalladas para el Sistema RAG

Este documento proporciona instrucciones paso a paso para configurar y utilizar el Sistema RAG para consultas inmobiliarias en Cataluña.

## Configuración inicial

### 1. Configuración de claves API

Debes configurar tus claves API de OpenAI y/o Anthropic en los archivos `app.py` e `ingestador.py`:

En ambos archivos, localiza las siguientes líneas:

```python
# En app.py, aproximadamente línea 30
OPENAI_API_KEY = "sk-..."
ANTHROPIC_API_KEY = "sk-ant-..."
```

Reemplaza los valores con tus propias claves API.

### 2. Preparación de los documentos

1. Crea una carpeta `documentos` en la raíz del proyecto si no existe
2. Coloca todos los archivos PDF relacionados con normativa inmobiliaria en la carpeta
3. Los documentos pueden ser PDFs estándar o protegidos con contraseña

## Procesamiento de la base de conocimiento

Para procesar los documentos y crear la base de datos vectorial:

```bash
python ingestador.py
```

El sistema mostrará el progreso de procesamiento de cada documento y un resumen final.

### Personalización del procesamiento

Si necesitas ajustar los parámetros de chunking, modifica estas constantes en `ingestador.py`:

```python
# Tamaño del chunk y solapamiento
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
```

## Ejecución de la aplicación

Para iniciar la aplicación web:

```bash
python app.py
```

Accede a la aplicación en tu navegador web:
http://localhost:5000

### Uso de la aplicación

1. **Seleccionar un modelo**: Elige entre diferentes modelos de OpenAI o Anthropic según disponibilidad
2. **Realizar consultas**: Escribe tu pregunta o selecciona una de las preguntas sugeridas
3. **Exportar resultados**: Utiliza los botones para descargar las respuestas en formato PDF o checklist

### Solución de problemas comunes

- **Error con el modelo seleccionado**: La aplicación cambiará automáticamente a GPT-3.5 si el modelo elegido no está disponible
- **Problemas de acceso a la API**: Verifica que tus claves API sean válidas y tengan saldo disponible
- **Errores de procesamiento de PDF**: Asegúrate de que tus PDFs no estén dañados o corruptos

## Actualización de la base de conocimiento

Si deseas actualizar la base de conocimiento con nuevos documentos:

1. Añade los nuevos PDFs a la carpeta `documentos`
2. Ejecuta nuevamente `ingestador.py`

Si deseas recrear completamente la base de conocimiento:

1. Elimina la carpeta `base_datos`
2. Ejecuta `ingestador.py`

## Mantenimiento

Se recomienda actualizar regularmente las dependencias ejecutando:

```bash
pip install --upgrade -r requirements.txt
``` 