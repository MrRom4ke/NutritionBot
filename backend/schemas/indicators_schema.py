from pydantic import BaseModel
from uuid import UUID
from datetime import datetime, date
from typing import Optional

class IndicatorBase(BaseModel):
    """Базовая схема для модели Indicator, содержащая общие поля."""
    name: str
    description: Optional[str] = None
    measurement_type: str
    theme: str

class IndicatorCreate(IndicatorBase):
    """Схема для создания нового Indicator, наследующая от IndicatorBase."""
    pass

class IndicatorSchema(IndicatorBase):
    """Схема, которая включает все поля модели Indicator, включая id, и устанавливает orm_mode в True."""
    id: UUID

    class Config:
        orm_mode = True

class IndicatorCollectionBase(BaseModel):
    """Базовая схема для модели IndicatorCollection, содержащая общие поля."""
    user_id: UUID
    indicator_id: UUID
    value: Optional[float] = None

class IndicatorCollectionCreate(IndicatorCollectionBase):
    """Схема для создания новой коллекции индикаторов. Она наследует поля из IndicatorCollectionBase."""
    pass

class IndicatorCollectionSchema(IndicatorCollectionBase):
    """Схема, которая включает все поля модели IndicatorCollection, включая id, и устанавливает orm_mode в True."""
    id: UUID
    collection_time: datetime = datetime.utcnow()

    class Config:
        orm_mode = True

class DailyIndicatorBase(BaseModel):
    """Базовая схема для модели DailyIndicator, содержащая общие поля."""
    user_id: UUID
    date: date = date.today()
    indicator_id: UUID
    value: Optional[float] = None

class DailyIndicatorCreate(DailyIndicatorBase):
    """Схема для создания нового DailyIndicator, наследующая от DailyIndicatorBase."""
    pass

class DailyIndicatorSchema(DailyIndicatorBase):
    """Схема, которая включает все поля модели DailyIndicator, включая id, и устанавливает orm_mode в True."""
    id: UUID
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()

    class Config:
        orm_mode = True
