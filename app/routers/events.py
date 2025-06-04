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
        # Build SELECT query for all Event rows ("SELECT * FROM event")
        statement = select(Event)

        # Execute query and build list of events
        events: List[Event] = session.exec(statement).all()

        return events
    
    # If exception occurs, rollback any pending transaction and raise HTTP 500 Internal Server Error
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
        # Build new event instance
        new_event = Event(**event.dict())

        # Add, commit to the DB session and then refresh
        session.add(new_event)
        session.commit()
        session.refresh(new_event)

        return f"Event \'{event.title}\' successfully added!"
    
    # If exception occurs, rollback any pending transaction and raise HTTP 500 Internal Server Error
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
        # Build DELETE query ("DELETE FROM event")
        statement = delete(Event)

        # Execute query and commit to DB
        session.exec(statement) 
        session.commit()

        return 'All events succesfully deleted!'

    # If exception occurs, rollback any pending transaction and raise HTTP 500 Internal Server Error
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
        # Build query and select event with corresponding ID
        # "SELECT * FROM event WHERE id = event_id"
        event = session.get(Event, event_id)

        # Raise Error 404 if no match is found
        if not event:
            raise HTTPException(status_code=404, detail=f"Event with id {event_id} not found")
        
        return event

    # If exception occurs, rollback any pending transaction and raise HTTP 500 Internal Server Error
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
    # Build query and select event with corresponding ID
    # "SELECT * FROM event WHERE id = event_id"
    event = session.get(Event, event_id)

    # Raise Error 404 if no match is found
    if not event:
        raise HTTPException(status_code=404, detail=f"Event with id {event_id} not found")

    try:
        # Store current title
        former_title = event.title
        
        # Update each field with the new data from the request body 
        event.title = updated_event.title
        event.description = updated_event.description
        event.date = updated_event.date
        event.location = updated_event.location

        # Add, commit to the DB session and then refresh
        session.add(event)
        session.commit()
        session.refresh(event)

        return f"Event \'{former_title}\' successfully updated!"
    
    # If exception occurs, rollback any pending transaction and raise HTTP 500 Internal Server Error
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating event: {e}")



# DELETE /events/{id}
@router.delete("/{event_id}", response_model=str)
async def delete_event_by_id(session : SessionDep, 
                             event_id: Annotated[int, Path(description="ID of the event to kill")]
                            ) -> str:
    '''
    Deletes an existing event by ID.
    '''
    # Build query and select event with corresponding ID
    # "SELECT * FROM event WHERE id = event_id"
    event = session.get(Event, event_id)

    # Raise Error 404 if no match is found
    if not event:
        raise HTTPException(status_code=404, detail=f"Event with id {event_id} not found")
    
    try:
        # Delete the event from the session and commit transaction to DB
        session.delete(event)
        session.commit()
        
        return f"Event \'{event.title}\' successfully deleted!"
    
    # If exception occurs, rollback any pending transaction and raise HTTP 500 Internal Server Error
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete event: {e}")