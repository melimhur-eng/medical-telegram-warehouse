from api.database import engine

connection = engine.connect()

print("Database connected successfully!")

connection.close()