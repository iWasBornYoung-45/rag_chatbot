import streamlit as st
from audio_recorder_streamlit import audio_recorder
import streamlit_float
import os
from utils import speech_to_text, get_answer, transcribe_audio, text_to_speech
import base64

streamlit_float.float_init()

def initialize_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "मी आपली कशी मदद करू शकते?"}]

def autoplay_audio(file_path: str):
    with open(file_path, "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        md = f"""
            <audio controls autoplay="true">
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
            """
        st.markdown(
            md,
            unsafe_allow_html=True,
        )

st.title("ई-समाधान हेल्प डेस्क")

initialize_session_state()

for message in st.session_state.messages:
    with st.chat_message(message['role']):
        st.write(message['content'])

footer_container = st.container()
with footer_container:
    audio_bytes = audio_recorder()

if audio_bytes:
    # st.audio(audio_bytes, format="audio/wav")
    print(f"Audio data length: {len(audio_bytes)} bytes")
    with st.spinner("Transcribing..."):
        file_path = "user_audio.mp3"
        with open(file_path, "wb") as f:
            f.write(audio_bytes)
    # transcript = speech_to_text(file_path)
    transcript = transcribe_audio(file_path)
    # print(transcript)
    if transcript:
        text_joined = ''
        for text in transcript:
            text_joined = text_joined + ' ' + text.alternatives[0].transcript
        print(text_joined, type(text_joined))
        with st.chat_message("user"):
            st.write(text_joined)
        
        st.session_state.messages.append({"role": "user", "content": text_joined})
        os.remove(file_path)

if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking🤔..."):
            final_response = get_answer(st.session_state.messages)
        with st.spinner("Generating audio response..."):    
            audio_file = text_to_speech(final_response)
            autoplay_audio(audio_file)
        st.write(final_response)
        st.session_state.messages.append({"role": "assistant", "content": final_response})
        os.remove(audio_file)