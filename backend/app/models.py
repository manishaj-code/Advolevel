"""Imports every model module so ``Base.metadata`` is complete for Alembic and tests."""

from app.identity import models as identity_models

__all__ = ["identity_models"]
