from rest_framework.views import exception_handler
from rest_framework import status
from rest_framework.exceptions import ValidationError, NotFound, PermissionDenied, AuthenticationFailed
from rest_framework.response import Response


def _flatten_validation(detail, prefix=""):
    """
    Convert DRF ValidationError detail into:
      [{ "path": "field.subfield", "message": "..." }, ...]
    """
    items = []

    if isinstance(detail, list):
        for v in detail:
            items.extend(_flatten_validation(v, prefix))
        return items

    if isinstance(detail, dict):
        for k, v in detail.items():
            next_prefix = f"{prefix}.{k}" if prefix else str(k)
            items.extend(_flatten_validation(v, next_prefix))
        return items

    # scalar / string
    items.append({"path": prefix or "", "message": str(detail)})
    return items


def api_exception_handler(exc, context):
    resp = exception_handler(exc, context)

    if resp is None:
        return Response(
            {"error": {"code": "SERVER_ERROR", "message": "Internal server error.", "details": []}},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    if isinstance(exc, ValidationError):
        details = _flatten_validation(resp.data)
        return Response(
            {"error": {"code": "VALIDATION_ERROR", "message": "Validation failed.", "details": details}},
            status=resp.status_code,
        )

    if isinstance(exc, (AuthenticationFailed,)):
        return Response(
            {"error": {"code": "UNAUTHENTICATED", "message": "Authentication failed.", "details": []}},
            status=resp.status_code,
        )

    if isinstance(exc, PermissionDenied):
        return Response(
            {"error": {"code": "FORBIDDEN", "message": "Permission denied.", "details": []}},
            status=resp.status_code,
        )

    if isinstance(exc, NotFound):
        return Response(
            {"error": {"code": "NOT_FOUND", "message": "Not found.", "details": []}},
            status=resp.status_code,
        )

    # fallback: wrap DRF’s message
    return Response(
        {"error": {"code": "API_ERROR", "message": "Request failed.", "details": [{"path": "", "message": str(resp.data)}]}},
        status=resp.status_code,
    )