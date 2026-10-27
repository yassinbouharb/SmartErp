
from config import FEUILLE_PRODUITS, NOM_TABLE_PRODUITS
from models.ProduitCatalogue import ProduitCatalogue
from ai.gemini_service import log
from utils import col, trouver_table
from openpyxl.utils import range_boundaries


class ProduitRepository:

    HEADER_ROW = 4

    def __init__(self, workbook):

        self.wb = workbook

        self.ws, self.table = trouver_table(
            workbook,
            FEUILLE_PRODUITS,
            NOM_TABLE_PRODUITS
        )


    def get_all_produits(
        self
    ) -> dict[str, ProduitCatalogue]:

        produits = {}

        min_col, min_row, max_col, max_row = (
            range_boundaries(
                self.table.ref
            )
        )

        idx_desc = col(
            "description",
            self.ws,
            self.table
        )

        idx_price = col(
            "Prix de Vente (TND)",
            self.ws,
            self.table
        )

        idx_sku = col(
            "SKU",
            self.ws,
            self.table
        )

        if idx_desc is None or idx_price is None:

            log.warning(
                "Colonnes produit introuvables"
            )

            return produits


        for row in range(
            min_row + 1,
            max_row + 1
        ):

            description = self.ws.cell(
                row=row,
                column=idx_desc
            ).value

            prix = self.ws.cell(
                row=row,
                column=idx_price
            ).value


            if idx_sku:

                sku = self.ws.cell(
                    row=row,
                    column=idx_sku
                ).value

            else:

                sku = "1"


            if not description or prix is None:

                continue


            try:

                produit = ProduitCatalogue(
                    description=str(
                        description
                    ).strip(),

                    sku=str(
                        sku
                    ).strip()
                    if sku
                    else "",

                    prix=float(
                        prix
                    )
                )


                produits[
                    produit.description
                ] = produit


            except (
                TypeError,
                ValueError
            ) as exc:

                log.warning(
                    "Ligne produit ignorée (%s) : %s",
                    description,
                    exc
                )

        return produits


    def rechercher_produit(
        self,
        recherche: str
    ) -> list[ProduitCatalogue]:

        produits = self.get_all_produits()

        recherche = (
            recherche
            .strip()
            .lower()
        )

        resultats = []

        for produit in produits.values():

            description = (
                produit.description
                .strip()
                .lower()
            )

            sku = (
                produit.sku
                .strip()
                .lower()
            )

            if (
                recherche in description
                or recherche in sku
            ):

                resultats.append(
                    produit
                )

        return resultats


    def obtenir_produit(
        self,
        nom: str
    ) -> ProduitCatalogue | None:

        produits = self.get_all_produits()

        nom = (
            nom
            .strip()
            .lower()
        )

        for produit in produits.values():

            if (
                produit.description
                .strip()
                .lower()
                == nom
            ):

                return produit


        return None


    def obtenir_prix(
        self,
        nom: str
    ) -> float | None:

        produit = self.obtenir_produit(
            nom
        )

        if not produit:

            return None

        return produit.prix
