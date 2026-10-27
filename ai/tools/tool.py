from services.facture_service import FactureService
from repositories.produit_repository import ProduitRepository


def Prompt_Maker(history, message, prompt):
    return f"""
    {prompt}
    Historique
    de
    la
    conversation:
    {history}

    Dernier
    message
    utilisateur:
    {message}
    """


class ERPTools:


    def __init__(
        self,
        facture_service,
        produit_repository
    ):
        self.facture_service = facture_service
        self.produit_repository = produit_repository



    def search_product(
        self,
        name:str
    ):

        produits = (
            self.produit_repository
            .get_all_produits()
        )


        result = []

        for nom, produit in produits.items():

            if name.lower() in nom.lower():

                result.append(
                    {
                        "name":nom,
                        "sku":produit.sku,
                        "price":produit.prix
                    }
                )


        return result



    def create_invoice(
        self,
        client:str,
        products:list
    ):

        # ici appel FactureService

        facture = (
            self.facture_service
            .creer_facture(
                client,
                products
            )
        )


        return {
            "status":"success",
            "invoice":facture
        }


