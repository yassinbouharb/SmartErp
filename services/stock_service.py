"""Stock service for SmartErp."""

from __future__ import annotations

from typing import Optional

from repositories.stock_repository import StockRepository
from repositories.produit_repository import ProduitRepository


class StockService:
    """Service de gestion du stock."""

    def __init__(self, stock_repo: StockRepository, produit_repo: ProduitRepository):
        self.stock_repo = stock_repo
        self.produit_repo = produit_repo

    def get_all_stock(self) -> list[dict]:
        """Retourne tout le stock."""
        return self.stock_repo.get_all_stock()

    def add_stock(self, sku: str, quantite: float, motif: str = "") -> dict:
        """Ajoute du stock."""
        produit = self.produit_repo.obtenir_produit_by_sku(sku) if hasattr(self.produit_repo, 'obtenir_produit_by_sku') else None
        if not produit:
            # Chercher dans le catalogue
            catalogue = self.produit_repo.get_all_produits()
            for p in catalogue.values():
                if p.sku == sku:
                    produit = p
                    break

        if not produit:
            return {
                "success": False,
                "message": f"Produit avec SKU {sku} introuvable"
            }

        self.stock_repo.add_stock(sku, quantite, motif)
        self.stock_repo.save()

        return {
            "success": True,
            "message": f"+{quantite} unités ajoutées pour {produit.description}",
            "sku": sku,
            "nouvelle_quantite": self.stock_repo.get_all_stock().get(sku, {}).get("quantite", 0)
        }

    def remove_stock(self, sku: str, quantite: float, motif: str = "") -> dict:
        """Retire du stock."""
        stock = self.stock_repo.get_all_stock()
        current = stock.get(sku, {}).get("quantite", 0)

        if current < quantite:
            return {
                "success": False,
                "message": f"Stock insuffisant: {current} disponible, {quantite} demandé"
            }

        self.stock_repo.remove_stock(sku, quantite, motif)
        self.stock_repo.save()

        return {
            "success": True,
            "message": f"-{quantite} unités retirées pour SKU {sku}",
            "nouvelle_quantite": self.stock_repo.get_all_stock().get(sku, {}).get("quantite", 0)
        }

    def update_stock(self, sku: str, quantite: float, motif: str = "") -> dict:
        """Met à jour le stock."""
        self.stock_repo.update_stock(sku, quantite, motif)
        self.stock_repo.save()

        return {
            "success": True,
            "message": f"Stock mis à jour pour {sku}: {quantite} unités",
            "sku": sku,
            "quantite": quantite
        }

    def get_low_stock_alerts(self) -> list[dict]:
        """Retourne les alertes de stock faible."""
        return self.stock_repo.get_low_stock()

    def get_stock_for_product(self, nom_produit: str) -> Optional[dict]:
        """Retourne le stock d'un produit par son nom."""
        catalogue = self.produit_repo.get_all_produits()
        for key, produit in catalogue.items():
            if nom_produit.lower() in key.lower():
                stock = self.stock_repo.get_all_stock()
                return stock.get(produit.sku, {"sku": produit.sku, "produit": key, "quantite": 0})
        return None
