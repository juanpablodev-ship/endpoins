# Importamos las herramientas de FastAPI para crear rutas
# APIRouter: permite agrupar endpoints bajo un prefijo común
# HTTPException: lanza errores HTTP con código de estado personalizado
# Response: permite modificar las cabeceras de la respuesta
from fastapi import APIRouter, HTTPException, Response
from typing import Optional
# Importamos los schemas de validación y respuesta
from app.schemas.user_schema import UserCreate, UserUpdate, UserPatch, UserResponse, Role

# Creamos un router con prefijo /users para agrupar todos los endpoints de usuarios
# tags=["users"] organiza los endpoints en el Swagger UI
router = APIRouter(prefix="/users", tags=["users"])

# Lista que simula una base de datos en memoria
# Cada usuario es un diccionario con id, name, email, role, is_active
users_db: list[dict] = [
    {"id": 1, "name": "Juan Perez", "email": "juan@test.com", "role": "admin", "is_active": True},
    {"id": 2, "name": "Maria Garcia", "email": "maria@test.com", "role": "support", "is_active": True},
    {"id": 3, "name": "Carlos Lopez", "email": "carlos@test.com", "role": "user", "is_active": True},
    {"id": 4, "name": "Ana Martinez", "email": "ana@test.com", "role": "user", "is_active": False},
    {"id": 5, "name": "Pedro Sanchez", "email": "pedro@test.com", "role": "admin", "is_active": True},
]

# Variable global que genera IDs automáticos para cada usuario nuevo
next_id = 6


# ============================================================
# GET /users/ - Listar todos los usuarios
# Acepta parámetros de consulta (query parameters) opcionales:
#   - role: filtra por rol (admin, support, user)
#   - is_active: filtra por estado (true/false)
# ============================================================
@router.get("/", response_model=list[UserResponse])
def get_users(
    response: Response,
    role: Optional[Role] = None,
    is_active: Optional[bool] = None,
):
    # Agregamos cabeceras personalizadas a la respuesta
    response.headers["X-App-Name"] = "device_systems"
    response.headers["X-API-Version"] = "1.0"

    # Copiamos la lista para no modificar la original
    result = users_db

    # Si se envió el parámetro role, filtramos solo los usuarios con ese rol
    if role is not None:
        result = [u for u in result if u["role"] == role]

    # Si se envió el parámetro is_active, filtramos por estado activo/inactivo
    if is_active is not None:
        result = [u for u in result if u["is_active"] == is_active]

    # Retorna la lista filtrada (o completa si no hay filtros)
    return result


# ============================================================
# GET /users/{user_id} - Obtener un usuario por su ID
# Path Parameter: user_id se extrae de la URL (ej: /users/1)
# ============================================================
@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, response: Response):
    response.headers["X-App-Name"] = "device_systems"
    response.headers["X-API-Version"] = "1.0"

    # Recorremos la lista buscando un usuario con el ID proporcionado
    for user in users_db:
        if user["id"] == user_id:
            return user

    # Si no se encontró ningún usuario con ese ID, lanzamos error 404
    raise HTTPException(status_code=404, detail="Usuario no encontrado")


# ============================================================
# POST /users/ - Crear un nuevo usuario
# Recibe un Body JSON con los datos del usuario
# Valida que el correo no esté duplicado
# Retorna el usuario creado con su ID generado automáticamente
# status_code=201 indica que el recurso fue creado exitosamente
# ============================================================
@router.post("/", response_model=UserResponse, status_code=201)
def create_user(user: UserCreate, response: Response):
    response.headers["X-App-Name"] = "device_systems"
    response.headers["X-API-Version"] = "1.0"

    # Verificamos que no exista otro usuario con el mismo correo
    for u in users_db:
        if u["email"] == user.email:
            raise HTTPException(status_code=400, detail="El correo ya esta registrado")

    # Usamos global para modificar la variable next_id fuera de la función
    global next_id

    # Convertimos el schema Pydantic a diccionario y agregamos el ID
    new_user = {"id": next_id, **user.model_dump()}

    # Incrementamos el contador para el siguiente usuario
    next_id += 1

    # Agregamos el nuevo usuario a la "base de datos"
    users_db.append(new_user)

    return new_user


# ============================================================
# PUT /users/{user_id} - Actualizar TODOS los campos de un usuario
# Reemplaza completamente el usuario con los nuevos datos
# Todos los campos del body son obligatorios
# Valida que el correo no esté duplicado con otro usuario
# ============================================================
@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user: UserUpdate, response: Response):
    response.headers["X-App-Name"] = "device_systems"
    response.headers["X-API-Version"] = "1.0"

    # enumerate() nos da el índice (i) y el usuario (u) en cada iteración
    # El índice es necesario para reemplazar el usuario en esa posición
    for i, u in enumerate(users_db):
        if u["id"] == user_id:
            # Verificamos que el correo no pertenezca a OTRO usuario
            for other in users_db:
                if other["id"] != user_id and other["email"] == user.email:
                    raise HTTPException(status_code=400, detail="El correo ya esta registrado")

            # Reemplazamos el usuario completo, manteniendo el mismo ID
            users_db[i] = {"id": user_id, **user.model_dump()}
            return users_db[i]

    # Si no se encontró el usuario, lanzamos error 404
    raise HTTPException(status_code=404, detail="Usuario no encontrado")


# ============================================================
# PATCH /users/{user_id} - Actualizar campos PARCIALES de un usuario
# Solo actualiza los campos que se envíen en el body
# Los campos no enviados mantienen su valor original
# Valida que el correo no esté duplicado si se está cambiando
# ============================================================
@router.patch("/{user_id}", response_model=UserResponse)
def patch_user(user_id: int, user: UserPatch, response: Response):
    response.headers["X-App-Name"] = "device_systems"
    response.headers["X-API-Version"] = "1.0"

    for i, u in enumerate(users_db):
        if u["id"] == user_id:
            # exclude_unset=True: solo incluye los campos que el usuario envió
            # Si no envió "name", ese campo no estará en update_data
            update_data = user.model_dump(exclude_unset=True)

            # Solo validamos duplicado de correo si se está cambiando el email
            if "email" in update_data:
                for other in users_db:
                    if other["id"] != user_id and other["email"] == update_data["email"]:
                        raise HTTPException(status_code=400, detail="El correo ya esta registrado")

            # Fusionamos los datos originales con los nuevos (**u, **update_data)
            # Los campos nuevos sobreescriben los originales
            users_db[i] = {**u, **update_data}
            return users_db[i]

    raise HTTPException(status_code=404, detail="Usuario no encontrado")


# ============================================================
# DELETE /users/{user_id} - Eliminar un usuario
# Elimina el usuario de la lista por su ID
# Retorna un mensaje de confirmación
# ============================================================
@router.delete("/{user_id}")
def delete_user(user_id: int, response: Response):
    response.headers["X-App-Name"] = "device_systems"
    response.headers["X-API-Version"] = "1.0"

    for i, u in enumerate(users_db):
        if u["id"] == user_id:
            # pop(i) elimina el elemento en la posición i de la lista
            users_db.pop(i)
            return {"detail": "Usuario eliminado correctamente"}

    raise HTTPException(status_code=404, detail="Usuario no encontrado")
