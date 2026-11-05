from __future__ import annotations

from models.BonLivraison import BonLivraison
from repositories.produit_repository import ProduitRepository
from repositories.BL_repository import BLRepository
from services.client_service import ClientService


class BLService:

    def __init__(
        self,
        produit_repository: ProduitRepository,
        bl_repository: BLRepository,
        client_service: ClientService,
    ):
        self.produit_repository = produit_repository
        self.bl_repository = bl_repository
        self.client_service = client_service

    # =========================================================
    # CREATE
    # =========================================================

    def creer_BL(self, commande):
        """Crée un nouveau bon de livraison."""
        from BL.generer import generate_bl

        produits = self.produit_repository.get_all_produits()

        ref_BL, nb_lignes, prix_total = (
            self.bl_repository.ajouter_BL(
                client_nom=commande.client,
                articles=commande.articles,
                produits=produits,
                devise=commande.devise,
            )
        )

        if nb_lignes == 0:
            return None

        generate_bl(commande, ref_BL)

        return ref_BL

    # =========================================================
    # LIST
    # =========================================================

    def get_all_BL(
        self,
        client: str = None,
        statut: str = None,
        paiement: str = None
    ) -> list[BonLivraison]:
        """Retourne la liste des BL avec filtres optionnels."""
        return self.bl_repository.list_BL(
            client=client,
            statut=statut,
            paiement=paiement,
        )

    # =========================================================
    # READ
    # =========================================================

    def get_BL(self, reference: str) -> BonLivraison | None:
        """Retourne un BL par sa référence."""
        return self.bl_repository.get_BL(reference)

    # =========================================================
    # UPDATE
    # =========================================================

    def update_BL(
        self,
        reference: str,
        statut: str = None,
        paiement: str = None
    ) -> bool:
        """Modifie le statut ou le paiement d'un BL."""
        return self.bl_repository.update_BL(
            reference=reference,
            statut=statut,
            paiement=paiement,
        )

    # =========================================================
    # DELETE
    # =========================================================

    def supprimer_BL(self, reference: str) -> bool:
        """Supprime un BL de l'Excel."""
        return self.bl_repository.supprimer_BL(reference)
