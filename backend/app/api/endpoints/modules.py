from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from uuid import UUID

from app.api.deps import get_db, get_admin_user
from app.models.user import Module
from app.schemas.user import ModuleCreate, ModuleResponse

router = APIRouter()

@router.get("/", response_model=List[ModuleResponse])
async def list_modules(
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """List all modules (admin only)"""
    query = select(Module).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

@router.post("/", response_model=ModuleResponse)
async def create_module(
    module_in: ModuleCreate,
    current_user = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Create new module (admin only)"""
    # Check if module exists
    result = await db.execute(
        select(Module).where(Module.name == module_in.name)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Module with this name already exists"
        )

    module = Module(**module_in.model_dump())
    db.add(module)
    await db.commit()
    await db.refresh(module)

    return module

@router.get("/{module_id}", response_model=ModuleResponse)
async def read_module(
    module_id: UUID,
    current_user = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Get module by ID (admin only)"""
    result = await db.execute(
        select(Module).where(Module.id == module_id)
    )
    module = result.scalar_one_or_none()

    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module not found"
        )

    return module

@router.put("/{module_id}", response_model=ModuleResponse)
async def update_module(
    module_id: UUID,
    module_update: ModuleCreate,
    current_user = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Update module (admin only)"""
    result = await db.execute(
        select(Module).where(Module.id == module_id)
    )
    module = result.scalar_one_or_none()

    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module not found"
        )

    update_data = module_update.model_dump()

    await db.execute(
        update(Module)
        .where(Module.id == module_id)
        .values(**update_data)
    )
    await db.commit()

    result = await db.execute(
        select(Module).where(Module.id == module_id)
    )
    return result.scalar_one()

@router.delete("/{module_id}")
async def delete_module(
    module_id: UUID,
    current_user = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete module (admin only)"""
    result = await db.execute(
        select(Module).where(Module.id == module_id)
    )
    module = result.scalar_one_or_none()

    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module not found"
        )

    await db.delete(module)
    await db.commit()

    return {"detail": "Module deleted successfully"}