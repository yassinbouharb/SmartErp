"""
Configuration du bot de facturation
====================================
Tu ne modifies QUE ce fichier si tu changes de PC, de nom de fichier, etc.
"""

import os

# ----------------------------------------------------------------------
# Chemin vers ton fichier Excel ERP
# ----------------------------------------------------------------------
FICHIER_ERP = "/home/ubuntu/SmartErp/ERP_Gestion.xlsx"

# ----------------------------------------------------------------------
# Noms des tables / feuilles dans ton classeur
# ----------------------------------------------------------------------
NOM_TABLE_PRODUITS = "TblProduits"
FEUILLE_PRODUITS="Produits"
FEUILLE_FACTURE = "Ventes"
NOM_TABLE_VENTES = "TblVentes"
FEUILLE_BL = "BL"
NOM_TABLE_BL = "TblBL"
# feuille où sera écrite la facture
DEVISE_PAR_DEFAUT = "TND"
FEUILLE_VENTES = "Ventes"  # nom de l'onglet
NOM_TABLE_Clients = "TblClients"
FEUILLE_Clients = "Clients"  # nom de l'onglet

COMPANY_INFO = {
    "name": "LYNA SERVICES SARL",
    "address": "Tunisie",
    "email": "Tunisiesanitaire@gmail.com",
    "phone": "+216 52200000"
}
