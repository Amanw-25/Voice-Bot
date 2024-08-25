import os

import streamlit as st
from audio_recorder_streamlit import audio_recorder
from streamlit_float import *

from utils import autoplay_audio, get_answer, speech_to_text, text_to_speech

# Initialize floating features for the interface
float_init()


# Initialize session state and other options
def initialize_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hi! How may I assist you today?"}
        ]
    if "tts_enabled" not in st.session_state:
        st.session_state.tts_enabled = False
    if "history" not in st.session_state:
        st.session_state.history = ""


initialize_session_state()

st.title("Your Partner in the Field 🤖")


footer_container = st.container()
with footer_container:
    col1, col2, col3 = st.columns([7, 1, 1])
    with col1:
        prompt = st.chat_input("Ask away!")
    with col2:
        audio_bytes = audio_recorder(
            text="",
            recording_color="#990000",
            neutral_color="#000000",
            icon_name="microphone",
            icon_size="2x",
        )
    with col3:
        st.session_state.tts_enabled = st.checkbox(
            "TTS", value=st.session_state.tts_enabled
        )

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

if audio_bytes:
    with st.spinner("Transcribing..."):
        # Write the audio bytes to a temporary file
        webm_file_path = "temp_audio.mp3"
        with open(webm_file_path, "wb") as f:
            f.write(audio_bytes)

        # Convert the audio to text using the speech_to_text function
        transcript = speech_to_text(webm_file_path)
        if transcript:
            st.session_state.messages.append({"role": "user", "content": transcript})
            with st.chat_message("user"):
                st.write(transcript)
            os.remove(webm_file_path)
        else:
            st.session_state.messages.append(
                {"role": "assistant", "content": "please speak again."}
            )
elif prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)


if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking🤔..."):
            response, code, history = get_answer(st.session_state.history, st.session_state.messages[-1]["content"])
        st.write(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.session_state.history += history

        print(history)

        if st.session_state.tts_enabled:
            with st.spinner("Generating audio response..."):
                audio_file = text_to_speech(response, code)
                autoplay_audio(audio_file)
            os.remove(audio_file)

st.session_state.stop_respond = False

footer_container.float("bottom: 0rem; background: #0E1117;")
col2.float("bottom: 0rem;")
col3.float("bottom: 0rem;")
