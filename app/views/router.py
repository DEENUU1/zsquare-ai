from fastapi import APIRouter
from views.dashboard import user, dashboard
from views.form_views import form

router = APIRouter(
    prefix=""
)

router.include_router(user.router)
router.include_router(dashboard.router)
router.include_router(form.router)
