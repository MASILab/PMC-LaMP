import logging
import uvicorn
import subprocess
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import routers.query_router as query_router
from services.utils import configure_logging
from contextlib import asynccontextmanager

configure_logging()
log = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for FastAPI."""
    from services.model_initializations import ModelLoader

    log.info("Starting FastAPI application...")
    app.state.model_dependencies = ModelLoader().load_models()

    subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "PMC-LaMP.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    print("✓ Streamlit interface started successfully.")
    
    yield
    log.info("Shutting down FastAPI application...")


app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(query_router.router)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
