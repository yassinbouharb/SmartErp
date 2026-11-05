#!/usr/bin/env python3
"""
SmartErp Telegram Bot
Deploy: python3 telegram/bot.py
"""

import sys
import os
import logging
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
os.chdir(str(PROJECT_ROOT))

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import FICHIER_ERP
from ai.gemini_service import GeminiService
from ai.agents.manager_agent import ManagerAgent
from ai.tools.conversation_context import ConversationContext
from repositories.produit_repository import ProduitRepository
from repositories.facture_repository import FactureRepository
from repositories.BL_repository import BLRepository
from repositories.client_repository import ClientRepository
from repositories.stock_repository import StockRepository
from services.facture_service import FactureService
from services.BL_service import BLService
from services.client_service import ClientService
from services.stock_service import StockService
from ai.agents.invoice_agent import InvoiceAgent
from ai.agents.product_agent import ProductAgent
from ai.agents.BL_agent import BL_agent as BLAgent
from ai.agents.client_agent import ClientAgent
from ai.agents.problem_solving_agent import ProblemSolverAgent
from ai.agents.stock_agent import StockAgent
from ai.agents.client_history_agent import ClientHistoryAgent
from ai.agents.reports_agent import ReportsAgent
from ai.agents.accounting_agent import AccountingAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load ERP workbook
wb = None
manager = None
catalogue = {}
stock_agent = None
client_history_agent = None
reports_agent = None
accounting_agent = None

try:
    from openpyxl import load_workbook
    wb = load_workbook(FICHIER_ERP)

    produit_repo = ProduitRepository(wb)
    facture_repo = FactureRepository(wb)
    bl_repo = BLRepository(wb)
    client_repo = ClientRepository(wb)
    stock_repo = StockRepository(wb)

    client_service = ClientService(client_repo)
    facture_service = FactureService(produit_repo, facture_repo, client_service)
    bl_service = BLService(produit_repo, bl_repo, client_service)
    stock_service = StockService(stock_repo, produit_repo)

    gemini = GeminiService()

    invoice_agent = InvoiceAgent(gemini, facture_service)
    product_agent = ProductAgent(gemini, produit_repo)
    bl_agent = BLAgent(gemini, bl_service)
    client_agent = ClientAgent(gemini, client_service)
    problem_solver = ProblemSolverAgent(gemini)
    stock_agent = StockAgent(gemini, stock_service)
    client_history_agent = ClientHistoryAgent(gemini, client_service, facture_service, bl_service)
    reports_agent = ReportsAgent(gemini, facture_service, bl_service, client_service, stock_service)
    accounting_agent = AccountingAgent(gemini, facture_service, client_service, stock_service)

    manager = ManagerAgent(
        gemini_service=gemini,
        invoice_agent=invoice_agent,
        product_agent=product_agent,
        client_agent=client_agent,
        problem_solver_agent=problem_solver,
        BL_agent=bl_agent
    )

    catalogue = produit_repo.get_all_produits()
    logger.info(f"SmartErp Telegram bot initialized - {len(catalogue)} products, {len(client_service.get_all_clients())} clients")

except Exception as e:
    logger.error(f"Failed to initialize SmartErp: {e}")
    import traceback
    traceback.print_exc()


# FSM States
class UserState(StatesGroup):
    WAITING_FOR_CLIENT = State()
    WAITING_FOR_PRODUCT = State()
    WAITING_FOR_MESSAGE = State()


# Create dispatcher
dp = Dispatcher()

# Bot token
BOT_TOKEN = "8722693842:AAF4Jkyyhn5EnDKTp9-UMy3_aMcsDeG-oHQ"
bot = Bot(token=BOT_TOKEN)


@dp.message(Command("start"))
async def cmd_start(message: Message):
    welcome_text = """
🤖 *SmartErp Bot*

Bienvenue ! Je suis votre assistant ERP pour LYNA SERVICES.

*Commandes :*
/start - Menu principal
/help - Aide
/products - Liste des produits
/invoices - Factures récentes
/bl - Bons de livraison
/clients - Liste des clients
/balance - Solde client
/stock - État du stock
/statistics - Statistiques
/historique - Historique client
/bilan - Bilan comptable

*Exemples :*
"Créer une facture pour [client]"
"Produit [nom]"
"Solde de [client]"
"""
    await message.answer(welcome_text, parse_mode="Markdown")


