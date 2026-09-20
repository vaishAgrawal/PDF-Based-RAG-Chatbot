"""Streamlit client for the document RAG API."""

import json
from datetime import datetime
from html import escape
from pathlib import Path
from uuid import uuid4

import requests
import streamlit as st

API_URL = "http://127.0.0.1:8000"
HISTORY_FILE = Path(__file__).with_name("chat_history.json")


def load_chats() -> list[dict]:
    if not HISTORY_FILE.exists():
        return []
    try:
        return json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []


def save_chats(chats: list[dict]) -> None:
    HISTORY_FILE.write_text(json.dumps(chats, ensure_ascii=False, indent=2), encoding="utf-8")


def new_chat() -> dict:
    return {
        "id": uuid4().hex,
        "title": "New conversation",
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "messages": [],
    }

st.set_page_config(
    page_title="Document RAG", page_icon="📄", layout="centered", initial_sidebar_state="expanded"
)
st.markdown(
    """
    <style>
    .stApp { background: #f5f6fc; }
    [data-testid="stHeader"] { background: transparent; }
    .block-container { max-width: 760px; padding: .35rem 1rem 6rem; }
    [data-testid="stSidebar"] { background: linear-gradient(180deg, #302b69 0%, #5149a5 48%, #7466d8 100%); border-right: 1px solid #423b8e; }
    [data-testid="stSidebar"] > div:first-child { padding-top: 1rem; }
    [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 { color: #ffffff; margin: .25rem 0 .45rem; }
    [data-testid="stSidebar"] [data-testid="stCaptionContainer"] { color: #e2e4ff; }
    [data-testid="stSidebar"] hr { border-color: rgba(255, 255, 255, .22); margin: .35rem 0; }
    [data-testid="stSidebarCollapseButton"] button,
    [data-testid="stSidebarNavCollapseButton"] button,
    button[aria-label="Close sidebar"], button[aria-label="Open sidebar"] { color: #ffffff !important; background: #635bdb !important; border: 1px solid #a9a2ff !important; border-radius: 8px; }
    [data-testid="stSidebarCollapseButton"] button:hover,
    [data-testid="stSidebarNavCollapseButton"] button:hover,
    button[aria-label="Close sidebar"]:hover, button[aria-label="Open sidebar"]:hover { color: #302b69 !important; background: #ffffff !important; }
    [data-testid="stSidebar"] .stButton > button { border-radius: 7px; border: 1px solid rgba(255, 255, 255, .35); color: #ffffff; background: rgba(255, 255, 255, .12); margin: .08rem 0; }
    [data-testid="stSidebar"] .stButton > button:hover { color: #302b69; background: #ffffff; }
    [data-testid="stSidebar"] .stPopover button { color: #ffffff; border: 0; background: transparent; padding: 0 .35rem; }
    .chat-header { display: flex; align-items: center; gap: .8rem; border-bottom: 1px solid #dde0ee; padding: .3rem 0 .7rem; margin-bottom: .8rem; }
    .bot-avatar { display: grid; place-items: center; width: 48px; height: 48px; border-radius: 50%; background: #635bdb; color: white; font-size: 1.5rem; }
    .chat-header h1 { color: #202124; font-size: 1.35rem; font-weight: 650; margin: 0; }
    .chat-header p { color: #73788c; font-size: .88rem; margin: .15rem 0 0; }
    .online { color: #34b47c; font-size: .85rem; }
    .welcome { color: #73788c; text-align: center; padding: 6rem 1rem; }
    .message-row { display: flex; gap: .6rem; margin: 1.1rem 0; align-items: flex-start; }
    .message-row.user { justify-content: flex-end; }
    .message-avatar { flex: 0 0 34px; display: grid; place-items: center; width: 34px; height: 34px; border-radius: 50%; background: #635bdb; color: white; font-size: 1rem; }
    .bubble { max-width: 78%; padding: .8rem 1rem; border-radius: 16px; color: #202124; line-height: 1.55; background: #ffffff; box-shadow: 0 3px 10px rgba(66, 70, 105, .08); }
    .user .bubble { color: #ffffff; background: #635bdb; border-bottom-right-radius: 5px; }
    .assistant .bubble { border-bottom-left-radius: 5px; }
    [data-testid="stFileUploader"] { padding: 0; }
    .stButton > button { border-radius: 8px; }
    [data-testid="stChatInput"] { background: #ffffff; border: 1px solid #dfe2ef; border-radius: 18px; }
    </style>
    """,
    unsafe_allow_html=True,
)

