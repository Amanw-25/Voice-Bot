import base64
import json
import os

import google.generativeai as genai
import streamlit as st
import env
from gtts import gTTS

genai.configure(api_key=env.GEMINI_API_KEY)
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "application/json",
}
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash", generation_config=generation_config
)


def speech_to_text(audio_data):
    try:
        audio_file = genai.upload_file(path=audio_data)
        prompt = "Generate a transcript of the speech. Format your response in JSON, including fields for 'transcript'."
        response = model.generate_content([prompt, audio_file]).text
        genai.delete_file(audio_file.name)
        res = json.loads(response)
        return res["transcript"]
    except Exception as e:
        print(e)
        return "error"


def text_to_speech(input_text, lang_code):
    try:
        tts = gTTS(text=input_text, lang=lang_code, slow=False)

        audio_file = "output.mp3"
        tts.save(audio_file)

        return audio_file
    except Exception as e:
        print(e)
        return None


def get_answer(history, messages):
    system_message = "You are an expert agricultural chatbot. Provide comprehensive and informative responses to farmer queries related to agriculture, crop management, soil health, weather, pests, diseases, and more. Ensure all responses are relevant to agriculture and avoid providing unrelated information. Format your response in JSON, including fields for 'response_text', 'language_code', 'context_on_chat'."
    messages = system_message + "Contexts on previous talks: " + history + messages
    response = model.generate_content(messages).text
    res = json.loads(response)
    return res["response_text"], res["language_code"], res["context_on_chat"]


def autoplay_audio(file_path: str):
    with open(file_path, "rb") as f:
        data = f.read()
    b64 = base64.b64encode(data).decode("utf-8")
    md = f"""
    <audio autoplay playbackRate=1.5>
    <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
    </audio>
    """
    st.markdown(md, unsafe_allow_html=True)
