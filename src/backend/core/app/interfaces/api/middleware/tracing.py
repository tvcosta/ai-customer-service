"""Tracing middleware for injecting interaction_id into response headers."""

from __future__ import annotations

import json

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response


class InteractionIdMiddleware(BaseHTTPMiddleware):
    """Middleware that injects ``X-Interaction-Id`` into response headers.

    Reads the JSON response body and, if it contains an ``interaction_id``
    field, adds it as the ``X-Interaction-Id`` HTTP response header. Only
    responses with ``Content-Type: application/json`` are inspected; all
    other responses pass through unchanged.
    """

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """Process the request and inject the interaction ID header.

        Args:
            request: Incoming HTTP request.
            call_next: Next middleware or route handler.

        Returns:
            HTTP response, potentially with ``X-Interaction-Id`` header added.
        """
        response = await call_next(request)

        content_type = response.headers.get("content-type", "")
        if "application/json" not in content_type:
            return response

        body = b""
        async for chunk in response.body_iterator:  # type: ignore[attr-defined]
            body += chunk

        try:
            payload = json.loads(body)
            interaction_id = payload.get("interaction_id")
        except (json.JSONDecodeError, AttributeError):
            interaction_id = None

        headers = dict(response.headers)
        if interaction_id:
            headers["x-interaction-id"] = str(interaction_id)

        return Response(
            content=body,
            status_code=response.status_code,
            headers=headers,
            media_type=response.media_type,
        )
