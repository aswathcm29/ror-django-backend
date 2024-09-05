import speech_recognition as sr
from pydub import AudioSegment
import io, os
import logging
from django.conf import settings
from langdetect import detect
from googletrans import Translator
from dotenv import load_dotenv
from groq import Groq
# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)

recognizer = sr.Recognizer()
translator = Translator()

categories = {
    "health_query": {
        "en": ["symptom", "sick", "ill", "pain", "ache", "fever", "cold", "flu"],
        "hi": ["लक्षण", "बीमार", "अस्वस्थ", "दर्द", "पीड़ा", "बुखार", "सर्दी", "फ्लू"],
        # Add more languages as needed
    },
    "medical_records": {
        "en": ["prescription", "record", "history", "past", "previous"],
        "hi": ["नुस्खा", "रिकॉर्ड", "इतिहास", "पिछला", "पूर्व"],
        # Add more languages as needed
    },
    # Add more categories as needed
}

responses = {
    "health_query": {
        "en": "Based on your symptoms, here are some suggestions: do this",
        "hi": "आपके लक्षणों के आधार पर, यहां कुछ सुझाव हैं: ...",
        # Add more languages as needed
    },
    "medical_records": {
        "en": "I'm retrieving your medical records. Please wait...",
        "hi": "मैं आपके चिकित्सा रिकॉर्ड प्राप्त कर रहा हूं। कृपया प्रतीक्षा करें...",
        # Add more languages as needed
    },
    "unknown": {
        "en": "I'm sorry, I couldn't understand your request. Can you please rephrase?",
        "hi": "क्षमा करें, मैं आपके अनुरोध को नहीं समझ सका। क्या आप कृपया इसे दोहरा सकते हैं?",
        # Add more languages as needed
    }
}

def detect_language(text):
    try:
        return detect(text)
    except:
        return "en"  # Default to English if detection fails

def classify_input(input_text, lang):
    input_text = input_text.lower()
    
    for category, lang_keywords in categories.items():
        if lang in lang_keywords:
            if any(keyword in input_text for keyword in lang_keywords[lang]):
                return category
    
    return "unknown"

def get_response(category, lang):
    if category in responses and lang in responses[category]:
        return responses[category][lang]
    return responses["unknown"][lang]

def process_audio(audio_file):
    try:
        with sr.AudioFile(audio_file) as source:
            audio_data = recognizer.record(source)
        logger.info("Audio file processed successfully")
        # Try recognition in English (Indian) first, then Hindi if no result
        try:
            text = recognizer.recognize_google(audio_data, language="en-IN")
        except sr.UnknownValueError:
            try:
                text = recognizer.recognize_google(audio_data, language="hi-IN")
            except sr.UnknownValueError:
                return "Speech could not be recognized"
         # Step 2: Language Detection
        lang = detect_language(text)
        logger.info(f"Detected language: {lang}")
        # Step 3: Classification
        category = classify_input(text, lang)

        # Step 4: Generate Response
        response = get_response(category, lang)

        return {"category": category, "text": text, "lang": lang}
    except Exception as e:
        logger.error(f"Error processing audio: {str(e)}", exc_info=True)
        return f"Error processing audio: {str(e)}"



# Generating response as both voice and text for the input voice


def generate_text_response(input_text, lang):
    logging.info(f"Loading groq api key")
    try:
        groq_text_generation_key = os.getenv("GORQ_TEXT_GENERATION_KEY")
    except:
        logging.error("Error loading groq api key", exc_info=True)
        return "Error loading groq api key"
    logging.info(f"Generating text response for input: {input_text}")
    try:
        client = Groq(
            api_key=os.getenv("GORQ_TEXT_GENERATION_KEY"),
        )

        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": f"{input_text}",
                }
            ],
            model="llama3-8b-8192",
        )

        return chat_completion.choices[0].message.content
    except:
        logging.error("Error generating text response", exc_info=True)
        return "Error generating text response"