if "chats" not in st.session_state:
    st.session_state.chats = load_chats()
if "active_chat_id" not in st.session_state:
    first_chat = st.session_state.chats[0] if st.session_state.chats else new_chat()
    if not st.session_state.chats:
        st.session_state.chats.append(first_chat)
        save_chats(st.session_state.chats)
    st.session_state.active_chat_id = first_chat["id"]

active_chat = next(
    chat for chat in st.session_state.chats if chat["id"] == st.session_state.active_chat_id
)

with st.sidebar:
    st.markdown("## 📄 Document RAG")

    st.markdown("### Upload documents")
    uploaded_file = st.file_uploader("Add a PDF", type=["pdf"])
    index_clicked = st.button("Upload and index", disabled=not uploaded_file, use_container_width=True, type="primary")
    if index_clicked:
        with st.spinner("Reading document..."):
            try:
                response = requests.post(
                    f"{API_URL}/upload",
                    files={"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")},
                    timeout=120,
                )
                if response.ok:
                    st.success(f"{response.json()['chunks_indexed']} sections indexed")
                else:
                    st.error(response.text)
            except requests.RequestException:
                st.error("The document service is unavailable. Start the backend and try again.")

    if st.button("＋ New chat", use_container_width=True):
        chat = new_chat()
        st.session_state.chats.insert(0, chat)
        st.session_state.active_chat_id = chat["id"]
        save_chats(st.session_state.chats)
        st.rerun()

    if st.button("Delete all chats", use_container_width=True):
        st.session_state.chats = [new_chat()]
        st.session_state.active_chat_id = st.session_state.chats[0]["id"]
        save_chats(st.session_state.chats)
        st.rerun()

    st.markdown("### History")
    for chat in st.session_state.chats:
        history_column, menu_column = st.columns([5, 1])
        with history_column:
            if st.button(chat["title"], key=f"chat-{chat['id']}", use_container_width=True):
                st.session_state.active_chat_id = chat["id"]
                st.rerun()
        with menu_column:
            with st.popover("⋯", use_container_width=True):
                renamed_title = st.text_input("Chat name", value=chat["title"], key=f"name-{chat['id']}")
                if st.button("Save name", key=f"save-{chat['id']}", use_container_width=True):
                    chat["title"] = renamed_title.strip() or "New conversation"
                    save_chats(st.session_state.chats)
                    st.rerun()
                if st.button("Delete", key=f"delete-{chat['id']}", use_container_width=True):
                    st.session_state.chats = [item for item in st.session_state.chats if item["id"] != chat["id"]]
                    if not st.session_state.chats:
                        st.session_state.chats = [new_chat()]
                    if st.session_state.active_chat_id == chat["id"]:
                        st.session_state.active_chat_id = st.session_state.chats[0]["id"]
                    save_chats(st.session_state.chats)
                    st.rerun()

st.markdown(
    '<div class="chat-header"><div class="bot-avatar">●</div><div><h1>Ask your questions</h1><p>I’ll find answers in your documents <span class="online">●</span></p></div></div>',
    unsafe_allow_html=True,
)

if not active_chat["messages"]:
    st.markdown('<div class="welcome">Hello!<br>Ask me anything about your documents.</div>', unsafe_allow_html=True)

for message in active_chat["messages"]:
    content = escape(message["content"]).replace("\n", "<br>")
    if message["role"] == "user":
        st.markdown(f'<div class="message-row user"><div class="bubble">{content}</div></div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="message-row assistant"><div class="message-avatar">●</div><div class="bubble">{content}</div></div>', unsafe_allow_html=True)

question = st.chat_input("Ask something about your documents...")
if question:
    with st.spinner("Searching..."):
        try:
            response = requests.post(
                f"{API_URL}/ask", json={"question": question}, timeout=120
            )
            if response.ok:
                result = response.json()
                if active_chat["title"] == "New conversation":
                    active_chat["title"] = question[:40]
                active_chat["messages"].extend(
                    [
                        {"role": "user", "content": question},
                        {"role": "assistant", "content": result["answer"]},
                    ]
                )
                save_chats(st.session_state.chats)
                st.rerun()
            else:
                st.error(response.text)
        except requests.RequestException:
            st.error("The document service is unavailable. Start the backend and try again.")
