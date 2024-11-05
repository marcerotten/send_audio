# This is server code to send video and audio frames over TCP

import socket
import threading, wave, pyaudio,pickle,struct
import numpy as np
from scipy.io import wavfile

host_name = socket.gethostname()
host_ip = '127.0.0.1'  # socket.gethostbyname(host_name)
print(host_ip)
port = 9611

# Ruta del archivo original y del archivo convertido
input_wav = "audios/demo.wav"
output_wav = "audios/demo_16bit.wav"

# Conversión del archivo a 16 bits usando scipy
fs, audio_data = wavfile.read(input_wav)
if audio_data.dtype != np.int16:
    audio_data = (audio_data * 32767).astype(np.int16)  # Convierte a 16 bits si es necesario

# Guardar el archivo en formato de 16 bits
wavfile.write(output_wav, fs, audio_data)

# Función para transmitir el audio
def audio_stream():
    server_socket = socket.socket()
    server_socket.bind((host_ip, (port - 1)))
    server_socket.listen(5)
    
    CHUNK = 1024
    wf = wave.open(output_wav, 'rb')  # Usa el archivo convertido de 16 bits
    
    p = pyaudio.PyAudio()
    print('server listening at', (host_ip, (port - 1)))
    
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    input=True,
                    frames_per_buffer=CHUNK)
    
    client_socket, addr = server_socket.accept()
    
    data = None
    while True:
        if client_socket:
            while True:
                data = wf.readframes(CHUNK)
                a = pickle.dumps(data)
                message = struct.pack("Q", len(a)) + a
                client_socket.sendall(message)

# Ejecuta la transmisión en un hilo
t1 = threading.Thread(target=audio_stream, args=())
t1.start()