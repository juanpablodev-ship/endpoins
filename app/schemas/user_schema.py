# Importamos las herramientas de Pydantic para crear modelos de validación
# BaseModel: clase base para crear schemas de entrada/salida de datos
# EmailStr: tipo de dato que valida formato de correo electrónico
# Field: permite definir reglas de validación en cada campo
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
# Enum: crea enumeraciones con valores permitidos (solo admin, support, user)
from enum import Enum


# Enumeración que define los roles válidos para un usuario
# Hereda de str y Enum para que pueda serializarse como string
class Role(str, Enum):
    admin = "admin"      # Rol de administrador
    support = "support"  # Rol de soporte
    user = "user"        # Rol de usuario básico


# Schema de entrada para CREAR un usuario (POST)
# Todos los campos son obligatorios excepto is_active (tiene valor por defecto)
class UserCreate(BaseModel):
    name: str = Field(..., min_length=3, description="Nombre del usuario")
    email: EmailStr = Field(..., description="Correo electronico")
    role: Role = Field(..., description="Rol del usuario")
    is_active: bool = Field(default=True, description="Estado activo/inactivo")


# Schema de entrada para ACTUALIZAR completamente un usuario (PUT)
# Todos los campos son obligatorios (reemplaza todos los valores)
class UserUpdate(BaseModel):
    name: str = Field(..., min_length=3, description="Nombre del usuario")
    email: EmailStr = Field(..., description="Correo electronico")
    role: Role = Field(..., description="Rol del usuario")
    is_active: bool = Field(default=True, description="Estado activo/inactivo")


# Schema de entrada para ACTUALIZAR parcialmente un usuario (PATCH)
# Todos los campos son opcionales, solo se actualizan los que se envíen
class UserPatch(BaseModel):
    name: Optional[str] = Field(None, min_length=3, description="Nombre del usuario")
    email: Optional[EmailStr] = Field(None, description="Correo electronico")
    role: Optional[Role] = Field(None, description="Rol del usuario")
    is_active: Optional[bool] = Field(None, description="Estado activo/inactivo")


# Schema de SALIDA que define qué datos devuelve la API
# Incluye el id que se genera automáticamente al crear el usuario
class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: Role
    is_active: bool
