from ..db.session import async_session
from ..models.user import User

class UserService:
    @staticmethod
    async def create_user(user_data):
        async with async_session() as session:
            user = User(**user_data.dict())
            session.add(user)
            await session.commit()
            return user