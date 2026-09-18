from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime, timezone
from app.models import UserSignupRequest, UserLoginRequest, TokenResponse, UserResponse
from app.database import get_users_collection
from app.auth import get_password_hash, verify_password, create_access_token, get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post(
    "/signup",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account"
)
async def signup(user_data: UserSignupRequest):
    users_collection = get_users_collection()

    # Check if username already exists
    existing_user = await users_collection.find_one({"username": user_data.username})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Username '{user_data.username}' is already registered."
        )

    # Hash the password and prepare document
    hashed_pwd = get_password_hash(user_data.password)
    now_iso = datetime.now(timezone.utc).isoformat()
    new_user_doc = {
        "name": user_data.name,
        "username": user_data.username,
        "hashed_password": hashed_pwd,
        "created_at": now_iso
    }

    result = await users_collection.insert_one(new_user_doc)
    user_id = str(result.inserted_id)

    # Generate JWT session token
    access_token = create_access_token(data={"sub": user_data.username, "user_id": user_id})

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(
            id=user_id,
            name=user_data.name,
            username=user_data.username,
            created_at=now_iso
        )
    )

@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Log in with username and password"
)
async def login(credentials: UserLoginRequest):
    users_collection = get_users_collection()

    user = await users_collection.find_one({"username": credentials.username})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not verify_password(credentials.password, user.get("hashed_password", "")):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = str(user["_id"])
    access_token = create_access_token(data={"sub": user["username"], "user_id": user_id})

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(
            id=user_id,
            name=user.get("name", ""),
            username=user.get("username", ""),
            created_at=user.get("created_at")
        )
    )

@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get currently logged in user info"
)
async def get_me(current_user: dict = Depends(get_current_user)):
    return UserResponse(
        id=current_user["id"],
        name=current_user["name"],
        username=current_user["username"]
    )
