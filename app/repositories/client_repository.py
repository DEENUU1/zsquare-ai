from sqlalchemy.orm import Session
from schemas.client_schema import ClientOutputSchema
from typing import List, Optional
from models.client import Client


def get_clients(
        db: Session,
        full_name: Optional[str] = None
) -> List[ClientOutputSchema]:
    query = db.query(Client)

    if full_name:
        query = query.filter(Client.full_name.ilike(f"%{full_name}%"))

    clients = query.all()

    return [ClientOutputSchema.from_orm(client) for client in clients]


def get_client_by_id(
        db: Session,
        client_id: int
) -> ClientOutputSchema:
    client = db.query(Client).filter(Client.id == client_id).first()

    if not client:
        raise ValueError(f"Client with id {client_id} not found")

    return ClientOutputSchema.from_orm(client)
