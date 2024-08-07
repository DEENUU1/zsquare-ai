import base64
import os
import tempfile
from datetime import datetime

from fastapi import APIRouter, Request, Depends, Form, HTTPException, UploadFile, File, Query
from fastapi.responses import HTMLResponse, RedirectResponse

from sqlalchemy.orm import Session
from starlette.background import BackgroundTask
from fastapi.responses import FileResponse
from starlette.responses import JSONResponse

from config.database import get_db
from models.client import Client
from models.form_data import FormData
from models.user import User
from services.auth import get_current_user, get_password_hash
from config.settings import settings
from services.chat import Chatbot
from services.client_service import create_client, get_clients, get_client_by_id, delete_client_by_id, search_clients
from services.form_data_service import get_forms_by_client_id, delete_form_by_id, get_form_by_id, create_form_data
from services.message_service import get_messages_by_form_id
from services.report import generate_report
from services.report_service import get_report_by_form_id
from services.user_service import get_users, delete_user_by_id, update_is_active_user
from utils.current_date import get_current_date
from utils.generate_password import generate_random_password
from utils.model_serializer import serialize_model

router = APIRouter(
    prefix="",
    tags=["Dashboard"],
)


@router.get("/", response_class=HTMLResponse)
def get_clients_handler(request: Request, db: Session = Depends(get_db)):
    current_user = get_current_user(request)
    if not current_user:
        return RedirectResponse("/user/login")

    return settings.TEMPLATES.TemplateResponse(
        "clients.html",
        {
            "users": get_users(db),
            "request": request,
            "clients": get_clients(db),
            "user": current_user
        }
    )


@router.get("/clients/search")
def search_clients_handler(request: Request, query: str = Query(..., min_length=1), db: Session = Depends(get_db)):
    current_user = get_current_user(request)
    if not current_user:
        return RedirectResponse("/user/login")

    clients = search_clients(db, query)
    return clients


@router.get("/clients/{client_id}", response_class=HTMLResponse)
def get_client_handler(request: Request, client_id: int, db: Session = Depends(get_db)):
    current_user = get_current_user(request)
    if not current_user:
        return RedirectResponse("/user/login")

    client = get_client_by_id(db, client_id)
    forms_raw = get_forms_by_client_id(db, client_id)
    forms = [serialize_model(form) for form in forms_raw]

    return settings.TEMPLATES.TemplateResponse(
        "client.html",
        {
            "request": request,
            "client": client,
            "forms": forms,
            "user": current_user
        }
    )


@router.post("/clients", response_class=RedirectResponse)
def create_visit_handler(
        request: Request,
        full_name: str = Form(None),
        email: str = Form(None),
        phone: str = Form(None),
        fitter: int = Form(...),
        visit_date: str = Form(...),
        client_id: int = Form(None),
        db: Session = Depends(get_db)
):
    current_user = get_current_user(request)
    if not current_user:
        return RedirectResponse("/user/login")

    visit_date = datetime.strptime(visit_date, "%Y-%m-%dT%H:%M")

    if not client_id:
        if not full_name or not email or not phone:
            raise HTTPException(status_code=400, detail="Missing required fields for a new client")

        client = create_client(db, Client(
            full_name=full_name,
            email=email,
            phone=phone,
        ))
        client_id = client.id

    create_form_data(db, FormData(
        user_id=fitter,
        visit_date=visit_date,
    ), client_id)

    return RedirectResponse(url=f"/clients/{client_id}", status_code=303)


@router.delete("/clients/{client_id}")
def delete_client_handler(request: Request, client_id: int, db: Session = Depends(get_db)):
    current_user = get_current_user(request)
    if not current_user:
        return RedirectResponse("/user/login")

    delete_client_by_id(db, client_id)
    return {"message": "Client deleted successfully"}


