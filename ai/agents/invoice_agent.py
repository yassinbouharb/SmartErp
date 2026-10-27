from __future__ import annotations

import json
import logging

from ai.prompts.invoice_prompt import INVOICE_PROMPT
from models.CommandeFacture import CommandeFacture


log = logging.getLogger(__name__)


class InvoiceAgent:

    def __init__(
        self,
        gemini_service,
        facture_service
    ):

        self.gemini = gemini_service
        self.facture_service = facture_service


    def extraire_commande(
        self,
        message,
        catalogue,

    ) -> CommandeFacture:

        print("test",catalogue)
        produits = "\n".join(
            [
                f"- {nom} prix:{p.prix}"
                for nom,p in catalogue.items()
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
                    "role":"user",
                    "text":prompt
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


    def creer_facture(
        self,
        message,
        catalogue,client
    ):


        # 1. Gemini comprend la commande
        commande = self.extraire_commande(
            message,
            catalogue
        )


        log.info(
            "Commande extraite %s",
            commande
        )


        # 2. Service métier
        ref_facture = (
            self.facture_service.creer_facture(
                commande,client
            )
        )


        return {
            "facture": ref_facture,
            "commande": commande
        }