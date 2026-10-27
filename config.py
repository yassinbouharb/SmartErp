"""
Configuration du bot de facturation
====================================
Tu ne modifies QUE ce fichier si tu changes de PC, de nom de fichier, etc.
"""

import os

# ----------------------------------------------------------------------
# Chemin vers ton fichier Excel ERP
# ----------------------------------------------------------------------
# Sur Windows, ton Desktop est en général : C:\Users\TON_NOM_UTILISATEUR\Desktop
# os.path.expanduser("~") récupère automatiquement ton dossier utilisateur,
# donc pas besoin de taper le chemin complet à la main.

FICHIER_ERP = os.path.join(
    os.path.expanduser("~"),
    "Desktop/L",
    "ERP_Gestion.xlsx"
)

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


