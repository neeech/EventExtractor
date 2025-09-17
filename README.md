# Event Extractor

Este proyecto utiliza modelos de lenguaje generativo (LLMs) para extraer entidades y eventos estructurados a partir de texto en español.

## Características

- **Extracción de Eventos**: Identifica y estructura eventos complejos y las entidades relacionadas (ej. fechas, lugares, participantes).
- **Soporte para Múltiples Modelos**: Permite intercambiar fácilmente diferentes modelos de la API de Google AI Studio (Gemini, Gemma, etc.) para la extracción.
- **Evaluación de Resultados**: Incluye un script para calcular métricas de rendimiento (precisión, recall, F1-score) comparando los resultados con un conjunto de datos de referencia.
- **Metodología de Evaluación**: Compara cada evento extraído con los de referencia, calculando las métricas (precisión, recall, F1-score) campo por campo. Luego, asigna los pares de eventos de manera óptima para maximizar el F1-score promedio total.

## Cómo Funciona

1.  **Entrada**: El script `extraer.py` lee archivos `.json` de la carpeta `data/`. Cada archivo debe contener un campo `"texto"` con el contenido a procesar.
2.  **Procesamiento**: Utiliza la clase `EventExtractor` que, a su vez, emplea un LLM para analizar el texto y extraer la información según las plantillas definidas en `prompts.py`.
3.  **Salida**: Los resultados de la extracción se guardan en la carpeta `resultados/`, organizados en subcarpetas según el modelo utilizado.
4.  **Evaluación**: El script `evaluar.py` compara los JSON generados con los datos de referencia en `data/` para medir la calidad de la extracción.

## Uso

### 1. Instalación

Clona el repositorio e instala las dependencias:

```bash
git clone <URL-del-repositorio>
cd EventExtractor
pip install -r requirements.txt
```

### 2. Configuración

Crea un archivo llamado `.env` en la raíz del proyecto y añade tu clave de API:

```
API_KEY="TU_API_KEY_AQUI"
```

### 3. Ejecutar la Extracción

Ejecuta el script `extraer.py` especificando el modelo que deseas utilizar.

```bash
python extraer.py --modelo <nombre-del-modelo>
```

Ejemplo:
```bash
python extraer.py --modelo gemini-2.5-flash
```

### 4. Evaluar los Resultados

Para evaluar los resultados de un modelo, modifica la ruta `results_dir` en `evaluar.py` y luego ejecútalo:

```bash
python evaluar.py
```

## Estructura del Proyecto

```
.
├── data/               # Datos de entrada y ground truth (JSON)
├── resultados/         # Resultados de la extracción por modelo
├── .env                # Archivo para la clave de API (ignorado por Git)
├── .gitignore          # Archivos ignorados por Git
├── evaluar.py          # Script para evaluar la calidad de la extracción
├── extractor.py        # Clase principal que se comunica con la API del LLM
├── extraer.py          # Script para ejecutar el proceso de extracción
├── prompts.py          # Plantillas de prompts para el LLM
├── requirements.txt    # Dependencias del proyecto
└── README.md           # Este archivo
```
