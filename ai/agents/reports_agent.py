"""Reports and analytics agent for SmartErp."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Optional

log = logging.getLogger(__name__)


class ReportsAgent:
    """Agent pour les rapports et statistiques."""

    def __init__(self, gemini_service, facture_service, bl_service, client_service, stock_service):
        self.gemini = gemini_service
        self.facture_service = facture_service
        self.bl_service = bl_service
        self.client_service = client_service
        self.stock_service = stock_service

    def run(self, message: str, context=None) -> dict:
        """Traite une demande de rapport."""
        msg_lower = message.lower()

        # Rapport de ventes
        if any(mot in msg_lower for mot in ["rapport", "statistiques", "statistics", "ventes", "chiffre"]):
            return self._rapport_ventes()

        # Top produits
        if any(mot in msg_lower for mot in ["top produits", "meilleurs", "plus vendu"]):
            return self._top_produits()

        # Top clients
        if any(mot in msg_lower for mot in ["top clients", "meilleurs clients", "plus client"]):
            return self._top_clients()

        # Résumé du jour
        if any(mot in msg_lower for mot in ["aujourd'hui", "aujourdhui", "daily", "jour"]):
            return self._resume_journalier()

        return {"success": False, "message": "Quel rapport souhaitez-vous?"}

    def _rapport_ventes(self) -> dict:
        """Génère un rapport de ventes."""
        factures = self.facture_service.get_all_factures()
        bl_list = self.bl_service.get_all_BL()

        total_factures = sum(f.total_ttc for f in factures)
        total_bl = sum(bl.total_ttc for bl in bl_list)
        total_ht = sum(f.total_ht for f in factures)
        total_tva = sum(f.tva for f in factures)

        # Factures payées vs en attente
        payees = [f for f in factures if f.paiement.lower() == "payé"]
        en_attente = [f for f in factures if f.paiement.lower() == "non payé"]

        msg = "📊 *Rapport de Ventes*\n\n"
        msg += f"📄 *Factures*\n"
        msg += f"- Total: {len(factures)} factures\n"
        msg += f"- Montant total: {total_factures:.2f} TND\n"
        msg += f"- HT: {total_ht:.2f} TND\n"
        msg += f"- TVA (19%): {total_tva:.2f} TND\n"
        msg += f"- Payées: {len(payees)} | En attente: {len(en_attente)}\n\n"

        msg += f"🚚 *Bons de Livraison*\n"
        msg += f"- Total: {len(bl_list)} BL\n"
        msg += f"- Montant total: {total_bl:.2f} TND\n"

        return {"success": True, "message": msg}

    def _top_produits(self, n: int = 5) -> dict:
        """Retourne les top N produits vendus."""
        factures = self.facture_service.get_all_factures()

        produit_qte = {}
        for f in factures:
            for ligne in f.lignes:
                nom = ligne.description
                produit_qte[nom] = produit_qte.get(nom, 0) + ligne.quantite

        # Trier par quantité
        top = sorted(produit_qte.items(), key=lambda x: x[1], reverse=True)[:n]

        if not top:
            return {"success": True, "message": "Aucune vente enregistrée"}

        msg = "🏆 *Top Produits*\n\n"
        for i, (nom, qte) in enumerate(top, 1):
            msg += f"{i}. {nom}: {qte} unités\n"

        return {"success": True, "message": msg}

    def _top_clients(self, n: int = 5) -> dict:
        """Retourne les top N clients."""
        factures = self.facture_service.get_all_factures()

        client_total = {}
        for f in factures:
            client_total[f.client] = client_total.get(f.client, 0) + f.total_ttc

        top = sorted(client_total.items(), key=lambda x: x[1], reverse=True)[:n]

        if not top:
            return {"success": True, "message": "Aucun client trouvé"}

        msg = "💎 *Top Clients*\n\n"
        for i, (nom, total) in enumerate(top, 1):
            msg += f"{i}. {nom}: {total:.2f} TND\n"

        return {"success": True, "message": msg}

    def _resume_journalier(self) -> dict:
        """Résumé des activités d'aujourd'hui."""
        today = datetime.now().strftime("%d/%m/%Y")

        factures = self.facture_service.get_all_factures()
        bl_list = self.bl_service.get_all_BL()

        # Filtrer par date
        factures_today = [f for f in factures if str(f.date) == today]
        bl_today = [bl for bl in bl_list if str(bl.date) == today]

        total_auj = sum(f.total_ttc for f in factures_today)
        total_bl_auj = sum(bl.total_ttc for bl in bl_today)

        msg = f"📅 *Résumé du {today}*\n\n"
        msg += f"📄 Factures: {len(factures_today)} | {total_auj:.2f} TND\n"
        msg += f"🚚 BL: {len(bl_today)} | {total_bl_auj:.2f} TND\n"
        msg += f"💰 Total aujourd'hui: {total_auj + total_bl_auj:.2f} TND"

        return {"success": True, "message": msg}
