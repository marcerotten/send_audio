import socket
import threading, wave, pickle, struct, time
import numpy as np
from scipy.io import wavfile

host_name = socket.gethostname()
host_ip = '127.0.0.1'
print(host_ip)
port = 9611

# Ruta del archivo original y del archivo convertido
input_wav = "audios/demo.wav"
output_wav = "audios/demo_16bit.wav"

# Conversión del archivo a 16 bits usando scipy
fs, audio_data = wavfile.read(input_wav)
if audio_data.dtype != np.int16:
    audio_data = (audio_data * 32767).astype(np.int16)

# Guardar el archivo en formato de 16 bits
wavfile.write(output_wav, fs, audio_data)

def audio_stream():
    server_socket = socket.socket()
    server_socket.bind((host_ip, (port - 1)))
    server_socket.listen(5)
    
    CHUNK_SIZE = fs * 5  # 5 segundos de audio en términos de número de muestras
    data_chunks = [audio_data[i:i + CHUNK_SIZE] for i in range(0, len(audio_data), CHUNK_SIZE)]
    print(f"Total chunks to send: {len(data_chunks)}")

    client_socket, addr = server_socket.accept()
    print('Client connected:', addr)

    try:
        for chunk in data_chunks:
            serialized_chunk = pickle.dumps(chunk)
            message = struct.pack("Q", len(serialized_chunk)) + serialized_chunk
            client_socket.sendall(message)
            print(f"Enviando chunk de tamaño: {len(chunk)}")

            # Pausa de 5 segundos para simular tiempo real
            time.sleep(5)

    except Exception as e:
        print("Error en la transmisión:", e)
    finally:
        client_socket.close()
        print("Transmisión finalizada.")

# Ejecuta la transmisión en un hilo
t1 = threading.Thread(target=audio_stream, args=())
t1.start()