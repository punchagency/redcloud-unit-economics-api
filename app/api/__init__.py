from fastapi import APIRouter

from .cities import router as cities_router
from .lgas import router as lgas_router
from .neighborhoods import router as neighborhoods_router
from .retailers import router as retailers_router
from .sales import router as sales_router
from .states import router as states_router

base_router = APIRouter()

base_router.include_router(cities_router, prefix="/cities", tags=["Cities"])
base_router.include_router(lgas_router, prefix="/lgas", tags=["LGAs"])
base_router.include_router(states_router, prefix="/states", tags=["States"])
base_router.include_router(
    neighborhoods_router, prefix="/neighborhoods", tags=["Neighborhoods"]
)
base_router.include_router(retailers_router, prefix="/retailers", tags=["Retailers"])
base_router.include_router(sales_router, prefix="/sales", tags=["Sales"])
