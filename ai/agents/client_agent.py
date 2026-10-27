from __future__ import annotations

import json
import logging
from typing import Any

from models.client import Client
from ai.prompts.client_prompt import CLIENT_PROMPT

log = logging.getLogger(__name__)


class ClientAgent:

    def __init__(
        self,
        gemini_service,
        client_service
    ):
        self.gemini = gemini_service
        self.client_service = client_service

    # =========================================================
    # EXTRAIRE DEMANDE
    # =========================================================

    def extraire_demande(
        self,
        message: str,
        history: list[dict[str, Any]] | None = None
    ) -> dict[str, Any]:

        historique = ""

        if history:
            historique = "\n".join(
                f"{h.get('role', '')}: {h.get('content', '')}"
                for h in history
                if isinstance(h, dict)
            )

        # -----------------------------------------------------
        # Récupérer tous les clients
        # -----------------------------------------------------

        clients = self.client_service.get_all_clients()

        clients_data = []

        for client in clients:

            clients_data.append({
                "code": client.code,
                "nom": client.nom,
                "contact": client.contact,
                "telephone": client.telephone,
                "ville": client.ville,
                "solde": client.solde,
                "matricule_fiscale": client.matricule_fiscale
            })

        clients_json = json.dumps(
            clients_data,
            ensure_ascii=False,
            indent=2,
            default=str
        )

        # -----------------------------------------------------
        # Prompt
        # -----------------------------------------------------

        prompt = f"""
{CLIENT_PROMPT}

=========================================================
CLIENTS EXISTANTS
=========================================================

Voici les clients actuellement enregistrés.

Utilise UNIQUEMENT ces données pour identifier
un client existant.

{clients_json}

=========================================================
HISTORIQUE
=========================================================

{historique}

=========================================================
DEMANDE UTILISATEUR
=========================================================

{message}

=========================================================
INSTRUCTION FINALE
=========================================================

Si l'utilisateur ne donne pas le code mais donne :

- nom
- téléphone
- contact
- ville
- matricule fiscale

cherche le client correspondant dans la liste.

Si un seul client correspond :
→ utilise son vrai code.

Si plusieurs clients correspondent :
→ ne choisis pas arbitrairement.

Si aucun client ne correspond :
→ n'invente rien.

Réponds UNIQUEMENT avec un JSON valide.
"""

        try:

            response = self.gemini.chat(
                [
                    {
                        "role": "user",
                        "text": prompt
                    }
                ]
            )

            raw_text = response.text.strip()

            log.debug(
                "Réponse Gemini ClientAgent : %s",
                raw_text
            )

            data = json.loads(raw_text)

            if not isinstance(data, dict):
                raise ValueError(
                    "La réponse Gemini doit être un objet JSON."
                )

            return data

        except json.JSONDecodeError as e:

            log.error(
                "Réponse Gemini invalide : %s",
                getattr(response, "text", "")
            )

            raise ValueError(
                "Le modèle a retourné une réponse JSON invalide."
            ) from e

    # =========================================================
    # RUN
    # =========================================================

    def run(
        self,
        message: str,
        history: list[dict[str, Any]] | None = None
    ) -> dict[str, Any]:

        data = self.extraire_demande(
            message,
            history
        )

        action = data.get("action")
        client_data = data.get("client") or {}

        log.info(
            "Client action : %s",
            action
        )

        # =====================================================
        # CREATE
        # =====================================================

        if action == "create":

            try:

                client = Client.model_validate(
                    client_data
                )

                result = self.client_service.ajouter_client(
                    client
                )

                if not result:

                    return {
                        "action": "create",
                        "success": False,
                        "message": (
                            "Un client avec ce code existe déjà."
                        )
                    }

                return {
                    "action": "create",
                    "success": True,
                    "message": "Client créé avec succès.",
                    "client": client
                }

            except Exception as e:

                log.exception(
                    "Erreur lors de la création du client"
                )

                return {
                    "action": "create",
                    "success": False,
                    "message": str(e)
                }

        # =====================================================
        # LIST
        # =====================================================

        if action == "list":

            try:

                clients = self.client_service.get_all_clients()

                return {
                    "action": "list",
                    "success": True,
                    "message": "Liste des clients récupérée.",
                    "clients": clients
                }

            except Exception as e:

                log.exception(
                    "Erreur récupération clients"
                )

                return {
                    "action": "list",
                    "success": False,
                    "message": str(e)
                }

        # =====================================================
        # SEARCH
        # =====================================================

        if action == "search":

            try:

                code = client_data.get("code")

                # Si un code a été identifié
                if code:

                    client = self.client_service.get_client(
                        code
                    )

                    if client:

                        return {
                            "action": "search",
                            "success": True,
                            "message": "Client trouvé.",
                            "clients": [client]
                        }

                result = self.client_service.search_clients(
                    code=client_data.get("code"),
                    nom=client_data.get("nom"),
                    ville=client_data.get("ville"),
                    telephone=client_data.get("telephone"),
                    contact=client_data.get("contact"),
                    matricule_fiscale=client_data.get(
                        "matricule_fiscale"
                    )
                )

                return {
                    "action": "search",
                    "success": True,
                    "message": "Recherche client effectuée.",
                    "clients": result
                }

            except Exception as e:

                log.exception(
                    "Erreur recherche client"
                )

                return {
                    "action": "search",
                    "success": False,
                    "message": str(e)
                }

        # =====================================================
        # UPDATE
        # =====================================================

        if action == "update":

            code = client_data.get("code")

            if not code:

                return {
                    "action": "update",
                    "success": False,
                    "message": (
                        "Impossible d'identifier le client."
                    )
                }

            try:

                client = self.client_service.get_client(
                    code
                )

                if not client:

                    return {
                        "action": "update",
                        "success": False,
                        "message": (
                            f"Client {code} introuvable."
                        )
                    }

                champs_modifiables = [
                    "nom",
                    "contact",
                    "telephone",
                    "ville",
                    "solde",
                    "matricule_fiscale"
                ]

                for field in champs_modifiables:

                    if field in client_data:

                        setattr(
                            client,
                            field,
                            client_data[field]
                        )

                result = self.client_service.update_client(
                    client
                )

                return {
                    "action": "update",
                    "success": bool(result),
                    "message": (
                        "Client modifié avec succès."
                        if result
                        else "Échec de la modification du client."
                    ),
                    "client": client
                }

            except Exception as e:

                log.exception(
                    "Erreur modification client %s",
                    code
                )

                return {
                    "action": "update",
                    "success": False,
                    "message": str(e)
                }

        # =====================================================
        # DELETE
        # =====================================================

        if action == "delete":

            code = client_data.get("code")

            if not code:

                return {
                    "action": "delete",
                    "success": False,
                    "message": (
                        "Impossible d'identifier le client."
                    )
                }

            try:

                result = self.client_service.delete_client(
                    code
                )

                return {
                    "action": "delete",
                    "success": bool(result),
                    "message": (
                        "Client supprimé avec succès."
                        if result
                        else "Client introuvable."
                    ),
                    "result": result
                }

            except Exception as e:

                log.exception(
                    "Erreur suppression client %s",
                    code
                )

                return {
                    "action": "delete",
                    "success": False,
                    "message": str(e)
                }

        # =====================================================
        # BALANCE
        # =====================================================

        if action == "balance":

            code = client_data.get("code")

            if not code:

                return {
                    "action": "balance",
                    "success": False,
                    "message": (
                        "Impossible d'identifier le client."
                    )
                }

            client = self.client_service.get_client(
                code
            )

            if not client:

                return {
                    "action": "balance",
                    "success": False,
                    "message": (
                        f"Client {code} introuvable."
                    )
                }

            return {
                "action": "balance",
                "success": True,
                "message": (
                    f"Le solde de {client.nom} "
                    f"est de {client.solde}."
                ),
                "client": client
            }

        # =====================================================
        # UNKNOWN
        # =====================================================

        log.warning(
            "Action client inconnue : %s",
            action
        )

        return {
            "action": "unknown",
            "success": False,
            "message": (
                "Je n'ai pas compris la demande "
                "concernant le client."
            )
        }

    import json
    import logging

    log = logging.getLogger(__name__)

    def getclient(self, cmd):

        clients = self.client_service.get_all_clients()

        clients_data = []

        for client in clients:
            clients_data.append({
                "code": client.code,
                "nom": client.nom,
                "contact": client.contact,
                "telephone": client.telephone,
                "ville": client.ville,
                "solde": float(client.solde or 0),
                "matricule_fiscale": client.matricule_fiscale
            })

        clients_json = json.dumps(
            clients_data,
            ensure_ascii=False,
            indent=2,
            default=str
        )

        prompt = f"""
    Tu es un agent chargé d'identifier un client à partir d'une facture.

    =========================================================
    CLIENTS EXISTANTS
    =========================================================

    Voici la liste des clients actuellement enregistrés :

    {clients_json}

    =========================================================
    FACTURE / DEMANDE UTILISATEUR
    =========================================================

    {cmd}

    =========================================================
    OBJECTIF
    =========================================================

    Extrais les informations du client présentes dans la facture.

    Informations à rechercher :

    - nom
    - contact
    - telephone
    - ville
    - matricule_fiscale

    Compare ensuite les informations extraites avec les clients existants.

    =========================================================
    RÈGLES D'IDENTIFICATION
    =========================================================

    1. Si un client existant correspond clairement aux informations
       de la facture :

       retourne son vrai code et ses informations enregistrées.

    2. Si le code client est présent dans la facture :
       utilise ce code pour identifier le client.

    3. Si le code n'est pas présent, utilise les autres informations
       disponibles pour rechercher le client.

    4. Si un seul client correspond clairement :
       considère ce client comme identifié.

    5. Si plusieurs clients peuvent correspondre :
       ne choisis pas arbitrairement.
       Retourne "client_existant": false.

    6. Si aucun client ne correspond :
       considère qu'il s'agit d'un nouveau client.

    7. N'invente jamais une information qui n'est pas présente
       dans la facture ou dans la liste des clients existants.

    8. Pour une information absente, utilise une chaîne vide "".

    9. Le solde d'un nouveau client doit être 0.0.

    =========================================================
    FORMAT DE RÉPONSE
    =========================================================

    Réponds UNIQUEMENT avec un JSON valide.

    Si le client existe :

    {{
        "client_existant": true,
        "client": {{
            "code": "CODE_CLIENT",
            "nom": "ABC",
            "contact": "",
            "telephone": "",
            "ville": "Tunis",
            "solde": 0.0,
            "matricule_fiscale": ""
        }}
    }}

    Si le client n'existe pas :

    {{
        "client_existant": false,
        "client": {{
            "code": "",
            "nom": "ABC",
            "contact": "",
            "telephone": "",
            "ville": "Tunis",
            "solde": 0.0,
            "matricule_fiscale": ""
        }}
    }}

    Si plusieurs clients correspondent :

    {{
        "client_existant": false,
        "client": {{
            "code": "",
            "nom": "",
            "contact": "",
            "telephone": "",
            "ville": "",
            "solde": 0.0,
            "matricule_fiscale": ""
        }}
    }}

    =========================================================
    IMPORTANT
    =========================================================

    Retourne uniquement le JSON.
    Aucun texte avant ou après le JSON.
    """

        response = None

        try:

            response = self.gemini.chat(
                [
                    {
                        "role": "user",
                        "text": prompt
                    }
                ]
            )

            raw_text = response.text.strip()

            log.debug(
                "Réponse Gemini ClientAgent : %s",
                raw_text
            )

            # Nettoyage éventuel des ```json ... ```
            if raw_text.startswith("```"):
                raw_text = raw_text.strip("`")

                if raw_text.startswith("json"):
                    raw_text = raw_text[4:].strip()

            data = json.loads(raw_text)
            print(data)
            if not isinstance(data, dict):
                raise ValueError(
                    "La réponse Gemini doit être un objet JSON."
                )

            if "client_existant" not in data:
                raise ValueError(
                    "Le champ 'client_existant' est obligatoire."
                )

            if "client" not in data:
                raise ValueError(
                    "Le champ 'client' est obligatoire."
                )

            if not isinstance(data["client"], dict):
                raise ValueError(
                    "Le champ 'client' doit être un objet JSON."
                )

            return data

        except json.JSONDecodeError as e:

            log.error(
                "Réponse Gemini invalide : %s",
                getattr(response, "text", "")
            )

            raise ValueError(
                "Gemini a retourné une réponse JSON invalide."
            ) from e