# Voice-Based Chatbot with Inappropriate Speech Detection (using better-profanity + sounddevice)

# ---- STEP 1: Install Required Packages ----
# Run this in terminal or notebook
#!pip install streamlit openai SpeechRecognition pyttsx3 better-profanity sounddevice wavio

# ---- STEP 2: Import Required Libraries ----
import speech_recognition as sr
import pyttsx3
from better_profanity import profanity
import openai
import sounddevice as sd
import wavio
import os
import time

# ---- STEP 3: Initialize Recognizer and Profanity Filter ----
recognizer = sr.Recognizer()
profanity.load_censor_words()

# ---- STEP 4: Define Helper Functions ----

def record_audio(duration=5, filename="output.wav", samplerate=44100):
    print("Recording...")
    audio_data = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1)
    sd.wait()
    wavio.write(filename, audio_data, samplerate, sampwidth=2)
    return filename

def get_voice_input():
    filename = record_audio()
    with sr.AudioFile(filename) as source:
        audio = recognizer.record(source)
    try:
        text = recognizer.recognize_google(audio)
        print(f"You said: {text}")
        return text
    except sr.UnknownValueError:
        print("Sorry, I could not understand the audio.")
        return ""
    except sr.RequestError:
        print("Request Failed from Google Speech Recognition API")
        return ""

def check_profanity(text):
    return profanity.contains_profanity(text)

def generate_response(text):
    # GPT-based response using OpenAI API
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": text}]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {str(e)}"

def speak_response(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

# ---- STEP 5: Main Loop ----
def main():
    while True:
        user_input = get_voice_input()
        if user_input == "":
            continue

        if check_profanity(user_input):
            warning = "Please refrain from using inappropriate language."
            print(warning)
            speak_response(warning)
            continue

        response = generate_response(user_input)
        print("Bot:", response)
        speak_response(response)

        if "bye" in user_input.lower():
            break

# ---- RUN ----
if __name__ == "__main__":
    print("Voice Chatbot with Inappropriate Speech Detection")
    main()
