from fastapi import FastAPI
from .database import init_db
from .routers import router as main_router

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    # Initialize the database on startup
    await init_db()

# Include the routers
app.include_router(main_router)
