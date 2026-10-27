from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field, field_validator

from models.Article import Article


class Devise(str, Enum):
    TND = "TND"
    EUR = "EUR"



class CommandeFacture(BaseModel):
    """Résultat structuré de l'extraction Gemini d'une commande client."""

    client: str = Field(..., min_length=1)
    devise: Devise = Devise.TND
    articles: list[Article] = Field(..., min_length=1)

    @field_validator("client")
    @classmethod
    def client_non_vide(cls, v: str) -> str:
        v = v.strip()
        if not v or v.lower() == "client inconnu":
            raise ValueError("Le nom du client n'a pas pu être identifié dans la commande")
        return v
