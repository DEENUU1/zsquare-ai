from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session
from config.database import get_db
from models.client import Client
from models.form_data import FormData
from schemas.form_schema import FormInputSchema
from services.client_service import client_exists_by_email

router = APIRouter(
    prefix="/form",
    tags=["Form"],
)


@router.post("/")
def submit_form(data: FormInputSchema, db: Session = Depends(get_db)):
    try:
        existing_user = client_exists_by_email(db, data.email)
        if not existing_user:
            return {"error": "Podaj poprawny adres email."}

        client = db.query(Client).filter(Client.email == data.email).first()

        client.birth_date = data.birth_date
        client.location = data.location
        db.commit()

        latest_form = db.query(FormData).filter(FormData.client_id == client.id).order_by(
            FormData.created_at.desc()).first()

        if latest_form:
            latest_form.bike_brand = data.bike_brand
            latest_form.bike_model = data.bike_model
            latest_form.bike_size = data.bike_size
            latest_form.bike_year = data.bike_year
            latest_form.drive_group = data.drive_group
            latest_form.year_distance = data.year_distance
            latest_form.weekly_frequency = data.weekly_frequency
            latest_form.avg_kilometer = data.avg_kilometer
            latest_form.ride_style = data.ride_style
            latest_form.event = data.event
            latest_form.other_activity = data.other_activity
            latest_form.visit_goal = data.visit_goal
            latest_form.visit_problems = data.visit_problems
            latest_form.injuries = data.injuries

            db.commit()

            return {"message": "Formularz wysłany!"}
        return {"error": "Wystąpił błąd, spróbuj ponownie później."}
    except Exception as e:
        return {"error": "Wystąpił błąd, spróbuj ponownie później."}
