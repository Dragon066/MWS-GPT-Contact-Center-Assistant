import os

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Integer,
    String,
    create_engine,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func

Base = declarative_base()


class Requests(Base):
    __tablename__ = "requests"

    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer)
    agent_statuses = Column(JSON, default={})
    actions = Column(JSON, default=[])
    emotion = Column(String, default=None)
    created_at = Column(DateTime, default=func.now())


class ChatSummary(Base):
    __tablename__ = "chatsummary"

    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer)
    intent = Column(String, default=None)
    short_chat_summary = Column(String, default=None)
    emotion_summary = Column(String, default=None)
    quality_summary = Column(JSON, default=None)
    crm_summary = Column(JSON, default=None)
    solved = Column(Boolean, default=False)


DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "postgres")
DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "")


class Database:
    def __init__(self):
        dsn = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

        self.engine = create_engine(dsn, pool_pre_ping=True)
        self.Session = sessionmaker(bind=self.engine)
        Base.metadata.create_all(self.engine)

    def _get_session(self):
        return self.Session()

    def close(self):
        self.Session.remove()

    def add_new_request(self, id_chat):
        with self._get_session() as session:
            if (
                not session.query(ChatSummary)
                .filter(ChatSummary.id_chat == id_chat)
                .first()
            ):
                new_data_chatsummary = ChatSummary(
                    chat_id=id_chat,
                )
                session.add(new_data_chatsummary)

            new_data_request = Requests(
                chat_id=id_chat,
            )
            session.add(new_data_request)
            session.commit()
            return new_data_request.id

    def update_request_status(self, id_request: int, agent: str, status: str):
        with self._get_session() as session:
            request = session.query(Requests).filter(Requests.id == id_request).first()
            if not request:
                raise ValueError(f"Request with id {id_request} not found")

            current_statuses = request.agent_statuses

            current_statuses[agent] = status

            request.agent_statuses = current_statuses

            session.commit()

    def update_request_actions(self, id_request: int, actions: dict):
        with self._get_session() as session:
            request = session.query(Requests).filter(Requests.id == id_request).first()
            if not request:
                raise ValueError(f"Request with id {id_request} not found")

            request.actions = actions

            session.commit()

    def update_request_emotion(self, id_request: int, emotion: str):
        with self._get_session() as session:
            request = session.query(Requests).filter(Requests.id == id_request).first()
            if not request:
                raise ValueError(f"Request with id {id_request} not found")

            request.emotion = emotion

            session.commit()

    def update_chat_summary_intent(self, id_chat: int, intent: str):
        with self._get_session() as session:
            request = (
                session.query(ChatSummary)
                .filter(ChatSummary.chat_id == id_chat)
                .first()
            )
            if not request:
                raise ValueError(f"Chat with id {id_chat} not found")

            request.intent = intent

            session.commit()

    def update_chat_summary_short_summary(self, id_chat: int, short_summary: str):
        with self._get_session() as session:
            request = (
                session.query(ChatSummary)
                .filter(ChatSummary.chat_id == id_chat)
                .first()
            )
            if not request:
                raise ValueError(f"Chat with id {id_chat} not found")

            request.short_chat_summary = short_summary

            session.commit()

    def update_chat_summary_emotion(self, id_chat: int, emotion: str):
        with self._get_session() as session:
            request = (
                session.query(ChatSummary)
                .filter(ChatSummary.chat_id == id_chat)
                .first()
            )
            if not request:
                raise ValueError(f"Chat with id {id_chat} not found")

            request.emotion_summary = emotion

            session.commit()

    def update_chat_quality(self, id_chat: int, quality: dict):
        with self._get_session() as session:
            request = (
                session.query(ChatSummary)
                .filter(ChatSummary.chat_id == id_chat)
                .first()
            )
            if not request:
                raise ValueError(f"Chat with id {id_chat} not found")

            request.quality_summary = quality

            session.commit()

    def update_chat_crm(self, id_chat: int, crm_summary: dict):
        with self._get_session() as session:
            request = (
                session.query(ChatSummary)
                .filter(ChatSummary.chat_id == id_chat)
                .first()
            )
            if not request:
                raise ValueError(f"Chat with id {id_chat} not found")

            request.crm_summary = crm_summary

            session.commit()

    def mark_as_solved(self, id_chat):
        with self._get_session() as session:
            record = (
                session.query(ChatSummary)
                .filter(ChatSummary.chat_id == id_chat)
                .first()
            )
            if record:
                record.solved = True
                session.commit()
                return True
            return False

    def get_request_data(self, request_id: int):
        with self._get_session() as session:
            request = session.query(Requests).filter(Requests.id == request_id).first()
            if not request:
                raise ValueError(f"Request with id {request_id} not found")

            return request

    def get_chat_summary_data(self, chat_id: int):
        with self._get_session() as session:
            request = (
                session.query(ChatSummary)
                .filter(ChatSummary.chat_id == chat_id)
                .first()
            )
            if not request:
                raise ValueError(f"Chat with id {chat_id} not found")

            return request
