import socket
import threading, pickle, struct, time
import numpy as np
from scipy.io import wavfile
import os

host_ip = '127.0.0.1'
port = 9611

# Ruta del archivo WAV
input_wav = "audios/demo9.wav"

# Obtener sólo nombre del archivo y sin extensión
name_wav = os.path.splitext(os.path.basename(input_wav))[0]
print('Nombre del archivo:', name_wav)

# Lectura del archivo WAV
fs, audio_data = wavfile.read(input_wav)

# Si el archivo no está en 16 bits, conviértelo
if audio_data.dtype != np.int16:
    audio_data = (audio_data / np.max(np.abs(audio_data))) * 32767
    audio_data = audio_data.astype(np.int16)

# Obtener número de canales
# Si es mono, el shape no tendrá dos dimensiones, así que lo manejamos
channels = audio_data.shape[1] if audio_data.ndim > 1 else 1

SECONDS_PER_CHUNK = 5
CHUNK_SIZE = fs * SECONDS_PER_CHUNK

def audio_stream():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host_ip, port))
    server_socket.listen(5)

    data_chunks = [audio_data[i:i + CHUNK_SIZE] for i in range(0, len(audio_data), CHUNK_SIZE)]
    print(f"Total chunks to send: {len(data_chunks)}")

    client_socket, addr = server_socket.accept()
    print('Client connected:', addr)

    try:
        # Convierte el nombre del archivo en bytes
        name_wav_bytes = name_wav.encode('utf-8')
        name_wav_length = len(name_wav_bytes)

        # Enviar parámetros iniciales al cliente
        initial_message = struct.pack("IIII", fs, channels,len(data_chunks), name_wav_length)  # envía freq y número de canales
        client_socket.sendall(initial_message)

        # Enviar el nombre del archivo
        client_socket.sendall(name_wav_bytes)

        for chunk in data_chunks:
            serialized_chunk = pickle.dumps(chunk)
            message = struct.pack("Q", len(serialized_chunk)) + serialized_chunk
            client_socket.sendall(message)
            print(f"Enviando chunk de tamaño: {len(chunk)} muestras")
            time.sleep(SECONDS_PER_CHUNK)

    except Exception as e:
        print("Error en la transmisión:", e)
    finally:
        client_socket.close()
        print("Transmisión finalizada.")

t1 = threading.Thread(target=audio_stream)
t1.start()