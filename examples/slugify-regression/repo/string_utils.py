def slugify(value: str) -> str:
    """Convert simple text into a lowercase dash-separated slug."""
    return value.strip().lower().replace(" ", "-")
