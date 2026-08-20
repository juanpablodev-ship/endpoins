from fastapi import FastAPI
from app.routes.user_routes import router as user_router

app = FastAPI(title="device_systems", version="1.0")

app.include_router(user_router)


@app.get("/")
def read_root():
    return {"mensaje": "Bienvenido a device_systems"}
