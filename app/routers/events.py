from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.config import config

from sqlmodel import Session, select, delete

from typing import List
from app.models.event import Event, EventCreate
from app.data.db import SessionDep

from datetime import datetime


router = APIRouter(prefix='/events')
templates = Jinja2Templates(directory=config.root_dir / "templates")



# GET - Events
@router.get("/", response_model=List[Event])
async def get_events(session: SessionDep):
    '''
    Returns the list of existing events.
    '''
    events = session.exec(select(Event)).all()
    return events


# POST - Events
@router.post("/", response_model=Event)
async def create_event(session: SessionDep, event: EventCreate):
    '''
    Creates a new event.
    '''
    new_event = Event(**event.dict())
    session.add(new_event)
    session.commit()
    session.refresh(new_event)
    return new_event


# DELETE - Events
@router.delete("/", status_code=204)
async def delete_all_events(session: SessionDep):
    '''
    Delete all events (Irreversible!!!).
    '''
    session.exec(delete(Event)) 
    session.commit()


# GET /events/{id}
@router.get("/{event_id}", response_model=Event)
async def get_event_by_id(session: SessionDep, event_id: int, title="The ID of the event to retrieve"):
    '''
    Returns the event with the given id.
    '''
    event = session.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail=f"Event with id {event_id} not found")
    return event