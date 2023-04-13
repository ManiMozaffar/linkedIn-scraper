from fastapi import APIRouter
from services.ads.repositories import router as ads_router
from services.proxy.repositories import router as proxy_router


router = APIRouter()
router.include_router(ads_router, tags=["ads"], prefix="/ads")
router.include_router(proxy_router, tags=["proxy"], prefix="/proxy")
