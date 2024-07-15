from sqlalchemy.orm import Session
from schemas.form_schema import FormOutputSchema
from typing import List
from models.form_data import FormData


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
