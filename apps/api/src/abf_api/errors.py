"""Centralised error handling for the API."""

import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

logger = logging.getLogger("abf_api.errors")


class ABFError(Exception):
    """Base exception for all ABF business-logic errors."""

    def __init__(self, message: str, status_code: int = 400, code: str = "ABF_ERROR"):
        self.message = message
        self.status_code = status_code
        self.code = code
        super().__init__(message)


class NotFoundError(ABFError):
    def __init__(self, entity: str, entity_id: str):
        super().__init__(
            message=f"{entity} not found: {entity_id}",
            status_code=404,
            code="NOT_FOUND",
        )


class ValidationError(ABFError):
    def __init__(self, message: str):
        super().__init__(message=message, status_code=422, code="VALIDATION_ERROR")


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(ABFError)
    async def abf_error_handler(_request: Request, exc: ABFError):
        logger.warning("Business error: %s (code=%s)", exc.message, exc.code)
        return JSONResponse(
            status_code=exc.status_code,
            content={"ok": False, "error": {"code": exc.code, "message": exc.message}},
        )

    @app.exception_handler(Exception)
    async def unhandled_error_handler(_request: Request, exc: Exception):
        logger.exception("Unhandled exception: %s", exc)
        return JSONResponse(
            status_code=500,
            content={
                "ok": False,
                "error": {"code": "INTERNAL_ERROR", "message": "An internal error occurred"},
            },
        )
