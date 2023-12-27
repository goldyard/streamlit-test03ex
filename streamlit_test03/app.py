import streamlit as st
from streamlit_test03.base.chatbot import ChatBot

if "chatbot" not in st.session_state:
    st.session_state.chatbot = ChatBot()

bot = st.session_state.get("chatbot")
bot.bot_title()
bot.chat()
