# streamlit run streamlitui.py

import os
import tempfile
import streamlit as st
from streamlit_chat import message
from youtubequery import YoutubeQuery

st.set_page_config(page_title="Youtube Vídeo Chatbot")


def display_messages():
    st.subheader("Chat")
    for i, (msg, is_user) in enumerate(st.session_state["messages"]):
        message(msg, is_user=is_user, key=str(i))
    st.session_state["thinking_spinner"] = st.empty()


def process_input():
    if st.session_state["user_input"] and len(st.session_state["user_input"].strip()) > 0:
        user_text = st.session_state["user_input"].strip()
        with st.session_state["thinking_spinner"], st.spinner(f"Thinking"):
            query_text = st.session_state["youtubequery"].ask(user_text)

        st.session_state["messages"].append((user_text, True))
        st.session_state["messages"].append((query_text, False))
        
def ingest_input():
    if st.session_state["input_url"] and len(st.session_state["input_url"].strip()) > 0:
        url = st.session_state["input_url"].strip()
        with st.session_state["thinking_spinner"], st.spinner(f"Thinking"):
            ingest_text = st.session_state["youtubequery"].ingest(url)        

def is_openai_api_key_set() -> bool:
    return len(st.session_state["OPENAI_API_KEY"]) > 0


def main():

    if len(st.session_state) == 0:
        st.session_state["messages"] = []
        st.session_state["url"] = ""
        st.session_state["OPENAI_API_KEY"] = os.environ["OPENAI_API_KEY"]
        if is_openai_api_key_set():
            st.session_state["youtubequery"] = YoutubeQuery(st.session_state["OPENAI_API_KEY"])
        else:
            st.session_state["youtubequery"] = None

    st.header("🎞 Youtube Vídeo Chatbot")

    if st.text_input("OpenAI API Key", value=st.session_state["OPENAI_API_KEY"], key="input_OPENAI_API_KEY", type="password"):
        if (
            len(st.session_state["input_OPENAI_API_KEY"]) > 0
            and st.session_state["input_OPENAI_API_KEY"] != st.session_state["OPENAI_API_KEY"]
        ):
            # st.session_state["OPENAI_API_KEY"] = st.session_state["input_OPENAI_API_KEY"]
            st.session_state["messages"] = []
            st.session_state["user_input"] = ""
            st.session_state["input_url"] = ""
            st.session_state["youtubequery"] = YoutubeQuery(st.session_state["OPENAI_API_KEY"])

    st.subheader("Adicione o url do Youtube")
    st.text_input("Url Youtube", value=st.session_state["url"], key="input_url", disabled=not is_openai_api_key_set(), on_change=ingest_input)

    st.session_state["ingestion_spinner"] = st.empty()

    # Verifica se o campo de entrada de URL não está vazio
    if st.session_state["input_url"] and len(st.session_state["input_url"].strip()) > 0:
        url = st.session_state["input_url"].strip()
        st.video(url)

    display_messages()
    st.text_input("Faça sua pergunta", key="user_input", disabled=not is_openai_api_key_set(), on_change=process_input)

    st.divider()
    st.markdown("Deves Tecnologia")


if __name__ == "__main__":
    main()