from fastapi import APIRouter, HTTPException, Response, Depends
from sqlmodel import SQLModel
from sqlmodel import Session, select
from typing import List
from app.models.user import User
from app.models.event import Event
from app.models.registration import Registration
from app.data.db import SessionDep

"""Creiamo un router con prefisso /events per le rotte di registrazione"""
router = APIRouter(prefix="/registrations", tags=["registrations"])

"""GET - /registrations"""
@router.get("/",response_model=List[Registration])
async def get_registrations(session: SessionDep):
    """
        Restituisce tutte le registrazioni presenti nel database.
        1) Esegue una query sulla tabella 'Registration'.
        2) Ritorna la lista completa delle registrazioni.
    """
    registrations = session.exec(select(Registration)).all()
    return registrations

"""DELETE - /registrations/?username={username}&event_id={event_id}"""
@router.delete("/",status_code=204)
async def delete_registrations(username: str, event_id: int, session: SessionDep):
    """
    DELETE /registrations/?username={username}&event_id={event_id}
    Elimina la registrazione di un utente per un determinato evento.Se la registrazione non esiste, restituisce errore 404.
    - Altrimenti elimina la registrazione e restituisce 204 No Content.
    """
    """ variabile che salva 'username' ed 'event_id' come parametri della richiesta"""
    request = (username, event_id)
    registration = session.get(Registration, request)
    """Se la registrazione non esiste, restituisce errore 404. """
    if not registration:
        raise HTTPException(status_code=404, detail="Registration not found")
    
    """elimina la registrazione"""
    session.delete(registration)
    session.commit()
    return Response(status_code=204)