@dp.message(Command("help"))
async def cmd_help(message: Message):
    help_text = """
📋 *Aide SmartErp*

*Factures :* Créer, voir, rechercher
*BL :* Créer, voir, rechercher
*Produits :* Rechercher, lister
*Clients :* Créer, solde, historique
*Stock :* Ajouter, retirer, alertes
*Comptabilité :* Bilan, résultat, compte client

Exemple: "Créer facture pour ABC"
"""
    await message.answer(help_text, parse_mode="Markdown")


@dp.message(Command("products"))
async def cmd_products(message: Message):
    if not catalogue:
        await message.answer("❌ Aucun produit")
        return
    products_list = []
    for name, prod in catalogue.items():
        products_list.append(f"• *{name}*\n  SKU: {prod.sku} | Prix: {prod.prix} TND")
    full_text = "\n\n".join(products_list[:20])
    if len(products_list) > 20:
        full_text += f"\n\n... et {len(products_list) - 20} autres"
    await message.answer(f"📦 *Produits* ({len(products_list)})\n\n{full_text}", parse_mode="Markdown")


@dp.message(Command("invoices"))
async def cmd_invoices(message: Message):
    if not manager:
        await message.answer("❌ ERP non initialisé")
        return
    result = manager.run("liste les factures", ConversationContext(catalogue=catalogue))
    response = result.get("message", str(result))
    await message.answer(f"📄 *Factures*\n\n{response}")


@dp.message(Command("bl"))
async def cmd_bl(message: Message):
    if not manager:
        await message.answer("❌ ERP non initialisé")
        return
    result = manager.run("liste les bons de livraison", ConversationContext(catalogue=catalogue))
    response = result.get("message", str(result))
    await message.answer(f"🚚 *BL*\n\n{response}")


@dp.message(Command("clients"))
async def cmd_clients(message: Message):
    if not manager:
        await message.answer("❌ ERP non initialisé")
        return
    result = manager.run("liste tous les clients", ConversationContext(catalogue=catalogue))
    response = result.get("message", str(result))
    await message.answer(f"👥 *Clients*\n\n{response}")


@dp.message(Command("balance"))
async def cmd_balance(message: Message):
    if not manager:
        await message.answer("❌ ERP non initialisé")
        return
    result = manager.run("solde des clients", ConversationContext(catalogue=catalogue))
    response = result.get("message", str(result))
    await message.answer(f"💰 *Soldes*\n\n{response}")


@dp.message(Command("statistics"))
async def cmd_statistics(message: Message):
    if not reports_agent:
        await message.answer("❌ Module stats non initialisé")
        return
    result = reports_agent.run("statistiques de vente")
    response = result.get("message", str(result))
    await message.answer(f"📊 *Statistiques*\n\n{response}")


@dp.message(Command("stock"))
async def cmd_stock(message: Message):
    if not stock_agent:
        await message.answer("❌ Module stock non initialisé")
        return
    result = stock_agent.run("liste tout le stock")
    response = result.get("message", str(result))
    await message.answer(response)


@dp.message(Command("stock_alerte"))
async def cmd_stock_alerte(message: Message):
    if not stock_agent:
        await message.answer("❌ Module stock non initialisé")
        return
    result = stock_agent.run("alertes stock faible")
    response = result.get("message", str(result))
    await message.answer(response)


@dp.message(Command("historique"))
async def cmd_historique(message: Message):
    if not client_history_agent:
        await message.answer("❌ Module historique non initialisé")
        return
    result = client_history_agent.run("historique client")
    response = result.get("message", str(result))
    await message.answer(response)


@dp.message(Command("bilan"))
async def cmd_bilan(message: Message):
    if not accounting_agent:
        await message.answer("❌ Module comptabilité non initialisé")
        return
    result = accounting_agent.run("bilan")
    response = result.get("message", str(result))
    await message.answer(response)


@dp.message()
async def handle_message(message: Message, state: FSMContext):
    if not manager:
        await message.answer("❌ ERP non disponible")
        return

    user_message = message.text.strip()
    context = ConversationContext(catalogue=catalogue)

    try:
        result = manager.run(message=user_message, context=context)
        response = result.get("message", str(result))

        if len(response) > 4000:
            chunks = [response[i:i+4000] for i in range(0, len(response), 4000)]
            for i, chunk in enumerate(chunks):
                if i == 0:
                    await message.answer(chunk)
                else:
                    await message.answer(f"(suite {i+1})\n{chunk}")
        else:
            await message.answer(response)

    except Exception as e:
        logger.error(f"Error: {e}")
        await message.answer(f"❌ Erreur: {str(e)}")


async def main():
    logger.info("Starting SmartErp Telegram bot...")
    print("🤖 Bot démarré ! Envoyez /start sur Telegram")
    await dp.start_polling(bot)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
