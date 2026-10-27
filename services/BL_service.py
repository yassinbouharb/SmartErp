from BL.generer import generate_invoice


class BLService:

    def __init__(
        self,
        produit_repository,
        BL_repository,
        client_service,
    ):
        self.produit_repository = produit_repository
        self.BL_repository = BL_repository
        self.client_service = client_service

    def creer_BL(self, commande):

        produits = self.produit_repository.get_all_produits()

        ref_BL, nb_lignes, prix_total = (
            self.BL_repository.ajouter_BL(
                client_nom=commande.client,
                articles=commande.articles,
                produits=produits,
                devise=commande.devise,
            )
        )

        if nb_lignes == 0:
            return None


        generate_invoice(commande, ref_BL)

        return ref_BL