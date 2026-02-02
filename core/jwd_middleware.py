"""
JWT Authentication Middleware for WebSocket connections.

Extracts JWT token from query string or Authorization header and attaches
the authenticated user to the connection scope.
"""

from urllib.parse import parse_qs

from django.contrib.auth.models import AnonymousUser
from django.db import close_old_connections
from channels.db import database_sync_to_async
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError


@database_sync_to_async
def get_user_from_token(token: str):
	"""Return user from JWT token or AnonymousUser if invalid."""
	try:
		jwt_auth = JWTAuthentication()
		validated_token = jwt_auth.get_validated_token(token)
		return jwt_auth.get_user(validated_token)
	except (InvalidToken, TokenError):
		return AnonymousUser()


class JWTAuthMiddleware:
	"""Custom JWT auth middleware for Django Channels."""

	def __init__(self, inner):
		self.inner = inner

	async def __call__(self, scope, receive, send):
		close_old_connections()

		token = None

		# 1) Try token from query string: ws://.../?token=...
		query_string = scope.get("query_string", b"").decode()
		if query_string:
			params = parse_qs(query_string)
			token_list = params.get("token")
			if token_list:
				token = token_list[0]

		# 2) Try token from Authorization header: Bearer <token>
		if not token:
			headers = dict(scope.get("headers", []))
			auth_header = headers.get(b"authorization")
			if auth_header:
				auth_header = auth_header.decode()
				if auth_header.lower().startswith("bearer "):
					token = auth_header.split(" ", 1)[1].strip()

		if token:
			scope["user"] = await get_user_from_token(token)
		else:
			scope["user"] = AnonymousUser()

		return await self.inner(scope, receive, send)


def JWTAuthMiddlewareStack(inner):
	"""Helper to apply JWTAuthMiddleware."""
	return JWTAuthMiddleware(inner)
