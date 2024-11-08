# Proyecto de Análisis de Sentimientos y Transcripción de Audio en Tiempo Real

Este proyecto permite realizar la transcripción y el análisis de sentimientos de audio en tiempo real. 
Se utiliza un servidor y un cliente para recibir y procesar datos de audio. 
El servidor envía fragmentos de audio al cliente, que se encarga de transcribirlos y analizar el sentimiento de los mismos
## Características

- **Transcripción de audio**: Utiliza el modelo `whisper-1` para la transcripción de audios en tiempo real.
- **Análisis de sentimientos**: Se realiza un análisis de sentimiento utilizando dos modelos de procesamiento de lenguaje natural usando modelos de Hugging Face.
- **Segmentación Automática**: Guarda el audio recibido en archivos de 5 segundos y genera un archivo de transcripción detallado para cada segmento.
- **Almacenamiento de resultados**: Los resultados de la transcripción y el análisis de sentimientos se guardan en archivos separados por segmentos de audio.
- **Compatibilidad con Mac y CPU**: Configurado para uso en Mac sin aceleración por GPU.


## Estructura del Proyecto

- `server.py`: Código del servidor que envía el audio al cliente en segmentos de 5 segundos.
- `client.py`: Código del cliente para la recepción, transcripción y análisis de audio.
- `.env`: Archivo para almacenar la API Key de OpenAI (excluido del repositorio).
- `requirements.txt`: Lista de dependencias necesarias para el proyecto.

## Requisitos Previos

Antes de ejecutar el proyecto, asegúrate de tener instaladas las siguientes dependencias:

- **Python 3.8+**
- **Bibliotecas**:
  - `pyaudio`
  - `numpy`
  - `scipy`
  - `whisper`
  - `transformers`
  - `dotenv`
  - `openai`
  - `speech_recognition`
  - `socket`
  - `pickle`

## Configuración

### 1. Clonar el Repositorio

Clona este repositorio en tu máquina local utilizando el siguiente comando:

```bash
git clone https://github.com/tu_usuario/proyecto.git
```

### 2. Crear un Entorno Virtual
Es recomendable utilizar un entorno virtual para gestionar las dependencias del proyecto. Para crear un entorno virtual, ejecuta:

```bash
python -m venv env
```
Y actívalo:

En Windows:
```bash
.\env\Scripts\activate
```
En Mac/Linux:

```bash
source env/bin/activate
```
### 3. Instalar Dependencias
Instala las dependencias del proyecto usando pip:
```bash
pip install -r requirements.txt
```
### 4. Configurar el Archivo .env
```bash
API_KEY=tu_api_key_de_openai
```

Asegúrate de que tu clave API de OpenAI esté correctamente configurada en este archivo.

## Ejecución del Proyecto

### 1. Ejecutar el Servidor
```bash
python server.py
```
El servidor comenzará a enviar los fragmentos de audio al cliente.

### 2. Ejecutar el Cliente
```bash
python client.py
```
El cliente comenzará a recibir los fragmentos de audio, a transcribirlos y a realizar el análisis de sentimientos. 
Los resultados se guardarán en archivos dentro de una carpeta de salida.

## Ejemplo de Uso y Resultados

### Archivos de Salida del Cliente
Cuando se ejecuta el cliente, se generarán archivos de transcripción y análisis en una carpeta de salida, que se crea con el nombre del archivo de audio y una marca de tiempo. Los archivos generados son:

Transcripción del audio: Un archivo de texto que contiene la transcripción de cada segmento de audio procesado.
Análisis de sentimientos: Los resultados del análisis de sentimientos se guardarán junto a las transcripciones.

