import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
sys.path.append(os.path.dirname(os.path.realpath(__file__)))
from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware

from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

from dotenv import load_dotenv
load_dotenv()

from db_utils import DBClient
from routers import committee
from routers import subscribers
from routers import events
from routers import rsvp
from routers import survey
from routers import sandesh
from routers import volunteer


origins = [
    "http://localhost:3000",
    "https://lohanadfw.org",
    "http://lohanadfw.org",
    "https://www.lohanadfw.org",
    "http://www.lohanadfw.org"
]

middlewares = [
    Middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )
]
#
app = FastAPI(middlewares=middlewares)
# app = FastAPI()

db_client = DBClient()
app.include_router(committee.router)
app.include_router(subscribers.router)
app.include_router(events.router)
app.include_router(rsvp.router)
app.include_router(survey.router)
app.include_router(sandesh.router)
app.include_router(volunteer.router)


@app.get("/")
async def read_root():
    return {"Hello": "World"}

app = CORSMiddleware(
    app=app,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
