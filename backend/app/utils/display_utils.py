"""Display utilities (stubs)."""

def format_currency(value):
    """Format a numeric value as currency (stub)."""
    try:
        return f"${float(value):.4f}"
    except Exception:
        return str(value)
