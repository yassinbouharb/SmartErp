from models.client import Client
from repositories.client_repository import ClientRepository


class ClientService:

    def __init__(self, client_repository):
        self.repo = client_repository

    # ================= ========================================
    # AJOUTER CLIENT
    # =========================================================

    def ajouter_client(
        self,
        nom,
        contact:None,
        telephone:None,
        ville:None,
        montant:0,
        Matricule_fiscale:None
    ):

        row = self.repo.find_by_name(nom)

        if row:
            self.repo.update_balance(row, montant)
            return

        client = Client(
            code=f"CL{self.repo.max_row:04d}",
            nom=nom,
            contact=contact,
            telephone=telephone,
            ville=ville,
            solde=montant,
            matricule_fiscale=Matricule_fiscale,
        )

        self.repo.add(client)

    # =========================================================
    # GET CLIENT
    # =========================================================

    def get_client(self, code: str) -> Client | None:
        """Get a client by its code."""
        return self.repo.get_by_code(code)

    # =========================================================
    # GET CLIENT BY NAME
    # =========================================================

    def get_client_by_name(self, nom: str) -> Client | None:
        """Get a client by its name."""
        return self.repo.get_by_name(nom)

    # =========================================================
    # GET ALL CLIENTS
    # =========================================================

    def get_all_clients(self) -> list[Client]:
        """Get all clients."""
        return self.repo.list_all()

    # =========================================================
    # CREATE
    # =========================================================

    def create_client(self, client: Client) -> bool:
        """Create a new client."""

        existing = self.repo.get_by_code(client.code)

        if existing is not None:
            return False

        self.repo.add(client)

        return True

    # =========================================================
    # UPDATE
    # =========================================================

    def update_client(self, client: Client) -> bool:
        """Update an existing client."""
        return self.repo.update(client)

    # =========================================================
    # DELETE
    # =========================================================

    def delete_client(self, code: str) -> bool:
        """Delete a client by its code."""
        return self.repo.delete(code)

    # =========================================================
    # SEARCH
    # =========================================================

    def search_clients(
        self,
        nom: str = None,
        ville: str = None,
        telephone: str = None,
        contact: str = None,
        matricule_fiscale: str = None,
        code: str = None
    ) -> list[Client]:
        """Search clients using multiple criteria."""

        clients = self.repo.list_all()

        if code:
            code = code.strip().lower()
            clients = [
                c for c in clients
                if c.code and code == c.code.lower()
            ]

        if nom:
            nom = nom.strip().lower()
            clients = [
                c for c in clients
                if c.nom and nom in c.nom.lower()
            ]

        if ville:
            ville = ville.strip().lower()
            clients = [
                c for c in clients
                if c.ville and ville in c.ville.lower()
            ]

        if telephone:
            telephone = telephone.strip()
            clients = [
                c for c in clients
                if c.telephone
                and telephone in str(c.telephone)
            ]

        if contact:
            contact = contact.strip().lower()
            clients = [
                c for c in clients
                if c.contact
                and contact in c.contact.lower()
            ]

        if matricule_fiscale:
            matricule_fiscale = matricule_fiscale.strip().lower()
            clients = [
                c for c in clients
                if c.matricule_fiscale
                and matricule_fiscale in c.matricule_fiscale.lower()
            ]

        return clients

    # =========================================================
    # BALANCE
    # =========================================================


    def get_balance(self, code: str) -> float | None:
        """Get the balance of a client."""

        client = self.get_client(code)

        if client is None:
            return None

        return client.solde
