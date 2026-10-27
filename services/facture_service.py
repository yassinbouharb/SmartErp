from google.genai._gaos.types.agents import agent

from facture.generer import generate_invoice


class FactureService:

    def __init__(
        self,
        produit_repository,
        facture_repository,
        client_service,
    ):
        self.produit_repository = produit_repository
        self.facture_repository = facture_repository
        self.client_service = client_service

    def creer_facture(self, commande,client_data):

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
                client= client_data["nom"],
                articles=commande.articles,
                produits=produits,
                devise=commande.devise,
            )
        )

        if nb_lignes == 0:
            return None

        print("commande",commande)
        generate_invoice(commande, ref_facture,client_data)

        return ref_facture