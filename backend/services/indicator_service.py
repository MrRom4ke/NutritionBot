from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session

from models.indicators_models import IndicatorModel, IndicatorCollectionModel, DailyIndicatorModel
from schemas.indicators_schema import IndicatorCreate, IndicatorSchema, IndicatorCollectionSchema, \
    IndicatorCollectionCreate, DailyIndicatorCreate, DailyIndicatorSchema


class IndicatorService:
    """Содержит методы для создания индикаторов, получения индикатора по ID и получения всех индикаторов."""

    def __init__(self, db: Session):
        self.db = db

    def create_indicator(self, indicator_data: IndicatorCreate) -> IndicatorSchema:
        """Создаёт новый индикатор и сохраняет его в базе данных."""
        indicator = IndicatorModel(**indicator_data.dict())
        self.db.add(indicator)
        self.db.commit()
        self.db.refresh(indicator)
        return IndicatorSchema.from_orm(indicator)

    def get_indicator(self, indicator_id: UUID) -> Optional[IndicatorSchema]:
        """Получает индикатор по его ID."""
        indicator = self.db.query(IndicatorModel).filter(IndicatorModel.id == indicator_id).first()
        if indicator:
            return IndicatorSchema.from_orm(indicator)
        return None  # Можно обработать этот случай в маршрутах

    def get_all_indicators(self) -> List[IndicatorSchema]:
        """Получает все индикаторы из базы данных."""
        indicators = self.db.query(IndicatorModel).all()
        return [IndicatorSchema.from_orm(ind) for ind in indicators]


class IndicatorCollectionService:
    """Содержит методы для создания коллекций индикаторов и получения коллекций индикаторов по ID пользователя."""

    def __init__(self, db: Session):
        self.db = db

    def create_indicator_collection(self, collection_data: IndicatorCollectionCreate) -> IndicatorCollectionSchema:
        """Создаёт новую коллекцию индикаторов и сохраняет её в базе данных."""
        collection = IndicatorCollectionModel(**collection_data.dict())
        self.db.add(collection)
        self.db.commit()
        self.db.refresh(collection)
        return IndicatorCollectionSchema.from_orm(collection)

    def get_collections_by_user(self, user_id: UUID) -> List[IndicatorCollectionSchema]:
        """Получает все коллекции индикаторов пользователя по его ID."""
        collections = self.db.query(IndicatorCollectionModel).filter(IndicatorCollectionModel.user_id == user_id).all()
        return [IndicatorCollectionSchema.from_orm(coll) for coll in collections]


class DailyIndicatorService:
    """Содержит методы для создания ежедневных индикаторов и получения ежедневных индикаторов по ID пользователя."""

    def __init__(self, db: Session):
        self.db = db

    def create_daily_indicator(self, indicator_data: DailyIndicatorCreate) -> DailyIndicatorSchema:
        """Создаёт новый ежедневный индикатор и сохраняет его в базе данных."""
        daily_indicator = DailyIndicatorModel(**indicator_data.dict())
        self.db.add(daily_indicator)
        self.db.commit()
        self.db.refresh(daily_indicator)
        return DailyIndicatorSchema.from_orm(daily_indicator)

    def get_daily_indicators_by_user(self, user_id: UUID) -> List[DailyIndicatorSchema]:
        """Получает все ежедневные индикаторы пользователя по его ID."""
        daily_indicators = self.db.query(DailyIndicatorModel).filter(DailyIndicatorModel.user_id == user_id).all()
        return [DailyIndicatorSchema.from_orm(di) for di in daily_indicators]