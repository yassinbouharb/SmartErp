"""Stock agent for SmartErp Telegram bot."""

from __future__ import annotations

import logging
from ai.prompts.product_prompt import PRODUCT_PROMPT

log = logging.getLogger(__name__)


class StockAgent:
    """Agent de gestion du stock."""

    def __init__(self, gemini_service, stock_service):
        self.gemini = gemini_service
        self.stock_service = stock_service

    def run(self, message: str, context=None) -> dict:
        """Traite une demande concernant le stock."""
        msg_lower = message.lower()

        # Ajouter du stock
        if any(mot in msg_lower for mot in ["ajouter", "reception", "entree", "approvisionnement"]):
            return self._ajouter_stock(message)

        # Retirer du stock
        if any(mot in msg_lower for mot in ["retirer", "sortie", "vente", "consommer"]):
            return self._retirer_stock(message)

        # Vérifier le stock
        if any(mot in msg_lower for mot in ["stock", "quantite", "quantité", "disponible"]):
            return self._verifier_stock(message)

        # Alertes stock faible
        if any(mot in msg_lower for mot in ["alerte", "faible", "seuil", "reapprovisionnement"]):
            return self._alertes_stock_faible()

        # Lister tout le stock
        if any(mot in msg_lower for mot in ["liste stock", "tout le stock", "inventaire"]):
            return self._liste_stock()

        return {
            "message": "Je n'ai pas compris votre demande concernant le stock."
        }

    def _ajouter_stock(self, message: str) -> dict:
        """Ajoute du stock."""
        from ai.gemini_service import GeminiService
        # Utiliser Gemini pour extraire les informations
        prompt = f"""
Tu es un assistant qui extrait les informations de réception de stock.
Retourne UNIQUEMENT le JSON suivant:

{{
  "sku": "SKU du produit",
  "quantite": nombre,
  "motif": "raison de l'ajout"
}}

Message: {message}
"""
        response = self.gemini.chat(prompt)
        try:
            import json
            data = json.loads(response.text.strip())
            return self.stock_service.add_stock(
                sku=data.get("sku", ""),
                quantite=float(data.get("quantite", 0)),
                motif=data.get("motif", "Réception")
            )
        except:
            return {"success": False, "message": "Erreur lors de l'extraction des informations"}

    def _retirer_stock(self, message: str) -> dict:
        """Retire du stock."""
        from ai.gemini_service import GeminiService
        prompt = f"""
Tu es un assistant qui extrait les informations de sortie de stock.
Retourne UNIQUEMENT le JSON suivant:

{{
  "sku": "SKU du produit",
  "quantite": nombre,
  "motif": "raison de la sortie"
}}

Message: {message}
"""
        response = self.gemini.chat(prompt)
        try:
            import json
            data = json.loads(response.text.strip())
            return self.stock_service.remove_stock(
                sku=data.get("sku", ""),
                quantite=float(data.get("quantite", 0)),
                motif=data.get("motif", "Sortie")
            )
        except:
            return {"success": False, "message": "Erreur lors de l'extraction des informations"}

    def _verifier_stock(self, message: str) -> dict:
        """Vérifie le stock d'un produit."""
        produit = self.stock_service.get_stock_for_product(message)
        if produit:
            return {
                "success": True,
                "message": f"📦 *{produit['produit']}*\nSKU: {produit['sku']}\nStock: {produit['quantite']} unités"
            }
        return {"success": False, "message": "Produit introuvable"}

    def _alertes_stock_faible(self) -> dict:
        """Retourne les alertes de stock faible."""
        alerts = self.stock_service.get_low_stock_alerts()
        if not alerts:
            return {"success": True, "message": "✅ Aucun alerte de stock faible"}

        msg = "⚠️ *Alertes stock faible:*\n\n"
        for alert in alerts:
            msg += f"• {alert['produit']} (SKU: {alert['sku']}): {alert['quantite']} unités\n"

        return {"success": True, "message": msg}

    def _liste_stock(self) -> dict:
        """Liste tout le stock."""
        stock = self.stock_service.get_all_stock()
        if not stock:
            return {"success": True, "message": "Aucun produit en stock"}

        msg = "📦 *Stock complet:*\n\n"
        for sku, data in list(stock.items())[:20]:
            msg += f"• {data['produit']}: {data['quantite']} unités (SKU: {sku})\n"

        if len(stock) > 20:
            msg += f"\n... et {len(stock) - 20} autres produits"

        return {"success": True, "message": msg}
