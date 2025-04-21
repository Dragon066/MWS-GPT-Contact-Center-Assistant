import os

from fake_meta import generate_subscriber
from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    create_engine,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.sql import func

Base = declarative_base()


class Records(Base):
    __tablename__ = "records"

    id = Column(Integer, primary_key=True)
    type = Column(String)
    solved = Column(Boolean, default=False)
    client_meta = Column(JSON, default={})
    crm_summary = Column(JSON, default={})

    chats = relationship("Chats", back_populates="record")


class Chats(Base):
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True)
    content = Column(String)
    role = Column(String)
    created_at = Column(DateTime, default=func.now())

    record_id = Column(Integer, ForeignKey("records.id"))
    record = relationship("Records", back_populates="chats")


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

    def add_data(self, chat_id, type, content, role="user"):
        with self._get_session() as session:
            if not session.query(Records).filter(Records.id == chat_id).first():
                new_data = Records(
                    id=chat_id,
                    type=type,
                    client_meta=generate_subscriber(),
                )
                session.add(new_data)
            new_data_chats = Chats(
                record_id=chat_id,
                content=content,
                role=role,
            )
            session.add(new_data_chats)
            session.commit()

    def get_all_records(self):
        with self._get_session() as session:
            query = session.query(Records)
            return query.all()

    def get_record(self, record_id=None):
        with self._get_session() as session:
            query = session.query(Records).filter(Records.id == record_id)
            return query.first()

    def get_all_messages(self, chat_id=None):
        with self._get_session() as session:
            query = session.query(Chats).filter(Chats.record_id == chat_id)
            return query.all()

    def get_last_chat_messages(self):
        with self._get_session() as session:
            subquery = (
                session.query(
                    Chats.record_id, func.max(Chats.created_at).label("max_created_at")
                )
                .group_by(Chats.record_id)
                .subquery()
            )

            query = (
                session.query(Chats)
                .join(
                    subquery,
                    (Chats.record_id == subquery.c.record_id)
                    & (Chats.created_at == subquery.c.max_created_at),
                )
                .order_by(Chats.record_id)
            )

            return query.all()

    def mark_as_solved(self, chat_id):
        with self._get_session() as session:
            record = session.query(Records).filter(Records.id == chat_id).first()
            if record:
                record.solved = True
                session.commit()
                return True
            return False

    def push_crm_summary(self, chat_id, summary):
        with self._get_session() as session:
            record = session.query(Records).filter(Records.id == chat_id).first()
            if record:
                record.crm_summary = summary
                session.commit()
                return True
            return False

    def execute_raw(self, sql, params=None):
        with self._get_session() as session:
            result = session.execute(sql, params or {})
            return [dict(row) for row in result]
