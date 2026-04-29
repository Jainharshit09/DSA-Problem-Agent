from fastapi import FastAPI
from .routes import router
from dotenv import load_dotenv
load_dotenv()

app = FastAPI(title="ADK Specialist Agent (DSA Solver)")
app.include_router(router)
