# Voice-Based Chatbot with Inappropriate Speech Detection (Streamlit + better-profanity + sounddevice)

# ---- STEP 1: Install Required Packages ----
# Run in terminal (not in code file)
# pip install streamlit openai SpeechRecognition pyttsx3 better-profanity sounddevice wavio

import streamlit as st
import speech_recognition as sr
import pyttsx3
from better_profanity import profanity
import openai
import sounddevice as sd
import wavio
import os
import time

recognizer = sr.Recognizer()
profanity.load_censor_words()

# ---- Audio Recording ----
def record_audio(duration=5, filename="output.wav", samplerate=44100):
    st.info("Recording... Please speak now")
    audio_data = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1)
    sd.wait()
    wavio.write(filename, audio_data, samplerate, sampwidth=2)
    return filename

# ---- Voice to Text ----
def get_voice_input():
    filename = record_audio()
    with sr.AudioFile(filename) as source:
        audio = recognizer.record(source)
    try:
        text = recognizer.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        return ""
    except sr.RequestError:
        return "[Speech Recognition API error]"

# ---- GPT Response ----
def generate_response(text):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": text}]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {str(e)}"

# ---- Text to Speech ----
def speak_response(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

# ---- Streamlit App ----
st.set_page_config(page_title="Voice Chatbot", layout="centered")
st.title("🗣️ Voice Chatbot with Moderation")

if "response" not in st.session_state:
    st.session_state.response = ""

if st.button("🎤 Start Recording"):
    user_input = get_voice_input()
    if user_input == "":
        st.warning("Sorry, I couldn't understand you. Please try again.")
    elif profanity.contains_profanity(user_input):
        st.error("🚫 Inappropriate language detected. Try being nicer!")
        speak_response("Please refrain from using inappropriate language.")
    else:
        st.markdown(f"**You said:** {user_input}")
        response = generate_response(user_input)
        st.session_state.response = response
        st.markdown(f"**Chatbot says:** {response}")
        speak_response(response)

if st.session_state.response:
    st.success("✅ Response complete")
