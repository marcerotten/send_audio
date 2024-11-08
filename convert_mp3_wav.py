from pydub import AudioSegment

def convert_mp3_to_wav(mp3_file_path, wav_file_path):
    # Cargar el archivo MP3
    audio = AudioSegment.from_mp3(mp3_file_path)
    
    # Exportar como WAV de 16 bits
    audio.export(wav_file_path, format='wav', parameters=["-sample_fmt", "s16"])

if __name__ == "__main__":
    mp3_file = "/Users/marcerotten/Downloads/demo9.mp3"  # Cambia esto por la ruta de tu archivo MP3
    wav_file = "/Users/marcerotten/Desktop/Marce/Proyectos/send_audio/audios/demo9.wav"   # Cambia esto por la ruta donde quieres guardar el WAV
    
    convert_mp3_to_wav(mp3_file, wav_file)
    print(f"Convertido {mp3_file} a {wav_file} exitosamente.")
