from fastapi import APIRouter, Depends
from .v1.endpoints.auth import router as auth_router
from .v1.endpoints.data import router as data_router
from .v1.endpoints.settings import router as settings_router
from .v1.endpoints.corporate import router as corporate_router

# Main API router for version 1
router = APIRouter()

# Include routers for different endpoint groups
router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
router.include_router(data_router, prefix="/data", tags=["Data Aggregation"])
router.include_router(settings_router, prefix="/settings", tags=["Settings"])
router.include_router(corporate_router, prefix="/corporate", tags=["Corporate HR"])
