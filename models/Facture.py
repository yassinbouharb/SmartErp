from __future__ import annotations

from pydantic import BaseModel, Field
from datetime import date


class LigneFacture(BaseModel):
    """Une ligne (article) dans une facture."""
    ref: str
    date: date
    client: str
    sku: str
    description: str
    quantite: float
    prix_unitaire: float
    montant_total: float
    statut: str
    paiement: str


class Facture(BaseModel):
    """Représentation d'une facture avec ses lignes."""
    reference: str
    date: date
    client: str
    lignes: list[LigneFacture] = Field(default_factory=list)
    total_ht: float = 0.0
    tva: float = 0.0
    total_ttc: float = 0.0
    statut: str = "En attente"
    paiement: str = "Non payé"

    @property
    def solde_total(self) -> float:
        return sum(l.montant_total for l in self.lignes)
