from openpyxl.utils import range_boundaries


def trouver_table(wb, nom_feuille: str, nom_table: str):
    """Retourne (feuille, table) en gérant le bug openpyxl où tables.items()
    peut renvoyer des chaînes de ref au lieu d'objets Table."""
    feuille = wb[nom_feuille]
    for nom, tbl in feuille.tables.items():
        if nom == nom_table:
            if hasattr(tbl, "ref"):
                return feuille, tbl
            # bug connu : tbl est une simple chaîne "A4:J20" -> on va la chercher
            # via l'objet officiel de la feuille
            return feuille, feuille.tables[nom_table]
    raise ValueError(f"Table '{nom_table}' introuvable dans la feuille '{nom_feuille}'")


def find_first_row( feuille, table):
    min_col, min_row, max_col, max_row = range_boundaries(table.ref)

    ligne_depart=max_row+1
    for r in range(min_row + 1, max_row + 1):

        ligne_vide = all(
            feuille.cell(r, c).value is None
            for c in range(min_col, max_col + 1)
        )

        if ligne_vide:
            ligne_depart = r
            break
    return ligne_depart


def col(nom,feuille,table):
        min_col, min_row, max_col, max_row = range_boundaries(table.ref)

        headers = {}

        for c in range(min_col, max_col + 1):
            valeur = feuille.cell(min_row, c).value
            if valeur:
                headers[str(valeur).strip().lower()] = c
        for h, c in headers.items():
            if nom.lower() in h:
                return c
        return None


