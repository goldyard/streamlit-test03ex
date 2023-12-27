# 【分享】Streamlit + Assistants API  Chatbot - 外发版

终于把整个Chatbot项目的训练过程完整记录如下, 可以作为一个练手项目， 每天重写一下， 用来训练肌肉记忆和手感。 

# 搭建项目框架

首先需要自己在openai.com创建assistant， 取得assistant id 和 api key， 分别填入.streamlit/secrets.toml文件中：

安装python环境并配置key和id

```bash
apt-get update && apt install python3.11 -y
pip3 install poetry --break-system-packages
poetry config virtualenvs.in-project true
poetry new streamlit-test03 && cd streamlit-test03
poetry add streamlit watchdog openai
mkdir .streamlit
echo 'OPENAI_API_KEY = "sk-xxx"' > .streamlit/secrets.toml
echo 'OPENAI_ASSISTANT_ID = "asst_astxxx"' >> .streamlit/secrets.toml
code .
```

pyproject.toml

```toml
[tool.poetry.scripts]
start = "main:main"
```

main.py

```python
from streamlit.web import bootstrap
from streamlit import config as _config

def main():
    _config.set_option("server.headless", True)
    _config.set_option("server.port", 8501)
    bootstrap.run(
        main_script_path="streamlit_test03/app.py",
        command_line="",
        args=[],
        flag_options={},
    )
```

app.py

```python
import streamlit as st
from streamlit_test03.base.chatbot import ChatBot

if "chatbot" not in st.session_state:
    st.session_state.chatbot = ChatBot()

bot = st.session_state.get("chatbot")
bot.bot_title()
bot.chat()
```

chatbot.py

```python
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
            with st.chat_message[message["role"]]:
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
```

启动程序

```bash
poetry install
start
```

Git账号配置及ubuntu服务器部署

```bash
git config --global credential.credentialStore plaintext
git config --global credential.helper store
git clone https://github.com/goldyard/streamlit-test03ex.git && cd streamlit-test03ex
apt-get update && apt install python3.11 -y
pip3 install poetry --break-system-packages
poetry config virtualenvs.in-project true
poetry install
source .venv/bin/activate
start
```

# 参考文档

1. Streamlit文档库
    
    [Streamlit Docs](https://docs.streamlit.io/)
    
2. OpenAI Assistants API Document
    [OpenAI Assistants API](https://platform.openai.com/docs/assistants/overview)
