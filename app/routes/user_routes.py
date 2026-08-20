from fastapi import APIRouter, HTTPException, Response
from typing import Optional
from app.schemas.user_schema import UserCreate, UserResponse, Role

router = APIRouter(prefix="/users", tags=["users"])

users_db: list[dict] = []
next_id = 1


@router.get("/", response_model=list[UserResponse])
def get_users(
    response: Response,
    role: Optional[Role] = None,
    is_active: Optional[bool] = None,
):
    response.headers["X-App-Name"] = "device_systems"
    response.headers["X-API-Version"] = "1.0"
    result = users_db
    if role is not None:
        result = [u for u in result if u["role"] == role]
    if is_active is not None:
        result = [u for u in result if u["is_active"] == is_active]
    return result


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, response: Response):
    response.headers["X-App-Name"] = "device_systems"
    response.headers["X-API-Version"] = "1.0"
    for user in users_db:
        if user["id"] == user_id:
            return user
    raise HTTPException(status_code=404, detail="Usuario no encontrado")


@router.post("/", response_model=UserResponse, status_code=201)
def create_user(user: UserCreate, response: Response):
    response.headers["X-App-Name"] = "device_systems"
    response.headers["X-API-Version"] = "1.0"
    for u in users_db:
        if u["email"] == user.email:
            raise HTTPException(status_code=400, detail="El correo ya esta registrado")
    global next_id
    new_user = {"id": next_id, **user.model_dump()}
    next_id += 1
    users_db.append(new_user)
    return new_user
