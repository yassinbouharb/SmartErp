from __future__ import annotations

import json
import logging

from ai.prompts.BL_prompt import BL_PROMPT
from ai.prompts.bl_read_prompt import BL_READ_PROMPT
from models.CommandeBL import CommandeBL
from models.BonLivraison import BonLivraison

log = logging.getLogger(__name__)


class BL_agent:

    def __init__(
        self,
        gemini_service,
        bl_service
    ):
        self.gemini = gemini_service
        self.bl_service = bl_service

    # =========================================================
    # CREATE - EXTRAIRE COMMANDE
    # =========================================================

    def extraire_commande(
        self,
        message,
        catalogue,
        history=None
    ) -> CommandeBL:
        produits = "\n".join(
            [
                f"- {nom} prix:{p.prix}"
                for nom, p in catalogue.items()
            ]
        )

        historique = ""
        if history:
            historique = "\n".join(
                f"{h.get('role', '')}: {h.get('content', '')}"
                for h in history
                if isinstance(h, dict)
            )

        prompt = f"""
{BL_PROMPT}


Catalogue:

{produits}


Historique de la conversation:
{historique}
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

        return CommandeBL.model_validate(
            data
        )

    # =========================================================
    # CREATE - CREER BL
    # =========================================================

    def creer_BL(
        self,
        message,
        catalogue,
        history=None
    ):
        commande = self.extraire_commande(
            message,
            catalogue,
            history=history
        )

        log.info(
            "Commande BL extraite %s",
            commande
        )

        ref_BL = self.bl_service.creer_BL(
            commande
        )

        return {
            "BL": ref_BL,
            "commande": commande
        }

    # =========================================================
    # READ - EXTRAIRE DEMANDE
    # =========================================================

    def extraire_demande_BL(
        self,
        message,
        bl_list,
        history=None,
    ) -> dict:
        """Extrait l'action et les paramètres depuis le message de l'utilisateur."""
        bl_json = json.dumps(
            [b.dict() for b in bl_list],
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
{BL_READ_PROMPT}

=========================================================
BONS DE LIVRAISON EXISTANTS
=========================================================

{bl_json}

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
        log.debug("Réponse Gemini BL_agent : %s", raw_text)
        return data

    # =========================================================
    # LIST
    # =========================================================

    def list_BL(self, filters: dict = None) -> list[BonLivraison]:
        """Liste les BL avec des filtres optionnels."""
        if filters is None:
            filters = {}
        return self.bl_service.get_all_BL(
            client=filters.get("client"),
            statut=filters.get("statut"),
            paiement=filters.get("paiement"),
        )

    # =========================================================
    # READ
    # =========================================================

    def get_BL(self, reference: str) -> BonLivraison | None:
        """Récupère un BL par sa référence."""
        return self.bl_service.get_BL(reference)

    # =========================================================
    # UPDATE
    # =========================================================

    def update_BL(
        self,
        reference: str,
        statut: str = None,
        paiement: str = None
    ) -> dict:
        """Met à jour le statut ou le paiement d'un BL."""
        success = self.bl_service.update_BL(
            reference=reference,
            statut=statut,
            paiement=paiement,
        )
        if success:
            return {
                "success": True,
                "message": f"BL {reference} mis à jour avec succès."
            }
        else:
            return {
                "success": False,
                "message": f"BL {reference} introuvable."
            }

    # =========================================================
    # DELETE
    # =========================================================

    def delete_BL(self, reference: str) -> dict:
        """Supprime un BL."""
        success = self.bl_service.supprimer_BL(reference)
        if success:
            return {
                "success": True,
                "message": f"BL {reference} supprimé avec succès."
            }
        else:
            return {
                "success": False,
                "message": f"BL {reference} introuvable."
            }

    # =========================================================
    # RUN - POINT D'ENTRÉE PRINCIPAL
    # =========================================================

    def run(
        self,
        message,
        catalogue,
        history=None
    ):
        """Point d'entrée principal pour tous les types de demande BL."""

        # Si c'est une demande de création de BL
        if any(mot in message.lower() for mot in ["creer", "nouveau bl", "nouvel bl", "générer", "éditer"]):
            return self.creer_BL(message, catalogue, history)

        # Sinon, extraire l'action depuis le contexte
        bl_list = self.list_BL()
        demande = self.extraire_demande_BL(message, bl_list, history)

        action = demande.get("action")

        # =========================================================
        # LIST
        # =========================================================
        if action == "list":
            filters = demande.get("filters", {})
            resultats = self.list_BL(filters)
            return {
                "action": "list",
                "success": True,
                "BL": [b.dict() for b in resultats]
            }

        # =========================================================
        # READ
        # =========================================================
        elif action == "read":
            ref = demande.get("bl", {}).get("reference", "")
            if not ref:
                return {
                    "success": False,
                    "message": "Veuillez fournir une référence de BL."
                }
            bl = self.get_BL(ref)
            if bl:
                return {
                    "action": "read",
                    "success": True,
                    "BL": bl.dict()
                }
            else:
                return {
                    "success": False,
                    "message": f"BL {ref} introuvable."
                }

        # =========================================================
        # UPDATE
        # =========================================================
        elif action == "update":
            bl_data = demande.get("bl", {})
            ref = bl_data.get("reference", "")
            statut = bl_data.get("statut")
            paiement = bl_data.get("paiement")

            if not ref:
                return {
                    "success": False,
                    "message": "Veuillez fournir une référence de BL."
                }
            return self.update_BL(ref, statut, paiement)

        # =========================================================
        # DELETE
        # =========================================================
        elif action == "delete":
            ref = demande.get("bl", {}).get("reference", "")
            if not ref:
                return {
                    "success": False,
                    "message": "Veuillez fournir une référence de BL."
                }
            return self.delete_BL(ref)

        # =========================================================
        # FALLBACK
        # =========================================================
        else:
            return {
                "success": False,
                "message": "Je n'ai pas compris l'action demandée sur le BL."
            }
