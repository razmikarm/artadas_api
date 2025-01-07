from fastapi import APIRouter, status

from app.db.database import DBSession
from app.models.auth import TokenResponse, RefreshTokenRequest, Login
from app.utils.auth import authenticate_user, get_current_user, generate_tokens, get_db_refresh_token


router = APIRouter(prefix="/auth")


@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def login(login_data: Login, session: DBSession) -> TokenResponse:
    user = authenticate_user(session, login_data.username, login_data.password)
    token_response = generate_tokens(user, session)
    return token_response


@router.post("/logout", response_model=dict, status_code=status.HTTP_201_CREATED)
def logout(refresh_request: RefreshTokenRequest, session: DBSession) -> dict:
    db_refresh_token = get_db_refresh_token(refresh_request.refresh_token, session)
    db_refresh_token.is_revoked = True
    session.add(db_refresh_token)
    session.commit()
    return {"message": "Successfully logged out."}


@router.post("/refresh", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def refresh_token(refresh_request: RefreshTokenRequest, session: DBSession) -> TokenResponse:
    user = get_current_user(refresh_request.refresh_token, "refresh", session)
    db_refresh_token = get_db_refresh_token(refresh_request.refresh_token, session)
    db_refresh_token.is_revoked = True
    session.add(db_refresh_token)
    session.commit()
    session.refresh(db_refresh_token)
    token_response = generate_tokens(user, session)
    return token_response
