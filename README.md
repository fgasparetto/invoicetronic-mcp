<!-- mcp-name: io.github.fgasparetto/invoicetronic-mcp -->

# Invoicetronic MCP Server

MCP server for the [Invoicetronic](https://invoicetronic.com) API — Italian electronic invoicing through the SDI (Servizio di Interscambio).

Built with [FastMCP](https://github.com/modelcontextprotocol/python-sdk) (Python).

## Features

20 tools covering the full Invoicetronic API:

| Category | Tools |
|----------|-------|
| **Account** | `account_status`, `health_check` |
| **Send** | `list_sent_invoices`, `get_sent_invoice`, `get_sent_invoice_by_identifier`, `get_sent_invoice_payload`, `send_invoice_xml`, `validate_invoice_xml` |
| **Receive** | `list_received_invoices`, `get_received_invoice`, `get_received_invoice_payload` |
| **Company** | `list_companies`, `get_company` |
| **Events** | `list_events`, `get_event` |
| **Updates** | `list_updates`, `get_update` |
| **Export** | `export_invoices` |

## Setup

### Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip
- An [Invoicetronic](https://invoicetronic.com) API key

### Claude Code

Add to your `.mcp.json`:

```json
{
  "mcpServers": {
    "invoicetronic": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/invoicetronic-mcp", "server.py"],
      "env": {
        "INVOICETRONIC_API_KEY": "your-api-key"
      }
    }
  }
}
```

### Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "invoicetronic": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/invoicetronic-mcp", "server.py"],
      "env": {
        "INVOICETRONIC_API_KEY": "your-api-key"
      }
    }
  }
}
```

## Authentication

The Invoicetronic API uses Basic auth with your API key as the username and an empty password. Set the `INVOICETRONIC_API_KEY` environment variable.

Get your API key at [invoicetronic.com](https://invoicetronic.com).

## API Reference

Full API docs: [api.invoicetronic.com](https://api.invoicetronic.com)

## License

MIT
