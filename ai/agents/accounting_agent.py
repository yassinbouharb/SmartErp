"""Accounting (Comptabilité) agent for SmartErp."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Optional

log = logging.getLogger(__name__)


class AccountingAgent:
    """Agent pour la comptabilité."""

    def __init__(self, gemini_service, facture_service, client_service, stock_service):
        self.gemini = gemini_service
        self.facture_service = facture_service
        self.client_service = client_service
        self.stock_service = stock_service

    def run(self, message: str, context=None) -> dict:
        """Traite une demande comptable."""
        msg_lower = message.lower()

        # Bilan simplifié
        if any(mot in msg_lower for mot in ["bilan", "balance", "situation"]):
            return self._bilan()

        # Compte client
        if any(mot in msg_lower for mot in ["compte client", "client compte", "dettes"]):
            return self._compte_clients()

        # Résultat
        if any(mot in msg_lower for mot in ["résultat", "resultat", "bénéfice", "benefice"]):
            return self._resultat()

        # Grand livre simplifié
        if any(mot in msg_lower for mot in ["grand livre", "journalier", "écritures"]):
            return self._grand_livre()

        return {"success": False, "message": "Que souhaitez-vous savoir? (bilan, compte client, résultat)"}

    def _bilan(self) -> dict:
        """Bilan simplifié."""
        factures = self.facture_service.get_all_factures()
        clients = self.client_service.get_all_clients()

        # Chiffre d'affaires HT
        ca_ht = sum(f.total_ht for f in factures)
        # TVA collectée
        tva = sum(f.tva for f in factures)
        # Total TTC
        ca_ttc = sum(f.total_ttc for f in factures)

        # Créances clients (soldes)
        creances = sum(c.solde for c in clients)

        msg = "📊 *Bilan Simplifié*\n\n"
        msg += f"📈 *Chiffre d'Affaires*\n"
        msg += f"- HT: {ca_ht:.2f} TND\n"
        msg += f"- TVA (19%): {tva:.2f} TND\n"
        msg += f"- TTC: {ca_ttc:.2f} TND\n\n"

        msg += f"👥 *Créances Clients*\n"
        msg += f"- Total dû: {creances:.2f} TND\n"
        msg += f"- Nombre de clients: {len(clients)}\n\n"

        msg += f"💰 *Total Recettes Attendes*: {creances:.2f} TND"

        return {"success": True, "message": msg}

    def _compte_clients(self) -> dict:
        """Compte détaillé des clients."""
        clients = self.client_service.get_all_clients()

        if not clients:
            return {"success": True, "message": "Aucun client enregistré"}

        msg = "👥 *Comptes Clients*\n\n"
        total_du = 0

        for c in clients:
            if c.solde != 0:
                msg += f"• {c.nom} ({c.code}): {c.solde:.2f} TND\n"
                total_du += c.solde

        msg += f"\n*Total dû*: {total_du:.2f} TND"

        return {"success": True, "message": msg}

    def _resultat(self) -> dict:
        """Résultat simplifié."""
        factures = self.facture_service.get_all_factures()
        ca_ht = sum(f.total_ht for f in factures)
        ca_ttc = sum(f.total_ttc for f in factures)
        tva = sum(f.tva for f in factures)

        # Estimation des coûts (hypothèse: 60% du CA HT)
        cout_estime = ca_ht * 0.6
        benefice_estime = ca_ht - cout_estime

        msg = "📊 *Résultat Estimé*\n\n"
        msg += f"📈 Chiffre d'Affaires HT: {ca_ht:.2f} TND\n"
        msg += f"📉 Coût estimé (60%): {cout_estime:.2f} TND\n"
        msg += f"✅ Bénéfice estimé: {benefice_estime:.2f} TND\n\n"
        msg += "⚠️ *Note*: Ceci est une estimation. Les coûts réels peuvent varier."

        return {"success": True, "message": msg}

    def _grand_livre(self) -> dict:
        """Grand livre simplifié."""
        factures = self.facture_service.get_all_factures()
        clients = self.client_service.get_all_clients()

        msg = "📖 *Grand Livre Simplifié*\n\n"

        # Écritures clients
        msg += "*Comptes Clients*\n"
        for c in clients:
            if c.solde != 0:
                msg += f"  - {c.nom}: Débit {c.solde:.2f} TND\n"

        msg += "\n*Comptes Clients (Crédit)*\n"
        # Clients avec solde négatif (crédits)
        credits = [c for c in clients if c.solde < 0]
        for c in credits:
            msg += f"  - {c.nom}: Crédit {abs(c.solde):.2f} TND\n"

        return {"success": True, "message": msg}
