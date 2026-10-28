from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import logging

# Set up logging to a file
logging.basicConfig(
    filename="backend_errors.log",
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s\n"
)
logger = logging.getLogger(__name__)

import os
from fastapi.staticfiles import StaticFiles
from app.routes.auth import router as auth_router 
from app.routes.creations import router as creations_router

app = FastAPI(
    title="FastApi Backend"
)

#  mount for serving generated videos
os.makedirs("storage/videos", exist_ok=True)
app.mount("/static", StaticFiles(directory="storage"), name="static")

  
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Error on {request.method} {request.url.path}: {str(exc)}", exc_info=exc)
    return JSONResponse(
        status_code=500,
        content={"success": False, "message": "Internal Server Error", "detail": str(exc)}
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router) 
app.include_router(creations_router)

@app.get("/")
def root():
    return {"message" : "Api is running"}