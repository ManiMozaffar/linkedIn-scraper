from fastapi import APIRouter
from services.ads.repositories import router as ads_router
from services.proxy.repositories import router as proxy_router
from services.jobs.repositories import router as jobs_router
from services.tel_users.repositories import router as tel_users
from services.tech.repositories import router as tech_router


router = APIRouter()
router.include_router(ads_router, tags=["ads"], prefix="/ads")
router.include_router(proxy_router, tags=["proxy"], prefix="/proxy")
router.include_router(jobs_router, tags=["jobs"], prefix="/jobs")
router.include_router(tech_router, tags=["tech"], prefix="/tech")
router.include_router(tel_users, tags=["telegram"], prefix="/telegram")
