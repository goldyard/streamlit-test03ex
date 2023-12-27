import streamlit as st
import threading
from openai import OpenAI
import time


class ChatBot:
    _name = "小智·Zero"
    _lock = threading.RLock()

    def __init__(self, name: str = None):
        if name is not None:
            self._name = name
        else:
            self._name = ChatBot._name
        self.__init_chatbot()

    @property
    def name(self):
        return self._name

    def __init_chatbot(self):
        # 1. Initialize the OpenAI API client
        self._client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        self._assistant_id = st.secrets["OPENAI_ASSISTANT_ID"]
        self._messages = []
        # Maximum allowed messages
        self._max_messages = 1000
        # 2. Create a Thread
        self._thread = self._client.beta.threads.create()

    def bot_title(self):
        st.title(f"{self._name} 我的私人智能助理")
        with st.expander(f"ℹ️ {self._name}"):
            st.caption(f"{self._name} 是一个私人智能助理，由OpenAI Assistants API提供支持。")

    def chat(self):
        for message in self._messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if len(self._messages) >= self._max_messages:
            st.info("对不起，消息太多了，我无法再显示更多了，请节省使用API额度。")
            return

        if prompt := st.chat_input("小智， 你好！"):
            self._messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                full_response = ""
                self.run_message(prompt)
                self.wait_chat_response()
                for response in self._client.beta.threads.messages.list(
                    thread_id=self._thread.id, limit=1
                ).data:
                    full_response += response.content[0].text.value or ""
                    message_placeholder.markdown(full_response + "▌")
                message_placeholder.markdown(full_response)
            self._messages.append({"role": "assistant", "content": full_response})

    def wait_chat_response(self):
        while True:
            time.sleep(2)

            self._run = self._client.beta.threads.runs.retrieve(
                thread_id=self._thread.id, run_id=self._run.id
            )

            if self._run.status == "completed":
                break

    def run_message(self, prompt):
        message = self._client.beta.threads.messages.create(
            thread_id=self._thread.id, role="user", content=prompt
        )

        self._run = self._client.beta.threads.runs.create(
            thread_id=self._thread.id, assistant_id=self._assistant_id
        )
