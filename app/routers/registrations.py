from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import SQLModel
from sqlmodel import Session
from app.models.user import User
from app.models.event import Event
from app.models.registration import Registration
from app.data.db import get_session

# Creiamo un router con prefisso /events per le rotte di registrazione
router = APIRouter(prefix="/events", tags=["registrations"])

#Schema di input per la registrazione: riceve username, name e email
class RegistrationRequest(SQLModel):
    username: str
    name:     str
    email:    str

# POST /events/{event_id}/register
@router.post("/{event_id}/register", response_model=Registration, status_code=201)
def register_event(
    event_id: int,                 # ID dell’evento nel path
    reg_req: RegistrationRequest,  # dati dell’utente nel body
    session: Session = Depends(get_session), # dependency injection della sessione DB
):
    """
    Registra un utente a un evento.
    1) Controlla se l'utente esiste; se no, lo crea.
    2) Verifica che l'evento esista.
    3) Impedisce registrazioni duplicate.
    4) Crea e restituisce la registrazione.
    """

    # 1) Controlla (o crea) l'utente
    user = session.get(User, reg_req.username)
    if not user:
        # L'utente non esiste: crealo con i dati forniti
        user = User(
            username=reg_req.username,
            name=reg_req.name,
            email=reg_req.email
        )
        session.add(user)
    else:
        # Se l'utente esiste, aggiorna nome ed email se cambiati
        user.name  = reg_req.name
        user.email = reg_req.email

    # 2) Controlla che l'evento esista
    event = session.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    # Salva eventuali modifiche all'utente prima di procedere
    session.commit()
    session.refresh(user)

    # 3) Verifica che non sia già registrato
    key = (user.username, event_id)
    if session.get(Registration, key):
        raise HTTPException(status_code=400, detail="Already registered")

    # 4) Crea la registrazione
    db_reg = Registration(username=user.username, event_id=event_id)
    session.add(db_reg)
    session.commit()
    session.refresh(db_reg)

    # Restituisce l'oggetto Registration creato
    return db_reg
