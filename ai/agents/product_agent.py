from __future__ import annotations

import logging

from ai.prompts.product_prompt import PRODUCT_PROMPT


log = logging.getLogger(__name__)


class ProductAgent:

    def __init__(
        self,
        gemini_service,
        product_repository
    ):

        self.gemini = gemini_service

        self.product_repository = (
            product_repository
        )


    def run(
        self,
        message
    ):

        prompt = f"""
{PRODUCT_PROMPT}

Demande utilisateur :

{message}
"""

        response = self.gemini.chat(
            prompt
        )

        return {
            "message": response.text.strip()
        }


    def rechercher_produit(
        self,
        recherche: str
    ):

        produits = (
            self.product_repository
            .rechercher_produit(
                recherche
            )
        )

        if not produits:

            return {
                "message":
                f"Aucun produit trouvé pour : {recherche}"
            }


        return {
            "produits": [

                {
                    "description":
                    produit.description,

                    "SKU":
                    produit.sku,

                    "prix":
                    produit.prix
                }

                for produit in produits
            ]
        }


    def obtenir_prix(
        self,
        nom: str
    ):

        produit = (
            self.product_repository
            .obtenir_produit(
                nom
            )
        )

        if not produit:

            return {
                "message":
                f"Produit introuvable : {nom}"
            }


        return {
            "description":
            produit.description,

            "SKU":
            produit.sku,

            "prix":
            produit.prix,

            "devise":
            "TND"
        }
