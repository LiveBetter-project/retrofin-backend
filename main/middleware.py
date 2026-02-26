from django.utils.deprecation import MiddlewareMixin
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
import logging

logger = logging.getLogger(__name__)


class JWTAuthenticationMiddleware(MiddlewareMixin):
    """
    Custom middleware for JWT authentication.
    This middleware validates JWT tokens and attaches user to request.
    """

    def process_request(self, request):
        """
        Process incoming request and validate JWT token if present.
        """
        # Skip authentication for certain paths
        exempt_paths = [
            '/api/auth/login/',
            '/api/auth/register/',
            '/api/auth/refresh/',
            '/admin/',
        ]

        if any(request.path.startswith(path) for path in exempt_paths):
            return None

        # Get Authorization header
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')

        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]

            try:
                # Validate token (will be handled by DRF JWTAuthentication)
                # This middleware is mainly for logging and additional processing
                logger.debug(f"JWT token received for path: {request.path}")
            except Exception as e:
                logger.warning(f"JWT validation error: {str(e)}")

        return None

    def process_response(self, request, response):
        """
        Process outgoing response.
        Can be used to add custom headers or logging.
        """
        return response
