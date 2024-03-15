import streamlit as st
from applications import chat, markdown, security
from enum import Enum
from dotenv import load_dotenv


class AppChoice(Enum):
    SECURITY = 'Security'
    NOTHING = 'Nothing'


class StateMachine:
    selectbox: str
    currentapp: AppChoice = AppChoice.NOTHING


_appstate = StateMachine


def switch_app(new_app: AppChoice):
    _appstate.currentapp = new_app
    match _appstate.currentapp:
        case AppChoice.SECURITY:
            security.run()
        case _:
            st.text("Here's your nothing:")


def refresh_app():
    st.sidebar.empty()
    st.empty()
    st.sidebar.title("AI Playground")
    # We need to persis the select-box ;)
    _appstate.selectBox = st.sidebar.selectbox(
        'Current App:',
        ('Nothing', 'Security')
    )

    new_app = AppChoice(_appstate.selectBox)
    if new_app != _appstate.currentapp:
        switch_app(AppChoice(new_app))


if __name__ == "__main__":
    load_dotenv()
    refresh_app()
