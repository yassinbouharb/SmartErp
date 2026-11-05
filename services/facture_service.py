from __future__ import annotations

from models.Facture import Facture
from repositories.produit_repository import ProduitRepository
from repositories.facture_repository import FactureRepository
from services.client_service import ClientService


class FactureService:

    def __init__(
        self,
        produit_repository: ProduitRepository,
        facture_repository: FactureRepository,
        client_service: ClientService,
    ):
        self.produit_repository = produit_repository
        self.facture_repository = facture_repository
        self.client_service = client_service

    # =========================================================
    # CREATE
    # =========================================================

    def creer_facture(self, commande, client_data):
        """Crée une nouvelle facture."""
        from facture.generer import generate_invoice

        produits = self.produit_repository.get_all_produits()
        client_data = client_data["client"]
        self.client_service.ajouter_client(
            client_data["nom"],
            client_data["contact"],
            client_data["telephone"],
            client_data["ville"],
            client_data["solde"],
            client_data["matricule_fiscale"]
        )

        ref_facture, nb_lignes, prix_total = (
            self.facture_repository.ajouter_facture(
                client=client_data["nom"],
                articles=commande.articles,
                produits=produits,
                devise=commande.devise,
            )
        )

        if nb_lignes == 0:
            return None

        generate_invoice(commande, ref_facture, client_data)

        return ref_facture

    # =========================================================
    # LIST
    # =========================================================

    def get_all_factures(
        self,
        client: str = None,
        statut: str = None,
        paiement: str = None
    ) -> list[Facture]:
        """Retourne la liste des factures avec filtres optionnels."""
        return self.facture_repository.list_factures(
            client=client,
            statut=statut,
            paiement=paiement,
        )

    # =========================================================
    # READ
    # =========================================================

    def get_facture(self, reference: str) -> Facture | None:
        """Retourne une facture par sa référence."""
        return self.facture_repository.get_facture(reference)

    # =========================================================
    # UPDATE
    # =========================================================

    def update_facture(
        self,
        reference: str,
        statut: str = None,
        paiement: str = None
    ) -> bool:
        """Modifie le statut ou le paiement d'une facture."""
        return self.facture_repository.update_facture(
            reference=reference,
            statut=statut,
            paiement=paiement,
        )

    # =========================================================
    # DELETE
    # =========================================================

    def supprimer_facture(self, reference: str) -> bool:
        """Supprime une facture de l'Excel."""
        return self.facture_repository.supprimer_facture(reference)
