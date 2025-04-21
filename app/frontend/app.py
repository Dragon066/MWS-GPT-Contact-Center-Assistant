from datetime import datetime
from urllib.parse import unquote

import requests
import streamlit as st

st.set_page_config(page_title="Чат с клиентом", page_icon="💬", layout="wide")

hide_streamlit_style = """
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        .stStatusWidget {display: none;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

if "previous_data" not in st.session_state:
    st.session_state.previous_data = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "actions" not in st.session_state:
    st.session_state.actions = []
if "agent_statuses" not in st.session_state:
    st.session_state.agent_statuses = {}
if "request_id" not in st.session_state:
    st.session_state.request_id = None
if "chat_info" not in st.session_state:
    st.session_state.chat_info = {}
if "is_solved" not in st.session_state:
    st.session_state.is_solved = False
if "chat_id" not in st.session_state:
    st.session_state.chat_id = None
if "llm_chat_history" not in st.session_state:
    st.session_state.llm_chat_history = []


def main():
    query_params = st.query_params
    chat_id = query_params.get("id", [None])
    st.session_state.chat_id = chat_id
    operator_name = unquote(query_params.get("operatorName", [""]))
    operator_position = unquote(query_params.get("operatorPosition", [""]))

    record = requests.get(f"http://crm:8003/api/records?id_chat={chat_id}").json()

    client_response = record["client_meta"]
    st.session_state.is_solved = record["solved"]

    if not chat_id:
        st.error("Не указан ID чата в параметрах URL")
        return

    if not st.session_state.request_id:
        response = requests.get(
            f"http://backend:8002/push_request?chat_id={chat_id}&operatorName={operator_name}&operatorPosition={operator_position}"
        )
        st.session_state.request_id = response.json().get("request_id")

    with st.sidebar:
        get_model_status()
        col1, col2 = st.columns([0.5, 0.5])
        with col1:
            st.markdown(
                f"""
                <div style="border:1px solid #ddd; padding:10px; border-radius:8px; background-color: #282832; margin-bottom:10px; min-height:350px">
                    <h3 style="font-weight: bold">Оператор</h3>
                    <p><strong>Имя:</strong> {operator_name or "Не указано"}</p>
                    <p><strong>Должность:</strong> {operator_position or "Не указана"}</p>
                </div>
            """,
                unsafe_allow_html=True,
            )

        with col2:
            st.markdown(
                f"""
                <div style="border:1px solid #ddd; padding:10px; border-radius:8px; background-color: #282832; margin-bottom:10px; min-height:350px">
                    <h3 style="font-weight: bold">Клиент</h3>
                    <p><strong>Номер телефона:</strong><span style="white-space: nowrap;"> {client_response["Номер телефона"]}</span></p>
                    <p><strong>Абонент МТС:</strong> {client_response["Абонент МТС"]}</p>
                    <p><strong>Тариф:</strong> {client_response["Тариф"]}</p>
                    <p><strong>Устройство:</strong> {client_response["Устройство"]}</p>
                    <p><strong>МТС Premium:</strong> {client_response["МТС Premium"]}</p>
                </div>
            """,
                unsafe_allow_html=True,
            )

        st.divider()
        render_chat_info(chat_id)
        st.divider()
        render_llm_chat(chat_id)
        render_model_controls()

    fetch_chat_data(chat_id, operator_name, operator_position)
    render_chat_messages()
    if not st.session_state.is_solved:
        render_suggestions()
        handle_message_input(chat_id)
    else:
        st.warning("⚠️ Чат закрыт. Новые сообщения нельзя отправить.")


@st.fragment(run_every=1)
def render_llm_chat(chat_id):
    st.header("Чат с моделью")
    with st.container(height=200, border=True):
        for msg in st.session_state.llm_chat_history:
            with st.chat_message(
                name=msg["role"], avatar="💬" if msg["role"] == "user" else "🤖"
            ):
                st.markdown(msg["content"])

    if prompt := st.chat_input("Введите запрос для модели", key="llm_chat_input"):
        try:
            with st.spinner("Модель генерирует ответ..."):
                response = requests.get(
                    f"http://backend:8002/llmquery?chat_id={chat_id}&query={prompt}"
                )

                if response.status_code == 200:
                    result = response.json().get("result", "Нет ответа от модели.")
                else:
                    result = "Ошибка при получении ответа от модели."

                st.session_state.llm_chat_history.append(
                    {"role": "user", "content": prompt}
                )
                st.session_state.llm_chat_history.append(
                    {"role": "assistant", "content": result}
                )

        except Exception as e:
            st.error(f"Ошибка запроса: {e}")
            st.session_state.llm_chat_history = st.session_state.llm_chat_history[:-1]


@st.fragment(run_every=1)
def get_model_status():
    if st.session_state.agent_statuses:
        circle_styles = """
        <style>
        .status-circles {
            position: static;
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }
        .circle {
            width: 20px;
            height: 20px;
            border-radius: 50%;
            display: inline-block;
            position: relative;
        }
        .circle[title]::after {
            content: attr(title);
            position: absolute;
            bottom: 125%;
            left: 50%;
            transform: translateX(-50%);
            background: #333;
            color: #fff;
            padding: 4px 8px;
            border-radius: 4px;
            white-space: nowrap;
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.2s ease;
            font-size: 12px;
            z-index: 100;
        }
        .circle[title]:hover::after {
            opacity: 1;
        }
        </style>
        """

        circle_html = '<div class="status-circles">'
        for agent, status in st.session_state.agent_statuses.items():
            if status == "done":
                color = "#4CAF50"  # Зеленый
            elif status == "in work":
                color = "#FFC107"  # Желтый
            else:
                color = "#F44336"  # Красный

            circle_html += f'<div class="circle" title="{agent}" style="background-color: {color};"></div>'
        circle_html += "</div>"

        st.markdown(circle_styles + circle_html, unsafe_allow_html=True)


@st.fragment(run_every=1)
def fetch_chat_data(chat_id, operator_name, operator_position):
    history_response = requests.get(f"http://crm:8003/api/chat?id_chat={chat_id}")
    if "last_user_message_id" not in st.session_state:
        last_msg = next(
            (m for m in reversed(st.session_state.chat_history) if m["role"] == "user"),
            None,
        )
        st.session_state.last_user_message_id = last_msg.get("id") if last_msg else None

    if history_response.status_code == 200:
        new_history = history_response.json()

        last_user_msg = next(
            (msg for msg in reversed(new_history) if msg["role"] == "user"), None
        )

    if last_user_msg:
        last_id = last_user_msg.get("id")
        if last_id != st.session_state.get("last_user_message_id"):
            response = requests.get(
                f"http://backend:8002/push_request?chat_id={chat_id}&operatorName={operator_name}&operatorPosition={operator_position}"
            )
            st.session_state.request_id = response.json().get("request_id")
            st.session_state.last_user_message_id = last_id

        if new_history != st.session_state.chat_history:
            st.session_state.chat_history = new_history

    info_response = requests.get(f"http://backend:8002/get_chat_info?chat_id={chat_id}")
    if info_response.status_code == 200:
        new_info = info_response.json()
        if new_info != st.session_state.chat_info:
            st.session_state.chat_info = new_info

    if st.session_state.request_id:
        actions_response = requests.get(
            f"http://backend:8002/get_request_info?request_id={st.session_state.request_id}"
        )
        if actions_response.status_code == 200:
            new_data = actions_response.json()
            if new_data.get("actions") != st.session_state.actions:
                st.session_state.actions = new_data.get("actions", [])
            if new_data.get("agent_statuses") != st.session_state.agent_statuses:
                st.session_state.agent_statuses = new_data.get("agent_statuses", {})


@st.fragment(run_every=1)
def render_chat_info(chat_id):
    st.header("Информация о чате")
    st.write(f"**ID чата**: {chat_id}")
    st.write(f"**Статус**: {'Решен' if st.session_state.is_solved else 'Активен'}")

    if st.session_state.chat_info.get("intent"):
        st.write(f"**Тема обращения**: {st.session_state.chat_info['intent']}")

    emotion = st.session_state.chat_info.get("emotion_summary", "нейтральное")
    emotion_avatars = {
        "радость": "😄",
        "нейтральное": "😐",
        "гнев": "😠",
        "грусть": "😔",
    }
    st.write(f"**Настроение клиента**: {emotion} {emotion_avatars.get(emotion, '🙂')}")

    if summary := st.session_state.chat_info.get("short_chat_summary"):
        st.write(f"**Краткое описание**: {summary}")


@st.fragment(run_every=1)
def render_model_controls():
    st.divider()
    if not st.session_state.is_solved:
        if st.button("Пометить как решенное"):
            requests.get(
                f"http://crm:8003/api/mark_as_solved?id_chat={st.session_state.chat_id}"
            )
            requests.get(
                f"http://backend:8002/push_solved_record?chat_id={st.session_state.chat_id}"
            )
            st.session_state.is_solved = True
            st.success("Чат помечен как решенный")
            st.rerun()
    else:
        st.warning("Чат уже помечен как решенный")


@st.fragment(run_every=1)
def render_chat_messages():
    emotion = st.session_state.get("chat_info", {}).get(
        "emotion_summary", "нейтральное"
    )
    user_avatar = {
        "радость": "😄",
        "нейтральное": "😐",
        "гнев": "😠",
        "грусть": "😔",
    }.get(emotion, "🙂")

    with st.container(height=500, border=True):
        st.markdown(
            """
        <style>
            .chat-messages {
                height: calc(100% - 20px);
                overflow-y: auto;
                padding: 10px;
                margin-bottom: 10px;
            }
            .message {
                margin-bottom: 16px;
            }
            .user-message {
                text-align: right;
            }
            .bot-message {
                text-align: left;
            }
            .message-bubble {
                display: inline-block;
                max-width: 70%;
                padding: 12px 16px;
                border-radius: 18px;
                line-height: 1.4;
                word-wrap: break-word;
            }
            .user-bubble {
                background-color: #007bff;
                color: white;
                border-bottom-right-radius: 4px;
            }
            .bot-bubble {
                background-color: #f1f1f1;
                color: #333;
                border-bottom-left-radius: 4px;
            }
            .message-sender {
                font-weight: bold;
                margin-bottom: 4px;
                font-size: 0.9em;
            }
            .message-time {
                font-size: 0.75em;
                color: #666;
                margin-top: 4px;
            }
        </style>
        """,
            unsafe_allow_html=True,
        )

        st.markdown('<div class="chat-messages">', unsafe_allow_html=True)

        for message in st.session_state.get("chat_history", []):
            if message["role"] == "user":
                st.markdown(
                    f"""
                <div class="message user-message">
                    <div class="message-sender">Клиент {user_avatar}</div>
                    <div class="message-bubble user-bubble">{message["content"]}</div>
                    <div class="message-time">{message.get("created_at", "")}</div>
                </div>
                """,
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f"""
                <div class="message bot-message">
                    <div class="message-sender">🤖 Оператор</div>
                    <div class="message-bubble bot-bubble">{message["content"]}</div>
                    <div class="message-time">{datetime.fromisoformat(message.get("created_at", "")).strftime("%d.%m.%Y, %H:%M:%S")}</div>
                </div>
                """,
                    unsafe_allow_html=True,
                )

        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown(
            """
        <script>
        // Ждем пока все элементы отрендерятся
        setTimeout(function() {
            const chatMessages = document.querySelector('.chat-messages');
            if (chatMessages) {
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }
        }, 100);
        </script>
        """,
            unsafe_allow_html=True,
        )


@st.fragment(run_every=1)
def render_suggestions():
    if st.session_state.actions:
        with st.container(height=100, border=True):
            st.markdown("Рекомендованные ответы:")
            cols = st.columns(2)
            for i, suggestion in enumerate(st.session_state.actions):
                with cols[i % 2]:
                    if st.button(
                        suggestion["title"],
                        key=f"suggestion_{i}",
                        use_container_width=True,
                    ):
                        st.session_state.reply_text = suggestion["text"]
                        st.rerun(scope="fragment")


@st.fragment(run_every=1)
def handle_message_input(chat_id):
    reply = st.text_area(
        "Ваш ответ",
        value=st.session_state.get("reply_text", ""),
        height=120,
        placeholder="Введите текст или выберите вариант выше...",
        key="reply_input",
    )

    if st.button("Отправить ответ", type="primary"):
        if reply.strip():
            try:
                requests.get(
                    "http://crm:8003/api/push_record",
                    params={
                        "id": chat_id,
                        "type": "chat",
                        "content": reply,
                        "role": "assistant",
                    },
                )
                st.session_state.reply_text = ""
                st.rerun()
            except Exception as e:
                st.error(f"Ошибка отправки: {str(e)}")
        else:
            st.warning("Введите текст сообщения")


if __name__ == "__main__":
    main()
