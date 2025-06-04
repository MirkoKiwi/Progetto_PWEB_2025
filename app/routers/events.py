from fastapi import APIRouter, HTTPException, Request, Path, Query, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.config import config

from sqlmodel import Session, select, delete

from typing import List, Annotated
from app.models.event import Event, EventForm
from app.data.db import SessionDep

from datetime import datetime



router = APIRouter(prefix='/events')
templates = Jinja2Templates(directory=config.root_dir / "templates")





# GET - events
@router.get("/", response_model=List[Event])
async def get_events(session: SessionDep) -> List[Event]:
    '''
    Returns the list of existing events.
    '''
    try:
        events = session.exec(select(Event)).all()
        return events
    
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500,detail=f"Error retrieving events: {e}")



# POST - events
@router.post("/", response_model=str)
async def create_event(session: SessionDep, 
                       event: EventForm
                      ) -> str:
    '''
    Creates a new event.
    '''
    try:
        new_event = Event(**event.dict())
        session.add(new_event)
        session.commit()
        session.refresh(new_event)
        return f"Event \'{event.title}\' successfully added!"
    
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500,detail=f"Error creating event: {e}")



# DELETE - events
@router.delete("/", status_code=200)
async def delete_all_events(session: SessionDep) -> str:
    '''
    Delete all events (Irreversible!!!).
    '''
    try:
        session.exec(delete(Event)) 
        session.commit()
        return 'All events succesfully deleted!'

    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500,detail=f"Error deleting all events: {e}")



# GET /events/{id}
@router.get("/{event_id}", response_model=Event)
async def get_event_by_id(session: SessionDep, 
                          event_id: int, 
                          title="Event ID"
                        ) -> Event:
    '''
    Returns the event with the given id.
    '''
    try:
        event = session.get(Event, event_id)
        if not event:
            raise HTTPException(status_code=404, detail=f"Event with id {event_id} not found")
        return event

    except HTTPException:
        raise

    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Error retrieving event: {e}")



# PUT /events/{id}
@router.put("/{event_id}",
            response_model=str)
async def update_event_by_id(session: SessionDep,
                             event_id: Annotated[int, Path(description="ID of the event to update")],
                             updated_event: EventForm,
                             title="Event ID"
                            ) -> str:
    '''
    Updates an existing event
    '''
    event = session.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail=f"Event with id {event_id} not found")

    try:
        # Update existing event values
        former_title = event.title
        event.title = updated_event.title
        event.description = updated_event.description
        event.date = updated_event.date
        event.location = updated_event.location

        session.add(event)
        session.commit()
        session.refresh(event)

        return f"Event \'{former_title}\' successfully updated!"
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating event: {e}")



# DELETE /events/{id}
@router.delete("/{event_id}", response_model=str)
async def delete_event_by_id(session : SessionDep, 
                             event_id: Annotated[int, Path(description="ID of the event to kill")]
                            ) -> str:
    '''
    Deletes an existing event by ID.
    '''
    event = session.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail=f"Event with id {event_id} not found")
    
    try:
        session.delete(event)
        session.commit()
        return f"Event \'{event.title}\' successfully deleted!"
    
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete event: {e}")