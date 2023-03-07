import motor.motor_asyncio as motor

client = motor.AsyncIOMotorClient('mongodb://localhost:27017')
db = client['public-sample']
