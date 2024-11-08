import socket
import os
import threading
import pyaudio
import pickle
import struct
import numpy as np
from scipy.io.wavfile import write
import whisper
import warnings
import logging
from datetime import datetime
from transformers import pipeline
import speech_recognition as sr
from dotenv import load_dotenv
from openai import OpenAI


# Configurar advertencias y logging
warnings.filterwarnings("ignore", message="emoji is not installed")
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)
logging.basicConfig(level=logging.ERROR)

os.environ["TOKENIZERS_PARALLELISM"] = "false" # Desactiva el uso de procesadores paralelos
## Load the API key from .env
load_dotenv()
api_key = os.getenv("API_KEY")

## Set the API key
client = OpenAI(api_key=api_key)

# Configuración de conexión
host_ip = '127.0.0.1'
port = 9611

# Inicializa el modelo de transcripción y análisis de sentimiento
model = whisper.load_model("base")
sentiment_analyzer = pipeline("sentiment-analysis", model="nlptown/bert-base-multilingual-uncased-sentiment", device=-1) # device=-1 para usar exclusivamente la CPU
# Inicializa el modelo para el segundo análisis de sentimiento en español
sentiment_analyzer_2 = pipeline("sentiment-analysis", model="finiteautomata/bertweet-base-sentiment-analysis", tokenizer="finiteautomata/bertweet-base-sentiment-analysis")


def create_output_folder(name_wav):
    """Crea una carpeta con la nomenclatura específica"""
    timestamp = datetime.now().strftime("%d%m%Y_%H%M%S")
    folder_name = f"{name_wav}_{timestamp}"
    output_folder = os.path.join("output", folder_name)
    os.makedirs(output_folder, exist_ok=True)
    return output_folder

def audio_stream():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host_ip, port))
    print("CLIENT CONNECTED TO", (host_ip, port))

    # Recibir parámetros iniciales
    param_size = struct.calcsize("IIII")
    initial_data = client_socket.recv(param_size)
    while len(initial_data) < param_size:
        additional_data = client_socket.recv(param_size - len(initial_data))
        initial_data += additional_data

    rate, channels, total_chunks, name_wav_length = struct.unpack("IIII", initial_data)

    # Recibir el nombre del archivo
    name_wav_data = client_socket.recv(name_wav_length)
    while len(name_wav_data) < name_wav_length:
        name_wav_data += client_socket.recv(name_wav_length - len(name_wav_data))
    name_wav = name_wav_data.decode('utf-8')

    output_folder = create_output_folder(name_wav)
    transcript_file = os.path.join(output_folder, "transcription.txt")

    p = pyaudio.PyAudio()
    FORMAT = pyaudio.paInt16
    stream = p.open(format=FORMAT, channels=channels, rate=rate, output=True)

    data = b""
    payload_size = struct.calcsize("Q")
    segment_data = []
    accumulated_samples = 0
    file_counter = 1

    try:
        while True:
            while len(data) < payload_size:
                packet = client_socket.recv(4 * 1024)
                if not packet:
                    break
                data += packet
            if len(data) < payload_size:
                break

            packed_msg_size = data[:payload_size]
            data = data[payload_size:]
            msg_size = struct.unpack("Q", packed_msg_size)[0]

            while len(data) < msg_size:
                data += client_socket.recv(4 * 1024)
            frame_data = data[:msg_size]
            data = data[msg_size:]

            # Reproducir y almacenar el audio recibido
            frame = pickle.loads(frame_data)
            stream.write(frame.tobytes())
            segment_data.append(frame)
            accumulated_samples += frame.size

            # Guardar segmentos en archivos de 5 segundos
            samples_per_5_seconds = rate * channels * 5
            if accumulated_samples >= samples_per_5_seconds:
                audio_data = np.concatenate(segment_data, axis=0)
                output_wav = os.path.join(output_folder, f"output_part_{file_counter}.wav")
                write(output_wav, rate, audio_data[:samples_per_5_seconds])

                # Transcribir y analizar el segmento
                transcribe_and_analyze(output_wav, transcript_file)
                
                # Actualizar datos acumulados
                remaining_samples = audio_data[samples_per_5_seconds:]
                segment_data = [remaining_samples]
                accumulated_samples = remaining_samples.size
                file_counter += 1

    except Exception as e:
        print("Error:", e)

    finally:
        # Guardar cualquier segmento restante
        if accumulated_samples > 0:
            final_output_wav = os.path.join(output_folder, f"output_final_part_{file_counter}.wav")
            audio_data = np.concatenate(segment_data, axis=0)
            write(final_output_wav, rate, audio_data)
            transcribe_and_analyze(final_output_wav, transcript_file)

        client_socket.close()
        stream.stop_stream()
        stream.close()
        p.terminate()
        print("Audio closed")

def transcribe_and_analyze(audio_path, transcript_file):
    """Transcribe y analiza el sentimiento del audio, y lo guarda en el archivo de transcripción."""
    try:
        # Transcripción con whisper-1
        transcription = client.audio.transcriptions.create(
        	model="whisper-1",
        	file=open(audio_path, "rb"),
    	)
        transcription_w1 = transcription.text
        
        # Transcripción del audio
        result = model.transcribe(audio_path, fp16=False)
        text = result['text']
        print(f"Audio transcrito: {audio_path}")
        print(f"Texto Transcrito: {text}")
        print("Texto Transcrito Whisper-1:", transcription_w1)

        # Análisis de sentimiento
        sentiment = sentiment_analyzer(text)

		# Análisis de sentimiento 2 (nuevo)
        sentiment_2 = analyze_sentiment_2(text)
        
		# Análisis de sentimiento whisper-1
        sentiment_w1 = sentiment_analyzer(transcription_w1)

		# Análisis de sentimiento 2 (nuevo) whisper-1
        sentiment_2_w1 = analyze_sentiment_2(transcription_w1)

        # Guardar la transcripción y el análisis en el archivo
        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        with open(transcript_file, "a") as file:
            file.write(f"Fecha: {timestamp}\n")
            file.write(f"Texto: {text}\n")
            file.write(f"Score: {sentiment}\n")
            file.write(f"Analisis2: {sentiment_2}\n")
            file.write(f"Texto_whisper-1: {transcription_w1}\n")
            file.write(f"Score: {sentiment_w1}\n")
            file.write(f"Analisis2: {sentiment_2_w1}\n")
            
            file.write("="*96 + "\n")
        print(f"Transcripción y análisis guardados en: {transcript_file}")

    except Exception as e:
        print(f"Error al transcribir y analizar el audio {audio_path}: {e}")
        
def analyze_sentiment_2(text):
    """Realiza el segundo análisis de sentimiento para el texto en español."""
    try:
        result = sentiment_analyzer_2(text)
        label = result[0]['label']
        
        # Convertir la etiqueta en algo más legible
        if label == 'POS':
            return "Positivo"
        elif label == 'NEU':
            return "Neutral"
        elif label == 'NEG':
            return "Negativo"
        else:
            return "Desconocido"
    except Exception as e:
        print(f"Error en Analisis2: {e}")
        return "Error en Analisis2"

# Iniciar hilo de transmisión de audio
t1 = threading.Thread(target=audio_stream, daemon=True) # daemon=True para que el hilo se destruya al cerrar el programa
t1.start()

# Al final del programa, esperar a que el hilo termine (opcional pero seguro)
t1.join()
