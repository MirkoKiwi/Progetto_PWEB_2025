from fastapi import APIRouter, HTTPException, Request, Path, Query, Form, Response
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.config import config

from sqlmodel import Session, select, delete

from typing import List, Annotated
from app.models.event import Event, EventForm
from app.models.registration import Registration, RegistrationRequest
from app.models.user import User
from app.data.db import SessionDep

from datetime import datetime



router = APIRouter(prefix='/events')
templates = Jinja2Templates(directory=config.root_dir / "templates")

# GET - events
@router.get("/", response_model=List[Event])
async def get_events(session: SessionDep) -> List[Event]:
    '''
    \nReturns the list of existing events.

    Args:
        session: DB session

    Return Value:
        list of all existing events fetched from the DB

    Raises:
        HTTPException: If no events are found / Any other kind of errors
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
@router.post("/", response_model=str, status_code=201)
async def create_event(session: SessionDep, 
                       event: EventForm
                      ) -> str:
    '''
    \nCreates a new event.

    Args:
        session: Database session
        event: EventForm object with user inserted values 
    
    Return value:
        success message
    
    Raises.
        HTTPException if the event couldn't be created
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
@router.delete("/", response_model=str)
async def delete_all_events(session: SessionDep) -> str:
    '''
    \nDelete all events (Irreversible!!!).

    Args:
        session: Database session

    Return value:
        success message

    Raises:
        HTTPException if the events couldn't be deleted 
    '''
    try:
        # Build DELETE query ("DELETE FROM event")
        statement = delete(Event)

        #Prima elimina tutte le registrazioni
        session.exec(delete(Registration))
        
        # Execute query and commit to DB
        session.exec(statement) 
        session.commit()

        return "All events and related registrations are succesfully deleted!"

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
    \nReturns the event with the given id.
    
    
    Args:
        session: Database session 
        event_id: ID of the event to be displayed 
        
    Return value:
        the event fetched by ID

    Raises:
        HTTPException if the event couldn't be retrieved

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
    \nUpdates an existing event

    Args:
        session: Database session 
        event_id: ID of the event to be updated 
        
    Return value:
        success message

    Raises:
        HTTPException if the event couldn't be updated

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
    \nDeletes an existing event by ID.
    
    Args:
        session: Database session 
        event_id: ID of the event to be deleted
        
    Return value:
        success message

    Raises:
        HTTPException if the event couldn't be deleted
    '''
    # Build query and select event with corresponding ID
    # "SELECT * FROM event WHERE id = event_id"
    event = session.get(Event, event_id)

    # Raise Error 404 if no match is found
    if not event:
        raise HTTPException(status_code=404, detail=f"Event with id {event_id} not found")
    
    try:
        # Elimina registrazioni prima
        session.exec(delete(Registration).where(Registration.event_id == event_id))

        # Delete the event from the session and commit transaction to DB
        session.delete(event)
        session.commit()
        
        return f"Event \'{event.title}\' successfully deleted!"
    
    # If exception occurs, rollback any pending transaction and raise HTTP 500 Internal Server Error
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete event: {e}")
    

"""POST /events/{event_id}/register"""
@router.post("/{event_id}/register", response_model=Registration, status_code=201)
async def register_event(
    event_id: int,                 # ID dell’evento nel path
    reg_req: RegistrationRequest,  # dati dell’utente nel body
    session: SessionDep, # dependency injection della sessione DB
):
    """
    Registra un utente a un evento.
    1) Controlla se l'utente esiste; se no, lo crea.
    2) Verifica che l'evento esista.
    3) Impedisce registrazioni duplicate.
    4) Crea e restituisce la registrazione.
    """

    """1) Controlla (o crea) l'utente"""
    user = session.get(User, reg_req.username)
    if not user:
        """L'utente non esiste: crealo con i dati forniti""" 
        user = User(
            username=reg_req.username,
            name=reg_req.name,
            email=reg_req.email
        )
        session.add(user)
    else:
        """Se l'utente esiste, aggiorna nome ed email se cambiati"""
        user.name  = reg_req.name
        user.email = reg_req.email

    """2) Controlla che l'evento esista"""
    event = session.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    """Salva eventuali modifiche all'utente prima di procedere"""
    session.commit()
    session.refresh(user)

    """3) Verifica che non sia già registrato"""
    key = (user.username, event_id)
    if session.get(Registration, key):
        raise HTTPException(status_code=409, detail="Already registered")

    """4) Crea la registrazione"""
    db_reg = Registration(username=user.username, event_id=event_id)
    session.add(db_reg)
    session.commit()
    session.refresh(db_reg)

    """Restituisce l'oggetto Registration creato"""
    return db_reg
