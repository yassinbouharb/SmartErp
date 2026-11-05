from __future__ import annotations

from datetime import date
from openpyxl.utils import range_boundaries

from ai.gemini_service import log
from config import FEUILLE_VENTES, NOM_TABLE_VENTES
from models.BonLivraison import BonLivraison, LigneBL
from utils import trouver_table, col, find_first_row


class BLRepository:

    def __init__(self, workbook):
        self.wb = workbook

    # =========================================================
    # ADD
    # =========================================================

    def ajouter_BL(
        self,
        client_nom,
        articles,
        produits,
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

    # =========================================================
    # NEXT REF
    # =========================================================

    def prochaine_ref_BL(
        self,
        feuille,
        table
    ):
        min_col, min_row, max_col, max_row = range_boundaries(
            table.ref
        )

        prefixe = f"BL-{date.today().strftime('%Y')}"

        compteur = 0

        for row in feuille.iter_rows(
            min_row=min_row + 1,
            max_row=max_row,
            min_col=min_col,
            max_col=min_col
        ):
            valeur = row[0].value
            if valeur and str(valeur).startswith(prefixe):
                compteur += 1

        return f"{prefixe}-{compteur + 1:02d}"

    # =========================================================
    # LIST
    # =========================================================

    def list_BL(
        self,
        client: str = None,
        statut: str = None,
        paiement: str = None
    ) -> list[BonLivraison]:
        """Retourne tous les BL, avec filtres optionnels."""
        feuille, table = trouver_table(
            self.wb,
            FEUILLE_VENTES,
            NOM_TABLE_VENTES
        )

        min_col, min_row, max_col, max_row = range_boundaries(
            table.ref
        )

        c_ref = col("ref", feuille, table)
        c_date = col("date", feuille, table)
        c_client = col("client", feuille, table)
        c_statut = col("statut", feuille, table)
        c_paiement = col("paiement", feuille, table)

        bl_map: dict[str, BonLivraison] = {}

        for row in range(min_row + 1, max_row + 1):
            ref = feuille.cell(row=row, column=c_ref).value
            if not ref:
                continue

            if ref not in bl_map:
                bl_map[ref] = BonLivraison(
                    reference=str(ref).strip(),
                    date=feuille.cell(row=row, column=c_date).value or date.today(),
                    client=str(feuille.cell(row=row, column=c_client).value or ""),
                    statut=str(feuille.cell(row=row, column=c_statut).value or "En attente"),
                    paiement=str(feuille.cell(row=row, column=c_paiement).value or "Non payé"),
                )

            lignes = bl_map[ref].lignes
            lignes.append(LigneBL(
                ref=str(ref).strip(),
                date=feuille.cell(row=row, column=c_date).value or date.today(),
                client=str(feuille.cell(row=row, column=c_client).value or ""),
                sku=str(feuille.cell(row=row, column=col("sku", feuille, table)).value or ""),
                description=str(feuille.cell(row=row, column=col("description", feuille, table)).value or ""),
                quantite=feuille.cell(row=row, column=col("quantite", feuille, table)).value or 0,
                prix_unitaire=feuille.cell(row=row, column=col("prix unitaire", feuille, table)).value or 0,
                montant_total=feuille.cell(row=row, column=col("montant total", feuille, table)).value or 0,
                statut=str(feuille.cell(row=row, column=c_statut).value or "En attente"),
                paiement=str(feuille.cell(row=row, column=c_paiement).value or "Non payé"),
            ))

        result = list(bl_map.values())

        if client:
            client_search = client.strip().lower()
            result = [b for b in result if client_search in b.client.lower()]

        if statut:
            statut_search = statut.strip().lower()
            result = [b for b in result if statut_search in b.statut.lower()]

        if paiement:
            paiement_search = paiement.strip().lower()
            result = [b for b in result if paiement_search in b.paiement.lower()]

        return result

    # =========================================================
    # GET
    # =========================================================

    def get_BL(self, reference: str) -> BonLivraison | None:
        """Retourne un BL par sa référence, ou None si introuvable."""
        bl_list = self.list_BL()
        for b in bl_list:
            if b.reference.lower() == reference.strip().lower():
                return b
        return None

    # =========================================================
    # UPDATE
    # =========================================================

    def update_BL(
        self,
        reference: str,
        statut: str = None,
        paiement: str = None
    ) -> bool:
        """Modifie le statut ou le mode de paiement d'un BL."""
        feuille, table = trouver_table(
            self.wb,
            FEUILLE_VENTES,
            NOM_TABLE_VENTES
        )

        c_ref = col("ref", feuille, table)
        c_statut = col("statut", feuille, table)
        c_paiement = col("paiement", feuille, table)

        if c_ref is None:
            return False

        found = False
        for row in range(feuille.min_row, feuille.max_row + 1):
            cell_ref = feuille.cell(row=row, column=c_ref).value
            if cell_ref and str(cell_ref).strip().lower() == reference.strip().lower():
                found = True
                if statut:
                    feuille.cell(row=row, column=c_statut, value=statut)
                if paiement:
                    feuille.cell(row=row, column=c_paiement, value=paiement)

        return found

    # =========================================================
    # DELETE
    # =========================================================

    def supprimer_BL(self, reference: str) -> bool:
        """Supprime toutes les lignes d'un BL."""
        feuille, table = trouver_table(
            self.wb,
            FEUILLE_VENTES,
            NOM_TABLE_VENTES
        )

        c_ref = col("ref", feuille, table)
        if c_ref is None:
            return False

        rows_to_clear: list[int] = []
        for row in range(feuille.min_row, feuille.max_row + 1):
            cell_ref = feuille.cell(row=row, column=c_ref).value
            if cell_ref and str(cell_ref).strip().lower() == reference.strip().lower():
                rows_to_clear.append(row)

        if not rows_to_clear:
            return False

        min_col, _, max_col, _ = range_boundaries(table.ref)
        for row in rows_to_clear:
            for c in range(min_col, max_col + 1):
                feuille.cell(row=row, column=c, value=None)

        log.info("BL %s supprimé (%d lignes)", reference, len(rows_to_clear))
        return True
