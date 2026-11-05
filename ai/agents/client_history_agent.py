"""Client history agent for SmartErp."""

from __future__ import annotations

import logging
from typing import Optional

log = logging.getLogger(__name__)


class ClientHistoryAgent:
    """Agent pour l'historique des clients."""

    def __init__(self, gemini_service, client_service, facture_service, bl_service):
        self.gemini = gemini_service
        self.client_service = client_service
        self.facture_service = facture_service
        self.bl_service = bl_service

    def run(self, message: str, context=None) -> dict:
        """Traite une demande d'historique client."""
        msg_lower = message.lower()

        # Chercher un historique client
        if any(mot in msg_lower for mot in ["historique", "historique", "historique"]):
            return self._get_historique(message)

        # Voir les factures d'un client
        if any(mot in msg_lower for mot in ["mes factures", "mes commandes", "historique factures"]):
            return self._get_factures_client(message)

        # Voir les BL d'un client
        if any(mot in msg_lower for mot in ["mes bl", "mes bons de livraison"]):
            return self._get_bl_client(message)

        # Solde client
        if any(mot in msg_lower for mot in ["solde", "dette", "crédit", "crédit"]):
            return self._get_solde(message)

        return {"success": False, "message": "Que voulez-vous savoir sur ce client?"}

    def _identifier_client(self, message: str) -> Optional[dict]:
        """Identifie le client depuis le message."""
        clients = self.client_service.get_all_clients()
        message_lower = message.lower()

        for client in clients:
            if client.nom.lower() in message_lower or client.code.lower() in message_lower:
                return {
                    "code": client.code,
                    "nom": client.nom,
                    "telephone": client.telephone,
                    "ville": client.ville
                }

        # Si aucun client identifié, demander
        return None

    def _get_historique(self, message: str) -> dict:
        """Récupère l'historique complet d'un client."""
        client = self._identifier_client(message)
        if not client:
            return {"success": False, "message": "Quel client? Donnez-moi son nom ou code."}

        # Factures
        factures = self.facture_service.get_all_factures(client=client["nom"])
        # BL
        bl_list = self.bl_service.get_all_BL(client=client["nom"])

        total_factures = sum(f.total_ttc for f in factures)
        total_bl = sum(bl.total_ttc for bl in bl_list)

        msg = f"📋 *Historique de {client['nom']}*\n\n"
        msg += f"📄 Factures: {len(factures)} | Total: {total_factures:.2f} TND\n"
        msg += f"🚚 BL: {len(bl_list)} | Total: {total_bl:.2f} TND\n"
        msg += f"💰 Solde: {client.get('solde', 0):.2f} TND"

        return {"success": True, "message": msg}

    def _get_factures_client(self, message: str) -> dict:
        """Récupère les factures d'un client."""
        client = self._identifier_client(message)
        if not client:
            return {"success": False, "message": "Quel client?"}

        factures = self.facture_service.get_all_factures(client=client["nom"])
        if not factures:
            return {"success": True, "message": f"Aucune facture pour {client['nom']}"}

        msg = f"📄 *Factures de {client['nom']}*\n\n"
        for f in factures[-5:]:  # 5 dernières
            msg += f"- {f.reference} du {f.date} - {f.total_ttc:.2f} TND ({f.paiement})\n"

        return {"success": True, "message": msg}

    def _get_bl_client(self, message: str) -> dict:
        """Récupère les BL d'un client."""
        client = self._identifier_client(message)
        if not client:
            return {"success": False, "message": "Quel client?"}

        bl_list = self.bl_service.get_all_BL(client=client["nom"])
        if not bl_list:
            return {"success": True, "message": f"Aucun BL pour {client['nom']}"}

        msg = f"🚚 *BL de {client['nom']}*\n\n"
        for bl in bl_list[-5:]:
            msg += f"- {bl.reference} du {bl.date} - {bl.total_ttc:.2f} TND ({bl.paiement})\n"

        return {"success": True, "message": msg}

    def _get_solde(self, message: str) -> dict:
        """Récupère le solde d'un client."""
        client = self._identifier_client(message)
        if not client:
            return {"success": False, "message": "Quel client?"}

        client_obj = self.client_service.get_client_by_name(client["nom"])
        solde = client_obj.solde if client_obj else 0

        msg = f"💰 *Solde de {client['nom']}*\n\n"
        msg += f"Code: {client['code']}\n"
        msg += f"Solde actuel: {solde:.2f} TND"

        return {"success": True, "message": msg}
