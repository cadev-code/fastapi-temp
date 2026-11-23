import structlog
from fastapi import Request, status
from fastapi.responses import ORJSONResponse

logger = structlog.get_logger(__name__)


class DomainError(Exception):
    """Base class for domain errors."""


class NotFoundError(DomainError):
    """Resource not found."""


class BusinessRuleError(DomainError):
    """Violation of a business rule."""


async def not_found_exception_handler(
    request: Request, exc: NotFoundError
) -> ORJSONResponse:
    return ORJSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "detail": str(exc) or "Recurso no encontrado.",
            "request_id": getattr(request.state, "request_id", None),
        },
    )


async def business_rule_exception_handler(
    request: Request, exc: BusinessRuleError
) -> ORJSONResponse:
    return ORJSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "detail": str(exc) or "Regla de negocio violada.",
            "request_id": getattr(request.state, "request_id", None),
        },
    )


async def global_exception_handler(request: Request, exc: Exception) -> ORJSONResponse:
    logger.exception(
        "unhandled_exception",
        path=request.url.path,
        method=request.method,
    )
    return ORJSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Error interno del servidor.",
            "request_id": getattr(request.state, "request_id", None),
        },
    )
