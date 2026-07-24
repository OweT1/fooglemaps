from fastapi import APIRouter, Depends, HTTPException
from loguru import logger
from sqlalchemy import select, insert, func
from sqlalchemy.ext.asyncio import AsyncSession

from ..deps import verify_google_token, get_session
from ..models import LoginResponse, UserResponse, SettingsResponse, User, UserSettings

router = APIRouter()


@router.post("/login", response_model=LoginResponse)
async def login(
    user_info: dict = Depends(verify_google_token),
    session: AsyncSession = Depends(get_session),
):
    sub = user_info["sub"]
    email = user_info["email"]
    name = user_info.get("name", "")
    picture = user_info.get("picture")

    logger.info("User login: sub={}, email={}", sub, email)
    result = await session.execute(
        insert(User)
        .values(google_sub=sub, email=email, display_name=name, avatar_url=picture)
        .on_conflict_do_update(
            index_elements=["google_sub"],
            set_=dict(email=email, display_name=name, avatar_url=picture, updated_at=func.now()),
        )
        .returning(User)
    )
    user = result.scalar_one()
    logger.debug("User upserted: id={}", user.id)

    await session.execute(
        insert(UserSettings).values(user_id=user.id).on_conflict_do_nothing(index_elements=["user_id"])
    )
    await session.commit()

    result = await session.execute(select(UserSettings).where(UserSettings.user_id == user.id))
    s = result.scalar_one()
    logger.info("Login successful: sub={}", sub)

    return LoginResponse(
        user=UserResponse(id=str(user.id), sub=sub, email=email, name=name, picture=picture),
        settings=SettingsResponse(
            id=str(s.id),
            user_id=str(s.user_id),
            theme=s.theme,
            default_zoom=s.default_zoom,
            map_type=s.map_type,
            notify_new_spots=s.notify_new_spots,
            notify_recommendations=s.notify_recommendations,
        ),
    )


@router.get("/me", response_model=LoginResponse)
async def me(
    user_info: dict = Depends(verify_google_token),
    session: AsyncSession = Depends(get_session),
):
    sub = user_info["sub"]
    logger.debug("Fetching user info: sub={}", sub)

    result = await session.execute(select(User).where(User.google_sub == sub))
    u = result.scalar_one_or_none()
    if not u:
        logger.warning("User not found: sub={}", sub)
        raise HTTPException(status_code=404, detail="User not found")

    result = await session.execute(select(UserSettings).where(UserSettings.user_id == u.id))
    s = result.scalar_one()
    logger.debug("User info retrieved: id={}", u.id)

    return LoginResponse(
        user=UserResponse(id=str(u.id), sub=u.google_sub, email=u.email, name=u.display_name, picture=u.avatar_url),
        settings=SettingsResponse(
            id=str(s.id),
            user_id=str(s.user_id),
            theme=s.theme,
            default_zoom=s.default_zoom,
            map_type=s.map_type,
            notify_new_spots=s.notify_new_spots,
            notify_recommendations=s.notify_recommendations,
        ),
    )
