from fastapi import APIRouter

from app.api.v1 import auth, employee, employee_import

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth.router)
api_router.include_router(employee.router)
api_router.include_router(employee_import.router)
