from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
from uuid import UUID

from app.api.deps import (
    get_db,
    get_current_active_user,
    get_admin_user,
    get_manager_user
)
from app.core.security import get_password_hash, verify_password, validate_password_strength
from app.models.user import User, UserRole, Module, user_modules
from app.schemas.user import (
    UserResponse,
    UserCreateByAdmin,
    UserUpdate,
    UserUpdateByAdmin,
    UserUpdatePassword,
    UserModuleAssignment
)

router = APIRouter()

@router.get("/me", response_model=UserResponse)
async def read_user_me(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current user info"""
    # Load modules relationship
    result = await db.execute(
        select(User)
        .options(selectinload(User.modules))
        .where(User.id == current_user.id)
    )
    user = result.scalar_one()
    return user

@router.put("/me", response_model=UserResponse)
async def update_user_me(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Update current user info"""
    update_data = user_update.model_dump(exclude_unset=True)

    if update_data:
        # Check if username/email already exists
        if "username" in update_data or "email" in update_data:
            query = select(User).where(User.id != current_user.id)
            if "username" in update_data:
                query = query.where(User.username == update_data["username"])
            if "email" in update_data:
                query = query.where(User.email == update_data["email"])

            result = await db.execute(query)
            if result.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username or email already exists"
                )

        await db.execute(
            update(User)
            .where(User.id == current_user.id)
            .values(**update_data)
        )
        await db.commit()

    result = await db.execute(
        select(User)
        .options(selectinload(User.modules))
        .where(User.id == current_user.id)
    )
    return result.scalar_one()

@router.put("/me/password")
async def change_password(
    password_update: UserUpdatePassword,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Change current user password"""
    # Verify current password
    if not verify_password(password_update.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect password"
        )

    # Validate new password
    is_valid, error_msg = validate_password_strength(password_update.new_password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )

    # Update password
    await db.execute(
        update(User)
        .where(User.id == current_user.id)
        .values(hashed_password=get_password_hash(password_update.new_password))
    )
    await db.commit()

    return {"detail": "Password updated successfully"}

@router.get("/", response_model=List[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    role: Optional[UserRole] = None,
    is_active: Optional[bool] = None,
    current_user: User = Depends(get_manager_user),
    db: AsyncSession = Depends(get_db)
):
    """List all users (admin and manager only)"""
    query = select(User).options(selectinload(User.modules))

    # Managers can only see kullanici role users
    if current_user.role == UserRole.YONETICI:
        query = query.where(User.role == UserRole.KULLANICI)
    elif role:
        query = query.where(User.role == role)

    if is_active is not None:
        query = query.where(User.is_active == is_active)

    query = query.offset(skip).limit(limit)

    result = await db.execute(query)
    return result.scalars().all()

@router.post("/", response_model=UserResponse)
async def create_user(
    user_in: UserCreateByAdmin,
    current_user: User = Depends(get_manager_user),
    db: AsyncSession = Depends(get_db)
):
    """Create new user (admin and manager only)"""
    # Managers can only create kullanici role users
    if current_user.role == UserRole.YONETICI and user_in.role != UserRole.KULLANICI:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Managers can only create regular users"
        )

    # Check if user exists
    result = await db.execute(
        select(User).where(
            (User.email == user_in.email) | (User.username == user_in.username)
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email or username already exists"
        )

    # Validate password
    is_valid, error_msg = validate_password_strength(user_in.password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )

    # Create user
    user = User(
        email=user_in.email,
        username=user_in.username,
        full_name=user_in.full_name,
        hashed_password=get_password_hash(user_in.password),
        role=user_in.role,
        is_active=user_in.is_active,
        created_by_id=current_user.id
    )

    db.add(user)
    await db.flush()

    # Assign modules if provided
    if user_in.module_ids:
        for module_id in user_in.module_ids:
            await db.execute(
                user_modules.insert().values(
                    user_id=user.id,
                    module_id=module_id,
                    granted_by=current_user.id
                )
            )

    await db.commit()
    await db.refresh(user)

    # Load modules
    result = await db.execute(
        select(User)
        .options(selectinload(User.modules))
        .where(User.id == user.id)
    )
    return result.scalar_one()

@router.get("/{user_id}", response_model=UserResponse)
async def read_user(
    user_id: UUID,
    current_user: User = Depends(get_manager_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user by ID (admin and manager only)"""
    query = select(User).options(selectinload(User.modules)).where(User.id == user_id)

    # Managers can only see kullanici role users
    if current_user.role == UserRole.YONETICI:
        query = query.where(User.role == UserRole.KULLANICI)

    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    user_update: UserUpdateByAdmin,
    current_user: User = Depends(get_manager_user),
    db: AsyncSession = Depends(get_db)
):
    """Update user (admin and manager only)"""
    import logging
    logger = logging.getLogger(__name__)

    # Log the incoming data
    logger.info(f"Updating user {user_id}")
    logger.info(f"Update data: {user_update.model_dump()}")

    # Get user
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Check permissions
    if current_user.role == UserRole.YONETICI:
        if user.role != UserRole.KULLANICI:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Managers can only update regular users"
            )
        # Prevent role change by managers
        if user_update.role and user_update.role != UserRole.KULLANICI:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Managers cannot change user roles"
            )

    update_data = user_update.model_dump(exclude_unset=True, exclude_none=True)

    # Handle password update
    if "password" in update_data:
        is_valid, error_msg = validate_password_strength(update_data["password"])
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg
            )
        update_data["hashed_password"] = get_password_hash(update_data["password"])
        del update_data["password"]

    # Handle module assignment
    if "module_ids" in update_data:
        module_ids = update_data.pop("module_ids")
        # Filter out None and invalid values
        if module_ids is not None:
            # Clear existing modules
            await db.execute(
                delete(user_modules).where(user_modules.c.user_id == user_id)
            )

            # Add new modules - convert string UUIDs to UUID objects
            for module_id_str in module_ids:
                try:
                    module_uuid = UUID(module_id_str) if isinstance(module_id_str, str) else module_id_str
                    await db.execute(
                        user_modules.insert().values(
                            user_id=user_id,
                            module_id=module_uuid,
                            granted_by=current_user.id
                        )
                    )
                except Exception as e:
                    logger.warning(f"Invalid module ID: {module_id_str} - {e}")

    # Update user
    if update_data:
        await db.execute(
            update(User)
            .where(User.id == user_id)
            .values(**update_data)
        )

    await db.commit()

    # Return updated user
    result = await db.execute(
        select(User)
        .options(selectinload(User.modules))
        .where(User.id == user_id)
    )
    return result.scalar_one()

@router.delete("/{user_id}")
async def delete_user(
    user_id: UUID,
    current_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete user (admin only)"""
    # Prevent self-deletion
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )

    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    await db.delete(user)
    await db.commit()

    return {"detail": "User deleted successfully"}