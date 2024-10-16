import uuid

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy import Column, String, Float, Date, DateTime, Index, ForeignKey, UniqueConstraint, func

from db.base import Base


class IndicatorModel(Base):
    __tablename__ = 'indicators'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=True)
    measurement_type = Column(String, nullable=False)
    theme = Column(String, nullable=False)

    collections = relationship('IndicatorCollectionModel', back_populates='indicator')
    daily_indicators = relationship('DailyIndicatorModel', back_populates='indicator')

class IndicatorCollectionModel(Base):
    __tablename__ = 'indicator_collections'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    collection_time = Column(DateTime, nullable=False, default=func.now())
    indicator_id = Column(UUID(as_uuid=True), ForeignKey('indicators.id'), nullable=False)
    value = Column(Float, nullable=True)

    user = relationship('UserModel', back_populates='collections')
    indicator = relationship('IndicatorModel', back_populates='collections')

class DailyIndicatorModel(Base):
    __tablename__ = 'daily_indicators'
    __table_args__ = (
        UniqueConstraint('user_id', 'date', 'indicator_id', name='uix_user_date_indicator'),
        Index('idx_user_date', 'user_id', 'date'),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    date = Column(Date, nullable=False, default=func.current_date())
    indicator_id = Column(UUID(as_uuid=True), ForeignKey('indicators.id'), nullable=False)
    value = Column(Float, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    user = relationship('UserModel', back_populates='daily_indicators')
    indicator = relationship('IndicatorModel', back_populates='daily_indicators')