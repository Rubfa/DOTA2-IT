"""
This app no longer defines its own models.
All data models are sourced from mocktrade.models directly.
"""

from mocktrade.models import (  # noqa: F401
    Cometics,
    Heros,
    Maket_records,
    Mock_tradings,
)
