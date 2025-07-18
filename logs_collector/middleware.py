"""Middleware for basic authentication in Django."""

import base64

from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from django.http.request import HttpRequest


class BasicAuthMiddleware:
    """Middleware for basic authentication in Django."""

    def __init__(self, get_response: callable) -> None:
        """Initialize the middleware."""
        self.get_response = get_response
        self.realm = 'Restricted Area'

    def __call__(self, request: HttpRequest) -> HttpResponse:
        """Process the request and apply basic authentication."""
        # Пропускаем аутентификацию для эндпоинта /receiver.
        if request.path.startswith('/receiver'):
            return self.get_response(request)

        auth = request.META.get('HTTP_AUTHORIZATION')
        if auth is None or not auth.startswith('Basic '):
            return self._unauthorized_response()
        # Декодируем и проверяем логин/пароль.
        encoded_credentials = auth.split(' ')[1]
        try:
            decoded_credentials = base64.b64decode(encoded_credentials).decode('utf-8')
        except Exception:
            return self._unauthorized_response()
        username, sep, password = decoded_credentials.partition(':')
        if not sep:
            return self._unauthorized_response()
        user = authenticate(request, username=username, password=password)
        if user is None:
            return self._unauthorized_response()
        # Логиним пользователя в сессии, чтобы Django понимал, что он авторизован
        login(request, user)

        return self.get_response(request)

    def _unauthorized_response(self) -> HttpResponse:
        """Return an unauthorized response with a WWW-Authenticate header."""
        response = HttpResponse('Unauthorized', status=401)
        response['WWW-Authenticate'] = f'Basic realm="{self.realm}"'
        return response
