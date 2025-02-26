from fastapi import APIRouter

from .cities import router as cities_router
from .neighborhoods import router as neighborhoods_router
from .retailers import router as retailers_router

base_router = APIRouter()

base_router.include_router(cities_router, prefix="/cities", tags=["Cities"])
base_router.include_router(
    neighborhoods_router, prefix="/neighborhoods", tags=["Neighborhoods"]
)
base_router.include_router(retailers_router, prefix="/retailers", tags=["Retailers"])
