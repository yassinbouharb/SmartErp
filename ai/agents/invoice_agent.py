from __future__ import annotations

import json
import logging

from ai.prompts.invoice_prompt import INVOICE_PROMPT
from ai.prompts.invoice_read_prompt import INVOICE_READ_PROMPT
from models.CommandeFacture import CommandeFacture
from models.Facture import Facture

log = logging.getLogger(__name__)


class InvoiceAgent:

    def __init__(
        self,
        gemini_service,
        facture_service
    ):
        self.gemini = gemini_service
        self.facture_service = facture_service

    # =========================================================
    # EXTRAIRE COMMANDE (création)
    # =========================================================

    def extraire_commande(
        self,
        message,
        catalogue,
    ) -> CommandeFacture:
        produits = "\n".join(
            [
                f"- {nom} prix:{p.prix}"
                for nom, p in catalogue.items()
            ]
        )

        prompt = f"""
{INVOICE_PROMPT}


Catalogue:

{produits}


Commande:

{message}
"""

        response = self.gemini.chat(
            [
                {
                    "role": "user",
                    "text": prompt
                }
            ]
        )

        data = json.loads(
            response.text
        )
        print(response.text)

        return CommandeFacture.model_validate(
            data
        )

    # =========================================================
    # EXTRAIRE DEMANDE FACTURE EXISTANTE
    # =========================================================

    def extraire_demande_facture(
        self,
        message,
        factures,
        history=None,
    ) -> dict:
        """Extrait l'action et les paramètres depuis le message de l'utilisateur."""
        factures_json = json.dumps(
            [f.dict() for f in factures],
            ensure_ascii=False,
            indent=2,
            default=str
        )

        historique = ""
        if history:
            historique = "\n".join(
                f"{h.get('role', '')}: {h.get('content', '')}"
                for h in history
                if isinstance(h, dict)
            )

        prompt = f"""
{INVOICE_READ_PROMPT}

=========================================================
FACTURES EXISTANTES
=========================================================

{factures_json}

=========================================================
HISTORIQUE
=========================================================

{historique}

=========================================================
DEMANDE UTILISATEUR
=========================================================

{message}
"""

        response = self.gemini.chat(
            [
                {
                    "role": "user",
                    "text": prompt
                }
            ]
        )

        raw_text = response.text.strip()
        if raw_text.startswith("```"):
            raw_text = raw_text.strip("`")
            if raw_text.startswith("json"):
                raw_text = raw_text[4:].strip()

        data = json.loads(raw_text)
        log.debug("Réponse Gemini InvoiceAgent : %s", raw_text)
        return data

    # =========================================================
    # CREER FACTURE
    # =========================================================

    def creer_facture(
        self,
        message,
        catalogue,
        client
    ):
        commande = self.extraire_commande(
            message,
            catalogue
        )

        log.info(
            "Commande extraite %s",
            commande
        )

        ref_facture = (
            self.facture_service.creer_facture(
                commande, client
            )
        )

        return {
            "facture": ref_facture,
            "commande": commande
        }

    # =========================================================
    # LIST FACTURES
    # =========================================================

    def list_factures(self, filters: dict = None) -> list[Facture]:
        """Liste les factures avec des filtres optionnels."""
        if filters is None:
            filters = {}
        return self.facture_service.get_all_factures(
            client=filters.get("client"),
            statut=filters.get("statut"),
            paiement=filters.get("paiement"),
        )

    # =========================================================
    # READ FACTURE
    # =========================================================

    def get_facture(self, reference: str) -> Facture | None:
        """Récupère une facture par sa référence."""
        return self.facture_service.get_facture(reference)

    # =========================================================
    # UPDATE FACTURE
    # =========================================================

    def update_facture(
        self,
        reference: str,
        statut: str = None,
        paiement: str = None
    ) -> dict:
        """Met à jour le statut ou le paiement d'une facture."""
        success = self.facture_service.update_facture(
            reference=reference,
            statut=statut,
            paiement=paiement,
        )
        if success:
            return {
                "success": True,
                "message": f"Facture {reference} mise à jour avec succès."
            }
        else:
            return {
                "success": False,
                "message": f"Facture {reference} introuvable."
            }

    # =========================================================
    # DELETE FACTURE
    # =========================================================

    def delete_facture(self, reference: str) -> dict:
        """Supprime une facture."""
        success = self.facture_service.supprimer_facture(reference)
        if success:
            return {
                "success": True,
                "message": f"Facture {reference} supprimée avec succès."
            }
        else:
            return {
                "success": False,
                "message": f"Facture {reference} introuvable."
            }

    # =========================================================
    # RUN
    # =========================================================

    def run(
        self,
        message,
        catalogue,
        client,
        history=None
    ):
        """Point d'entrée principal pour tous les types de demande."""

        # Si c'est une demande de création de facture
        if any(mot in message.lower() for mot in ["creer", "nouvelle facture", "generer", "editer"]):
            return self.creer_facture(message, catalogue, client)

        # Sinon, extraire l'action depuis le contexte
        factures = self.list_factures()
        demande = self.extraire_demande_facture(message, factures, history)

        action = demande.get("action")

        # =========================================================
        # LIST
        # =========================================================
        if action == "list":
            filters = demande.get("filters", {})
            resultats = self.list_factures(filters)
            return {
                "action": "list",
                "success": True,
                "factures": [f.dict() for f in resultats]
            }

        # =========================================================
        # READ
        # =========================================================
        elif action == "read":
            ref = demande.get("facture", {}).get("reference", "")
            if not ref:
                return {
                    "success": False,
                    "message": "Veuillez fournir une référence de facture."
                }
            facture = self.get_facture(ref)
            if facture:
                return {
                    "action": "read",
                    "success": True,
                    "facture": facture.dict()
                }
            else:
                return {
                    "success": False,
                    "message": f"Facture {ref} introuvable."
                }

        # =========================================================
        # UPDATE
        # =========================================================
        elif action == "update":
            facture_data = demande.get("facture", {})
            ref = facture_data.get("reference", "")
            statut = facture_data.get("statut")
            paiement = facture_data.get("paiement")

            if not ref:
                return {
                    "success": False,
                    "message": "Veuillez fournir une référence de facture."
                }
            return self.update_facture(ref, statut, paiement)

        # =========================================================
        # DELETE
        # =========================================================
        elif action == "delete":
            ref = demande.get("facture", {}).get("reference", "")
            if not ref:
                return {
                    "success": False,
                    "message": "Veuillez fournir une référence de facture."
                }
            return self.delete_facture(ref)

        # =========================================================
        # FALLBACK
        # =========================================================
        else:
            return {
                "success": False,
                "message": "Je n'ai pas compris l'action demandée sur la facture."
            }
