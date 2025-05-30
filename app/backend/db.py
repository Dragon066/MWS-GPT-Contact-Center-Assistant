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
    chat_length = Column(Integer)
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
    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self):
        dsn = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

        self.engine = create_engine(dsn, pool_pre_ping=True)
        self.Session = sessionmaker(bind=self.engine)
        Base.metadata.create_all(self.engine)

    def _get_session(self):
        return self.Session()

    def close(self):
        self.Session.remove()

    def add_new_request(self, chat_id, chat_length: int) -> tuple[int, bool]:
        with self._get_session() as session:
            if (
                not session.query(ChatSummary)
                .filter(ChatSummary.chat_id == chat_id)
                .first()
            ):
                new_data_chatsummary = ChatSummary(
                    chat_id=chat_id,
                )
                session.add(new_data_chatsummary)

            existing_request = (
                session.query(Requests)
                .filter(
                    Requests.chat_id == chat_id,
                    Requests.chat_length == chat_length,
                )
                .first()
            )

            if existing_request:
                return existing_request.id, False

            new_data_request = Requests(
                chat_id=chat_id,
                chat_length=chat_length,
            )
            session.add(new_data_request)
            session.commit()
            return new_data_request.id, True

    def get_last_request(self, chat_id) -> int:
        with self._get_session() as session:
            if (
                not session.query(ChatSummary)
                .filter(ChatSummary.chat_id == chat_id)
                .first()
            ):
                return {"error": f"no chat #{chat_id}"}

            existing_request = (
                session.query(Requests)
                .filter(
                    Requests.chat_id == chat_id,
                )
                .order_by(Requests.id.desc())
                .first()
            )

            return existing_request.id

    def update_request_status(self, request_id: int, agent: str, status: str):
        with self._get_session() as session:
            request = session.query(Requests).filter(Requests.id == request_id).first()
            if not request:
                raise ValueError(f"Request with id {request_id} not found")

            current_statuses = dict(request.agent_statuses)

            current_statuses[agent] = status

            request.agent_statuses = current_statuses

            session.commit()

    def update_request_actions(self, request_id: int, actions: dict):
        with self._get_session() as session:
            request = session.query(Requests).filter(Requests.id == request_id).first()
            if not request:
                raise ValueError(f"Request with id {request_id} not found")

            request.actions = actions

            session.commit()

    def update_request_emotion(self, request_id: int, emotion: str):
        with self._get_session() as session:
            request = session.query(Requests).filter(Requests.id == request_id).first()
            if not request:
                raise ValueError(f"Request with id {request_id} not found")

            request.emotion = emotion

            session.commit()

    def update_chat_summary_intent(self, chat_id: int, intent: str):
        with self._get_session() as session:
            request = (
                session.query(ChatSummary)
                .filter(ChatSummary.chat_id == chat_id)
                .first()
            )
            if not request:
                raise ValueError(f"Chat with id {chat_id} not found")

            request.intent = intent

            session.commit()

    def update_chat_summary_short_summary(self, chat_id: int, short_summary: str):
        with self._get_session() as session:
            request = (
                session.query(ChatSummary)
                .filter(ChatSummary.chat_id == chat_id)
                .first()
            )
            if not request:
                raise ValueError(f"Chat with id {chat_id} not found")

            request.short_chat_summary = short_summary

            session.commit()

    def update_chat_summary_emotion(self, chat_id: int, emotion: str):
        with self._get_session() as session:
            request = (
                session.query(ChatSummary)
                .filter(ChatSummary.chat_id == chat_id)
                .first()
            )
            if not request:
                raise ValueError(f"Chat with id {chat_id} not found")

            request.emotion_summary = emotion

            session.commit()

    def update_chat_quality(self, chat_id: int, quality: dict):
        with self._get_session() as session:
            request = (
                session.query(ChatSummary)
                .filter(ChatSummary.chat_id == chat_id)
                .first()
            )
            if not request:
                raise ValueError(f"Chat with id {chat_id} not found")

            request.quality_summary = quality

            session.commit()

    def update_chat_crm(self, chat_id: int, crm_summary: dict):
        with self._get_session() as session:
            request = (
                session.query(ChatSummary)
                .filter(ChatSummary.chat_id == chat_id)
                .first()
            )
            if not request:
                raise ValueError(f"Chat with id {chat_id} not found")

            request.crm_summary = crm_summary

            session.commit()

    def mark_as_solved(self, chat_id):
        with self._get_session() as session:
            record = (
                session.query(ChatSummary)
                .filter(ChatSummary.chat_id == chat_id)
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
