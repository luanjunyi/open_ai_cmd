import configparser
import openai
import re
import time
from mac_say import say
from chat import chat_response
import speech_recognition as sr

conf = configparser.ConfigParser()
conf.read("config.ini")
OPENAI_API_KEY = conf.get("open_ai", "api_key")


openai.api_key = OPENAI_API_KEY

r = sr.Recognizer()

def whisper_rec(audio):
    audio_data = audio.get_wav_data()
    TEMP_AUDIO_FILE_NAME = 'temp_audio.wav'
    
    with open(TEMP_AUDIO_FILE_NAME, 'wb') as audio_file:
        audio_file.write(audio_data)

    with open(TEMP_AUDIO_FILE_NAME, 'rb') as audio_file:
        print("Using Whisper to recoganize...")
        result = openai.Audio.transcribe("whisper-1", audio_file)
        return result["text"]

def should_activate(text):
    text = text.lower()
    tokens = set(re.findall('[a-zA-Z]+', text))
    for t in 'show me the money'.split():
        if t not in tokens:
            return False
    return True

def should_inactivate(text):
    text = text.lower()
    tokens = set(re.findall('[a-zA-Z]+', text))
    for t in 'that will be all'.split():
        if t not in tokens:
            return False
    return True


def listen_forever():
    activated = False
    
    mic = sr.Microphone()
    with mic as source:
        r.adjust_for_ambient_noise(source)

    while True:
        print("......")
        with mic as source:
            audio = r.listen(source)
        voice_text = whisper_rec(audio)
        print(">", voice_text, "\n")

        if not activated and should_activate(voice_text):
            say("At your service!")
            activated = True
            continue

        elif activated and should_inactivate(voice_text):
            say("Dismissed")
            activated= False
            continue

        if activated:
            if len(voice_text.strip().split()) >= 3:
                response = chat_response(voice_text)
                print(response)
                say(response)        
        

        time.sleep(0.5)


if __name__ == '__main__':
    say("All systems go!")
    listen_forever()
