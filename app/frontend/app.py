from urllib.parse import unquote

import requests
import streamlit as st


def main():
    st.set_page_config(page_title="Чат с клиентом", page_icon="💬", layout="wide")

    # Получаем параметры из URL
    query_params = st.query_params
    chat_id = query_params.get("id", [None])[0]
    operator_name = unquote(query_params.get("operatorName", [""]))
    operator_position = unquote(query_params.get("operatorPosition", [""]))

    if not chat_id:
        st.error("Не указан ID чата в параметрах URL")
        return

    # Получаем историю чата из БД
    chat_history = requests.get(f"http://crm:8003/api/chat?id_chat={chat_id}").json()

    if not chat_history:
        st.error(f"Чат с ID {chat_id} не найден")
        return

    # Боковая панель с информацией
    with st.sidebar:
        st.header("Оператор")
        if operator_name:
            st.write(f"**Имя:** {operator_name}")
            st.write(f"**Должность:** {operator_position}")
        else:
            st.warning("Информация об операторе не указана")

        st.divider()

        st.header("Информация о чате")
        st.write(f"**ID чата:** {chat_id}")
        st.write("**Тип обращения:** chat/email")

        st.divider()

        st.header("Действия")
        if st.button("Пометить как решенное"):
            r = requests.get(f"http://crm:8003/api/mark_as_solved?id_chat={chat_id}")
            st.success("Статус обновлен")

    # Основное содержимое - история чата
    st.title(f"Чат #{chat_id}")

    for message in chat_history:
        # Определяем стиль сообщения в зависимости от типа
        if message["role"] == "user":
            with st.chat_message("user"):
                st.write(message["content"])
                st.caption(f"{message['created_at']} (клиент)")
        else:
            with st.chat_message("assistant"):
                st.write(message["content"])
                st.caption(f"{message['created_at']} (оператор)")

    # Форма для ответа
    with st.form("reply_form"):
        reply_text = st.text_area("Ваш ответ", height=100)
        submitted = st.form_submit_button("Отправить")
        if submitted and reply_text:
            r = requests.get(
                f"http://crm:8003/api/push_record?id={chat_id}&type={'chat'}&content={reply_text}&role=assistent"
            )
            st.success("Ответ отправлен")
            st.rerun()


if __name__ == "__main__":
    main()
