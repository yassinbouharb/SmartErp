from openpyxl.utils import range_boundaries, get_column_letter

from config import FEUILLE_Clients, NOM_TABLE_Clients
from utils import trouver_table, col, find_first_row
from models.client import Client


class ClientRepository:

    def __init__(self, workbook):
        self.wb = workbook

        # =====================================================
        # FEUILLE + TABLE
        # =====================================================

        self.ws, self.table = trouver_table(
            workbook,
            FEUILLE_Clients,
            NOM_TABLE_Clients
        )

        # =====================================================
        # COLONNES
        # =====================================================

        self.c_code = col(
            "code",
            self.ws,
            self.table
        )

        self.c_nom = col(
            "nom",
            self.ws,
            self.table
        )

        self.c_contact = col(
            "contact",
            self.ws,
            self.table
        )

        self.c_tel = col(
            "telephone",
            self.ws,
            self.table
        )

        self.c_ville = col(
            "ville",
            self.ws,
            self.table
        )

        self.c_solde = col(
            "solde",
            self.ws,
            self.table
        )

        self.c_matricule_fiscale = col(
            "matricule fiscale",
            self.ws,
            self.table
        )

        # =====================================================
        # VERIFICATION DES COLONNES
        # =====================================================

        colonnes = {
            "code": self.c_code,
            "nom": self.c_nom,
            "contact": self.c_contact,
            "telephone": self.c_tel,
            "ville": self.c_ville,
            "solde": self.c_solde,
            "matricule fiscale": self.c_matricule_fiscale,
        }

        for nom_colonne, numero_colonne in colonnes.items():

            if numero_colonne is None:
                raise ValueError(
                    f"Colonne '{nom_colonne}' introuvable "
                    f"dans la table '{NOM_TABLE_Clients}'."
                )

        # =====================================================
        # LIMITES DE LA TABLE
        # =====================================================

        (
            self.min_col,
            self.min_row,
            self.max_col,
            self.max_row
        ) = range_boundaries(
            self.table.ref
        )

        print(
            f"[ClientRepository] "
            f"Feuille={self.ws.title} | "
            f"Table={self.table.name} | "
            f"Ref={self.table.ref}"
        )

        print(
            f"[ClientRepository] "
            f"Lignes clients : "
            f"{self.min_row + 1} -> {self.max_row}"
        )

    # =========================================================
    # FIND BY NAME
    # =========================================================

    def find_by_name(self, nom: str):

        for row in range(
            self.min_row + 1,
            self.max_row + 1
        ):

            nom_excel = self.ws.cell(
                row=row,
                column=self.c_nom
            ).value

            if (
                nom_excel
                and str(nom_excel).strip().lower()
                == nom.strip().lower()
            ):
                return row

        return None

    # =========================================================
    # UPDATE BALANCE
    # =========================================================

    def update_balance(
        self,
        row: int,
        montant: float
    ):

        ancien = (
            self.ws.cell(
                row=row,
                column=self.c_solde
            ).value
            or 0
        )

        self.ws.cell(
            row=row,
            column=self.c_solde,
            value=float(ancien) + float(montant)
        )

    # =========================================================
    # ADD
    # =========================================================

    def add(self, client: Client):

        nouvelle_ligne = find_first_row(
            self.ws,
            self.table
        )

        valeurs = {
            self.c_code: client.code,
            self.c_nom: client.nom,
            self.c_contact: client.contact,
            self.c_tel: client.telephone,
            self.c_ville: client.ville,
            self.c_solde: client.solde,
            self.c_matricule_fiscale: client.matricule_fiscale,
        }

        for colonne, valeur in valeurs.items():

            self.ws.cell(
                row=nouvelle_ligne,
                column=colonne,
                value=valeur
            )

        # Agrandir la table
        self.table.ref = (
            f"{get_column_letter(self.min_col)}"
            f"{self.min_row}:"
            f"{get_column_letter(self.max_col)}"
            f"{nouvelle_ligne}"
        )

        # Mettre à jour max_row
        self.max_row = nouvelle_ligne

    # =========================================================
    # GET BY CODE
    # =========================================================

    def get_by_code(
        self,
        code: str
    ) -> Client | None:

        if not code:
            return None

        code = str(code).strip().lower()

        for row in range(
            self.min_row + 1,
            self.max_row + 1
        ):

            cell_value = self.ws.cell(
                row=row,
                column=self.c_code
            ).value

            if (
                cell_value
                and str(cell_value).strip().lower()
                == code
            ):
                return self._row_to_client(row)

        return None

    # =========================================================
    # GET BY NAME
    # =========================================================

    def get_by_name(
        self,
        nom: str
    ) -> Client | None:

        row = self.find_by_name(nom)

        if row is not None:
            return self._row_to_client(row)

        return None

    # =========================================================
    # UPDATE
    # =========================================================

    def update(
        self,
        client: Client
    ) -> bool:

        row = None

        for r in range(
            self.min_row + 1,
            self.max_row + 1
        ):

            cell_value = self.ws.cell(
                row=r,
                column=self.c_code
            ).value

            if (
                cell_value
                and str(cell_value).strip()
                == str(client.code).strip()
            ):
                row = r
                break

        if row is None:
            return False

        valeurs = {
            self.c_code: client.code,
            self.c_nom: client.nom,
            self.c_contact: client.contact,
            self.c_tel: client.telephone,
            self.c_ville: client.ville,
            self.c_solde: client.solde,
            self.c_matricule_fiscale: client.matricule_fiscale,
        }

        for colonne, valeur in valeurs.items():

            self.ws.cell(
                row=row,
                column=colonne,
                value=valeur
            )

        return True

    # =========================================================
    # DELETE
    # =========================================================

    def delete(
        self,
        code: str
    ) -> bool:

        row = None

        for r in range(
            self.min_row + 1,
            self.max_row + 1
        ):

            cell_value = self.ws.cell(
                row=r,
                column=self.c_code
            ).value

            if (
                cell_value
                and str(cell_value).strip()
                == str(code).strip()
            ):
                row = r
                break

        if row is None:
            return False

        colonnes = [
            self.c_code,
            self.c_nom,
            self.c_contact,
            self.c_tel,
            self.c_ville,
            self.c_solde,
            self.c_matricule_fiscale,
        ]

        for colonne in colonnes:

            self.ws.cell(
                row=row,
                column=colonne,
                value=""
            )

        return True

    # =========================================================
    # LIST ALL
    # =========================================================

    def list_all(self) -> list[Client]:

        clients = []

        print(
            f"[ClientRepository] list_all() "
            f"table={self.table.ref}"
        )

        for row in range(
            self.min_row + 1,
            self.max_row + 1
        ):

            code = self.ws.cell(
                row=row,
                column=self.c_code
            ).value

            nom = self.ws.cell(
                row=row,
                column=self.c_nom
            ).value

            print(
                f"[ClientRepository] "
                f"row={row} | "
                f"code={code!r} | "
                f"nom={nom!r}"
            )

            client = self._row_to_client(row)

            if client is not None:
                clients.append(client)

        print(
            f"[ClientRepository] "
            f"{len(clients)} client(s) trouvé(s)"
        )

        return clients

    # =========================================================
    # ROW -> CLIENT
    # =========================================================

    def _row_to_client(
        self,
        row: int
    ) -> Client | None:

        code = self.ws.cell(
            row=row,
            column=self.c_code
        ).value

        nom = self.ws.cell(
            row=row,
            column=self.c_nom
        ).value

        # Ligne vide
        if not code or not nom:
            return None

        contact = self.ws.cell(
            row=row,
            column=self.c_contact
        ).value or ""

        telephone = self.ws.cell(
            row=row,
            column=self.c_tel
        ).value or ""

        ville = self.ws.cell(
            row=row,
            column=self.c_ville
        ).value or ""

        solde = self.ws.cell(
            row=row,
            column=self.c_solde
        ).value

        matricule_fiscale = self.ws.cell(
            row=row,
            column=self.c_matricule_fiscale
        ).value or ""

        # Solde vide
        if solde is None or solde == "":
            solde = 0.0

        try:
            solde = float(solde)
        except (TypeError, ValueError):

            print(
                f"[ClientRepository] "
                f"Solde invalide ligne {row}: {solde!r}"
            )

            solde = 0.0

        try:

            client = Client(
                code=str(code).strip(),
                nom=str(nom).strip(),
                contact=str(contact).strip(),
                telephone=str(telephone).strip(),
                ville=str(ville).strip(),
                solde=solde,
                matricule_fiscale=str(
                    matricule_fiscale
                ).strip()
            )

            return client

        except Exception as e:

            # IMPORTANT :
            # On affiche maintenant l'erreur au lieu
            # de la cacher silencieusement.

            print(
                f"[ClientRepository] "
                f"ERREUR ligne {row}: {e}"
            )

            print(
                f"  code={code!r}"
            )

            print(
                f"  nom={nom!r}"
            )

            print(
                f"  contact={contact!r}"
            )

            print(
                f"  telephone={telephone!r}"
            )

            print(
                f"  ville={ville!r}"
            )

            print(
                f"  solde={solde!r}"
            )

            print(
                f"  matricule_fiscale="
                f"{matricule_fiscale!r}"
            )

            return None

