import speech_recognition as sr
from pydub import AudioSegment
import io
import logging
from django.conf import settings
logger = logging.getLogger(__name__)

recognizer = sr.Recognizer()

def process_audio(audio_file):
    try:
        with sr.AudioFile(audio_file) as source:
            audio_data = recognizer.record(source)
        
        # Try recognition in English (Indian) first, then Hindi if no result
        try:
            text = recognizer.recognize_google(audio_data, language="en-IN")
        except sr.UnknownValueError:
            try:
                text = recognizer.recognize_google(audio_data, language="hi-IN")
            except sr.UnknownValueError:
                return "Speech could not be recognized"
        return text
    except Exception as e:
        logger.error(f"Error processing audio: {str(e)}", exc_info=True)
        return f"Error processing audio: {str(e)}"