@router.delete("/forms/{form_id}")
def delete_form_handler(request: Request, form_id: int, db: Session = Depends(get_db)):
    current_user = get_current_user(request)
    if not current_user:
        return RedirectResponse("/user/login")

    delete_form_by_id(db, form_id)
    return {"message": "Form deleted successfully"}


@router.get("/forms/{form_id}/report")
def get_report_handler(request: Request, form_id: int, db: Session = Depends(get_db)):
    current_user = get_current_user(request)
    if not current_user:
        return RedirectResponse("/user/login")

    report = get_report_by_form_id(db, form_id)
    if not report or not report.report_content:
        raise HTTPException(status_code=404, detail="Report not found")

    report_content = base64.b64decode(report.report_content)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        temp_file.write(report_content)
        temp_file_path = temp_file.name

    return FileResponse(
        path=temp_file_path,
        filename="report.pdf",
        media_type="application/pdf",
        background=BackgroundTask(lambda: os.unlink(temp_file_path))
    )


@router.get("/users")
def get_users_handler(request: Request, db: Session = Depends(get_db)):
    current_user = get_current_user(request)
    if not current_user:
        return RedirectResponse("/user/login")

    users = get_users(db)
    return settings.TEMPLATES.TemplateResponse(
        "users.html",
        {
            "request": request,
            "users": users,
            "user": current_user
        }
    )


@router.post("/users")
def create_new_user_handler(
        request: Request,
        full_name: str = Form(...),
        email: str = Form(...),
        db: Session = Depends(get_db)):
    current_user = get_current_user(request)
    if not current_user:
        return RedirectResponse("/user/login")

    password = generate_random_password(10, use_uppercase=False, use_special_chars=False)
    hashed_password = get_password_hash(password)
    new_user = User(email=email, full_name=full_name, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "User created successfully",
        "password": password
    }


@router.delete("/users/{user_id}")
def delete_user_handler(request: Request, user_id: int, db: Session = Depends(get_db)):
    current_user = get_current_user(request)
    if not current_user:
        return RedirectResponse("/user/login")

    delete_user_by_id(db, user_id)
    return {"message": "Client deleted successfully"}


@router.put("/users/{user_id}/update-isactive")
def update_isactive_user_handler(request: Request, user_id: int, db: Session = Depends(get_db)):
    current_user = get_current_user(request)
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    new_is_active = update_is_active_user(db, user_id)
    return {"message": "User updated successfully", "is_active": new_is_active}


chatbot = Chatbot()


@router.get("/forms/{form_id}/report-generate")
async def generate_report_handler(request: Request, form_id: int):
    current_user = get_current_user(request)
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    generate_report(next(get_db()), form_id)

    return {"message": "Report generated successfully"}


@router.get("/forms/{form_id}/chat", response_class=HTMLResponse)
async def chat_dashboard(request: Request, form_id: int, db: Session = Depends(get_db)):
    current_user = get_current_user(request)
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    messages = get_messages_by_form_id(db, form_id)

    form_details = get_form_by_id(db, form_id)

    if not form_details:
        raise HTTPException(status_code=404, detail="Form not found")

    client_data = get_client_by_id(db, form_details.client_id)

    return settings.TEMPLATES.TemplateResponse(
        "chat.html",
        {
            "request": request,
            "form_id": form_id,
            "messages": messages,
            "client": client_data
        }
    )


@router.post("/chat")
async def chat(request: Request, message: str = Form(...), form_id: int = Form(...)):
    current_user = get_current_user(request)
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    user_message, bot_response = await chatbot.get_response(message, form_id)
    return JSONResponse(content={"user_message": user_message, "bot_response": bot_response})


@router.post("/audio")
async def audio(request: Request, audio: UploadFile = File(...), form_id: int = Form(...)):
    current_user = get_current_user(request)
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    contents = await audio.read()
    user_message, bot_response = await chatbot.get_response(contents, form_id, is_audio=True)
    return JSONResponse(content={"user_message": user_message, "bot_response": bot_response})
