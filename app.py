import logging
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import routers.query_router as query_router
from services.utils import configure_logging

configure_logging()
log = logging.getLogger(__name__)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    from services.model_initializations import ModelLoader

    app.state.model_dependencies = ModelLoader().load_models()
    log.info("Models loaded and assigned to app state during startup")


app.include_router(query_router.router)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
