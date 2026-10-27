from __future__ import annotations

import json
import logging

from ai.prompts.BL_prompt import BL_PROMPT
from models.CommandeFacture import CommandeFacture


log = logging.getLogger(__name__)


class BL_agent:

    def __init__(
        self,
        gemini_service,
        bl_service
    ):

        self.gemini = gemini_service
        self.facture_service = bl_service


    def run(self, action: str, **kwargs):
        if action == "creer_facture":
            return self.creer_facture(**kwargs)
        elif action == "extraire_commande":
            return self.extraire_commande(**kwargs)
        else:
            raise ValueError(f"Unknown action: {action}")

    def extraire_commande(
        self,
        message,
        catalogue,
        history
    ) -> CommandeFacture:

        produits = "\n".join(
            [
                f"- {nom} prix:{p.prix}"
                for nom,p in catalogue.items()
            ]
        )


        prompt = f"""
{BL_PROMPT}


Catalogue:

{produits}


Historique
de
la
conversation:
{history}
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

        return CommandeFacture.model_validate(
            data
        )


    def creer_facture(
        self,
        message,
        catalogue,
        history
    ):


        # 1. Gemini comprend la commande
        commande = self.extraire_commande(
            message,
            catalogue,history=history
        )


        log.info(
            "Commande extraite %s",
            commande
        )


        # 2. Service mÃ©tier
        ref_facture = (
            self.facture_service.creer_facture(
                commande
            )
        )


        return {
            "facture": ref_facture,
            "commande": commande
        }
