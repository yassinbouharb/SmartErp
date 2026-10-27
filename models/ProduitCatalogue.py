
from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field, field_validator


class ProduitCatalogue(BaseModel):
    """Une ligne du catalogue produits (TblProduits)."""

    description: str
    sku: str = ""
    prix: float = Field(..., ge=0)