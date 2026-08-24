# Importamos FastAPI, la clase principal para crear la aplicación
from fastapi import FastAPI
# Importamos el router de usuarios (lo renombramos como user_router para evitar conflictos)
from app.routes.user_routes import router as user_router

# Creamos la instancia de FastAPI con título y versión de la API
# Estos datos aparecen en la documentación Swagger UI
app = FastAPI(title="device_systems", version="1.0")

# Registramos el router de usuarios para que sus endpoints estén disponibles
# Todos los endpoints del router (prefijo /users) se agregan a la app
app.include_router(user_router)


# Endpoint raíz que verifica que la API esté funcionando
# GET / retorna un mensaje de bienvenida
@app.get("/")
def read_root():
    return {"mensaje": "Bienvenido a device_systems"}
