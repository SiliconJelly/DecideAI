from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from .models import User, Expert
from .schemas import UserCreate, ExpertCreate
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(select(User).where(User.email == email))
    return result.scalars().first()

async def create_user(db: AsyncSession, user: UserCreate):
    hashed_password = pwd_context.hash(user.password)
    db_user = User(
        name=user.name,
        email=user.email,
        role=user.role,
        password_hash=hashed_password
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def create_expert(db: AsyncSession, expert: ExpertCreate, cv_url: str = None):
    db_expert = Expert(
        **expert.dict(),
        cv_url=cv_url
    )
    db.add(db_expert)
    await db.commit()
    await db.refresh(db_expert)
    return db_expert

async def get_expert_by_email(db: AsyncSession, email: str):
    result = await db.execute(select(Expert).where(Expert.email == email))
    return result.scalars().first()

async def get_experts(db: AsyncSession, skip: int = 0, limit: int = 10):
    result = await db.execute(select(Expert).offset(skip).limit(limit))
    return result.scalars().all() 