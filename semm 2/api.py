from fastapi import FastAPI, HTTPException, Response, Depends, Request, status
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
import jwt

from app.models import UserModel
from app.schemas import UserEmPasSchema, EncodeResponse, Data
from app.cruds import SessionDep
from app.core import security, config
from app.services import Coding

app = FastAPI()


@app.post("/sign-up/", status_code=status.HTTP_201_CREATED)
async def sign_up(data: UserEmPasSchema, session: SessionDep):
    try:
        # Проверяем существование пользователя
        existing_user = await session.scalar(
            select(UserModel).where(UserModel.email == data.email)
        )

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пользователь с таким email уже зарегистрирован."
            )

        # Создаем нового пользователя
        new_user = UserModel(email=data.email, password=data.password)
        session.add(new_user)
        await session.commit()

        # Генерируем токен
        access_token = security.create_access_token(uid=str(new_user.id))

        return {
            "message": "Добавлен новый пользователь",
            "id": new_user.id,
            "email": new_user.email,
            "token": access_token
        }

    except SQLAlchemyError:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при создании пользователя"
        )


@app.post("/login/")
async def login(data: UserEmPasSchema, session: SessionDep, response: Response):
    # Проверяем существование пользователя
    user = await session.scalar(
        select(UserModel).where(
            (UserModel.email == data.email) &
            (UserModel.password == data.password)
        )
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неверный email или пароль"
        )

    # Генерируем и устанавливаем токен
    access_token = security.create_access_token(uid=str(user.id))
    response.set_cookie(
        key=config.JWT_ACCESS_COOKIE_NAME,
        value=access_token,
        httponly=True,
        secure=True  # В продакшене должно быть True
    )

    return {
        "message": "Пользователь авторизован",
        "id": user.id,
        "email": user.email,
        "token": access_token
    }


@app.get("/users/me/")
async def user_data(request: Request, session: SessionDep):
    access_token = request.cookies.get(config.JWT_ACCESS_COOKIE_NAME)

    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Требуется авторизация"
        )

    try:
        decoded_token = jwt.decode(
            access_token,
            config.JWT_SECRET_KEY,
            algorithms=["HS256"]
        )
        user_id = decoded_token.get("sub")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный формат токена"
            )

        user = await session.scalar(select(UserModel).where(UserModel.id == user_id))

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден"
            )

        return {"id": user.id, "email": user.email}

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Токен истек"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный токен"
        )


@app.post("/encode", response_model=EncodeResponse, dependencies=[Depends(security.access_token_required)])
async def encode(data: Data):
    try:
        huffman_coding = Coding()
        return huffman_coding.compress_and_encrypt(data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при кодировании: {str(e)}"
        )


@app.post("/decode", dependencies=[Depends(security.access_token_required)])
async def decode(data: EncodeResponse):
    try:
        huffman_coding = Coding()
        return huffman_coding.decrypt_and_decompress(data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при декодировании: {str(e)}"
        )