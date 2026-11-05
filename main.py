from openpyxl import load_workbook

from ai.agents.client_agent import ClientAgent
from ai.agents.BL_agent import BL_agent
from ai.agents.problem_solving_agent import ProblemSolverAgent
from config import FICHIER_ERP

from ai.gemini_service import GeminiService
from repositories.client_repository import ClientRepository

# Repositories
from repositories.produit_repository import ProduitRepository
from repositories.facture_repository import FactureRepository
from repositories.BL_repository import BLRepository


# Services
from services.client_service import ClientService
from services.facture_service import FactureService
from services.BL_service import BLService


# Agents
from ai.agents.invoice_agent import InvoiceAgent
from ai.agents.product_agent import ProductAgent
from ai.agents.manager_agent import ManagerAgent
from ai.tools.conversation_context import ConversationContext


# ==================================================
# Chargement ERP
# ==================================================

try:
    wb = load_workbook(FICHIER_ERP)
    
    
    # ==================================================
    # Repositories
    # ==================================================
    
    produit_repository = ProduitRepository(wb)
    facture_repository = FactureRepository(wb)
    bl_repository = BLRepository(wb)
    
    
    # ==================================================
    # Services
    # ==================================================
    client_repository=ClientRepository(wb)
    client_service = ClientService(client_repository)
    
    facture_service = FactureService(
        produit_repository,
        facture_repository,
        client_service
    )
    
    bl_service = BLService(
        produit_repository,
        bl_repository,
        client_service
    )
    
    
    # ==================================================
    # Gemini
    # ==================================================
    
    gemini_service = GeminiService()
    
    
    # ==================================================
    # Agents
    # ==================================================
    
    invoice_agent = InvoiceAgent(
        gemini_service,
        facture_service
    )
    
    product_agent = ProductAgent(
        gemini_service=gemini_service,
        product_repository=produit_repository
    )
    
    problem_solver_agent = ProblemSolverAgent(
        gemini_service
    )
    BL_agent = BL_agent(
        gemini_service,
        bl_service
    )
    client_agent = ClientAgent(
        gemini_service,
        client_service
    )
    manager = ManagerAgent(
        gemini_service=gemini_service,
        invoice_agent=invoice_agent,
        product_agent=product_agent,
        client_agent=client_agent,
        problem_solver_agent=problem_solver_agent,
        BL_agent=BL_agent
    )
    
    
    # ==================================================
    # Contexte de conversation
    # ==================================================
    
    catalogue = produit_repository.get_all_produits()
    context = ConversationContext(
        catalogue=catalogue
    
    )
    print(context)
    
    # ==================================================
    # Chat ERP
    # ==================================================
    
    print("🤖 SmartERP Agent démarré")
    print("Tape 'exit' pour quitter.\n")
    
except Exception as e:
    print(f"Erreur lors de l'initialisation de l'ERP : {e}")
    print("Vérifiez que le fichier ERP existe et est accessible.")
    exit(1)

while True:

    message = input("Vous : ").strip()

    if message.lower() == "exit":
        break

    context.add_user_message(message)
    try:

        result = manager.run(
            message=message,
            context=context
        )

        print("\nAgent :", result, "\n")

        context.add_assistant_message(result)

        wb.save(FICHIER_ERP)

    except Exception as e:
        print("Erreur :", e)
