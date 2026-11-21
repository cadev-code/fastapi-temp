class DomainError(Exception):
    """Base class for domain errors."""

class NotFoundError(DomainError):
    """Resource not found."""

class BusinessRuleError(DomainError):
    """Violation of a business rule."""