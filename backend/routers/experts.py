from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from ..schemas import ExpertCreate, ExpertOut
from ..crud import create_expert, get_experts
from ..deps import get_db
from typing import List
import shutil
import os

router = APIRouter(prefix="/experts", tags=["experts"])

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/submit", response_model=ExpertOut)
async def submit_expert(
    name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(None),
    bio: str = Form(None),
    roles: str = Form(None),
    sectors: str = Form(None),
    regions: str = Form(None),
    languages: str = Form(None),
    years_experience: int = Form(None),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    # Save file
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    cv_url = file_path
    # Mock parsing and embedding
    expert_data = ExpertCreate(
        name=name,
        email=email,
        phone=phone,
        bio=bio,
        roles=roles.split(",") if roles else [],
        sectors=sectors.split(",") if sectors else [],
        regions=regions.split(",") if regions else [],
        languages=languages.split(",") if languages else [],
        years_experience=years_experience,
        prior_engagements={}
    )
    return await create_expert(db, expert_data, cv_url=cv_url)

@router.get("/list", response_model=List[ExpertOut])
async def list_experts(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)):
    return await get_experts(db, skip=skip, limit=limit) 