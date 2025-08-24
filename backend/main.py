# NOTE: If you see 'Import "fastapi" could not be resolved', ensure FastAPI is installed in your environment.
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import auth, experts

app: FastAPI = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(experts.router)

@app.get("/health")
def health_check() -> dict:
    return {"status": "ok"} 