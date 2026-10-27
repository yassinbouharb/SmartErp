"""
GeminiService
=============
Isole toute la logique d'appel à l'API Gemini : construction du prompt,
appel réseau, nettoyage de la réponse, validation via Pydantic.

Avant : cette logique était mélangée avec l'écriture Excel dans
facture_bot.py. Maintenant : ce module ne connaît RIEN d'Excel, et
facture_bot.py (ou le futur SalesService) ne connaît RIEN de Gemini.
Ça permet de tester chaque brique séparément (ex: mocker GeminiService
dans les tests sans jamais toucher l'ERP réel).
"""

from __future__ import annotations

import json
import logging
import re

from google import genai
from pydantic import ValidationError

from models.CommandeFacture import CommandeFacture
from models.ProduitCatalogue import ProduitCatalogue

log = logging.getLogger(__name__)


class GeminiExtractionError(Exception):
    """Levée quand Gemini ne renvoie pas un JSON exploitable ou invalide."""


SYSTEM_PROMPT = """Tu es un assistant qui extrait les informations de commande d'un
import/revendeur pour générer une facture. Analyse le texte en langage naturel
(français, parfois avec des tournures tunisiennes) et retourne UNIQUEMENT le JSON
demandé, sans texte autour, sans balises markdown ```.
Format attendu :
{
  "client": "...",
  "devise": "TND" ou "EUR",
  "articles": [
    {"nom_produit": "...", "quantite": 0, "prix_unitaire": 0 ou null}
  ]
}
Pour chaque produit, cherche la correspondance la plus proche dans la liste des
produits fournie (la commande peut contenir des fautes de frappe). Le nom_produit
retourné DOIT être recopié EXACTEMENT comme il apparaît dans la liste des produits
fournie, pas comme il apparaît dans la commande. Si le prix unitaire n'est pas donné
dans la phrase, mets prix_unitaire à null (il sera complété depuis le catalogue).
Si la devise n'est pas précisée, déduis-la des symboles utilisés (TND, DT, EUR, €),
sinon laisse vide. Si un produit de la commande ne correspond à rien dans la liste,
mets son nom_produit tel quel et prix_unitaire à null."""


class GeminiService:
    """Enrobe le client Gemini pour l'extraction de commandes en JSON structuré."""

    def __init__(self, model: str = "gemini-3.1-flash-lite") -> None:
        self._model = model
        # Le client lit GEMINI_API_KEY dans l'environnement (chargé via load_dotenv
        # côté appelant, typiquement dans le point d'entrée main.py).
        self._client = genai.Client()

    def extraire_commande(
            self, texte_commande: str, catalogue: dict[str, ProduitCatalogue]
    ) -> CommandeFacture:
        """Envoie la commande en langage naturel à Gemini et retourne un
        CommandeFacture validé.

        Lève GeminiExtractionError si l'appel échoue, si le JSON est
        malformé, ou si le contenu ne respecte pas le schéma attendu.
        """
        prompt = self._construire_prompt(texte_commande, catalogue)

        try:
            interaction = self._client.interactions.create(
                model=self._model,
                input=prompt,
                response_format={"type": "text"},

            )
        except Exception as exc:  # erreurs réseau / auth / quota API
            log.error("Appel Gemini échoué : %s", exc)
            raise GeminiExtractionError(f"Appel à l'API Gemini échoué : {exc}") from exc

        texte_nettoye = self._nettoyer_reponse(interaction.output_text)
        log.debug("Réponse Gemini nettoyée : %s", texte_nettoye)

        try:
            data = json.loads(texte_nettoye)
        except json.JSONDecodeError as exc:
            log.error("JSON invalide reçu de Gemini : %s", interaction.output_text)
            raise GeminiExtractionError("La réponse de Gemini n'est pas un JSON valide") from exc

        try:
            return CommandeFacture.model_validate(data)
        except ValidationError as exc:
            log.error("Commande invalide extraite par Gemini : %s", exc)
            raise GeminiExtractionError(f"Commande extraite invalide : {exc}") from exc

    @staticmethod
    def _construire_prompt(texte_commande: str, catalogue: dict[str, ProduitCatalogue]) -> str:
        liste_produits_txt = "\n".join(
            f"- {nom} (SKU: {p.sku}, prix: {p.prix} TND)" for nom, p in catalogue.items()
        )
        return (
            f"{SYSTEM_PROMPT}\n\n"
            f"Liste des produits disponibles :\n{liste_produits_txt}\n\n"
            f'Commande à analyser :\n"""{texte_commande}"""'
        )

    @staticmethod
    def _nettoyer_reponse(texte_brut: str) -> str:
        # Gemini renvoie parfois du JSON entouré de ```json ... ``` malgré la consigne
        return re.sub(r"^```(?:json)?|```$", "", texte_brut.strip(), flags=re.MULTILINE).strip()