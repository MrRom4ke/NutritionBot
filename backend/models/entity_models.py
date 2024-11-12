from sqlalchemy import Column, Integer, String, ForeignKey, UUID, ARRAY, JSON, UniqueConstraint
from sqlalchemy.orm import relationship
from db.base import Base

class EntityModel(Base):
    __tablename__ = "entities"

    message_id = Column(UUID(as_uuid=True), ForeignKey('messages.id', ondelete="CASCADE"), primary_key=True)  # Связь с сообщением
    action = Column(String, nullable=True)  # Действие, например, "гулял"
    object = Column(String, nullable=True)  # Объект действия, например, "сигарету"
    specific_object = Column(String, nullable=True)  # Специфический объект, например, "гороховый суп"
    location = Column(String, nullable=True)  # Место, например, "парк"
    quantity = Column(String, nullable=True)  # Количество, например, "30 минут"
    size = Column(String, nullable=True)  # Размер или порция, например, "маленькая порция"
    conditions = Column(String, nullable=True)  # Условия, например, "без сахара"
    duration = Column(String, nullable=True)  # Продолжительность, например, "30 минут"
    time = Column(String, nullable=True)  # Время, например, "07:30" или "утро"
    date = Column(String, nullable=True)  # Дата, например, "2024-11-01" или "понедельник"
    theme_id = Column(Integer, ForeignKey("topics.id", ondelete="SET NULL"), nullable=True)  # Ссылка на тему, если определена
    entity_requirements_id = Column(Integer, ForeignKey("entity_requirements.id"), nullable=True) # Ссылка на требования, если определена

    # Связи
    message = relationship("MessageModel", back_populates="entities")
    theme = relationship("Topic")
    entity_requirement = relationship("EntityRequirement")


class Topic(Base):
    __tablename__ = "topics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)  # Название темы, уникальное

    # Связь с таблицей 'keywords' через тему
    keys = relationship("Keyword", back_populates="topic", cascade="all, delete-orphan")


class Keyword(Base):
    __tablename__ = "keywords"

    id = Column(Integer, primary_key=True, autoincrement=True)
    word = Column(String, nullable=False)  # Ключевое слово для темы
    topic_id = Column(Integer, ForeignKey("topics.id", ondelete="CASCADE"), nullable=False)  # Ссылка на тему

    # Связь с моделью 'Topic'
    topic = relationship("Topic", back_populates="keys", foreign_keys=[topic_id])

class EntityRequirement(Base):
    __tablename__ = "entity_requirements"

    id = Column(Integer, primary_key=True, autoincrement=True)
    action = Column(String, nullable=True)
    object = Column(String, nullable=True)
    required_fields = Column(ARRAY(String), nullable=True)
    questions = Column(JSON, nullable=True)

    __table_args__ = (UniqueConstraint('action', 'object', name='unique_action_object'),)