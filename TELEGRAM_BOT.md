# SmartErp Telegram Bot

🤖 **SmartErp Bot** - Assistant ERP pour LYNA SERVICES SARL

## Bot Info
- **Token**: `8722693842:AAF4Jkyyhn5EnDKTp9-UMy3_aMcsDeG-oHQ`
- **Username**: @lyna_services_BOT
- **Status**: ✅ Connecté

## Commandes Disponibles

### Menu Principal
| Commande | Description |
|----------|-------------|
| `/start` | Menu principal |
| `/help` | Aide complète |
| `/products` | Liste des produits |
| `/invoices` | Factures récentes |
| `/bl` | Bons de livraison |
| `/clients` | Liste des clients |
| `/balance` | Solde des clients |
| `/statistics` | Statistiques de vente |
| `/stock` | État du stock |
| `/stock_alerte` | Alertes stock faible |
| `/reappro` | Produits à réapprovisionner |
| `/historique` | Historique client |
| `/bilan` | Bilan comptable |

### Exemples de Commandes Naturelles
```
"Créer une facture pour [client]"
"Produit [nom du produit]"
"Solde de [client]"
"Ajouter 10 unités de [produit]"
"Supprimer 5 unités de [produit]"
"Facture de [client]"
"BL de [client]"
```

## Structure du Projet

```
SmartErp/
├── telegram/
│   ├── config.py          # Token du bot
│   └── bot.py             # Bot principal
├── ai/
│   └── agents/
│       ├── stock_agent.py          # Stock/Inventory
│       ├── client_history_agent.py # Historique clients
│       ├── reports_agent.py        # Rapports & Analytics
│       └── accounting_agent.py     # Comptabilité
├── repositories/
│   └── stock_repository.py        # Stock (Excel)
├── services/
│   └── stock_service.py           # Stock service
└── run_bot.py                     # Lanceur du bot
```

## Démarrage

```bash
# Activer l'environnement virtuel
source .venv/Scripts/activate

# Démarrer le bot
python run_bot.py
# ou
python telegram/bot.py
```

## Modules Ajoutés

### 1. Stock/Inventory
- Suivi des quantités par SKU
- Alertes de stock faible
- Mouvements de stock (entrée/sortie)
- Seuil minimum configurable

### 2. Client History
- Historique complet par client
- Factures et BL par client
- Solde client
- Recherche par nom/code

### 3. Reports & Analytics
- Rapport de ventes global
- Top produits vendus
- Top clients
- Résumé journalier

### 4. Accounting (Comptabilité)
- Bilan simplifié
- Compte client détaillé
- Résultat estimé
- Grand livre simplifié

## Fonctionnement

Le bot utilise votre base Excel existante (`ERP_Gestion.xlsx`) avec:
- Feuille `Clients` - données clients
- Feuille `Ventes` - factures et BL
- Feuille `Produits` - catalogue produits
- Feuille `Stock` - stock (créée automatiquement)

## API Telegram

Pour tester le bot via API:
```
https://api.telegram.org/bot8722693842:AAF4Jkyyhn5EnDKTp9-UMy3_aMcsDeG-oHQ/getMe
```
