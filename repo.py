from sqlalchemy.orm import Session
from schemas import ClientOutputSchema, FormOutputSchema, MessageOutputSchema, MessageInputSchema
from typing import List, Optional
from models import FormData, Client, Message


def get_clients(
        db: Session,
        full_name: Optional[str] = None
) -> List[ClientOutputSchema]:
    query = db.query(Client)

    if full_name:
        query = query.filter(Client.full_name.ilike(f"%{full_name}%"))

    clients = query.all()

    return [ClientOutputSchema.from_orm(client) for client in clients]


def get_forms_by_client(
        db: Session,
        client_id: int
) -> List[FormOutputSchema]:
    forms = db.query(FormData).filter(FormData.client_id == client_id).all()

    return [FormOutputSchema.from_orm(form) for form in forms]


def get_form_by_id(
        db: Session,
        form_id: int
) -> FormOutputSchema:
    form = db.query(FormData).filter(FormData.id == form_id).first()

    return FormOutputSchema.from_orm(form) if form else None


def create_message(
        db: Session,
        message: MessageInputSchema
) -> MessageOutputSchema:
    message = Message(**message.dict())
    db.add(message)
    db.commit()
    db.refresh(message)

    return MessageOutputSchema.from_orm(message)


def get_messages_by_form_id(
        db: Session,
        form_id: int
) -> List[MessageOutputSchema]:
    messages = db.query(Message).filter(Message.form_id == form_id).all()

    return [MessageOutputSchema.from_orm(message) for message in messages]
