# Creiamo un router FastAPI dedicato agli endpoint /users

from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlmodel import select, Session, delete
from app.models.user import User
from app.data.db import get_session

# prefix="/users" indica che tutte le rotte partiranno con /users
# tags=["users"] serve per raggruppare le rotte nella documentazione Swagger
router = APIRouter(prefix="/users", tags=["users"])

# GET /users
@router.get("/", response_model=List[User])
def list_users(session: Session = Depends(get_session)) -> List[User]:  #Usa la dependency get_session per ottenere una Session SQLModel
    """
    GET /users
    Restituisce la lista di tutti gli utenti presenti nel database.
    - Usa la dependency get_session per ottenere una Session SQLModel.
    - Esegue SELECT * FROM user
    - Ritorna i risultati come lista di oggetti User.
    """
    # Costruisci la query per selezionare tutti i record User
    users = session.exec(select(User)).all()
    # Converte il risultato in una lista Python e restituisce
    return list(users)

# POST /users
# Crea un nuovo utente
@router.post("/", response_model=User, status_code=201)
def create_user(user: User, session: Session = Depends(get_session)) -> User:
    """
        POST /users
        Crea un nuovo utente.
        - Il body della richiesta deve avere i campi di User:
          {
            "username": "string",
            "name":     "string",
            "email":    "string"
          }
        - Verifica che lo username non esista già.
        - Se esiste, solleva HTTP 400.
        - Altrimenti aggiunge il nuovo User al DB, committa e restituisce l'oggetto creato.
        """

    # Controllo di unicità dello username
    if session.get(User, user.username):
        raise HTTPException(status_code=400, detail="Username already exists")
    # Aggiunge il nuovo utente alla sessione
    session.add(user)
    # Salva le modifiche sul database
    session.commit()
    # Ricarica l'istanza per ottenere eventuali valori generati (non applicabile per User)
    session.refresh(user)
    # Restituisce l'utente creato
    return user

#   DELETE /users
@router.delete("/", status_code=204)
def delete_all_users(session: Session = Depends(get_session)) -> None:
    """
    DELETE /users
    Elimina tutti gli utenti dal database.
    - Esegue una query DELETE senza WHERE (cancella tutte le righe).
    - Commita la transazione.
    - Restituisce 204 No Content.
    """
    # Esegue DELETE FROM user
    session.exec(delete(User))
    # Esegue DELETE FROM user
    session.commit()