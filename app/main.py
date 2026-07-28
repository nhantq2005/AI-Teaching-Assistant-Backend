from fastapi import FastAPI

from app.routers import user, subject, enrollment, question, option, quiz
from app.routers.document import router as document_router

from app.core.config import settings

app = FastAPI()

settings.configure_cloudinary()


app.include_router(document_router, prefix="/api")
app.include_router(user.router, prefix="/api")
app.include_router(subject.router, prefix="/api")
app.include_router(enrollment.router, prefix="/api")
app.include_router(question.router, prefix="/api")
app.include_router(option.router, prefix="/api")
app.include_router(quiz.router, prefix="/api")


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


