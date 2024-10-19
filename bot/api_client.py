import aiohttp

from config import BACKEND_URL


class APIClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = None

    async def init_session(self):
        if self.session is None:
            self.session = aiohttp.ClientSession()

    async def close(self):
        if self.session:
            await self.session.close()

    async def post(self, endpoint: str, data: dict) -> dict:
        """Метод для выполнения POST-запросов"""
        await self.init_session()
        url = f"{self.base_url}{endpoint}"
        async with self.session.post(url, json=data) as response:
            if response.status != 200:
                raise Exception(f"API error: {response.status}")
            return await response.json()

    async def get(self, endpoint: str, params: dict = None) -> dict:
        """Метод для выполнения GET-запросов"""
        await self.init_session()
        url = f"{self.base_url}{endpoint}"
        async with self.session.get(url, params=params) as response:
            if response.status != 200:
                raise Exception(f"API error: {response.status}")
            return await response.json()

    async def delete(self, endpoint: str) -> dict:
        """Метод для выполнения DELETE-запросов"""
        await self.init_session()
        url = f"{self.base_url}{endpoint}"
        async with self.session.delete(url) as response:
            if response.status != 200:
                raise Exception(f"API error: {response.status}")
            return await response.json()

    async def update(self, endpoint: str, data: dict, method: str = "put") -> dict:
        """Метод для выполнения UPDATE-запросов (PUT или PATCH)"""
        await self.init_session()
        url = f"{self.base_url}{endpoint}"

        if method == "put":
            async with self.session.put(url, json=data) as response:
                if response.status != 200:
                    raise Exception(f"API error: {response.status}")
                return await response.json()
        elif method == "patch":
            async with self.session.patch(url, json=data) as response:
                if response.status != 200:
                    raise Exception(f"API error: {response.status}")
                return await response.json()
        else:
            raise ValueError("Метод должен быть либо 'put', либо 'patch'")

# Инициализация клиента
api_client = APIClient(base_url=BACKEND_URL)