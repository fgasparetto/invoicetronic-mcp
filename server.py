# /// script
# requires-python = ">=3.11"
# dependencies = ["mcp[cli]>=1.0.0", "httpx>=0.27.0"]
# ///
"""Invoicetronic MCP Server — Italian e-invoicing via SDI (Servizio di Interscambio).

Tools: account status, send/list/get invoices, receive invoices, validate, events log.
Auth: Basic auth (API key as username, empty password).
"""

import base64
import os
from typing import Any

import httpx
from mcp.server.fastmcp import FastMCP

API_BASE = "https://api.invoicetronic.com/v1"
API_KEY = os.environ.get("INVOICETRONIC_API_KEY", "")

mcp = FastMCP(
    "invoicetronic",
    instructions=(
        "Invoicetronic MCP server for Italian electronic invoicing (fatturazione elettronica). "
        "Manages sending and receiving invoices through the SDI (Servizio di Interscambio). "
        "Use account_status to check credits/limits. Use list_sent_invoices and list_received_invoices "
        "to browse invoices. Use send_invoice_xml to send FatturaPA XML. Use validate_invoice_xml to "
        "validate before sending."
    ),
)


def _auth_headers() -> dict[str, str]:
    token = base64.b64encode(f"{API_KEY}:".encode()).decode()
    return {
        "Authorization": f"Basic {token}",
        "Accept": "application/json",
    }


def _client() -> httpx.Client:
    return httpx.Client(base_url=API_BASE, headers=_auth_headers(), timeout=30)


def _format_error(resp: httpx.Response) -> str:
    try:
        data = resp.json()
        return f"HTTP {resp.status_code}: {data}"
    except Exception:
        return f"HTTP {resp.status_code}: {resp.text[:500]}"


# --- Account ---


@mcp.tool()
def account_status() -> dict[str, Any]:
    """Get Invoicetronic account status (credits, limits, usage)."""
    with _client() as c:
        r = c.get("/status")
        if r.status_code != 200:
            return {"error": _format_error(r)}
        return r.json()


@mcp.tool()
def health_check() -> dict[str, Any]:
    """Check if the Invoicetronic API is healthy."""
    with _client() as c:
        r = c.get("/health")
        if r.status_code != 200:
            return {"error": _format_error(r)}
        return r.json()


# --- Send (outgoing invoices) ---


@mcp.tool()
def list_sent_invoices(
    company_id: int | None = None,
    identifier: str | None = None,
    committente: str | None = None,
    prestatore: str | None = None,
    file_name: str | None = None,
) -> dict[str, Any]:
    """List sent (outgoing) invoices. Filter by company_id, SDI identifier, VAT/fiscal code (committente/prestatore), or file_name."""
    params = {}
    if company_id is not None:
        params["company_id"] = company_id
    if identifier:
        params["identifier"] = identifier
    if committente:
        params["committente"] = committente
    if prestatore:
        params["prestatore"] = prestatore
    if file_name:
        params["file_name"] = file_name
    with _client() as c:
        r = c.get("/send", params=params)
        if r.status_code != 200:
            return {"error": _format_error(r)}
        return {"invoices": r.json()}


@mcp.tool()
def get_sent_invoice(invoice_id: int) -> dict[str, Any]:
    """Get a sent invoice by its numeric ID."""
    with _client() as c:
        r = c.get(f"/send/{invoice_id}")
        if r.status_code != 200:
            return {"error": _format_error(r)}
        return r.json()


@mcp.tool()
def get_sent_invoice_by_identifier(identifier: str) -> dict[str, Any]:
    """Get a sent invoice by its SDI identifier string."""
    with _client() as c:
        r = c.get(f"/send/{identifier}")
        if r.status_code != 200:
            return {"error": _format_error(r)}
        return r.json()


@mcp.tool()
def get_sent_invoice_payload(invoice_id: int) -> dict[str, Any]:
    """Get the XML payload of a sent invoice by ID."""
    with _client() as c:
        r = c.get(f"/send/{invoice_id}/payload")
        if r.status_code != 200:
            return {"error": _format_error(r)}
        return {"payload": r.text}


