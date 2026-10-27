from __future__ import annotations


from pydantic import BaseModel, Field, field_validator


class Article(BaseModel):
    """Un article détecté dans la commande en langage naturel."""

    nom_produit: str = Field(..., min_length=1, description="Nom exact tel qu'il apparaît dans le catalogue")
    quantite: float = Field(..., gt=0, description="Quantité commandée (doit être > 0)")
    prix_unitaire: float | None = Field(
        default=None,
        ge=0,
        description="Prix unitaire donné dans la commande, None si absent (complété depuis le catalogue)",
    )

    @field_validator("nom_produit")
    @classmethod
    def nom_produit_non_vide(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("nom_produit ne peut pas être vide")
        return v
