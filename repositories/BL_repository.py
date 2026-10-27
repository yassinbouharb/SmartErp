from datetime import date
from openpyxl.utils import range_boundaries

from ai.gemini_service import log
from config import FEUILLE_VENTES, NOM_TABLE_VENTES
from utils import trouver_table, col, find_first_row


class BLRepository:


    def __init__(self, workbook):
        self.wb = workbook



    def ajouter_BL(
        self,
        client_nom,
        articles,
        devise="TND"
    ):

        feuille, table = trouver_table(
            self.wb,
            FEUILLE_VENTES,
            NOM_TABLE_VENTES
        )


        ref_BL = self.prochaine_ref_BL(
            feuille,
            table
        )


        c_ref = col("ref", feuille, table)
        c_date = col("date", feuille, table)
        c_client = col("client", feuille, table)
        c_sku = col("sku", feuille, table)
        c_desc = col("description", feuille, table)
        c_qte = col("quantite", feuille, table)
        c_prix = col("prix unitaire", feuille, table)
        c_total = col("montant total", feuille, table)
        c_statut = col("statut", feuille, table)
        c_paiement = col("paiement", feuille, table)


        ligne = find_first_row(
            feuille,
            table
        )


        total = 0
        nb_lignes = 0


        catalogue = {
            str(k).strip().lower(): v
            for k, v in produits.items()
        }


        for article in articles:

            nom = article.nom_produit.strip()


            produit = catalogue.get(
                nom.lower()
            )


            if not produit:
                log.warning(
                    "Produit introuvable : %s",
                    nom
                )
                continue



            prix = (
                article.prix_unitaire
                if article.prix_unitaire is not None
                else produit.prix
            )


            montant = round(
                article.quantite * prix,
                3
            )


            valeurs = {

                c_ref: ref_BL,
                c_date: date.today(),
                c_client: client_nom,
                c_sku: produit.sku,
                c_desc: nom,
                c_qte: article.quantite,
                c_prix: prix,
                c_total: montant,
                c_statut: "En attente",
                c_paiement: "Non payé"

            }


            for colonne, valeur in valeurs.items():

                if colonne:
                    feuille.cell(
                        row=ligne,
                        column=colonne,
                        value=valeur
                    )


            total += montant
            nb_lignes += 1
            ligne += 1



        return ref_BL, nb_lignes, total




    def prochaine_ref_BL(
        self,
        feuille,
        table
    ):

        min_col, min_row, max_col, max_row = range_boundaries(
            table.ref
        )


        prefixe = f"FAC-{date.today().strftime('%Y')}"


        compteur = 0

        valeur=prefixe
        for row in feuille.iter_rows(
            min_row=min_row + 1,
            max_row=max_row,
            min_col=min_col,
            max_col=min_col
        ):



            if valeur!=row[0].value and str(valeur).startswith(prefixe):
                compteur += 1
            valeur = row[0].value

        return f"{prefixe}-{compteur + 1:02d}"