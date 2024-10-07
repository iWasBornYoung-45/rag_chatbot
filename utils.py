from openai import OpenAI
import openai
from dotenv.main import load_dotenv
import os
import io
from google.oauth2 import service_account
from google.cloud import speech, texttospeech

load_dotenv()
OPENAI_API_KEY = openai.api_key = os.environ.get('OPENAI_API_KEY')
# print(OPENAI_API_KEY)
client = OpenAI()

def speech_to_text(audio_data):
    with open(audio_data, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            language="mr",
            file=audio_file
        )
    return transcript.text

def get_answer(messages):
    system_message = [{"role": "system", "content": "You are a conversational chatbot inside a help desk kiosk installed at a government office in Maharashtra, India. Reply to the user's queries in the most politically correct way possible . Reply in standard marathi only."}]
    messages = system_message + messages
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )
    return response.choices[0].message.content

credentials_file = "rag-chatbot-437807-bb1531483d3f.json"
credentials = service_account.Credentials.from_service_account_file(credentials_file)
client_gcp = speech.SpeechClient(credentials=credentials)

def transcribe_audio(file):
    with io.open(file, 'rb') as f:
        content = f.read()
        audio = speech.RecognitionAudio(content=content)

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.MP3,
        sample_rate_hertz=16000,
        language_code="mr",
    )
    response = client_gcp.recognize(config=config, audio=audio)
    print(response.results)
    return response.results

def text_to_speech(text):
    cred_file = "text_to_speech_gcp.json"
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = cred_file

    client = texttospeech.TextToSpeechClient()
    voice = texttospeech.VoiceSelectionParams(
        language_code='mr-IN',
        name="mr-IN-Standard-A"
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )
    synthesis_input = texttospeech.SynthesisInput(
        text = text
    )
    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )
    out_file_path = 'output.mp3'
    with open(out_file_path, 'wb') as out:
        out.write(response.audio_content)
    return out_file_path
