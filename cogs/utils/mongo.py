import motor.motor_asyncio as motor
from typing import Optional

client = motor.AsyncIOMotorClient('mongodb://localhost:27017')
db = client['public-sample']


class User:
    def __init__(self, user: int) -> None:
        self.users = db['users']
        self.filter = {'_id': user}

    async def new(self) -> None:
        await self.users.insert_one(self.filter)

    async def find(self) -> Optional[dict]:
        return await self.users.find_one(self.filter)

    async def check(self) -> dict:
        user_info = await self.find()
        if not user_info:
            await self.new()
            user_info = await self.find()
        return user_info

    async def update(self, query: dict, method: str = 'set') -> None:
        update_query = {f'${method}': query}
        await self.users.update_one(self.filter, update_query, upsert=True)
