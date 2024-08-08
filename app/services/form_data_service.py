from sqlalchemy.orm import Session, joinedload
from models.form_data import FormData
from models.message import Message
from models.report import Report
from schemas.message_schema import MessageInputSchema
from services.message_service import create_message


def create_form_data(db: Session, form_data: FormData, client_id: int):
    form_data.client_id = client_id
    db.add(form_data)
    db.commit()
    db.refresh(form_data)
    created_form = form_data

    create_message(
        db,
        MessageInputSchema(
            role="assistant",
            text="Hej👋 jestem tu aby Ci pomóc, zacznijmy od wzrostu klienta",
            form_id=created_form.id
        )
    )

    return created_form


def get_forms_by_client_id(db: Session, client_id: int):
    return db.query(FormData).filter(FormData.client_id == client_id).options(joinedload(FormData.user)).all()


def delete_form_by_id(db: Session, form_id: int):
    db.query(Message).filter(Message.form_id == form_id).delete()
    db.query(Report).filter(Report.form_data_id == form_id).delete()
    db.query(FormData).filter(FormData.id == form_id).delete()
    db.commit()


def get_form_by_id(db: Session, form_id: int):
    return db.query(FormData).filter(FormData.id == form_id).first()
