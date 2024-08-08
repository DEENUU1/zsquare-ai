from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from starlette import status

from config.database import get_db
from services.auth import verify_password, get_user_by_email, create_access_token
from config.settings import settings

router = APIRouter(
    prefix="/user",
    tags=["Users"],
)


@router.get("/login", response_class=HTMLResponse)
async def login_form(request: Request):
    return settings.TEMPLATES.TemplateResponse("login.html", {"request": request})


@router.post("/login")
async def login(
        request: Request,
        email: str = Form(...),
        password: str = Form(...),
        db: Session = Depends(get_db)
):
    user = get_user_by_email(db, email)

    # TODO uncomment it later
    # if not user.is_active:
    #     return settings.TEMPLATES.TemplateResponse(
    #         "login.html",
    #         {"request": request, "error": "Użytkownik jest nieaktywny"}
    #     )

    if not user or not verify_password(password, user.hashed_password):
        return settings.TEMPLATES.TemplateResponse(
            "login.html",
            {"request": request, "error": "Nieprawidłowe dane logowania"}
        )
    access_token = create_access_token(data={"sub": user.email})
    response = RedirectResponse(url="/clients", status_code=status.HTTP_302_FOUND)
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    return response


@router.get("/logout")
async def logout(request: Request):
    response = RedirectResponse(url="/user/login", status_code=303)
    response.delete_cookie(key="access_token")
    return response
