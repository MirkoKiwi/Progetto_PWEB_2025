from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.config import config

from sqlmodel import Session, select

from typing import List
from app.models.event import Event, EventCreate
from app.data.db import SessionDep

from datetime import datetime


router = APIRouter(prefix='/events')
templates = Jinja2Templates(directory=config.root_dir / "templates")



# GET - Events
@router.get("/", response_model=List[Event])
async def get_events(session: SessionDep):
    events = session.exec(select(Event)).all()
    return events


# POST - Events
@router.post("/", response_model=Event)
async def create_event(session: SessionDep, event: EventCreate):
    new_event = Event(**event.dict())
    session.add(new_event)
    session.commit()
    session.refresh(new_event)
    return new_event

