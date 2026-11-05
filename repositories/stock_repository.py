"""Stock/Inventory repository for SmartErp."""

from __future__ import annotations

from datetime import date
from dataclasses import dataclass
from typing import Optional
from openpyxl.utils import range_boundaries

from utils import trouver_table, col, find_first_row
from config import NOM_TABLE_PRODUITS, FEUILLE_PRODUITS


@dataclass
class StockMouvement:
    """Un mouvement de stock (entrée ou sortie)."""
    date: date
    produit: str
    sku: str
    quantite: float
    type_mouvement: str  # "entree" ou "sortie"
    motif: str
    reference: str = ""


class StockRepository:
    """Gère le stock dans l'Excel."""

    def __init__(self, workbook):
        self.wb = workbook
        self.ws, self.table = trouver_table(
            workbook, FEUILLE_PRODUITS, NOM_TABLE_PRODUITS
        )
        self.stock_feuille = None
        self.stock_table = None
        self._ensure_stock_sheet()

    def _ensure_stock_sheet(self):
        """Crée la feuille Stock si elle n'existe pas."""
        if "Stock" not in self.wb.sheetnames:
            ws = self.wb.create_sheet("Stock")
            # En-têtes
            headers = ["SKU", "Produit", "Quantité", "Seuil minimum", "Date dernière mise à jour"]
            for i, header in enumerate(headers, 1):
                ws.cell(row=1, column=i, value=header)
            # Créer une table
            ws.create_table(
                name="TblStock",
                ref=f"A1:E1"
            )
            self.stock_feuille = ws
            self.stock_table = ws.tables["TblStock"]
        else:
            self.stock_feuille = self.wb["Stock"]
            self.stock_table = self.stock_feuille.tables["TblStock"]

    def get_all_stock(self) -> dict[str, StockMouvement]:
        """Récupère tout le stock."""
        stock = {}
        min_col, min_row, max_col, max_row = range_boundaries(self.stock_table.ref)

        c_sku = col("SKU", self.stock_feuille, self.stock_table)
        c_produit = col("Produit", self.stock_feuille, self.stock_table)
        c_qte = col("Quantité", self.stock_feuille, self.stock_table)
        c_seuil = col("Seuil minimum", self.stock_feuille, self.stock_table)
        c_date = col("Date dernière mise à jour", self.stock_feuille, self.stock_table)

        for row in range(min_row, max_row + 1):
            sku = self.stock_feuille.cell(row=row, column=c_sku).value
            if not sku:
                continue

            produit = self.stock_feuille.cell(row=row, column=c_produit).value
            qte = self.stock_feuille.cell(row=row, column=c_qte).value or 0
            seuil = self.stock_feuille.cell(row=row, column=c_seuil).value or 5
            date_maj = self.stock_feuille.cell(row=row, column=c_date).value

            stock[str(sku).strip()] = {
                "sku": str(sku).strip(),
                "produit": str(produit).strip() if produit else "",
                "quantite": float(qte),
                "seuil_minimum": float(seuil),
                "date_maj": date_maj
            }

        return stock

    def update_stock(self, sku: str, quantite: float, motif: str = "") -> bool:
        """Met à jour la quantité d'un produit."""
        stock = self.get_all_stock()

        min_col, min_row, max_col, max_row = range_boundaries(self.stock_table.ref)
        c_sku = col("SKU", self.stock_feuille, self.stock_table)
        c_qte = col("Quantité", self.stock_feuille, self.stock_table)
        c_date = col("Date dernière mise à jour", self.stock_feuille, self.stock_table)

        for row in range(min_row, max_row + 1):
            cell_sku = self.stock_feuille.cell(row=row, column=c_sku).value
            if cell_sku and str(cell_sku).strip().lower() == sku.lower():
                self.stock_feuille.cell(row=row, column=c_qte, value=quantite)
                self.stock_feuille.cell(row=row, column=c_date, value=date.today())
                return True

        # Si le SKU n'existe pas, l'ajouter
        nouvelle_ligne = find_first_row(self.stock_feuille, self.stock_table)
        self.stock_feuille.cell(row=nouvelle_ligne, column=c_sku, value=sku)
        self.stock_feuille.cell(row=nouvelle_ligne, column=c_qte, value=quantite)
        self.stock_feuille.cell(row=nouvelle_ligne, column=c_date, value=date.today())

        # Agrandir la table
        self.stock_table.ref = f"{self.stock_table.ref}:{chr(64 + c_date)}{nouvelle_ligne}"
        return True

    def add_stock(self, sku: str, quantite: float, motif: str = "") -> bool:
        """Ajoute de la quantité au stock."""
        stock = self.get_all_stock()
        current = stock.get(sku, {}).get("quantite", 0)
        return self.update_stock(sku, current + quantite, motif)

    def remove_stock(self, sku: str, quantite: float, motif: str = "") -> bool:
        """Retire de la quantité du stock."""
        stock = self.get_all_stock()
        current = stock.get(sku, {}).get("quantite", 0)
        nouvelle_qte = max(0, current - quantite)
        return self.update_stock(sku, nouvelle_qte, motif)

    def get_low_stock(self, seuil: Optional[float] = None) -> list[dict]:
        """Récupère les produits en stock faible."""
        stock = self.get_all_stock()
        low_stock = []
        for sku, data in stock.items():
            if data["quantite"] <= data["seuil_minimum"]:
                low_stock.append(data)
        return low_stock

    def save(self):
        """Sauvegarde le workbook."""
        self.wb.save(self.wb.filename)
