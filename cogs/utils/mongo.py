import motor.motor_asyncio as motor
from typing import Optional

client = motor.AsyncIOMotorClient('mongodb://localhost:27017')
db = client['bitacora']


class Giveaway:
    def __init__(self, giveaway: int = 0) -> None:
        self.giveaways = db['giveaways']
        self.filter = {'_id': giveaway}

    async def create(self, query: dict) -> None:
        await self.giveaways.insert_one(query)

    async def check(self) -> dict:
        return await self.giveaways.find_one(self.filter)

    async def update(self, query: dict, method: str = 'set') -> None:
        update_query = {f'${method}': query}
        await self.giveaways.update_one(self.filter, update_query, upsert=True)

    async def delete(self) -> None:
        await self.giveaways.delete_one(self.filter)


class Guild:
    def __init__(self, guild: int) -> None:
        self.guilds = db['guilds']
        self.filter = {'_id': guild}

    async def new(self) -> None:
        await self.guilds.insert_one(self.filter)

    async def find(self) -> Optional[dict]:
        return await self.guilds.find_one(self.filter)

    async def check(self) -> dict:
        guild_info = await self.find()
        if not guild_info:
            await self.new()
            guild_info = await self.find()
        return guild_info

    async def update(self, query: dict, method: str = 'set') -> None:
        update_query = {f'${method}': query}
        await self.guilds.update_one(self.filter, update_query, upsert=True)


class Poll:
    def __init__(self, poll: int = 0) -> None:
        self.polls = db['polls']
        self.filter = {'_id': poll}

    async def create(self, query: dict) -> None:
        await self.polls.insert_one(query)

    async def check(self) -> dict:
        return await self.polls.find_one(self.filter)

    async def update(self, query: dict, method: str = 'set') -> None:
        update_query = {f'${method}': query}
        await self.polls.update_one(self.filter, update_query, upsert=True)

    async def delete(self) -> None:
        await self.polls.delete_one(self.filter)


class User:
    def __init__(self, user: int = 0) -> None:
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

    def cursor(self) -> motor.AsyncIOMotorCursor:
        return self.users.find()
