"""
Dev Utilities MCP Server
A collection of developer tools exposed via the Model Context Protocol.
"""

import base64
import json
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from mcp.server.fastmcp import FastMCP

# ── Server definition ──────────────────────────────────────────────────────────
mcp = FastMCP(
    name="dev-utils",
    instructions=(
        "A toolkit of everyday developer utilities: JSON formatting, UUID generation, "
        "Base64 encoding/decoding, timestamp conversion, and HTTP status-code lookup."
    ),
)

# ── HTTP status code reference ─────────────────────────────────────────────────
HTTP_STATUS_CODES: dict[int, tuple[str, str]] = {
    # 1xx
    100: ("Continue", "The server received the request headers and the client should proceed."),
    101: ("Switching Protocols", "The server agrees to switch protocols as requested."),
    # 2xx
    200: ("OK", "The request was successful."),
    201: ("Created", "The request succeeded and a new resource was created."),
    204: ("No Content", "The request succeeded but returns no message body."),
    # 3xx
    301: ("Moved Permanently", "The resource has been permanently moved to a new URL."),
    302: ("Found", "The resource is temporarily at a different URL."),
    304: ("Not Modified", "The cached version of the resource is still valid."),
    # 4xx
    400: ("Bad Request", "The server could not understand the request due to invalid syntax."),
    401: ("Unauthorized", "Authentication is required and has failed or not been provided."),
    403: ("Forbidden", "The server refuses the request even with valid credentials."),
    404: ("Not Found", "The requested resource could not be found."),
    405: ("Method Not Allowed", "The HTTP method is not supported for this resource."),
    409: ("Conflict", "The request conflicts with the current state of the resource."),
    410: ("Gone", "The resource has been permanently deleted and will not return."),
    422: ("Unprocessable Entity", "The request was well-formed but contains semantic errors."),
    429: ("Too Many Requests", "The client has sent too many requests in a given time window."),
    # 5xx
    500: ("Internal Server Error", "The server encountered an unexpected error."),
    501: ("Not Implemented", "The server does not support the request method."),
    502: ("Bad Gateway", "The server received an invalid response from an upstream server."),
    503: ("Service Unavailable", "The server is temporarily unable to handle requests."),
    504: ("Gateway Timeout", "The upstream server failed to respond in time."),
}


# ── Tools ──────────────────────────────────────────────────────────────────────

@mcp.tool(description="Format and validate a JSON string. Returns pretty-printed JSON or a clear error message.")
def format_json(json_string: str, indent: Optional[int] = 2) -> str:
    """
    Args:
        json_string: Raw JSON string to format.
        indent:      Number of spaces per indentation level (default 2).
    """
    try:
        parsed: Any = json.loads(json_string)
        formatted = json.dumps(parsed, indent=indent, ensure_ascii=False)
        lines = formatted.splitlines()
        return (
            f"✓ Valid JSON — {len(lines)} lines, "
            f"{len(json_string)} → {len(formatted)} bytes\n\n"
            f"{formatted}"
        )
    except json.JSONDecodeError as exc:
        return f"✗ Invalid JSON at line {exc.lineno}, column {exc.colno}: {exc.msg}"


@mcp.tool(description="Generate one or more random UUID v4 values.")
def generate_uuid(count: int = 1) -> str:
    """
    Args:
        count: Number of UUIDs to generate (1–20).
    """
    count = max(1, min(count, 20))
    ids = [str(uuid.uuid4()) for _ in range(count)]
    if count == 1:
        return ids[0]
    return "\n".join(f"{i + 1}. {uid}" for i, uid in enumerate(ids))


@mcp.tool(description="Encode a UTF-8 string to Base64 or decode a Base64 string back to text.")
def base64_convert(text: str, mode: str = "encode") -> str:
    """
    Args:
        text: The string to encode or decode.
        mode: Either 'encode' or 'decode' (default 'encode').
    """
    if mode == "encode":
        result = base64.b64encode(text.encode("utf-8")).decode("ascii")
        return f"Encoded ({len(text)} → {len(result)} chars):\n{result}"
    elif mode == "decode":
        try:
            # Accept both standard and URL-safe Base64
            padding = "=" * (-len(text) % 4)
            result = base64.b64decode(text + padding).decode("utf-8")
            return f"Decoded ({len(text)} → {len(result)} chars):\n{result}"
        except Exception as exc:
            return f"✗ Decode failed: {exc}"
    else:
        return f"✗ Unknown mode '{mode}'. Use 'encode' or 'decode'."


@mcp.tool(description="Look up an HTTP status code to get its name and description.")
def http_status(code: int) -> str:
    """
    Args:
        code: HTTP status code (e.g. 404, 500).
    """
    if code in HTTP_STATUS_CODES:
        name, description = HTTP_STATUS_CODES[code]
        family = {1: "Informational", 2: "Success", 3: "Redirection",
                  4: "Client Error", 5: "Server Error"}.get(code // 100, "Unknown")
        return f"{code} {name} [{family}]\n{description}"
    return (
        f"Status code {code} is not in the reference list. "
        f"Standard families: 1xx Informational, 2xx Success, "
        f"3xx Redirection, 4xx Client Error, 5xx Server Error."
    )


@mcp.tool(description="Convert a Unix timestamp (seconds since epoch) to a human-readable UTC datetime, or get the current time.")
def unix_timestamp(timestamp: float | None = None) -> str:
    """
    Args:
        timestamp: Unix timestamp to convert. Omit to get the current time.
    """
    if timestamp is None:
        dt = datetime.now(timezone.utc)
        ts = dt.timestamp()
    else:
        try:
            dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
            ts = timestamp
        except (OSError, OverflowError, ValueError) as exc:
            return f"✗ Invalid timestamp: {exc}"

    return (
        f"Unix:     {ts:.0f}\n"
        f"ISO 8601: {dt.isoformat()}\n"
        f"UTC:      {dt.strftime('%A, %d %B %Y %H:%M:%S UTC')}"
    )


# ── Resources ──────────────────────────────────────────────────────────────────

@mcp.resource("utils://http-status-codes")
def all_http_status_codes() -> str:
    """A reference list of all HTTP status codes known to this server."""
    lines = ["# HTTP Status Code Reference\n"]
    current_family = None
    for code, (name, desc) in sorted(HTTP_STATUS_CODES.items()):
        family = code // 100
        if family != current_family:
            current_family = family
            labels = {1: "1xx — Informational", 2: "2xx — Success",
                      3: "3xx — Redirection", 4: "4xx — Client Error",
                      5: "5xx — Server Error"}
            lines.append(f"\n## {labels.get(family, f'{family}xx')}\n")
        lines.append(f"**{code} {name}** — {desc}")
    return "\n".join(lines)


# ── Entry point ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    mcp.run()
