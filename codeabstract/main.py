"""FastAPI application entrypoint."""

from fastapi import FastAPI

from codeabstract.routes import router

app = FastAPI(title="CodeAbstract API")
app.include_router(router)

