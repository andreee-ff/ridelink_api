from fastapi import FastAPI
from app.database import Base, engine
from app.routers import auth
from app import models


app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "RideLink API is running!"}

# Create the database tables
Base.metadata.create_all(bind=engine)

# Include the authentication router
app.include_router(auth.router)
