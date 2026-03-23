"""Custom exceptions for the semitone API."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class InvalidNoteError(Exception):
    def __init__(self, note: str):
        self.note = note


class InvalidScaleTypeError(Exception):
    def __init__(self, scale_type: str):
        self.scale_type = scale_type


def register_exception_handlers(app: FastAPI):
    @app.exception_handler(InvalidNoteError)
    async def invalid_note_handler(_: Request, exc: InvalidNoteError):
        return JSONResponse(
            status_code=400,
            content={
                "error": "invalid_note",
                "detail": f"'{exc.note}' is not a recognized note name.",
            },
        )

    @app.exception_handler(InvalidScaleTypeError)
    async def invalid_scale_type_handler(
        _: Request, exc: InvalidScaleTypeError
    ):
        return JSONResponse(
            status_code=400,
            content={
                "error": "invalid_scale_type",
                "detail": f"'{exc.scale_type}' is not a supported scale type.",
            },
        )