@mcp.tool()
def send_invoice_xml(
    xml_content: str,
    validate: bool = True,
    signature: bool = True,
) -> dict[str, Any]:
    """Send a FatturaPA XML invoice to SDI. Set validate=True to pre-validate, signature=True for digital signing."""
    headers = _auth_headers()
    headers["Content-Type"] = "application/xml"
    params = {"validate": str(validate).lower(), "signature": str(signature).lower()}
    with _client() as c:
        r = c.post("/send/xml", content=xml_content.encode("utf-8"), headers=headers, params=params)
        if r.status_code not in (200, 201):
            return {"error": _format_error(r)}
        return r.json()


@mcp.tool()
def validate_invoice_xml(xml_content: str) -> dict[str, Any]:
    """Validate a FatturaPA XML invoice without sending it."""
    headers = _auth_headers()
    headers["Content-Type"] = "application/xml"
    with _client() as c:
        r = c.post("/send/validate/xml", content=xml_content.encode("utf-8"), headers=headers)
        if r.status_code not in (200, 201):
            return {"error": _format_error(r)}
        return r.json()


# --- Receive (incoming invoices) ---


@mcp.tool()
def list_received_invoices(
    company_id: int | None = None,
    identifier: str | None = None,
    unread: bool | None = None,
    committente: str | None = None,
    prestatore: str | None = None,
) -> dict[str, Any]:
    """List received (incoming) invoices. Filter by company_id, SDI identifier, unread status, VAT/fiscal code."""
    params = {}
    if company_id is not None:
        params["company_id"] = company_id
    if identifier:
        params["identifier"] = identifier
    if unread is not None:
        params["unread"] = str(unread).lower()
    if committente:
        params["committente"] = committente
    if prestatore:
        params["prestatore"] = prestatore
    with _client() as c:
        r = c.get("/receive", params=params)
        if r.status_code != 200:
            return {"error": _format_error(r)}
        return {"invoices": r.json()}


@mcp.tool()
def get_received_invoice(invoice_id: int) -> dict[str, Any]:
    """Get a received invoice by its numeric ID."""
    with _client() as c:
        r = c.get(f"/receive/{invoice_id}")
        if r.status_code != 200:
            return {"error": _format_error(r)}
        return r.json()


@mcp.tool()
def get_received_invoice_payload(invoice_id: int) -> dict[str, Any]:
    """Get the XML payload of a received invoice by ID."""
    with _client() as c:
        r = c.get(f"/receive/{invoice_id}/payload")
        if r.status_code != 200:
            return {"error": _format_error(r)}
        return {"payload": r.text}


# --- Company ---


@mcp.tool()
def list_companies() -> dict[str, Any]:
    """List all companies configured in the Invoicetronic account."""
    with _client() as c:
        r = c.get("/company")
        if r.status_code != 200:
            return {"error": _format_error(r)}
        return {"companies": r.json()}


@mcp.tool()
def get_company(company_id: int) -> dict[str, Any]:
    """Get a company by its numeric ID."""
    with _client() as c:
        r = c.get(f"/company/{company_id}")
        if r.status_code != 200:
            return {"error": _format_error(r)}
        return r.json()


# --- Events log ---


@mcp.tool()
def list_events() -> dict[str, Any]:
    """List recent events/log entries from the Invoicetronic account."""
    with _client() as c:
        r = c.get("/log")
        if r.status_code != 200:
            return {"error": _format_error(r)}
        return {"events": r.json()}


@mcp.tool()
def get_event(event_id: int) -> dict[str, Any]:
    """Get a specific event/log entry by ID."""
    with _client() as c:
        r = c.get(f"/log/{event_id}")
        if r.status_code != 200:
            return {"error": _format_error(r)}
        return r.json()


# --- Updates (SDI status updates) ---


@mcp.tool()
def list_updates() -> dict[str, Any]:
    """List SDI status updates (notifications about invoice processing)."""
    with _client() as c:
        r = c.get("/update")
        if r.status_code != 200:
            return {"error": _format_error(r)}
        return {"updates": r.json()}


@mcp.tool()
def get_update(update_id: int) -> dict[str, Any]:
    """Get a specific SDI update by ID."""
    with _client() as c:
        r = c.get(f"/update/{update_id}")
        if r.status_code != 200:
            return {"error": _format_error(r)}
        return r.json()


# --- Export ---


@mcp.tool()
def export_invoices() -> dict[str, Any]:
    """Export all invoices as a ZIP archive. Returns the download URL or binary info."""
    with _client() as c:
        r = c.get("/export")
        if r.status_code != 200:
            return {"error": _format_error(r)}
        return {"content_type": r.headers.get("content-type"), "size": len(r.content)}


if __name__ == "__main__":
    mcp.run()
