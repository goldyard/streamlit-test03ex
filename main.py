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
