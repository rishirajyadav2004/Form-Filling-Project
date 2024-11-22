import whisper
import os
from googletrans import Translator

# Load the Whisper model
model = whisper.load_model("base")

# Translator for multilingual support
translator = Translator()

def transcribe_speech(audio_path, target_language='en'):
    # Transcribe audio using Whisper
    result = model.transcribe(audio_path)
    original_text = result['text']

    # Translate the text if needed
    if target_language != 'en':
        translated_text = translator.translate(original_text, dest=target_language).text
        return translated_text
    return original_text
